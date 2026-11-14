"""Analyse R1 rush runs: did we win the contract, did the Professor contest it, how did it re-plan."""
import json, glob, os, sys
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from mintime import contract_times
D = os.path.join(os.path.dirname(__file__), '..', 'data')
passive = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); passive[(r['group'], r['seed'], r['game'])] = r
rush = [json.loads(l) for f in sorted(glob.glob(os.path.join(D, 'rush_*.jsonl'))) for l in open(f)]
print('rush runs', len(rush))
rows = []
for r in rush:
    p = passive.get((r['group'], r['seed'], r['game']))
    if p is None: continue
    c = r['contract']; m = r['map']; seat = r['seat']
    ours = next((e[0] for e in r['events'] if e[1] == 'deliver' and e[2] == c), None)
    pc = p['claim_round'][c]
    cr = r['claim_round'][c]
    prof_now = cr[0] if cr and cr[1] != seat else None
    tmin = contract_times(m, m['homes'][seat])[c]
    # prof changes on other contracts
    pclaims = [x[0] if x and x[1] != seat else None for x in r['claim_round']]
    others = [i for i in range(8) if i != c]
    changed = [i for i in others if pclaims[i] != p['claim_round'][i]]
    lost_any = [i for i in others if p['claim_round'][i] is not None and pclaims[i] is None]
    gained = [i for i in others if p['claim_round'][i] is None and pclaims[i] is not None]
    rows.append(dict(key=(r['group'], r['seed'], r['game']), c=c, raw=c < 4, ours=ours, tmin=tmin, pc=pc,
                     prof_now=prof_now, changed=changed, lost_any=lost_any, gained=gained,
                     dscore=r['result']['scores'][1] - p['result']['scores'][1], us=r['result']['scores'][0],
                     prof=r['result']['scores'][1]))
json.dump(rows, open(os.path.join(D, 'rush_rows.json'), 'w'))
def pct(a, b): return f"{a}/{b} ({100*a/max(b,1):.0f}%)"
for kind in (True, False):
    R = [x for x in rows if x['raw'] == kind]
    print('\n==', 'raw' if kind else 'manufactured', 'contracts, runs', len(R))
    won = [x for x in R if x['ours'] is not None]
    print('we delivered:', pct(len(won), len(R)))
    ok = [x for x in won if x['ours'] == x['tmin']]
    print('  ...at the analytic min time:', pct(len(ok), len(won)), ' later:', Counter(x['ours'] - x['tmin'] for x in won))
    # expected outcome by passive timing
    ahead = [x for x in R if x['pc'] is None or x['pc'] > x['tmin']]
    print('our min time beats passive Professor claim (or it never claims):', pct(len(ahead), len(R)))
    print('  ...of those we actually delivered:', pct(sum(1 for x in ahead if x['ours'] is not None), len(ahead)))
    contested = [x for x in R if x['prof_now'] is not None and (x['pc'] is None or x['prof_now'] < x['pc'])]
    print('Professor claimed it EARLIER than in passive play (contest):', pct(len(contested), len(R)))
    for x in contested[:8]: print('   ', x['key'], 'c', x['c'], 'passive', x['pc'], 'now', x['prof_now'], 'our tmin', x['tmin'])
    later = [x for x in R if x['prof_now'] is not None and x['pc'] is not None and x['prof_now'] > x['pc']]
    print('Professor claimed it LATER than passive:', pct(len(later), len(R)))
    # reaction when we stole a contract the Professor claims in passive
    stolen = [x for x in won if x['pc'] is not None]
    print('we took a contract the Professor claims in passive:', len(stolen))
    if stolen:
        print('  Professor score change: mean %+.1f' % (sum(x['dscore'] for x in stolen) / len(stolen)),
              Counter(x['dscore'] for x in stolen).most_common(8))
        print('  other contracts with changed claim round: mean %.1f' % (sum(len(x['changed']) for x in stolen) / len(stolen)))
        print('  picked up a contract it skipped in passive:', pct(sum(1 for x in stolen if x['gained']), len(stolen)))
        print('  dropped another contract it took in passive:', pct(sum(1 for x in stolen if x['lost_any']), len(stolen)))
    free = [x for x in won if x['pc'] is None]
    if free:
        print('we took a contract the Professor skips in passive:', len(free), 'Professor score change mean %+.1f' % (sum(x['dscore'] for x in free) / len(free)),
              'runs with any change in its other claims:', pct(sum(1 for x in free if x['changed']), len(free)))
