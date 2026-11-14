"""Differential test: fastcore.py vs the validated reference work/binary/professor.py.

    pypy3 difftest.py [--games 2000] [--seed 1] [--jobs 8] [--mode games|tracker|both]

games mode: every game runs a reference world (P.Engine + P.Professor) and a fast world
(F.Engine + F.Professor with the shared replan cache) in lockstep. Our seat plays one of several
policies (orders picked on the reference world, applied to both):
    wait     never moves (the Professor plays alone)
    random   random legal orders biased to deliver / build / craft (as test_professor.py)
    chaos    random legal orders biased to sails and gathers (route conflicts, stock denial)
             and building a third boat
    mirror   a Professor of a random style in our seat (ref and fast copies, both compared)
    twin     a Professor of the opponent's own style in our seat (maximal contract contention)
    mirror3  a mirror that first builds a third boat (3-boat Sim, 3-queue interleave)
Every round it compares: both views (all fields), both legal lists, the Professor's order, its
remaining plan, plan contracts, stock estimates, last_round and replan count, mirror orders/plans,
the engine step's ok flags and the full engine state after the step.
Each map is played twice with different policies sharing one fast Map, so the second game runs on
a warm replan cache. In 1/3 of the games we also fork both worlds (Engine.clone/deepcopy +
Professor.clone) at a random round and play 12 rounds of a different random policy from the
fork, comparing again (clones + cache hits from diverging futures).

tracker mode: the fast Tracker (fed JSON observations and our orders) against reference tracking
(five P.Engine + P.Professor hypotheses pruned with compare_observation from test_professor.py):
same surviving styles every round, same predicted Professor orders, the true style never dropped,
and the true hypothesis's engine equals the real game state.
"""
import argparse
import copy
import json
import multiprocessing as mpc
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P          # noqa: E402
import fastcore as F           # noqa: E402
from test_professor import compare_observation   # noqa: E402

POLICIES = ('wait', 'random', 'chaos', 'mirror', 'twin', 'mirror3')


def side_state(side):
    return (side.home, side.score, side.crafted, [list(b) for b in side.boats], list(side.wh),
            [bool(x) for x in side.ws], list(side.jobs))


def eng_state(e):
    return (e.round, list(e.stocks), list(e.claims), side_state(e.sides[0]), side_state(e.sides[1]))


def view_state(v):
    return (v.round, v.seat, v.opponent_score, list(v.stocks), [bool(x) for x in v.visible],
            list(v.claims), sorted(v.enemy_boats), side_state(v.side))


def prof_state(p):
    return (list(p.plan), list(p.plan_contracts), list(p.est), p.last_round, p.replans,
            (p.B, p.A, p.W), p.seat)


class Mismatch(Exception):
    pass


def check(what, a, b, ctx):
    if a != b:
        raise Mismatch('%s %s: ref=%r fast=%r' % (ctx, what, a, b))


def pick(policy, rng, legal, mirror_order, rnd):
    """Our order on the reference world's legal list."""
    if policy == 'wait':
        return P.WAIT
    if policy in ('mirror', 'twin', 'mirror3'):
        if policy == 'mirror3' and P.BUILD_BOAT in legal:
            return P.BUILD_BOAT
        return mirror_order
    if policy == 'random':
        if rng.random() < 0.25:
            return P.WAIT
        pool = [a for a in legal if a[0] in ('deliver', 'build_workshop', 'craft')]
        if not pool or rng.random() < 0.2:
            pool = legal
        return rng.choice(pool)
    # chaos
    r = rng.random()
    if P.BUILD_BOAT in legal and r < 0.3:
        return P.BUILD_BOAT
    pool = [a for a in legal if a[0] == 'deliver']
    if pool and r < 0.8:
        return rng.choice(pool)
    pool = [a for a in legal if a[0] in ('sail', 'gather')]
    if pool and rng.random() < 0.75:
        return rng.choice(pool)
    return rng.choice(legal)


def run_world(ctx, rng, policy, refw, fastw, seat, rounds=None):
    """Plays both worlds in lockstep. refw/fastw: dict(eng, prof, mirror). Returns rounds played."""
    ps = 1 - seat
    reng, rprof, rmir = refw['eng'], refw['prof'], refw['mirror']
    feng, fprof, fmir = fastw['eng'], fastw['prof'], fastw['mirror']
    n = 0
    while reng.round < 80 and (rounds is None or n < rounds):
        c = '%s r%d' % (ctx, reng.round)
        check('engine', eng_state(reng), eng_state(feng), c)
        for s in (0, 1):
            check('view%d' % s, view_state(reng.view(s)), view_state(feng.view(s)), c)
            check('legal%d' % s, reng.legal(s), feng.legal(s), c)
        legal = reng.legal(seat)
        mo = None
        if policy in ('mirror', 'twin', 'mirror3'):
            mo = rmir.choose(reng.view(seat))
            fmo = fmir.choose(feng.view(seat))
            check('mirror order', mo, fmo, c)
            check('mirror state', prof_state(rmir), prof_state(fmir), c)
        mine = pick(policy, rng, legal, mo, reng.round)
        po = rprof.choose(reng.view(ps))
        fpo = fprof.choose(feng.view(ps))
        check('prof order', po, fpo, c)
        check('prof state', prof_state(rprof), prof_state(fprof), c)
        orders = [None, None]
        orders[seat] = mine
        orders[ps] = po
        ok1 = reng.step(orders)
        ok2 = feng.step(list(orders))
        check('step ok', ok1, ok2, c)
        n += 1
    check('final engine', eng_state(reng), eng_state(feng), ctx)
    return n


def new_worlds(md, fmp, style, seat, mirror_style):
    ps = 1 - seat
    rmp = P.Map(md)
    refw = dict(eng=P.Engine(rmp), prof=P.Professor(style, ps),
                mirror=P.Professor(mirror_style, seat) if mirror_style is not None else None)
    fastw = dict(eng=F.Engine(fmp), prof=F.Professor(style, ps),
                 mirror=F.Professor(mirror_style, seat) if mirror_style is not None else None)
    return refw, fastw


def fork(w, fast):
    if fast:
        return dict(eng=w['eng'].clone(), prof=w['prof'].clone(),
                    mirror=w['mirror'].clone() if w['mirror'] else None)
    return dict(eng=copy.deepcopy(w['eng']), prof=w['prof'].clone(),
                mirror=w['mirror'].clone() if w['mirror'] else None)


def game_job(args):
    """One map, two games (different policies, shared fast Map = warm cache 2nd time)."""
    idx, seed0 = args
    rng = random.Random(seed0 * 1000003 + idx)
    topo = rng.randrange(4)
    seat = rng.randrange(2)
    seed = rng.randrange(2 ** 32)
    md = F.generate_map(topo, seed)
    if md != P.generate_map(topo, seed):
        return dict(idx=idx, games=0, rounds=0, error='generate_map differs')
    fmp = F.Map(md)
    out = dict(idx=idx, games=0, rounds=0, forks=0, fork_rounds=0, error=None, policies=[], replans=0, cpu_ref=0.0, cpu_fast=0.0)
    try:
        for g in range(2):
            policy = POLICIES[(idx * 2 + g) % len(POLICIES)]
            style = rng.randrange(5)
            mstyle = None
            if policy in ('mirror', 'mirror3'):
                mstyle = rng.randrange(5)
            elif policy == 'twin':
                mstyle = style
            refw, fastw = new_worlds(md, fmp, style, seat, mstyle)
            ctx = 'job%d game%d topo%d seed%d seat%d style%d policy %s' % (idx, g, topo, seed, seat, style, policy)
            prng = random.Random(rng.randrange(2 ** 31))
            fork_at = rng.randrange(1, 70) if rng.random() < 0.34 else -1
            if fork_at > 0:
                out['rounds'] += run_world(ctx, prng, policy, refw, fastw, seat, rounds=fork_at)
                frng_state = prng.getstate()
                r2, f2 = fork(refw, False), fork(fastw, True)
                fpol = POLICIES[rng.randrange(len(POLICIES))]
                if fpol in ('mirror', 'twin', 'mirror3') and r2['mirror'] is None:
                    fpol = 'chaos'
                out['fork_rounds'] += run_world(ctx + ' fork@%d %s' % (fork_at, fpol),
                                                random.Random(rng.randrange(2 ** 31)), fpol, r2, f2, seat, rounds=12)
                out['forks'] += 1
                prng.setstate(frng_state)
            out['rounds'] += run_world(ctx, prng, policy, refw, fastw, seat)
            out['games'] += 1
            out['policies'].append(policy)
            out['replans'] += refw['prof'].replans
    except Mismatch as e:
        out['error'] = str(e)[:2000]
    except Exception as e:   # noqa: BLE001
        import traceback
        out['error'] = 'CRASH ' + traceback.format_exc()[-1500:]
    return out


# ---------------------------------------------------------------------------------------------
# tracker mode
# ---------------------------------------------------------------------------------------------

def obs_dict(eng, seat, map_dict):
    """The JSON observation the agent receives (same as work/lab/fasteval.py)."""
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


def tracker_job(args):
    idx, seed0 = args
    rng = random.Random(seed0 * 7919 + idx + 17)
    topo = rng.randrange(4)
    seat = rng.randrange(2)
    seed = rng.randrange(2 ** 32)
    style = rng.randrange(5)
    ps = 1 - seat
    policy = POLICIES[idx % len(POLICIES)]
    md = P.generate_map(topo, seed)
    rmp = P.Map(md)
    real = P.Engine(rmp)
    prof = P.Professor(style, ps)
    mir = None
    if policy in ('mirror', 'mirror3'):
        mir = P.Professor(rng.randrange(5), seat)
    elif policy == 'twin':
        mir = P.Professor(style, seat)
    ref_h = {s: (P.Engine(rmp), P.Professor(s, ps)) for s in range(5)}
    tr = None
    out = dict(idx=idx, rounds=0, error=None, unique_at=None, left=None, style=style, policy=policy,
               cpu_ref=0.0, cpu_fast=0.0)
    ctx = 'tracker job%d topo%d seed%d seat%d style%d policy %s' % (idx, topo, seed, seat, style, policy)
    try:
        while real.round < 80:
            obs = obs_dict(real, seat, md)
            c = '%s r%d' % (ctx, real.round)
            t0 = time.process_time()
            for s in list(ref_h):
                if compare_observation(obs, ref_h[s][0], seat):
                    del ref_h[s]
            preds = {s: p.choose(e.view(ps)) for s, (e, p) in ref_h.items()}
            t1 = time.process_time()
            if tr is None:
                tr = F.Tracker(obs)
            alive = tr.observe(obs)
            fpreds = {h.style: h.order() for h in alive}
            t2 = time.process_time()
            out['cpu_ref'] += t1 - t0
            out['cpu_fast'] += t2 - t1
            check('survivors', sorted(ref_h), sorted(fpreds), c)
            check('predicted orders', preds, fpreds, c)
            if style not in ref_h:
                raise Mismatch('%s: true style dropped' % c)
            h = [x for x in alive if x.style == style][0]
            check('true hypothesis engine', eng_state(real), eng_state(h.eng), c)
            if out['unique_at'] is None and len(alive) == 1:
                out['unique_at'] = real.round
            legal = real.legal(seat)
            mo = mir.choose(real.view(seat)) if mir is not None else None
            mine = pick(policy, rng, legal, mo, real.round)
            po = prof.choose(real.view(ps))
            check('true order', po, fpreds[style], c)
            orders = [None, None]
            orders[seat] = mine
            orders[ps] = po
            real.step(orders)
            t0 = time.process_time()
            for s, (e, p) in ref_h.items():
                o2 = [None, None]
                o2[seat] = mine
                o2[ps] = preds[s]
                e.step(o2)
            t1 = time.process_time()
            tr.commit(P.order_to_json(mine) if rng.random() < 0.5 else mine)
            t2 = time.process_time()
            out['cpu_ref'] += t1 - t0
            out['cpu_fast'] += t2 - t1
            out['rounds'] += 1
        out['left'] = sorted(h.style for h in tr.hyps)
    except Mismatch as e:
        out['error'] = str(e)[:2000]
    except Exception:   # noqa: BLE001
        import traceback
        out['error'] = 'CRASH ' + traceback.format_exc()[-1500:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--games', type=int, default=2000, help='games in games mode (2 per map)')
    ap.add_argument('--tracker-games', type=int, default=300)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--mode', default='both', choices=['games', 'tracker', 'both'])
    a = ap.parse_args()
    t0 = time.time()
    ok = True
    summary = {}
    if a.mode in ('games', 'both'):
        jobs = [(i, a.seed) for i in range((a.games + 1) // 2)]
        with mpc.Pool(a.jobs) as pool:
            res = []
            for r in pool.imap_unordered(game_job, jobs, chunksize=1):
                res.append(r)
                if r['error']:
                    print('FAIL', r['error'], flush=True)
                if len(res) % 100 == 0:
                    print('  %d/%d maps done, %d errors, %.0fs' % (len(res), len(jobs), sum(1 for x in res if x['error']),
                                                                  time.time() - t0), flush=True)
        errs = [r for r in res if r['error']]
        pol = {}
        for r in res:
            for p in r['policies']:
                pol[p] = pol.get(p, 0) + 1
        summary['games'] = dict(games=sum(r['games'] for r in res), rounds=sum(r['rounds'] for r in res),
                                forks=sum(r['forks'] for r in res), fork_rounds=sum(r.get('fork_rounds', 0) for r in res),
                                replans=sum(r['replans'] for r in res),
                                failed_maps=len(errs), policies=pol)
        ok = ok and not errs
    if a.mode in ('tracker', 'both'):
        jobs = [(i, a.seed) for i in range(a.tracker_games)]
        with mpc.Pool(a.jobs) as pool:
            res = []
            for r in pool.imap_unordered(tracker_job, jobs, chunksize=1):
                res.append(r)
                if r['error']:
                    print('FAIL', r['error'], flush=True)
        errs = [r for r in res if r['error']]
        uq = sorted(r['unique_at'] for r in res if r['unique_at'] is not None)
        summary['tracker'] = dict(games=len(res), rounds=sum(r['rounds'] for r in res), failed=len(errs),
                                  never_unique=sum(1 for r in res if r['unique_at'] is None and not r['error']),
                                  unique_median=uq[len(uq) // 2] if uq else None,
                                  cpu_ref=round(sum(r['cpu_ref'] for r in res), 1),
                                  cpu_fast=round(sum(r['cpu_fast'] for r in res), 1))
        ok = ok and not errs
    summary['wall'] = round(time.time() - t0, 1)
    summary['result'] = 'PASS' if ok else 'FAIL'
    print(json.dumps(summary))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
