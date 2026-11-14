"""Profile phantom rollouts + decode (CPython cProfile, or PyPy timing)."""
import sys, os, json, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F
A = F.load_agent(os.path.abspath(sys.argv[1]))
A.PARAMS['debug'] = True
rng = random.Random(20261114)
seeds = [rng.randrange(2 ** 32) for _ in range(8)]
m = 3
g = F.GROUPS[m % 8]; topo, seat = g // 2, g % 2
md = P.generate_map(topo, seeds[m]); mp = P.Map(md); eng = P.Engine(mp)
ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
G = A.new_game(ob)
for h in G.hyps:
    h.prof0 = h.prof.clone(); h.pred = A.prof_choose(G, h.prof, h.eng, None)
e = G.hyps[0].eng; side = e.sides[seat]
res = A.exact_eval(G, None, None)
null = A.make_cand(G, ((), 0), None, res)
sg = A.seed_genomes(G, side, e.claims, 0)
plans = [A.decode(G, gm[0], gm[1], side, e.stocks, e.claims, 0) for gm in sg]
def run(n):
    for _ in range(n):
        for p in plans:
            A.phantom_rollout(G, G.hyps[0], p, res[0][4], res[0][5])
def rund(n):
    for _ in range(n):
        for gm in sg:
            A.decode(G, gm[0], gm[1], side, e.stocks, e.claims, 0)
if 'prof' in sys.argv:
    import cProfile, pstats
    cProfile.run('run(3)', '/tmp/pc_prof.out')
    pstats.Stats('/tmp/pc_prof.out').sort_stats('tottime').print_stats(14)
else:
    run(int(sys.argv[2]) if len(sys.argv) > 2 else 3); rund(3)
    t0 = time.process_time(); run(10); t = time.process_time() - t0
    print('phantom rollout %.3f ms' % (1000 * t / (10 * len(plans))))
    t0 = time.process_time(); rund(10); t = time.process_time() - t0
    print('decode %.3f ms' % (1000 * t / (10 * len(sg))))
