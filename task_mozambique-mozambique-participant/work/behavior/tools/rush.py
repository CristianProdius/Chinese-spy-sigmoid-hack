"""R1 rush: for each contract c, we go for c alone as fast as a simple plan allows.
raw: load 2 of the good at home, sail, deliver.
manufactured: boat A loads 2T+1F, boat B loads 2T+1F, both go to manufacturing site m
(best m by dist(home,m)+dist(m,dest)), A unloads + builds workshop, B unloads + crafts,
B loads the product and delivers.
usage: python3 rush.py OUT.jsonl WORKER NWORKERS [MAPS_PER_GROUP]"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from passive import maps, ROOT
from arena import Arena
from observe import dijkstra
from runner import run_plan

def rush_plan(m, seat, c):
    home = m['homes'][seat]
    ct = m['contracts'][c]
    d = ct['destination']
    if ct['good'] != 2:
        return [[('load', ct['good'], 2), ('goto', d), ('deliver', c)]], None
    dh, _ = dijkstra(m['routes'], home)
    best = None
    for s, r in enumerate(m['roles']):
        if r != 2: continue
        ds, _ = dijkstra(m['routes'], s)
        cost = dh[s] + ds[d]
        if best is None or cost < best[0]: best = (cost, s)
    ms = best[1]
    A = [('load', 0, 2), ('load', 1, 1), ('goto', ms), ('unload', 0, 2), ('unload', 1, 1), ('build_workshop',)]
    B = [('load', 0, 2), ('load', 1, 1), ('goto', ms), ('unload', 0, 2), ('unload', 1, 1), ('craft',),
         ('await_goods', ms, 2, 1), ('load', 2, 1), ('goto', d), ('deliver', c)]
    return [A, B], ms

if __name__ == '__main__':
    out, w, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    ms_ = maps(); sel = []
    for g in range(8):
        sel += [x for x in ms_ if x[0] == g and x[2] == 'rand'][:k]
    jobs = [(g, sd, game, c) for (g, sd, src) in sel for game in range(5) for c in range(8)][w::n]
    done = set()
    if os.path.exists(out):
        for line in open(out):
            d = json.loads(line); done.add((d['group'], d['seed'], d['game'], d['contract']))
    with Arena() as a, open(out, 'a') as f:
        for g, sd, game, c in jobs:
            if (g, sd, game, c) in done: continue
            s = a.reset(g, sd, game); o = s['observation']
            plan, msite = rush_plan(o['map'], o['seat'], c)
            rec = run_plan(a, g, sd, game, plan)
            log = rec.pop('log')
            rec['contract'] = c; rec['msite'] = msite
            rec['sightings'] = [(L['r'], e['boat'], e['position'], e['destination'], e['eta']) for L in log for e in L['enemy']]
            rec['acts'] = [(L['r'], L['act']) for L in log if L['act']['op'] != 'wait']
            f.write(json.dumps(rec) + '\n'); f.flush()
