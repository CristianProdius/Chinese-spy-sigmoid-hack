"""Our first manufactured delivery: engine-measured plan variants vs the analytic bound."""
import json, glob, os, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from mintime import contract_times
D = os.path.join(os.path.dirname(__file__), '..', 'data')
P = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        d = json.loads(l)
        if d['game'] == 0: P[(d['group'], d['seed'])] = d
res = defaultdict(list); lost = Counter()
for f in glob.glob(os.path.join(D, 'mfg_*.jsonl')):
    for l in open(f):
        d = json.loads(l); p = P[(d['group'], d['seed'])]; m = p['map']
        t = contract_times(m, m['homes'][p['seat']])[d['contract']]
        if d['ours'] is None: lost[d['variant']] += 1; continue
        res[d['variant']].append(d['ours'] - t)
names = {'v1': 'A: load 2T,1F; B: load 2T,1F; boat order priority',
         'v2': 'same, sails get priority',
         'v3': 'A: load 3T; B: load 1T,2F, builds and crafts; sails get priority'}
print('| plan | delivered | rounds later than the bound 11+d(home,m)+d(m,dest): distribution | median |')
print('|---|---|---|---|')
for v in sorted(res):
    x = sorted(res[v])
    print(f"| {v}: {names[v]} | {len(x)}/{len(x)+lost[v]} | {sorted(Counter(x).items())} | {x[len(x)//2]} |")
