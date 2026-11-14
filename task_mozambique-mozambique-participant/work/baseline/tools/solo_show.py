import sys, json, random, importlib.util, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
spec = importlib.util.spec_from_file_location('ag', sys.argv[1])
ag = importlib.util.module_from_spec(spec); spec.loader.exec_module(ag)
group, seed = int(sys.argv[2]), int(sys.argv[3])
names = {0: 'GO', 1: 'TAKE', 2: 'DROP', 3: 'PROC', 4: 'PICK', 5: 'DELIV'}
with Arena() as a:
    o = a.reset(group, seed, 0)['observation']
    mp = o['map']; home = o['own']['home']
    print('roles', mp['roles'], 'home', home, 'edges', [(i, j, mp['routes'][i][j]) for i in range(10) for j in range(i + 1, 10) if mp['routes'][i][j]])
    print('contracts', [(c['good'], c['destination'], c['deadline']) for c in mp['contracts']])
    geo = ag.Geo(mp, home, home); s = ag.fresh_state(geo, home)
    pl = ag.Planner(geo, home, lambda c, t: 1.0)
    qs, tags, _ = pl.greedy(s, [[], []], [[], []], 0, budget=20000, max_iter=12)
    for b in range(2):
        print('boat', b, ' '.join('%s%s' % (names[st[0]], list(st[1:])) for st in qs[b]))
    d, sf, f = ag.simulate(s, geo, qs, [0, 0])
    print(sorted((t, c) for c, t in d.items()))
