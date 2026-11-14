"""R3: drain the Professor's first natural-stock source (both our boats gather there) vs a decoy
trip (same trip, no gathering)."""
import json, glob, os, sys, statistics as st
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from styles import style_of
D = os.path.join(os.path.dirname(__file__), '..', 'data')
P = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        d = json.loads(l); P[(d['group'], d['seed'], d['game'])] = d
runs = [json.loads(l) for f in glob.glob(os.path.join(D, 'drain_*.jsonl')) for l in open(f)]
by = defaultdict(dict)
for r in runs: by[(r['group'], r['seed'], r['game'])][r['variant']] = r
rows = []
for k, v in sorted(by.items()):
    p = P[k]
    for var, r in v.items():
        c = [x[0] if x and x[1] != r['seat'] else None for x in r['claim_round']]
        first_ours = r['our_gathers'][0][0] if r['our_gathers'] else None
        taken = sum(q for _, q in r['our_gathers'])
        rows.append(dict(key=k, style=style_of(k[1], k[2]), var=var, site=r['site'], prof_first_gather=r['prof_first_gather'],
                         arrive=max(a for a in r['arrive'] if a is not None) if any(a is not None for a in r['arrive']) else None,
                         our_first_gather=first_ours, taken=taken, before=first_ours is not None and first_ours < r['prof_first_gather'],
                         changed=c != p['claim_round'], d=r['result']['scores'][1] - p['result']['scores'][1],
                         sightings_at_site=sum(1 for s in r['sightings'] if s[2] == r['site'] and s[3] == -1)))
print('runs', len(rows))
for var in ('decoy', 'drain'):
    R = [x for x in rows if x['var'] == var]
    if not R: continue
    print(f"\n{var}: n={len(R)} Professor plan changed {sum(x['changed'] for x in R)} | score change mean {st.mean(x['d'] for x in R):+.2f} dist {sorted(Counter(x['d'] for x in R).items())}")
    if var == 'drain':
        B = [x for x in R if x['before']]; A = [x for x in R if not x['before']]
        print(f"  drained before its first gather there: {len(B)} -> changed {sum(x['changed'] for x in B)}, score change mean {st.mean(x['d'] for x in B) if B else 0:+.2f}, dist {sorted(Counter(x['d'] for x in B).items())}")
        print(f"  arrived too late:                     {len(A)} -> changed {sum(x['changed'] for x in A)}, score change mean {st.mean(x['d'] for x in A) if A else 0:+.2f}")
        print('  units we took: mean %.1f' % st.mean(x['taken'] for x in R))
json.dump(rows, open(os.path.join(D, 'drain_rows.json'), 'w'), default=list)
