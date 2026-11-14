"""Round-0 search quality: phantom vs exact value of the best plans, short vs long GA budget.
    pypy3 lab0.py AGENT.py --maps 6 [--first-map 0] [--secs 0.55,6]
"""
import sys, os, json, time, random, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F
ap = argparse.ArgumentParser()
ap.add_argument('agent'); ap.add_argument('--maps', type=int, default=4); ap.add_argument('--seed', type=int, default=20261114)
ap.add_argument('--first-map', type=int, default=0); ap.add_argument('--secs', default='0.55,6')
ap.add_argument('--show', type=int, default=0)
a = ap.parse_args()
A = F.load_agent(os.path.abspath(a.agent))
A.PARAMS['debug'] = True
rng = random.Random(a.seed)
seeds = [rng.randrange(2 ** 32) for _ in range(a.first_map + a.maps)]
for m in range(a.first_map, a.first_map + a.maps):
    g = F.GROUPS[m % 8]
    topo, seat = g // 2, g % 2
    md = P.generate_map(topo, seeds[m]); mp = P.Map(md)
    eng = P.Engine(mp)
    ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
    for secs in [float(x) for x in a.secs.split(',')]:
        G = A.new_game(ob)
        for h in G.hyps:
            h.prof0 = h.prof.clone(); h.pred = A.prof_choose(G, h.prof, h.eng, None)
        e = G.hyps[0].eng; side = e.sides[seat]
        for h in G.hyps:
            r = A.exact_rollout(G, h, None, None); h.pc = r[4]; h.pg = r[5]
        passive = [A.exact_rollout(G, h, None, None)[2] for h in G.hyps]
        t0 = time.process_time()
        pool = A.ga_search(G, side, e.stocks, e.claims, 0, t0 + secs, A.seed_genomes(G, side, e.claims, 0))
        out = []
        for v, genome, plan in pool[:4]:
            res = [A.exact_rollout(G, h, plan, None) for h in G.hyps]
            out.append((v, A.value_of(res), [r[0] for r in res]))
        print('map %2d g%d secs %.2f evals %5d passive %s | %s' % (m, g, secs, G.stats['ph'], passive,
              ' | '.join('ph %.1f ex %.1f %s' % o for o in out)), flush=True)
        if a.show:
            print('   best genome', pool[0][1])
