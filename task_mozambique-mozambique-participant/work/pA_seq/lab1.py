import sys, time, random, itertools
import core as P
import old_brain as B

def setup(group, seed):
    topo, seat = group // 2, group % 2
    md = P.generate_map(topo, seed)
    mp = P.Map(md)
    return mp, seat

def main():
    group = int(sys.argv[1]); seed = int(sys.argv[2])
    mp, seat = setup(group, seed)
    ps = 1 - seat
    planner = B.Planner(mp, seat)
    print('roles', mp.roles, 'homes', mp.homes, 'seat', seat)
    print('contracts', list(zip(mp.c_good, mp.c_dest, mp.c_deadline)))
    seqs = [[], [4, 5, 6], [4, 5, 6, 7], [0, 4, 5, 6], [4, 0, 5, 6, 7, 1], [8, 4, 5, 6, 7], [4, 5, 1, 6, 7, 3], [0, 1, 4, 5, 6, 7]]
    for style in range(5):
        for seq in seqs:
            for Bv in (0.0, 3.5):
                eng = P.Engine(mp); prof = B.CProf(style, ps)
                t0 = time.perf_counter(); m0 = B.STATS['miss']; mt0 = B.STATS['miss_t']
                q, kept = planner.decode(eng.sides[seat], eng.stocks, eng.claims, 0, seq, Bv)
                t1 = time.perf_counter()
                plan = B.Plan(kept, Bv, 0, q)
                info = {'ours': [], 'theirs': []}
                m = B.rollout(eng, prof, plan, seat, planner, info)
                t2 = time.perf_counter()
                print('style %d seq %-22s B %.1f margin %4d us %2d them %2d | decode %.1fms roll %.1fms miss %d (%.1fms) | ours %s theirs %s rep %d' % (
                    style, seq, Bv, m, eng.sides[seat].score, eng.sides[ps].score, (t1 - t0) * 1e3, (t2 - t1) * 1e3,
                    B.STATS['miss'] - m0, (B.STATS['miss_t'] - mt0) * 1e3, info['ours'], info['theirs'], info['repairs']))
main()
