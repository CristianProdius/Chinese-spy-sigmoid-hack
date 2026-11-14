"""Compare Professor claim rounds (from prof_timeline JSON) with single-project lower bounds from our simulator."""
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
from collections import defaultdict
diffs = defaultdict(list)
with Arena() as a:
    for m in range(n):
        o = a.reset(GROUPS[m % 8], seeds[m], 0)['observation']
        mp = o['map']; seat = o['seat']
        lb = ag.single_lb(mp, mp['homes'][1 - seat])
        rows = [d for d in data if d['map'] == m]
        print('map', m, 'grp', GROUPS[m % 8], 'LB', lb)
        for d in rows:
            print('   game', d['game'], 'claims', d['claim'], ' diff', [None if x is None else x - l for x, l in zip(d['claim'], lb)])
            for c, (x, l) in enumerate(zip(d['claim'], lb)):
                diffs[(c, d['game'])].append(None if x is None else x - l)
for c in range(8):
    print('contract', c, ' '.join('g%d:%s' % (g, sorted([v for v in diffs[(c, g)] if v is not None])) for g in range(5)))
