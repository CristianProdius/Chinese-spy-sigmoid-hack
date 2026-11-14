"""Parallel evaluation harness for a main.py-format agent (same stdin/stdout protocol as arena.py).

    pypy3/python3 eval.py AGENT.py [--maps 48] [--seed 20261114] [--jobs 6] [--games 0,1,2,3,4]
                                   [--groups 0,1,...] [--cases FILE.json] [--out results.json] [--quiet]

Maps: like arena.py, map m gets group GROUPS[m % 8] and a seed drawn from random.Random(--seed),
so a fixed --seed gives the same maps every run. Every map is played for each game index in --games
(default all 5) and counts by its worst game. --cases FILE plays exact (group, seed, game) entries
instead (e.g. ../../train-input.json); then every case is its own "map".

Each worker owns one engine process and one agent process (agent under PyPy by default, both under
`nice`) and pulls games from a shared queue, so module globals in the agent survive across games as
in the real evaluation. Thinking time per game is measured as wall time between sending an
observation and reading the action, and as the agent process's CPU time (utime+stime from /proc).
An illegal action, crash, bad JSON or timeout scores the game as a loss and restarts the agent.
"""
import argparse
import json
import os
import queue
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENGINE = ROOT / 'mozambique-engine'
PYPY = '/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3'
GROUPS = [2 * topology + seat for topology in range(4) for seat in range(2)]
CLK = os.sysconf('SC_CLK_TCK')
DECISION_TIMEOUT = 30.0   # hard per-decision wall cap in the harness (machine is loaded; the real cap is CPU 10 s/game)


def proc_cpu(pid):
    try:
        with open('/proc/%d/stat' % pid) as f:
            parts = f.read().rsplit(')', 1)[1].split()
        return (int(parts[11]) + int(parts[12])) / CLK
    except (OSError, IndexError, ValueError):
        return 0.0


class Engine:
    def __init__(self, nice):
        self.p = subprocess.Popen(['nice', '-n', str(nice), str(ENGINE)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, encoding='utf-8', bufsize=1)

    def request(self, command, **data):
        self.p.stdin.write(json.dumps(dict(command=command, **data)) + '\n')
        self.p.stdin.flush()
        line = self.p.stdout.readline()
        if not line:
            raise RuntimeError('engine stopped')
        res = json.loads(line)
        if 'error' in res:
            raise RuntimeError('engine error: %s' % res['error'])
        return res

    def close(self):
        if self.p.poll() is None:
            try:
                self.p.stdin.write('{"command":"quit"}\n')
                self.p.stdin.flush()
                self.p.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                self.p.kill()


class AgentProc:
    def __init__(self, script, python, nice):
        path = Path(script).resolve()
        self.p = subprocess.Popen(['nice', '-n', str(nice), python, path.name], cwd=str(path.parent),
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, bufsize=1)
        self.games_played = 0
        self.lines = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for line in self.p.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def cpu(self):
        return proc_cpu(self.p.pid)

    def ask(self, observation):
        self.p.stdin.write(json.dumps({'observation': observation}) + '\n')
        self.p.stdin.flush()
        try:
            line = self.lines.get(timeout=DECISION_TIMEOUT)
        except queue.Empty:
            raise RuntimeError('timeout')
        if line is None:
            raise RuntimeError('agent crashed')
        return json.loads(line)

    def close(self):
        if self.p.poll() is None:
            try:
                self.p.stdin.close()
                self.p.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                self.p.kill()


def play_game(engine, agent, task):
    state = engine.request('reset', group=task['group'], seed=task['seed'], game=task['game'])
    obs0 = state['observation']
    rec = dict(task)
    rec['obs_seat'] = obs0['seat']
    rec['first_in_process'] = agent.games_played == 0
    wall = 0.0
    cpu0 = agent.cpu()
    max_decision = 0.0
    error = None
    rounds = 0
    claim_round = [None] * len(obs0['claims'])
    claim_by = [None] * len(obs0['claims'])
    while not state['game_done']:
        obs = state['observation']
        for c, who in enumerate(obs['claims']):
            if who != -1 and claim_round[c] is None:
                claim_round[c] = obs['round'] - 1
                claim_by[c] = 'U' if who == obs0['seat'] else 'P'
        t = time.monotonic()
        try:
            action = agent.ask(obs)
        except (RuntimeError, ValueError, OSError) as e:
            error = 'agent: %s' % e
            break
        dt = time.monotonic() - t
        wall += dt
        max_decision = max(max_decision, dt)
        if action not in obs['legal_actions']:
            error = 'illegal action at round %d: %s' % (obs['round'], json.dumps(action))
            break
        try:
            state = engine.request('step', action=action)
        except RuntimeError as e:
            error = str(e)
            break
        rounds += 1
    if state.get('observation'):
        for c, who in enumerate(state['observation']['claims']):
            if who != -1 and claim_round[c] is None:
                claim_round[c] = state['observation']['round'] - 1
                claim_by[c] = 'U' if who == obs0['seat'] else 'P'
    rec['claim_round'] = claim_round
    rec['claim_by'] = ''.join(x or '.' for x in claim_by)
    rec['cpu'] = round(agent.cpu() - cpu0, 3)
    rec['wall'] = round(wall, 3)
    rec['max_decision'] = round(max_decision, 3)
    rec['rounds'] = rounds
    agent.games_played += 1
    if error:
        rec['error'] = error
        rec['scores'] = None
        rec['half_points'] = 0
    else:
        rec['scores'] = state['result']['scores']
        rec['half_points'] = state['result']['half_points']
        rec['margin'] = rec['scores'][0] - rec['scores'][1]
    return rec, error


def worker(script, python, nice, tasks, results, lock, progress):
    engine = Engine(nice)
    agent = AgentProc(script, python, nice)
    try:
        while True:
            try:
                task = tasks.get_nowait()
            except queue.Empty:
                break
            try:
                rec, error = play_game(engine, agent, task)
            except RuntimeError as e:   # engine died
                rec, error = dict(task, error='engine: %s' % e, scores=None, half_points=0, cpu=0, wall=0,
                                  first_in_process=False), 'engine'
                engine.close()
                engine = Engine(nice)
            if error:
                agent.close()
                agent = AgentProc(script, python, nice)
                engine.close()
                engine = Engine(nice)
            with lock:
                results.append(rec)
                progress(rec)
    finally:
        agent.close()
        engine.close()


def make_tasks(args):
    games = [int(g) for g in args.games.split(',')]
    tasks = []
    if args.cases:
        cases = json.load(open(args.cases))
        for i, c in enumerate(cases):
            tasks.append(dict(map=i, group=c['group'], seed=c['seed'], game=c['game']))
    else:
        rng = random.Random(args.seed)
        seeds = [rng.randrange(2 ** 32) for _ in range(args.maps)]
        groups = None if args.groups is None else set(int(g) for g in args.groups.split(','))
        for m in range(args.maps):
            group = GROUPS[m % 8]
            if groups is not None and group not in groups:
                continue
            for g in games:
                tasks.append(dict(map=m, group=group, seed=seeds[m], game=g))
    for t in tasks:
        t['topology'] = t['group'] // 2
        t['seat'] = t['group'] % 2
    return tasks


def rate(recs):
    n = len(recs)
    if not n:
        return None
    w = sum(r['half_points'] == 2 for r in recs)
    d = sum(r['half_points'] == 1 for r in recs)
    margins = [r['margin'] for r in recs if r.get('margin') is not None]
    return dict(n=n, win=w, draw=d, loss=n - w - d, win_rate=round(w / n, 3),
                points=round(sum(r['half_points'] for r in recs) / (2 * n), 3),
                mean_margin=round(sum(margins) / len(margins), 1) if margins else None,
                min_margin=min(margins) if margins else None)


def summarize(recs, args):
    by_map = {}
    for r in recs:
        by_map.setdefault(r['map'], []).append(r)
    maps = []
    for m in sorted(by_map):
        rs = sorted(by_map[m], key=lambda r: r['game'])
        worst = min(r['half_points'] for r in rs)
        maps.append(dict(map=m, group=rs[0]['group'], seed=rs[0]['seed'], worst=worst,
                         games={r['game']: (r['scores'], r['half_points']) for r in rs}))
    total = sum(m['worst'] for m in maps)
    ok = [r for r in recs if not r['first_in_process']]
    summary = dict(
        agent=str(args.agent), seed=args.seed, n_maps=len(maps), n_games=len(recs),
        match_score=round(total / (2 * len(maps)), 4) if maps else 0,
        map_half_points=total, map_wins=sum(m['worst'] == 2 for m in maps),
        map_draws=sum(m['worst'] == 1 for m in maps), map_losses=sum(m['worst'] == 0 for m in maps),
        games=rate(recs),
        by_game={g: rate([r for r in recs if r['game'] == g]) for g in sorted(set(r['game'] for r in recs))},
        by_seat={s: rate([r for r in recs if r['seat'] == s]) for s in (0, 1)},
        by_topology={t: rate([r for r in recs if r['topology'] == t]) for t in range(4)},
        by_group={g: rate([r for r in recs if r['group'] == g]) for g in range(8)},
        by_seat_game={'%d/%d' % (s, g): rate([r for r in recs if r['seat'] == s and r['game'] == g])
                      for s in (0, 1) for g in sorted(set(r['game'] for r in recs))},
        errors=[dict(map=r['map'], group=r['group'], seed=r['seed'], game=r['game'], error=r['error'])
                for r in recs if r.get('error')],
        cpu_max=max((r['cpu'] for r in recs), default=0),
        cpu_max_not_first=max((r['cpu'] for r in ok), default=0),
        cpu_mean=round(sum(r['cpu'] for r in recs) / max(1, len(recs)), 3),
        wall_max=max((r['wall'] for r in recs), default=0),
        wall_mean=round(sum(r['wall'] for r in recs) / max(1, len(recs)), 3),
        max_decision_wall=max((r.get('max_decision', 0) for r in recs), default=0),
    )
    return summary, maps


def fmt_rate(x):
    if not x:
        return '-'
    return '%3d/%-3d W%-3d D%-2d L%-3d %5.1f%%  m%+.1f min%+d' % (
        x['win'], x['n'], x['win'], x['draw'], x['loss'], 100 * x['win_rate'],
        x['mean_margin'] or 0, x['min_margin'] if x['min_margin'] is not None else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('agent')
    ap.add_argument('--maps', type=int, default=48)
    ap.add_argument('--seed', type=int, default=20261114)
    ap.add_argument('--games', default='0,1,2,3,4')
    ap.add_argument('--groups', default=None, help='comma list of groups (0-7) to keep')
    ap.add_argument('--cases', default=None, help='JSON list of {group, seed, game}')
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--nice', type=int, default=10)
    ap.add_argument('--python', default=PYPY if os.path.exists(PYPY) else sys.executable)
    ap.add_argument('--out', default=None)
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    tasks = make_tasks(args)
    q = queue.Queue()
    for t in tasks:
        q.put(t)
    results = []
    lock = threading.Lock()
    start = time.monotonic()
    done = [0]

    def progress(rec):
        done[0] += 1
        if not args.quiet:
            sc = rec['scores']
            print('[%3d/%d] map %2d g%d grp%d game%d  %s  hp=%d  cpu=%.2fs wall=%.2fs%s' % (
                done[0], len(tasks), rec['map'], rec['group'], rec['group'], rec['game'],
                '%3d-%-3d' % tuple(sc) if sc else ' ERROR ', rec['half_points'], rec['cpu'], rec['wall'],
                ('  ' + rec['error']) if rec.get('error') else ''), file=sys.stderr, flush=True)

    threads = [threading.Thread(target=worker, args=(args.agent, args.python, args.nice, q, results, lock, progress))
               for _ in range(min(args.jobs, len(tasks)))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    summary, maps = summarize(results, args)
    summary['seconds'] = round(time.monotonic() - start, 1)
    out = args.out or str(HERE / 'results' / ('%s_%s.json' % (Path(args.agent).stem, time.strftime('%Y%m%d-%H%M%S'))))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(dict(summary=summary, maps=maps, games=sorted(results, key=lambda r: (r['map'], r['game']))), f, indent=1)

    print('agent %s  maps %d  games %d  seed %s  (%.0fs)' % (args.agent, summary['n_maps'], summary['n_games'],
                                                           args.seed, summary['seconds']))
    print('MATCH SCORE %.4f   map half-points %d/%d   map W/D/L %d/%d/%d' % (
        summary['match_score'], summary['map_half_points'], 2 * summary['n_maps'], summary['map_wins'],
        summary['map_draws'], summary['map_losses']))
    print('all games     ' + fmt_rate(summary['games']))
    for g, x in summary['by_game'].items():
        print('game %d        %s' % (g, fmt_rate(x)))
    for s, x in summary['by_seat'].items():
        print('seat %d        %s' % (s, fmt_rate(x)))
    for t, x in summary['by_topology'].items():
        print('topology %d    %s' % (t, fmt_rate(x)))
    for k, x in summary['by_seat_game'].items():
        print('seat/game %s %s' % (k, fmt_rate(x)))
    print('cpu/game max %.2fs (excl. first game of process %.2fs) mean %.2fs | wall/game max %.2fs mean %.2fs | max decision wall %.2fs' % (
        summary['cpu_max'], summary['cpu_max_not_first'], summary['cpu_mean'], summary['wall_max'],
        summary['wall_mean'], summary['max_decision_wall']))
    if summary['errors']:
        print('ERRORS (%d):' % len(summary['errors']))
        for e in summary['errors'][:20]:
            print('  ', e)
    if not args.quiet:
        lost = [m for m in maps if m['worst'] < 2]
        print('maps not won: ' + ', '.join('m%d(g%d):%s' % (m['map'], m['group'], ''.join(
            'WDL'[2 - m['games'][g][1]] for g in sorted(m['games']))) for m in lost))
    print('saved', out)


if __name__ == '__main__':
    main()
