"""Offline upper-bound probe with the timetable scheduler: known style, static round-0 beam, exact rollouts."""
import sys, time, random, json, multiprocessing as mpc
import core as P
import brain as B

GROUPS = [2 * t + s for t in range(4) for s in range(2)]

def search(group, seed, style, width=5, depth=7, Bs=(0.0, 3.5)):
    topo, seat = group // 2, group % 2
    mp = P.Map(P.generate_map(topo, seed)); ps = 1 - seat
    eng0 = P.Engine(mp)
    def ev(seq, Bv):
        eng = B.clone_engine(eng0); prof = B.CProf(style, ps)
        plan, S = B.make_tplan(mp, eng.sides[seat], eng.stocks, eng.claims, 0, seq, Bv)
        if plan.seq != list(seq):
            return None
        info = {'ours': [], 'theirs': []}
        m = B.rollout2(eng, prof, plan, seat, info)
        last = max([r for _, r in info['ours']] or [0])
        return m, -last, info
    t0 = time.time()
    base = ev([], 0.0)
    best = (base[0], 0, [], 0.0, base[2])
    n = 0
    for Bv in Bs:
        frontier = [[], [8]]
        for d in range(depth):
            nxt = []
            for seq in frontier:
                for c in range(8):
                    if c in seq: continue
                    r = ev(seq + [c], Bv); n += 1
                    if r is None: continue
                    nxt.append((r[0], r[1], seq + [c], Bv, r[2]))
            if not nxt: break
            nxt.sort(key=lambda x: (-x[0], -x[1]))
            if (nxt[0][0], nxt[0][1]) > (best[0], best[1]):
                best = nxt[0]
            frontier = [x[2] for x in nxt[:width]]
    return dict(group=group, seed=seed, style=style, passive=base[0], best=best[0], seq=best[2], B=best[3],
                ours=best[4]['ours'], theirs=best[4]['theirs'], rep=best[4].get('repairs'), evals=n, secs=round(time.time() - t0, 1))

def work(job):
    return search(*job)

if __name__ == '__main__':
    nmaps = int(sys.argv[1]); jobs = int(sys.argv[2]); seed0 = int(sys.argv[3]) if len(sys.argv) > 3 else 20261114
    rng = random.Random(seed0)
    seeds = [rng.randrange(2 ** 32) for _ in range(nmaps)]
    js = [(GROUPS[m % 8], seeds[m], st) for m in range(nmaps) for st in range(5)]
    with mpc.Pool(jobs) as pool:
        res = []
        for r in pool.imap(work, js, chunksize=1):
            res.append(r)
            print(json.dumps(r), flush=True)
    wins = sum(r['best'] > 0 for r in res); draws = sum(r['best'] == 0 for r in res)
    print('games', len(res), 'win', wins, 'draw', draws)
    bymap = {}
    for r in res: bymap.setdefault((r['group'], r['seed']), []).append(r['best'])
    print('maps all-win', sum(min(v) > 0 for v in bymap.values()), 'of', len(bymap), 'half-points', sum((2 if min(v) > 0 else (1 if min(v) == 0 else 0)) for v in bymap.values()))
