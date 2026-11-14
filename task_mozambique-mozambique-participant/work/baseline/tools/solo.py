"""Solo planning quality: run the agent's planner with no opponent from our home; print plan deliveries."""
import sys, json, random, importlib.util, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
spec = importlib.util.spec_from_file_location('ag', sys.argv[1])
ag = importlib.util.module_from_spec(spec); spec.loader.exec_module(ag)
GROUPS = [2 * t + s for t in range(4) for s in range(2)]
rng = random.Random(int(sys.argv[2])); n = int(sys.argv[3])
seeds = [rng.randrange(2 ** 32) for _ in range(n)]
tot = 0
with Arena() as a:
    for m in range(n):
        o = a.reset(GROUPS[m % 8], seeds[m], 0)['observation']
        mp = o['map']; home = o['own']['home']
        geo = ag.Geo(mp, home, home); s = ag.fresh_state(geo, home)
        pl = ag.Planner(geo, home, lambda c, t: 1.0)
        t0 = time.time()
        qs, tags, _ = pl.greedy(s, [[], []], [[], []], 0, budget=20000, max_iter=12)
        d, sf, f = ag.simulate(s, geo, qs, [0, 0])
        pts = sum(mp['contracts'][c]['points'] for c in d)
        tot += pts
        print(m, GROUPS[m % 8], 'pts', pts, sorted((t, c) for c, t in d.items()), 'sims', pl.sims, '%.2fs' % (time.time() - t0))
print('mean', tot / n)
