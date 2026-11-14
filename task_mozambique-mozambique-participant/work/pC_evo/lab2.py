"""Round-0 search with the real search(): value found vs budget.   pypy3 lab2.py AGENT.py MAP [secs...]"""
import sys, os, json, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F
A = F.load_agent(os.path.abspath(sys.argv[1]))
A.PARAMS['debug'] = True
maps = [int(x) for x in sys.argv[2].split(',')]
import os as _os
ONLY = [int(x) for x in _os.environ.get('STYLES', '0,1,2,3,4').split(',')]
rng = random.Random(int(_os.environ.get('SEED', '20261114')))
seeds = [rng.randrange(2 ** 32) for _ in range(max(maps) + 1)]
for m in maps:
    g = F.GROUPS[m % 8]; topo, seat = g // 2, g % 2
    md = P.generate_map(topo, seeds[m]); mp = P.Map(md); eng = P.Engine(mp)
    ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
    for secs in [float(x) for x in sys.argv[3:]] or [1.0, 8.0]:
        G = A.new_game(ob)
        G.hyps = [h for h in G.hyps if h.style in ONLY]
        for h in G.hyps:
            h.prof0 = h.prof.clone(); h.pred = A.prof_choose(G, h.prof, h.eng, None)
        e = G.hyps[0].eng; side = e.sides[seat]
        res = A.exact_eval(G, None, None)
        null = A.make_cand(G, ((), 0), None, res)
        t0 = time.process_time()
        pool = A.search(G, side, e.stocks, e.claims, 0, t0 + secs, [null], A.seed_genomes(G, side, e.claims, 0), 3, 10.0)
        b = pool[0]
        print('map %d g%d secs %.1f: best %.1f margins %s | ph %d ex %d pool %d | passive %s' % (
            m, g, secs, b.v, [r[0] for r in b.res], G.stats['ph'], G.stats['ex'], len(pool), [r[2] for r in res]), flush=True)
        print('    ', b.genome)
