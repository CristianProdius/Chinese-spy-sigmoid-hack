"""Analyse E1 park sweep: (a) which parked sites change the Professor's plan, (b) stitched routes
from runs that did not change it. Writes data/routes.json and prints tables."""
import json, glob, os, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from mintime import all_dist
D = os.path.join(os.path.dirname(__file__), '..', 'data')
passive = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); passive[(r['group'], r['seed'], r['game'])] = r
park = [json.loads(l) for f in sorted(glob.glob(os.path.join(D, 'park_*.jsonl'))) for l in open(f)]
print('park runs', len(park))

def cat(m, seat, s):
    if s == m['homes'][seat]: return 'own home'
    if s == m['homes'][1 - seat]: return 'enemy home'
    return {0: 'timber', 1: 'fibre', 2: 'manufacturing'}[m['roles'][s]]

def claims(rec):
    return [x[0] if x else None for x in rec['claim_round']]

stats = defaultdict(lambda: [0, 0]); dscore = defaultdict(list)
stats2 = defaultdict(lambda: [0, 0])
div_rel = []
unchanged = defaultdict(list)
for r in park:
    key = (r['group'], r['seed'], r['game'])
    p = passive.get(key)
    if p is None: continue
    m = r['map']; seat = r['seat']; s = r['site']
    ch = claims(r) != p['claim_round']
    c = cat(m, seat, s)
    stats[c][0] += 1; stats[c][1] += ch
    # does the passive Professor deliver to this site, or do we ever share a site with its boats?
    met = any(sg[2] == s and sg[3] == -1 for sg in r['sightings'] if r['arrive'] is not None and sg[0] >= r['arrive'])
    stats2[(c, met)][0] += 1; stats2[(c, met)][1] += ch
    if ch:
        dscore[c].append(r['result']['scores'][1] - p['result']['scores'][1])
        pr = p['claim_round']; qr = claims(r)
        first = min(min(x for x in (pr[i], qr[i]) if x is not None) for i in range(8) if pr[i] != qr[i])
        meet = next((sg[0] for sg in r['sightings'] if sg[2] == s and sg[3] == -1 and sg[0] >= (r['arrive'] or 99)), None)
        div_rel.append((c, r['arrive'], meet, first))
    else:
        unchanged[key].append(r)
print('\n| parked site | runs | Professor plan changed | mean score change when changed |')
print('|---|---|---|---|')
for c in ['own home', 'enemy home', 'timber', 'fibre', 'manufacturing']:
    n, k = stats[c]; ds = dscore[c]
    print(f"| {c} | {n} | {k} ({100*k/max(n,1):.0f}%) | {sum(ds)/len(ds) if ds else 0:+.1f} |")
print('\n| parked site | Professor boat later docked with ours | runs | changed |')
print('|---|---|---|---|')
for (c, met), (n, k) in sorted(stats2.items()):
    print(f"| {c} | {met} | {n} | {k} ({100*k/max(n,1):.0f}%) |")
# divergence timing relative to first co-location
before = sum(1 for c, a, meet, f in div_rel if meet is None)
rel = Counter()
for c, a, meet, f in div_rel:
    if meet is None: rel['never docked together'] += 1
    elif f < meet: rel['diverged before first docking'] += 1
    elif f <= meet + 3: rel['diverged 0-3 rounds after docking'] += 1
    else: rel['diverged >3 rounds after docking'] += 1
print('\ndivergence timing vs first docking with a Professor boat (changed runs):', dict(rel))
rel2 = Counter()
for c, a, meet, f in div_rel:
    if a is None: rel2['we never arrived'] += 1
    elif f < a: rel2['first divergent claim while we were still sailing'] += 1
    else: rel2['first divergent claim came after we parked (claims lag the cause; see replay_park)'] += 1
print('divergence timing vs our arrival:', dict(rel2))
print('changed runs detail (site category, our arrival, first docking with Prof boat, first divergent claim round):')
for x in div_rel: print('   ', x)

# stitched routes from unchanged runs
routes = {}
for key, rs in unchanged.items():
    p = passive[key]; m = p['map']; seat = p['seat']
    obs = defaultdict(dict)  # boat -> round -> (pos,dest,eta)
    stock = defaultdict(dict)
    covered = defaultdict(set)
    for r in rs:
        for (rd, b, pos, dst, eta) in r['sightings']:
            obs[b][rd] = (pos, dst, eta)
        if r['arrive'] is not None:
            for rd in range(r['arrive'], 80): covered[rd].add(r['site'])
        for rd, v in enumerate(r['site_stock']):
            if v is not None and m['roles'][r['site']] in (0, 1): stock[r['site']][rd] = v
    # gather events: stock drop between consecutive observed rounds
    gathers = []
    for s, ser in stock.items():
        prev = None
        for rd in sorted(ser):
            v = ser[rd]
            if prev is not None and prev[0] == rd - 1 and v < prev[1]:
                gathers.append((rd, s, prev[1] - v))
            prev = (rd, v)
    docks = defaultdict(list)
    for b, ser in obs.items():
        for rd, (pos, dst, eta) in sorted(ser.items()):
            if dst == -1: docks[b].append((rd, pos))
    man_sites = [s for s, ro in enumerate(m['roles']) if ro == 2]
    man_dwell = {s: sorted({rd for b in docks for rd, pos in docks[b] if pos == s}) for s in man_sites}
    routes['%d/%d/%d' % key] = dict(seat=seat, homes=m['homes'], roles=m['roles'],
        boats_seen=sorted(obs.keys()), third_boat_first_seen=min(obs[2]) if 2 in obs else None,
        gathers=sorted(gathers), man_dwell={str(k): v for k, v in man_dwell.items()},
        docks={str(b): v for b, v in docks.items()}, coverage_sites=len(rs),
        claim_round=p['claim_round'], score=p['result']['scores'][1])
json.dump(routes, open(os.path.join(D, 'routes.json'), 'w'))
print('\nstitched (map,game) with >=1 unchanged park run:', len(routes))
nb = Counter(); tb = []
for k, v in routes.items():
    nb[len(v['boats_seen'])] += 1
    if v['third_boat_first_seen'] is not None: tb.append(v['third_boat_first_seen'])
print('boats seen per game:', dict(nb), 'third boat first-seen rounds:', sorted(tb))
