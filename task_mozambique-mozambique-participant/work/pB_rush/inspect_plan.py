"""Show the round-0 beam plans for a map: pypy3 inspect_plan.py AGENT.py MAPIDX [--seed S] [--top 5]"""
import argparse, os, sys, random, time, importlib.util, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab')); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import fasteval as FE
ap = argparse.ArgumentParser(); ap.add_argument('agent'); ap.add_argument('m', type=int)
ap.add_argument('--seed', type=int, default=20261114); ap.add_argument('--top', type=int, default=5)
ap.add_argument('--exact', action='store_true')
a = ap.parse_args()
spec = importlib.util.spec_from_file_location('ag', os.path.abspath(a.agent)); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
rng = random.Random(a.seed); seeds = [rng.randrange(2 ** 32) for _ in range(a.m + 1)]
grp = FE.GROUPS[a.m % 8]; seed = seeds[a.m]
md = A.generate_map(grp // 2, seed); mp = A.Map(md); seat = grp % 2
print('map', a.m, 'group', grp, 'seed', seed, 'seat', seat, 'homes', md['homes'], 'roles', md['roles'])
print('routes', [(i, j, md['routes'][i][j]) for i in range(10) for j in range(i + 1, 10) if md['routes'][i][j]])
print('contracts', [(c, x['good'], x['destination'], x['deadline']) for c, x in enumerate(md['contracts'])])
eng = A.Engine(mp)
ob = FE.obs_dict(eng, seat, md); ob = json.loads(json.dumps(ob))
g = A.new_game(ob)
side = A.obs_side(ob)
hyps = sorted(g.hyps.items())
t9=time.process_time(); k0, Ps = A.evaluate_exact(g, A.Exe([[],[]],[[0],[0]]), hyps); print("null %.2fs" % (time.process_time()-t9))
print('threat per style', Ps)
t0 = time.process_time()
pool = A.beam(g, side, A.CX.mp and hyps[0][1][0].stocks[:], list(ob['claims']), 0, Ps, time.process_time() + 30)
print('beam %.2fs, pool %d' % (time.process_time() - t0, len(pool)))
for n in pool[:a.top]:
    print('%-22s proxy %6.2f deliv %s' % (n.tag, n.val, sorted((r, c) for c, r in n.res.items())))
    for b, q in enumerate(n.q):
        print('   b%d: %s' % (b, ' '.join(st[0][:2] + ''.join(',%s' % x for x in st[2:]) for st in q)))
    if a.exact:
        t1 = time.process_time()
        key, ths = A.evaluate_exact(g, n.finish(), hyps)
        print('   exact', key, '%.2fs' % (time.process_time() - t1))
if os.environ.get('KTAG'):
    sel = [n for n in pool if n.tag.startswith(os.environ['KTAG'])][:a.top]
    for n in sel:
        print('%-22s proxy %6.2f deliv %s' % (n.tag, n.val, sorted((r, c) for c, r in n.res.items())))
        for b, q in enumerate(n.q):
            print('   b%d: %s' % (b, ' '.join(st[0][:2] + ''.join(',%s' % x for x in st[2:]) for st in q)))
        key, ths = A.evaluate_exact(g, n.finish(), hyps)
        print('   exact', key)
