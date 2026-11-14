"""Check professor.py against the real engine.

For each game the real engine runs with trace/hook.so preloaded (it logs the Professor's
actual order and remaining plan every round). In parallel the Python Engine + Professor
simulate the same game. Every round we compare:
  * the Professor's order (exact, from the trace),
  * the Professor's remaining plan and stock estimates (exact, from the trace),
  * our whole observation (own side, stocks, visible, claims, enemy boats, opponent_score,
    legal_actions) against the Python engine's view,
  * the final scores.

Usage: python3 test_professor.py [--games N] [--seed S] [--policy mix|wait|random|mirror] [-v]
Our seat is driven by a seeded policy: wait, random legal moves, or a mirror Professor.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import professor as P   # noqa: E402

ENGINE = os.path.join(ROOT, 'mozambique-engine')
HOOK = os.path.join(HERE, 'trace', 'hook.so')


class TracedEngine:
    def __init__(self):
        self.trace_path = tempfile.mktemp(prefix='moz_trace_', suffix='.jsonl')
        env = dict(os.environ, LD_PRELOAD=HOOK, MOZ_TRACE=self.trace_path)
        self.proc = subprocess.Popen([ENGINE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     text=True, bufsize=1, env=env)
        self.trace = None

    def request(self, **data):
        self.proc.stdin.write(json.dumps(data) + '\n')
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError('engine stopped')
        r = json.loads(line)
        if 'error' in r:
            raise RuntimeError(r['error'])
        return r

    def read_trace(self):
        if self.trace is None:
            self.trace = open(self.trace_path)
        line = self.trace.readline()
        return json.loads(line) if line else None

    def close(self):
        try:
            self.proc.stdin.write('{"command":"quit"}\n')
            self.proc.stdin.flush()
            self.proc.wait(timeout=2)
        except Exception:
            self.proc.kill()
        if self.trace:
            self.trace.close()
        try:
            os.unlink(self.trace_path)
        except OSError:
            pass


def trace_order(t):
    return (t['op'], t['boat'], t['destination'], t['good'], t['quantity'], t['contract'])


def compare_observation(obs, eng, seat):
    """Returns a list of mismatch descriptions between the engine observation and our model."""
    bad = []
    v = eng.view(seat)
    side = v.side
    own = obs['own']
    mine = dict(
        round=v.round, seat=v.seat, opponent_score=v.opponent_score,
        claims=list(v.claims),
        visible=[bool(x) for x in v.visible],
        stocks=[(v.stocks[s] if v.visible[s] else None) for s in range(10)],
        score=side.score, crafted=side.crafted, home=side.home,
        boats=[dict(position=b[0], destination=b[1], eta=b[2], cargo=b[3:6]) for b in side.boats],
        warehouses=[side.wh[s * 3:s * 3 + 3] for s in range(10)],
        workshops=[bool(x) for x in side.ws], jobs=list(side.jobs),
        enemy=sorted(v.enemy_boats),
        legal=[P.order_to_json(o) for o in eng.legal(seat)],
    )
    theirs = dict(
        round=obs['round'], seat=obs['seat'], opponent_score=obs['opponent_score'],
        claims=obs['claims'], visible=[bool(x) for x in obs['visible']], stocks=obs['stocks'],
        score=own['score'], crafted=own['crafted_deliveries'], home=own['home'],
        boats=[dict(position=b['position'], destination=b['destination'], eta=b['eta'],
                    cargo=list(b['cargo'])) for b in own['boats']],
        warehouses=[list(w) for w in own['warehouses']],
        workshops=[bool(x) for x in own['workshops']], jobs=own['jobs'],
        enemy=sorted((b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats']),
        legal=obs['legal_actions'],
    )
    for k in mine:
        if mine[k] != theirs[k]:
            bad.append('%s: python=%r engine=%r' % (k, mine[k], theirs[k]))
    return bad


def play(te, group, seed, game, policy, rng, verbose=False):
    """Plays one game; returns dict with mismatch counts."""
    state = te.request(command='reset', group=group, seed=seed, game=game)
    obs = state['observation']
    seat = obs['seat']
    prof_seat = 1 - seat
    mp = P.Map(obs['map'])
    eng = P.Engine(mp)
    style_id = P.style_permutation(seed)[game]
    prof = P.Professor(style_id, prof_seat)
    mirror = P.Professor(rng.randrange(5), seat) if policy == 'mirror' else None
    res = dict(rounds=0, action_mismatch=0, plan_mismatch=0, est_mismatch=0, obs_mismatch=0,
               style_mismatch=0, score_mismatch=0, first_bad=None, replans=0, prof_time=0.0)

    def note(kind, msg):
        res[kind] += 1
        if res['first_bad'] is None:
            res['first_bad'] = 'g%d s%d game%d round %d: %s %s' % (group, seed, game, eng.round, kind, msg)
        if verbose:
            print('  MISMATCH', kind, msg)

    while not state['game_done']:
        obs = state['observation']
        for m in compare_observation(obs, eng, seat):
            note('obs_mismatch', m)
        # our move
        legal = obs['legal_actions']
        if policy == 'wait':
            mine = P.WAIT
        elif policy == 'mirror':
            mine = mirror.choose(eng.view(seat))
        else:
            r = rng.random()
            if r < 0.25:
                mine = P.WAIT
            else:
                # prefer state-changing moves so the game gets interesting
                pool = [a for a in legal if a['op'] in ('deliver', 'build_workshop', 'craft')]
                if not pool or rng.random() < 0.2:
                    pool = legal
                mine = P.order_from_json(rng.choice(pool))
        # predicted Professor move
        t0 = time.time()
        pred = prof.choose(eng.view(prof_seat))
        res['prof_time'] += time.time() - t0
        state = te.request(command='step', action=P.order_to_json(mine))
        tr = te.read_trace()
        if tr is None:
            note('action_mismatch', 'no trace line')
            break
        if tr['round'] != eng.round or tr['seat'] != prof_seat:
            note('action_mismatch', 'trace out of sync %r' % tr)
            break
        if abs(tr['style'][0] - prof.B) > 1e-9 or abs(tr['style'][1] - prof.A) > 1e-9 or tr['style'][2] != prof.W:
            note('style_mismatch', 'engine %r python %r' % (tr['style'], (prof.B, prof.A, prof.W)))
            prof.B, prof.A, prof.W = tr['style']
        actual = trace_order(tr['action'])
        if actual != pred:
            note('action_mismatch', 'python=%r engine=%r' % (pred, actual))
        actual_plan = [trace_order(x) for x in tr['plan']]
        if actual_plan != list(prof.plan) or tr['plan_contracts'] != prof.plan_contracts:
            note('plan_mismatch', 'python=%r/%r engine=%r/%r' % (list(prof.plan)[:6], prof.plan_contracts,
                                                             actual_plan[:6], tr['plan_contracts']))
        if tr['est'] != prof.est:
            note('est_mismatch', 'python=%r engine=%r' % (prof.est, tr['est']))
        if actual != pred or actual_plan != list(prof.plan):
            # resynchronise on the engine's real behaviour so later rounds stay comparable
            from collections import deque
            prof.plan = deque(actual_plan)
            prof.plan_contracts = list(tr['plan_contracts'])
        orders = [None, None]
        orders[seat] = mine
        orders[prof_seat] = actual
        eng.step(orders)
        res['rounds'] += 1
    result = state.get('result')
    if result:
        mine_scores = [eng.sides[seat].score, eng.sides[prof_seat].score]
        if result['scores'] != mine_scores:
            note('score_mismatch', 'python=%r engine=%r' % (mine_scores, result['scores']))
        res['scores'] = result['scores']
    res['replans'] = prof.replans
    res['style'] = style_id
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--games', type=int, default=20)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--policy', default='mix', choices=['mix', 'wait', 'random', 'mirror'])
    ap.add_argument('-v', action='store_true')
    args = ap.parse_args()
    rng = random.Random(args.seed)
    te = TracedEngine()
    totals = {}
    bad_games = 0
    t0 = time.time()
    try:
        for i in range(args.games):
            group = rng.randrange(8)
            seed = rng.randrange(2 ** 32)
            game = rng.randrange(5)
            policy = args.policy
            if policy == 'mix':
                policy = ('wait', 'random', 'mirror')[i % 3]
            r = play(te, group, seed, game, policy, rng, args.v)
            keys = ('rounds', 'action_mismatch', 'plan_mismatch', 'est_mismatch', 'obs_mismatch',
                    'style_mismatch', 'score_mismatch', 'replans', 'prof_time')
            for k in keys:
                totals[k] = totals.get(k, 0) + r[k]
            bad = any(r[k] for k in keys if k.endswith('mismatch'))
            bad_games += bad
            print('game %3d group %d seed %10d idx %d style %d policy %-6s scores %s replans %3d %5.2fs %s' % (
                i, group, seed, game, r['style'], policy, r.get('scores'), r['replans'], r['prof_time'],
                ('BAD: ' + r['first_bad']) if bad else 'ok'), flush=True)
    finally:
        te.close()
    totals['prof_time'] = round(totals['prof_time'], 2)
    print(json.dumps(dict(games=args.games, bad_games=bad_games, wall=round(time.time() - t0, 1), **totals)))
    return 1 if bad_games else 0


if __name__ == '__main__':
    sys.exit(main())
