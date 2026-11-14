"""How early can a passive observer tell the 5 styles apart from public info only
(claims + opponent_score timeline)? For each map and style: the first round after which that
style's public trace differs from all 4 other styles' traces."""
import json, glob, os, sys, statistics as st
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from styles import style_of
D = os.path.join(os.path.dirname(__file__), '..', 'data')
bm = defaultdict(dict)
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); bm[(r['group'], r['seed'])][style_of(r['seed'], r['game'])] = r
def events(r):  # set of (round, contract) claims
    return sorted((x, c) for c, x in enumerate(r['claim_round']) if x is not None)
def sep_round(a, b):
    ea, eb = events(a), events(b)
    for i in range(max(len(ea), len(eb))):
        x = ea[i] if i < len(ea) else (999, -1); y = eb[i] if i < len(eb) else (999, -1)
        if x != y: return min(x[0], y[0])
    return None  # identical public traces
ident = defaultdict(list); never = Counter(); n = 0
for k, gs in bm.items():
    if len(gs) < 5: continue
    n += 1
    for s in range(5):
        rs = [sep_round(gs[s], gs[t]) for t in range(5) if t != s]
        if any(x is None for x in rs): never[s] += 1; ident[s].append(80)
        else: ident[s].append(max(rs))
print('maps', n)
print('| style | median round when unique (claims only) | p25 | p75 | identifiable by round 10 | by round 20 | never (twin style on this map) |')
print('|---|---|---|---|---|---|---|')
for s in range(5):
    v = sorted(ident[s])
    print(f"| {s} | {st.median(v)} | {v[len(v)//4]} | {v[3*len(v)//4]} | {100*sum(x<=10 for x in v)/len(v):.0f}% | {100*sum(x<=20 for x in v)/len(v):.0f}% | {never[s]} |")
# which style pairs are twins (identical public traces) most often
tw = Counter()
for k, gs in bm.items():
    if len(gs) < 5: continue
    for s in range(5):
        for t in range(s + 1, 5):
            if gs[s]['claim_round'] == gs[t]['claim_round']: tw[(s, t)] += 1
print('identical claim vectors by style pair:', sorted(tw.items()))
