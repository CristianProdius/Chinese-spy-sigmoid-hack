"""Cost of exact / phantom evaluations at round 0 (warm)."""
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
for m in range(1, 6):
    g = F.GROUPS[m % 8]; topo, seat = g // 2, g % 2
    md = P.generate_map(topo, seeds[m]); mp = P.Map(md); eng = P.Engine(mp)
    ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
    G = A.new_game(ob)
    t0 = time.process_time()
    for h in G.hyps:
        h.prof0 = h.prof.clone(); h.pred = A.prof_choose(G, h.prof, h.eng, None)
    e = G.hyps[0].eng; side = e.sides[seat]
    for h in G.hyps:
        r = A.exact_rollout(G, h, None, None); h.pc = r[4]; h.pg = r[5]
    tp = time.process_time() - t0
    seeds_g = A.seed_genomes(G, side, e.claims, 0)
    plans = [A.decode(G, gm[0], gm[1], side, e.stocks, e.claims, 0) for gm in seeds_g[:40]]
    t0 = time.process_time(); n0 = G.nrep
    for p in plans[:12]:
        A.exact_value(G, p, None, False)
    te = (time.process_time() - t0) / 12
    nr = (G.nrep - n0) / 12.0
    t0 = time.process_time()
    for p in plans:
        A.phantom_value(G, p)
    tph = (time.process_time() - t0) / len(plans)
    t0 = time.process_time()
    for gm in seeds_g[:40]:
        A.decode(G, gm[0], gm[1], side, e.stocks, e.claims, 0)
    td = (time.process_time() - t0) / 40
    print('map %d passive %.3fs | exact_value(5 hyps) %.1f ms (%.1f replans) | phantom_value %.2f ms | decode %.3f ms' % (m, tp, te * 1000, nr, tph * 1000, td * 1000), flush=True)
