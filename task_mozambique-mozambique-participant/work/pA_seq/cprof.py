import cProfile, pstats, random, sys
import core as P
import tsched as S
rng = random.Random(5)
maps = []
for it in range(30):
    topo = rng.randrange(4); seat = rng.randrange(2); sd = rng.randrange(2 ** 32)
    maps.append((P.Map(P.generate_map(topo, sd)), seat))
def run():
    for mp, seat in maps:
        eng = P.Engine(mp)
        for seq in ([4, 5, 6, 7], [0, 4, 5, 1, 6], [5, 2, 6, 7, 3]):
            S.decode_seq(mp, eng.sides[seat], eng.stocks, eng.claims, 0, seq, 3.5)
cProfile.run('run()', '/tmp/pA_prof.out')
p = pstats.Stats('/tmp/pA_prof.out'); p.sort_stats('tottime').print_stats(18)
