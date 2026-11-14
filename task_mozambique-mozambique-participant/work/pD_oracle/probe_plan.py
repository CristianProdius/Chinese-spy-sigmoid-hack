"""Dump our planner's nodes at round 0 for a (group, seed, style), with the predicted opponent
claims as deadlines.   pypy3 probe_plan.py AGENT GROUP SEED STYLE 'B,A,W' [lam] [eff 0/1]"""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab')); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
from fasteval import obs_dict
path, group, seed, style = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
B, Aa, W = [float(x) for x in sys.argv[5].split(',')]
lam = float(sys.argv[6]) if len(sys.argv) > 6 else 0.6
use_eff = int(sys.argv[7]) if len(sys.argv) > 7 else 1
spec = importlib.util.spec_from_file_location('ag', path); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
A.CHEAT = style
topo, seat = group // 2, group % 2
md = P.generate_map(topo, seed)
eng = P.Engine(P.Map(md))
ob = json.loads(json.dumps(obs_dict(eng, seat, md)))
g = A.Game(ob)
mp = g.mp
h = g.hyps[0]
base = g.predict((), 0)
pr = base[style]
print('opp claims (we wait):', pr.opp_claim, 'opp score', pr.them)
dl = list(mp.c_deadline)
for c in range(8):
    r = pr.opp_claim[c]
    if r >= 0:
        e = r + 1 if (r & 1) == seat else r
        dl[c] = min(dl[c], e)
print('eff', dl)
pts = [mp.c_points[c] * (1 + lam) if pr.opp_claim[c] >= 0 else mp.c_points[c] for c in range(8)]
pl = A.Planner((B, Aa, int(W)), seat, depth=4, width=8)
pl.mp = A.eff_map(mp, dl if use_eff else list(mp.c_deadline), pts)
pl.og = pr.og
pl.est = h.eng.stocks[:]
view = h.eng.view(seat); view.mp = pl.mp
nodes = []
pl.replan(view, nodes)
nodes.sort(key=lambda nd: (-nd[2], nd[0].round))
seen = set()
for nd in nodes[:40]:
    acts = nd[0].actions()
    dr = [(i, o[5]) for i, o in enumerate(acts) if o[0] == 'deliver']
    key = tuple(nd[1])
    if key in seen: continue
    seen.add(key)
    r = A.rollout(h.eng, h.prof, acts, seat)
    print('%-14s score %.3f end %d delivers %s -> rollout %d-%d' % (nd[1], nd[2], nd[0].round, dr, r.us, r.them))
