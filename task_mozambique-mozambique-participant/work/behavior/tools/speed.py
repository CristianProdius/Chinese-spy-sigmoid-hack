"""How fast is the Professor relative to the theoretical single-contract minimum from its home?"""
import json, glob, os, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from mintime import contract_times
from styles import style_of
D = os.path.join(os.path.dirname(__file__), '..', 'data')
recs = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); recs[(r['group'], r['seed'], r['game'])] = r
gap = defaultdict(list); first_at_min = defaultdict(list); faster = 0
for r in recs.values():
    m = r['map']; t = contract_times(m, m['homes'][1 - r['seat']]); s = style_of(r['seed'], r['game'])
    ev = sorted((x, c) for c, x in enumerate(r['claim_round']) if x is not None)
    if ev: first_at_min[s].append(ev[0][0] == t[ev[0][1]])
    for c in range(8):
        x = r['claim_round'][c]
        if x is None: continue
        gap[(c, s)].append(x - t[c]); gap[(c, 'all')].append(x - t[c])
        faster += x < t[c]
print('claims faster than the analytic bound (should be 0):', faster)
print('| contract | ' + ' | '.join(f'style {s}' for s in range(5)) + ' | all |')
print('|---|' + '---|' * 6)
for c in range(8):
    cells = []
    for s in list(range(5)) + ['all']:
        v = gap[(c, s)]; cells.append(f"{st.median(v):g}" if v else '-')
    print(f"| {c} | " + ' | '.join(cells) + ' |')
print('(median rounds between the Professor claim and the fastest possible single-contract trip from its home)')
print('first claim of the game at the theoretical minimum:', {s: f"{100*sum(v)/len(v):.0f}%" for s, v in sorted(first_at_min.items())})
