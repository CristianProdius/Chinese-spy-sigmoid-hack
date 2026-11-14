"""How fast can a simple plan deliver a first manufactured contract? Compares plan variants with
the analytic bound 11 + d(home,m) + d(m,dest). usage: python3 mfg_check.py OUT.jsonl WORKER NWORKERS"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from passive import maps, ROOT
from arena import Arena
from observe import dijkstra
from runner import run_plan
from rush import rush_plan

def plan_v3(m, seat, c):
    home = m['homes'][seat]; d = m['contracts'][c]['destination']
    dh, _ = dijkstra(m['routes'], home)
    ms = min((s for s, r in enumerate(m['roles']) if r == 2), key=lambda s: dh[s] + dijkstra(m['routes'], s)[0][d])
    A = [('load', 0, 3), ('goto', ms), ('unload', 0, 3)]
    B = [('load', 0, 1), ('load', 1, 2), ('goto', ms), ('unload', 0, 1), ('unload', 1, 2), ('build_workshop',), ('craft',),
         ('await_goods', ms, 2, 1), ('load', 2, 1), ('goto', d), ('deliver', c)]
    return [A, B], ms

if __name__ == '__main__':
    out, w, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ms_ = maps(); sel = [x for g in range(8) for x in [m for m in ms_ if m[0] == g and m[2] == 'rand'][:2]]
    jobs = [(g, sd, c, v) for (g, sd, _) in sel for c in range(4, 8) for v in ('v1', 'v2', 'v3')][w::n]
    with Arena() as a, open(out, 'a') as f:
        for g, sd, c, v in jobs:
            o = a.reset(g, sd, 0)['observation']
            if v == 'v3': plan, msite = plan_v3(o['map'], o['seat'], c)
            else: plan, msite = rush_plan(o['map'], o['seat'], c)
            rec = run_plan(a, g, sd, 0, plan, record=False, sail_first=(v != 'v1'))
            ours = next((e[0] for e in rec['events'] if e[1] == 'deliver'), None)
            f.write(json.dumps(dict(group=g, seed=sd, contract=c, variant=v, msite=msite, ours=ours, events=rec['events'])) + '\n'); f.flush()
