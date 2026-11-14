"""E1: park boat 0 at each non-home site (boat 1 stays home), every game index, on a subset of maps.
usage: python3 park_sweep.py OUT.jsonl WORKER NWORKERS [MAPS_PER_GROUP]
Stores compact logs: per round enemy sightings, stock at parked site, own boat 0 position."""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from passive import maps, ROOT
from arena import Arena
from observe import observe

if __name__ == '__main__':
    out, w, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    ms = maps()
    sel = []
    for g in range(8):
        sel += [m for m in ms if m[0] == g and m[2] == 'rand'][:k]
    jobs = []
    for (g, sd, src) in sel:
        for game in range(5):
            for site in range(10):
                jobs.append((g, sd, game, site))
    jobs = jobs[w::n]
    done = set()
    if os.path.exists(out):
        for line in open(out):
            d = json.loads(line); done.add((d['group'], d['seed'], d['game'], d['site']))
    with Arena() as a, open(out, 'a') as f:
        for g, sd, game, site in jobs:
            if (g, sd, game, site) in done: continue
            o0 = a.reset(g, sd, game)['observation']
            if o0['map']['homes'][o0['seat']] == site: continue  # own home == passive (verified), skip
            rec = observe(a, g, sd, game, [site])
            if rec['map']['homes'][rec['seat']] == site:
                pass  # parking at own home == passive with observer; still recorded as a control
            log = rec.pop('log')
            rec['site'] = site
            rec['arrive'] = next((L['r'] for L in log if L['own'][0][0] == site and L['own'][0][1] == -1), None)
            rec['sightings'] = [(L['r'], e['boat'], e['position'], e['destination'], e['eta']) for L in log for e in L['enemy']]
            rec['site_stock'] = [L['stocks'][site] for L in log]
            rec['seen_sites'] = sorted({v for L in log for v in L['vis']})
            rec.pop('targets', None); rec.pop('build', None)
            f.write(json.dumps(rec) + '\n'); f.flush()
