"""Benchmarks: fastcore.py vs work/binary/professor.py (run with PyPy).

    pypy3 bench.py [--parts replan,game,tracker,lookahead] [--games 12] [--corpus corpus_b.pkl]

Every (part, implementation) runs in its own fresh process (fair JIT warm-up), one at a time.
CPU = time.process_time. "cold" = first unit of work in a fresh process (includes JIT warm-up),
"warm" = median of the rest.

replan     the replans recorded in the corpus (mkcorpus.py: games vs wait/random/mirror), one
           pass cold, then 4 warm passes; fast runs with the cache off (pure replan speed)
game       full games: Engine + opponent Professor + a mirror Professor of another style in our
           seat (two Professors replanning), per-game CPU; fast with and without the cache
tracker    five-hypothesis style tracking over a game, our seat played by a mirror Professor:
           reference = 5 x (P.Engine + P.Professor) pruned by compare_observation,
           fast = fastcore.Tracker (observe/commit), per-game CPU
lookahead  from the tracked true hypothesis at rounds 8, 24, 40: 40 rollouts of 16 rounds with
           random own orders each (clone + step); reference = deepcopy(Engine) +
           Professor.clone(); fast = Hypothesis.clone() with / without the shared cache
"""
import argparse
import copy
import json
import os
import pickle
import random
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))


def load_impl(name):
    if name == 'ref':
        import professor as M
    else:
        import fastcore as M
    return M


def maps_for(n, seed):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        topo = rng.randrange(4)
        seat = rng.randrange(2)
        s = rng.randrange(2 ** 32)
        style = rng.randrange(5)
        mstyle = (style + 1 + rng.randrange(4)) % 5
        out.append((topo, seat, s, style, mstyle))
    return out


# ---- parts (run inside a child process) ------------------------------------------------------

def part_replan(impl, a):
    M = load_impl('ref' if impl == 'ref' else 'fast')
    recs = pickle.load(open(a.corpus, 'rb'))
    maps = {}
    jobs = []
    for md, style, st, est, out in recs:
        mp = maps.get(id(md)) or maps.setdefault(id(md), M.Map(md))
        side = M.Side(st[0])
        side.score, side.crafted = st[1], st[2]
        side.boats = [b[:] for b in st[3]]
        side.wh = st[4][:]
        side.ws = st[5][:]
        side.jobs = st[6][:]
        v = M.View()
        v.mp = mp
        v.side = side
        v.claims = st[7]
        v.round = st[8]
        v.seat = st[9]
        jobs.append((v, style, est))
    times = []
    for _p in range(5):
        t0 = time.process_time()
        for v, style, est in jobs:
            if impl == 'ref':
                pr = M.Professor(style, v.seat)
            else:
                pr = M.Professor(style, v.seat, use_cache=False)
            pr.mp = v.mp
            pr.est = est[:]
            pr.replan(v)
        times.append(time.process_time() - t0)
    n = len(jobs)
    return dict(replans=n, cold_ms=1000 * times[0] / n, warm_ms=1000 * statistics.median(times[1:]) / n)


def part_game(impl, a):
    M = load_impl('ref' if impl == 'ref' else 'fast')
    per = []
    replans = 0
    for topo, seat, seed, style, mstyle in maps_for(a.games, a.seed):
        md = M.generate_map(topo, seed)
        mp = M.Map(md)
        eng = M.Engine(mp)
        if impl == 'ref':
            prof = M.Professor(style, 1 - seat)
            mir = M.Professor(mstyle, seat)
        else:
            uc = impl == 'fast_cache'
            prof = M.Professor(style, 1 - seat, use_cache=uc)
            mir = M.Professor(mstyle, seat, use_cache=uc)
        t0 = time.process_time()
        while eng.round < 80:
            o = [None, None]
            o[seat] = mir.choose(eng.view(seat))
            o[1 - seat] = prof.choose(eng.view(1 - seat))
            eng.step(o)
        per.append(time.process_time() - t0)
        replans += prof.replans + mir.replans
    return dict(games=len(per), replans=replans, cold_s=per[0], warm_mean_s=statistics.mean(per[1:]),
                warm_max_s=max(per[1:]))


def obs_dict(P, eng, seat, map_dict):
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
    return json.loads(json.dumps(dict(claims=list(eng.claims), enemy_boats=enemy,
                                      legal_actions=[P.order_to_json(o) for o in legal], map=map_dict,
                                      opponent_score=other.score, own=own, round=eng.round, seat=seat,
                                      stocks=stocks, visible=vis)))


def record_trajectories(a):
    """Real games (reference engine + Professor, our seat = mirror Professor of another style):
    the observation stream and our orders, so tracking can be timed without the real world."""
    import professor as P
    out = []
    for topo, seat, seed, style, mstyle in maps_for(a.games, a.seed):
        md = P.generate_map(topo, seed)
        rmp = P.Map(md)
        real = P.Engine(rmp)
        prof = P.Professor(style, 1 - seat)
        mir = P.Professor(mstyle, seat)
        obs_list = []
        mine_list = []
        while real.round < 80:
            obs_list.append(obs_dict(P, real, seat, md))
            mine = mir.choose(real.view(seat))
            o = [None, None]
            o[seat] = mine
            o[1 - seat] = prof.choose(real.view(1 - seat))
            real.step(o)
            mine_list.append(mine)
        out.append(dict(seat=seat, style=style, obs=obs_list, mine=mine_list))
    return out


def play_tracked(impl, traj, on_round=None):
    """Replays a recorded game through tracking. Returns tracking CPU. on_round(round, state,
    preds) is called (outside the timing) after the observation is processed."""
    import professor as P
    from test_professor import compare_observation
    seat = traj['seat']
    ps = 1 - seat
    cpu = 0.0
    hyps = tr = preds = None
    for obs, mine in zip(traj['obs'], traj['mine']):
        t0 = time.process_time()
        if impl == 'ref':
            if hyps is None:
                rmp = P.Map(obs['map'])
                hyps = {s: (P.Engine(rmp), P.Professor(s, ps)) for s in range(5)}
            for s in list(hyps):
                if compare_observation(obs, hyps[s][0], seat):
                    del hyps[s]
            preds = {s: p.choose(e.view(ps)) for s, (e, p) in hyps.items()}
        else:
            if tr is None:
                import fastcore as F
                tr = F.Tracker(obs)
            tr.observe(obs)
        cpu += time.process_time() - t0
        if on_round is not None:
            on_round(obs['round'], hyps if impl == 'ref' else tr, preds)
        t0 = time.process_time()
        if impl == 'ref':
            for s, (e, p) in hyps.items():
                o2 = [None, None]
                o2[seat] = mine
                o2[ps] = preds[s]
                e.step(o2)
        else:
            tr.commit(mine)
        cpu += time.process_time() - t0
    return cpu


def load_traj(a):
    with open(a.traj, 'rb') as f:
        return pickle.load(f)


def part_tracker(impl, a):
    per = [play_tracked(impl, t) for t in load_traj(a)]
    return dict(games=len(per), cold_s=per[0], warm_mean_s=statistics.mean(per[1:]), warm_max_s=max(per[1:]))


def part_lookahead(impl, a):
    """Rollouts from the true hypothesis at rounds 8, 24, 40 of each recorded game."""
    import professor as P
    import fastcore as F
    per_rollout = []
    stats = dict(rollouts=0, rounds=0)
    hits0 = [0, 0]
    for traj in load_traj(a):
        seat = traj['seat']
        style = traj['style']
        ps = 1 - seat
        snaps = {}

        def on_round(rnd, state, preds):
            if rnd in (8, 24, 40):
                if impl == 'ref':
                    if style in state:
                        e, p = state[style]
                        snaps[rnd] = (copy.deepcopy(e), p.clone(), preds[style])
                else:
                    for h in state.hyps:
                        if h.style == style:
                            snaps[rnd] = h.clone()

        play_tracked('ref' if impl == 'ref' else 'fast', traj, on_round)
        if impl == 'fast_nocache':
            for h in snaps.values():
                h.prof.use_cache = False
        rng = random.Random(len(traj['obs']) * 7 + seat * 3 + style)
        cache = None
        if impl == 'fast_cache' and snaps:
            cache = list(snaps.values())[0].prof.cache
            h0, m0 = cache.hits, cache.misses
        t0 = time.process_time()
        for rnd in sorted(snaps):
            base = snaps[rnd]
            for _k in range(40):
                if impl == 'ref':
                    e = copy.deepcopy(base[0])
                    p = base[1].clone()
                    pend = base[2]
                    for _h in range(16):
                        if e.round >= 80:
                            break
                        legal = e.legal(seat)
                        mine = P.WAIT if rng.random() < 0.3 else rng.choice(legal)
                        o = [None, None]
                        o[seat] = mine
                        o[ps] = pend
                        e.step(o)
                        stats['rounds'] += 1
                        if e.round < 80:
                            pend = p.choose(e.view(ps))
                else:
                    h = base.clone()
                    for _h in range(16):
                        if h.eng.round >= 80:
                            break
                        legal = h.eng.legal(seat)
                        mine = F.WAIT if rng.random() < 0.3 else rng.choice(legal)
                        h.step(mine)
                        h.order()
                        stats['rounds'] += 1
                stats['rollouts'] += 1
        per_rollout.append((time.process_time() - t0, len(snaps) * 40))
        if cache is not None:
            hits0[0] += cache.hits - h0
            hits0[1] += cache.misses - m0
    tot = sum(t for t, n in per_rollout)
    n = sum(n for t, n in per_rollout)
    out = dict(rollouts=stats['rollouts'], rounds=stats['rounds'], ms_per_rollout=1000 * tot / max(1, n),
               ms_per_rollout_warm=1000 * sum(t for t, k in per_rollout[1:]) / max(1, sum(k for t, k in per_rollout[1:])))
    if impl == 'fast_cache':
        out['cache_hit_rate'] = round(hits0[0] / max(1, hits0[0] + hits0[1]), 3)
    return out


PARTS = dict(replan=(part_replan, ('ref', 'fast')),
             game=(part_game, ('ref', 'fast', 'fast_cache')),
             tracker=(part_tracker, ('ref', 'fast')),
             lookahead=(part_lookahead, ('ref', 'fast_nocache', 'fast_cache')))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parts', default='replan,game,tracker,lookahead')
    ap.add_argument('--games', type=int, default=12)
    ap.add_argument('--seed', type=int, default=4242)
    ap.add_argument('--corpus', default=os.path.join(HERE, 'corpus_b.pkl'))
    ap.add_argument('--child', default=None)
    ap.add_argument('--impl', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--traj', default=None)
    a = ap.parse_args()
    if a.child == 'record':
        with open(a.traj, 'wb') as f:
            pickle.dump(record_trajectories(a), f)
        print('RESULT {}')
        return
    if a.child:
        res = PARTS[a.child][0](a.impl, a)
        print('RESULT ' + json.dumps(res))
        return
    allres = {}
    parts = a.parts.split(',')
    a.traj = os.path.join(HERE, '.bench_traj_%d_%d.pkl' % (a.games, a.seed))
    if ('tracker' in parts or 'lookahead' in parts) and not os.path.exists(a.traj):
        subprocess.run([sys.executable, os.path.abspath(__file__), '--child', 'record', '--games', str(a.games),
                        '--seed', str(a.seed), '--traj', a.traj], check=True, stdout=subprocess.PIPE)
    for part in parts:
        fn, impls = PARTS[part]
        allres[part] = {}
        for impl in impls:
            cmd = [sys.executable, os.path.abspath(__file__), '--child', part, '--impl', impl,
                   '--games', str(a.games), '--seed', str(a.seed), '--corpus', a.corpus, '--traj', a.traj]
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            line = [x for x in p.stdout.splitlines() if x.startswith('RESULT ')]
            if not line:
                print('child failed', part, impl, p.stderr[-2000:])
                continue
            r = json.loads(line[0][7:])
            allres[part][impl] = r
            print('%-10s %-12s %s' % (part, impl, json.dumps({k: (round(v, 3) if isinstance(v, float) else v)
                                                           for k, v in r.items()})), flush=True)
        ref = allres[part].get('ref')
        if ref:
            for impl, r in allres[part].items():
                if impl == 'ref':
                    continue
                sp = {}
                for k in r:
                    if k in ref and isinstance(r[k], float) and r[k] > 0 and k != 'cache_hit_rate':
                        sp[k] = round(ref[k] / r[k], 2)
                print('%-10s %-12s speedup vs ref %s' % (part, impl, json.dumps(sp)), flush=True)
    if a.out:
        with open(a.out, 'w') as f:
            json.dump(allres, f, indent=1)


if __name__ == '__main__':
    main()
