"""When does the Professor's plan diverge from passive in rush runs, relative to our first visible
move and our delivery? Uses score timeline (round of each of its deliveries) as the trace."""
import json, glob, os
from collections import Counter
D = os.path.join(os.path.dirname(__file__), '..', 'data')
P = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        d = json.loads(l); P[(d['group'], d['seed'], d['game'])] = d
res = Counter(); ex = []
for f in glob.glob(os.path.join(D, 'rush_*.jsonl')):
    for l in open(f):
        d = json.loads(l); p = P.get((d['group'], d['seed'], d['game']))
        if not p: continue
        seat = d['seat']
        ours = next((e[0] for e in d['events'] if e[1] == 'deliver'), None)
        pc = {c: p['claim_round'][c] for c in range(8)}
        nc = {c: (x[0] if x and x[1] != seat else None) for c, x in enumerate(d['claim_round'])}
        # first round at which the Professor's claim sequence differs
        evp = sorted((r, c) for c, r in pc.items() if r is not None)
        evn = sorted((r, c) for c, r in nc.items() if r is not None)
        div = None
        for i in range(max(len(evp), len(evn))):
            a = evp[i] if i < len(evp) else (999, -1); b = evn[i] if i < len(evn) else (999, -1)
            if a != b: div = min(a[0], b[0]); break
        kind = 'raw' if d['contract'] < 4 else 'man'
        if div is None: res[(kind, 'no change')] += 1
        elif ours is None: res[(kind, 'changed, we never delivered')] += 1; ex.append((d['group'], d['seed'], d['game'], d['contract'], div))
        elif div <= ours: res[(kind, 'changed at/before our delivery')] += 1; ex.append((d['group'], d['seed'], d['game'], d['contract'], div, ours))
        else: res[(kind, 'changed only after our delivery')] += 1
for k in sorted(res): print(k, res[k])
print('examples of change not explained by our delivery:', ex[:15])
