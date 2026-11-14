import sys, random, time
import core as P
import tsched as S
cnt = {'copy': 0}
orig = S.Sched.copy
def cp(self):
    cnt['copy'] += 1
    return orig(self)
S.Sched.copy = cp
rng = random.Random(5)
maps = []
for it in range(40):
    topo = rng.randrange(4); seat = rng.randrange(2); sd = rng.randrange(2 ** 32)
    mp = P.Map(P.generate_map(topo, sd)); maps.append((mp, seat))
for rep in range(4):
    for name, seq in (('M1', [4]), ('M4', [4, 5, 6, 7]), ('R2', [0, 1]), ('mix', [0, 4, 5, 1, 6])):
        cnt['copy'] = 0
        t0 = time.perf_counter()
        for _ in range(5):
            for mp, seat in maps:
                eng = P.Engine(mp)
                S.decode_seq(mp, eng.sides[seat], eng.stocks, eng.claims, 0, seq, 3.5)
        dt = time.perf_counter() - t0
        n = 5 * len(maps)
        print(rep, name, 'ms/decode %.3f copies/decode %.0f us/copy(all-in) %.2f' % (1e3 * dt / n, cnt['copy'] / n, 1e6 * dt / max(1, cnt['copy'])))
