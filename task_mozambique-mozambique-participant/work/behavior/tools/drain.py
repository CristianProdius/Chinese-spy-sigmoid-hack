"""R3 drain: both our boats sail to the natural-stock site the Professor first gathers from
(per stitched routes.json) and gather as much as they can carry. Also a 'decoy' variant: same trip,
no gathering (separates 'our boats are there' from 'the stock is gone').
usage: python3 drain.py OUT.jsonl WORKER NWORKERS"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from passive import ROOT
from arena import Arena
from runner import run_plan
D = os.path.join(os.path.dirname(__file__), '..', 'data')

if __name__ == '__main__':
    out, w, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    routes = json.load(open(os.path.join(D, 'routes.json')))
    jobs = []
    for key, v in sorted(routes.items()):
        if not v['gathers']: continue
        rg, s, amt = v['gathers'][0]
        g = v['roles'][s]
        for variant in ('drain', 'decoy'):
            jobs.append((key, s, g, rg, variant))
    jobs = jobs[w::n]
    with Arena() as a, open(out, 'a') as f:
        for key, s, g, rg, variant in jobs:
            grp, seed, game = map(int, key.split('/'))
            if variant == 'drain':
                plan = [[('goto', s), ('gather_max', g)], [('goto', s), ('gather_max', g)]]
            else:
                plan = [[('goto', s)], [('goto', s)]]
            rec = run_plan(a, grp, seed, game, plan)
            log = rec.pop('log')
            rec.update(variant=variant, site=s, good=g, prof_first_gather=rg)
            rec['our_gathers'] = [(L['r'], L['act']['quantity']) for L in log if L['act']['op'] == 'gather']
            rec['arrive'] = [next((L['r'] for L in log if len(L['own']) > b and L['own'][b][0] == s and L['own'][b][1] == -1), None) for b in range(2)]
            rec['site_stock'] = [L['stocks'][s] for L in log]
            rec['sightings'] = [(L['r'], e['boat'], e['position'], e['destination'], e['eta']) for L in log for e in L['enemy']]
            f.write(json.dumps(rec) + '\n'); f.flush()
