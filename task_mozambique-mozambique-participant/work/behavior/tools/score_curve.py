"""Professor passive score by round, per style (median and p90)."""
import json, glob, os, sys, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from styles import style_of
D = os.path.join(os.path.dirname(__file__), '..', 'data')
recs = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); recs[(r['group'], r['seed'], r['game'])] = r
cuts = [10, 20, 30, 40, 50, 60, 70, 80]
by = defaultdict(lambda: defaultdict(list))
for r in recs.values():
    s = style_of(r['seed'], r['game'])
    for cut in cuts:
        v = 0
        for rd, sc in r['score_tl']:
            if rd < cut: v = sc
        by[s][cut].append(v); by['all'][cut].append(v)
print('| style | ' + ' | '.join(f'by rnd {c}' for c in cuts) + ' |')
print('|---|' + '---|' * len(cuts))
for s in list(range(5)) + ['all']:
    cells = []
    for c in cuts:
        v = sorted(by[s][c]); cells.append(f"{st.median(v):g} / {v[int(len(v)*0.9)]}")
    print(f"| {s} | " + ' | '.join(cells) + ' |')
print('(cells: median / p90 of the Professor score accumulated before that round, passive play)')
