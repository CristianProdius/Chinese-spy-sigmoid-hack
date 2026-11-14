"""Summaries from stitched routes (unchanged park runs): workshop base, gathering, boat count."""
import json, os, statistics as st
from collections import Counter
sys_path = os.path.dirname(__file__)
import sys; sys.path.insert(0, sys_path)
from mintime import all_dist
D = os.path.join(sys_path, '..', 'data')
R = json.load(open(os.path.join(D, 'routes.json')))
P = {}
import glob
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        d = json.loads(l); P['%d/%d/%d' % (d['group'], d['seed'], d['game'])] = d
base_near = Counter(); nbase = Counter(); first_g = []; g_amt = Counter(); g_role = Counter(); n_g = []
base_first = []; dwell = []
for k, v in R.items():
    m = P[k]['map']; dist = all_dist(m['routes'])
    ph = v['homes'][1 - v['seat']]; oh = v['homes'][v['seat']]
    md = {int(s): d for s, d in v['man_dwell'].items()}
    used = [s for s, d in md.items() if len(d) >= 3]
    nbase[len(used)] += 1
    if md:
        main = max(md, key=lambda s: len(md[s]))
        if md[main]:
            others = [s for s in md if s != main]
            near = all(dist[ph][main] <= dist[ph][o] for o in others)
            base_near[near] += 1
            base_first.append(md[main][0]); dwell.append(len(md[main]))
    gs = v['gathers']
    n_g.append(len(gs))
    if gs: first_g.append(gs[0][0])
    for rd, s, a in gs:
        g_amt[a] += 1; g_role['timber' if m['roles'][s] == 0 else 'fibre'] += 1
print('games', len(R))
print('manufacturing sites with >=3 rounds of Professor docking:', dict(nbase))
print('main workshop site is the manufacturing site nearest its home:', dict(base_near))
print('first docking at main manufacturing site: median', st.median(base_first), 'range', min(base_first), max(base_first))
print('rounds docked at main site (of 80, only rounds we could see): median', st.median(dwell))
print('gather events seen per game: median', st.median(n_g), '; first gather round median', st.median(first_g), 'range', min(first_g), max(first_g))
print('gather amounts:', dict(g_amt), 'by good:', dict(g_role))
print('third boat ever seen:', sum(1 for v in R.values() if v['third_boat_first_seen'] is not None))
