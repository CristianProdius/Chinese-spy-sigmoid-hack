"""Fast in-process evaluation: exact Python engine + Professor clone (work/binary/professor.py)
against an agent file in main.py format. No engine binary, no pipes.

    pypy3 fasteval.py AGENT.py [--maps 48] [--seed 20261114] [--jobs 6] [--styles 0,1,2,3,4]
                               [--groups 0..7] [--out res.json] [--quiet] [--first-map 0]

Map m: group GROUPS[m % 8], seed from random.Random(--seed) (same scheme as arena.py / eval.py,
so map m is identical to eval.py's map m). Each map is played once per style (the five games of
a real map use the five styles in some order) and counts by its worst game.
Each worker process imports the agent once, so module globals persist across its games, like the
real evaluator. Every action is checked against the legal list (illegal = loss, reported).
CPU time per game = time.process_time() spent inside agent() calls.
"""
import argparse
import importlib.util
import json
import multiprocessing as mpc
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P  # noqa: E402

GROUPS = [2 * t + s for t in range(4) for s in range(2)]


def obs_dict(eng, seat, map_dict):
    side = eng.sides[seat]
    other = eng.sides[1 - seat]
    vis = [False] * 10
    vis[side.home] = True
    for s in range(10):
        if side.ws[s]:
            vis[s] = True
    for b in side.boats:
        if b[2] == 0:
            vis[b[0]] = True
    stocks = [eng.stocks[s] if vis[s] else None for s in range(10)]
    enemy = [dict(boat=i, destination=b[1], eta=b[2], position=b[0])
             for i, b in enumerate(other.boats) if vis[b[0]] or (b[1] >= 0 and vis[b[1]])]
    legal = P.legal_actions(eng.mp, side, [eng.stocks[s] if vis[s] else 4 for s in range(10)],
                            eng.claims, eng.round) if eng.round < 80 else []
    own = dict(boats=[dict(cargo=[b[3], b[4], b[5]], destination=b[1], eta=b[2], position=b[0])
                      for b in side.boats],
               crafted_deliveries=side.crafted, home=side.home, jobs=list(side.jobs), score=side.score,
               warehouses=[side.wh[3 * s:3 * s + 3] for s in range(10)], workshops=list(side.ws))
    return dict(claims=list(eng.claims), enemy_boats=enemy,
                legal_actions=[P.order_to_json(o) for o in legal], map=map_dict,
                opponent_score=other.score, own=own, round=eng.round, seat=seat,
                stocks=stocks, visible=vis)


_AGENT = None


def load_agent(path):
    spec = importlib.util.spec_from_file_location('agent_under_test', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def play(agent_mod, group, seed, style, trace=False):
    topo, seat = group // 2, group % 2
    map_dict = P.generate_map(topo, seed)
    mp = P.Map(map_dict)
    eng = P.Engine(mp)
    prof = P.Professor(style, 1 - seat)
    memory = {}
    cpu = 0.0
    wall = 0.0
    error = None
    claim_round = [-1] * 8
    while eng.round < 80:
        ob = obs_dict(eng, seat, map_dict)
        # same JSON round trip as the real protocol
        ob = json.loads(json.dumps(ob))
        t0 = time.process_time(); w0 = time.perf_counter()
        try:
            act = agent_mod.agent(ob, memory)
        except Exception as e:  # noqa: BLE001
            import traceback
            error = 'crash r%d: %s' % (eng.round, traceback.format_exc()[-600:])
            break
        cpu += time.process_time() - t0; wall += time.perf_counter() - w0
        if act not in ob['legal_actions']:
            error = 'illegal r%d: %r' % (eng.round, act)
            break
        mine = P.order_from_json(act)
        po = prof.choose(eng.view(1 - seat))
        orders = [None, None]
        orders[seat] = mine
        orders[1 - seat] = po
        before = list(eng.claims)
        eng.step(orders)
        for c in range(8):
            if before[c] == -1 and eng.claims[c] != -1:
                claim_round[c] = eng.round - 1
    us = eng.sides[seat].score
    them = eng.sides[1 - seat].score
    if error:
        hp = 0
    else:
        hp = 2 if us > them else (1 if us == them else 0)
    return dict(group=group, seed=seed, style=style, us=us, them=them, hp=hp, cpu=round(cpu, 3),
                wall=round(wall, 3), error=error,
                claims=''.join('U' if eng.claims[c] == seat else ('P' if eng.claims[c] == 1 - seat else '.')
                               for c in range(8)),
                claim_round=claim_round)


def _worker_init(path):
    global _AGENT
    _AGENT = load_agent(path)


def _worker(job):
    m, group, seed, style = job
    r = play(_AGENT, group, seed, style)
    r['map'] = m
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('agent')
    ap.add_argument('--maps', type=int, default=48)
    ap.add_argument('--first-map', type=int, default=0)
    ap.add_argument('--seed', type=int, default=20261114)
    ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--styles', default='0,1,2,3,4')
    ap.add_argument('--groups', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    rng = random.Random(a.seed)
    seeds = [rng.randrange(2 ** 32) for _ in range(a.first_map + a.maps)]
    styles = [int(x) for x in a.styles.split(',')]
    groups_ok = set(int(x) for x in a.groups.split(',')) if a.groups else None
    jobs = []
    for m in range(a.first_map, a.first_map + a.maps):
        g = GROUPS[m % 8]
        if groups_ok is not None and g not in groups_ok:
            continue
        for st in styles:
            jobs.append((m, g, seeds[m], st))
    t0 = time.time()
    path = os.path.abspath(a.agent)
    if a.jobs <= 1:
        _worker_init(path)
        res = [_worker(j) for j in jobs]
    else:
        with mpc.Pool(a.jobs, initializer=_worker_init, initargs=(path,)) as pool:
            res = pool.map(_worker, jobs, chunksize=1)
    by_map = {}
    for r in res:
        by_map.setdefault(r['map'], []).append(r)
    worst = {m: min(x['hp'] for x in v) for m, v in by_map.items()}
    n = len(by_map)
    games = len(res)
    wins = sum(r['hp'] == 2 for r in res)
    draws = sum(r['hp'] == 1 for r in res)
    errors = [r for r in res if r['error']]
    out = dict(agent=a.agent, maps=n, match=round(sum(worst.values()) / (2.0 * max(1, n)), 4),
               map_w=sum(v == 2 for v in worst.values()), map_d=sum(v == 1 for v in worst.values()),
               map_l=sum(v == 0 for v in worst.values()),
               games=games, win=round(wins / max(1, games), 4), draw=round(draws / max(1, games), 4),
               mean_us=round(sum(r['us'] for r in res) / max(1, games), 2),
               mean_them=round(sum(r['them'] for r in res) / max(1, games), 2),
               cpu_max=max((r['cpu'] for r in res), default=0), cpu_mean=round(sum(r['cpu'] for r in res) / max(1, games), 3),
               errors=len(errors), seconds=round(time.time() - t0, 1))
    per = {}
    for key, f in (('style', lambda r: r['style']), ('seat', lambda r: r['group'] % 2), ('topo', lambda r: r['group'] // 2)):
        d = {}
        for r in res:
            d.setdefault(f(r), []).append(r['hp'])
        per[key] = {k: '%.0f%%W %.0f%%D' % (100.0 * sum(x == 2 for x in v) / len(v), 100.0 * sum(x == 1 for x in v) / len(v))
                    for k, v in sorted(d.items())}
    out['per'] = per
    print(json.dumps(out))
    if not a.quiet:
        for m in sorted(by_map):
            v = sorted(by_map[m], key=lambda x: x['style'])
            print('map %3d g%d seed %10d worst %d | %s' % (m, v[0]['group'], v[0]['seed'], worst[m],
                  ' '.join('s%d:%d-%d%s' % (x['style'], x['us'], x['them'], '!' if x['error'] else '') for x in v)))
        for r in errors[:5]:
            print('ERROR', r['map'], r['style'], r['error'])
    if a.out:
        with open(a.out, 'w') as f:
            json.dump(dict(summary=out, games=res), f)


if __name__ == '__main__':
    main()
