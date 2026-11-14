"""Empirical survival of Professor claim time minus its single-contract LB, per contract index."""
import sys, json, random, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
spec = importlib.util.spec_from_file_location('ag', str(Path(__file__).resolve().parents[1] / 'agent_v1.py'))
ag = importlib.util.module_from_spec(spec); spec.loader.exec_module(ag)
GROUPS = [2 * t + s for t in range(4) for s in range(2)]
data = json.load(open(sys.argv[1])); n = max(d['map'] for d in data) + 1; seed = int(sys.argv[2])
rng = random.Random(seed); seeds = [rng.randrange(2 ** 32) for _ in range(n)]
diffs = {c: [] for c in range(8)}
with Arena() as a:
    for m in range(n):
        o = a.reset(GROUPS[m % 8], seeds[m], 0)['observation']
        mp = o['map']; seat = o['seat']
        lb = ag.single_lb(mp, mp['homes'][1 - seat])
        for d in data:
            if d['map'] != m: continue
            for c in range(8):
                x = d['claim'][c]
                diffs[c].append(999 if x is None else x - lb[c])
xs = [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]
for c in range(8):
    v = diffs[c]; N = len(v)
    print('c%d' % c, ' '.join('%d:%.2f' % (x, sum(1 for y in v if y > x) / N) for x in xs))
json.dump(diffs, open(sys.argv[3], 'w'))
