"""Coverage of rare situations in validation traces (what the validator actually exercised).
python3 coverage.py traces.jsonl ..."""
import gzip
import json
import sys
from collections import Counter

c = Counter()
for fn in sys.argv[1:]:
    for line in (gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        c['games'] += 1
        roles = d['obs'][0]['map']['roles']
        for o, a in zip(d['obs'], d['acts']):
            c['rounds'] += 1
            c['act_' + a['op']] += 1
            ops = [x['op'] for x in o['legal_actions']]
            for op in set(ops):
                c['legal_has_' + op] += 1
            own = o['own']
            if len(own['boats']) == 3:
                c['rounds_with_3_boats'] += 1
            for p in range(10):
                w = own['warehouses'][p]
                if own['workshops'][p] and own['jobs'][p] > 0 and w[0] >= 2 and w[1] >= 1 and \
                        any(b['position'] == p and b['destination'] == -1 for b in own['boats']):
                    c['job_running_with_materials_and_boat'] += 1
            if 'deliver' in ops and ('craft' in ops or 'build_workshop' in ops):
                c['deliver_and_craft_or_workshop_listed'] += 1
            if any(x['op'] == 'load' and x['good'] == 2 for x in o['legal_actions']):
                c['legal_load_M'] += 1
            if any(x['op'] == 'unload' and x['good'] == 2 for x in o['legal_actions']):
                c['legal_unload_M'] += 1
            for x in o['legal_actions']:
                if x['op'] == 'deliver' and o['map']['contracts'][x['contract']]['good'] == 2:
                    c['legal_deliver_M'] += 1
                    break
            dl = [x for x in o['legal_actions'] if x['op'] == 'deliver']
            if len(dl) >= 2:
                c['legal_two_or_more_delivers'] += 1
            if a['op'] == 'build_boat' and not any(b['position'] == own['home'] and b['destination'] == -1 for b in own['boats']):
                c['build_boat_with_no_boat_home'] += 1
        fo = d['obs'][-1]['own']
        c['games_crafted_ge1'] += fo['crafted_deliveries'] >= 1
        r = d.get('final', {}).get('result')
        if r:
            c['final_hp_%d' % r['half_points']] += 1
for k in sorted(c):
    print('%-45s %d' % (k, c[k]))
