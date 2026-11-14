"""Play a game with the agent (style known) up to round R, then inspect our planner there.
   pypy3 dbg_state.py AGENT GROUP SEED STYLE R"""
import importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab')); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
from fasteval import obs_dict
path, group, seed, style, R = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
spec = importlib.util.spec_from_file_location('ag', path); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
A.CHEAT = style
topo, seat = group // 2, group % 2
md = P.generate_map(topo, seed); mp = P.Map(md); eng = P.Engine(mp); prof = P.Professor(style, 1 - seat)
memory = {}
while eng.round < R:
    ob = json.loads(json.dumps(obs_dict(eng, seat, md)))
    act = A.agent(ob, memory)
    po = prof.choose(eng.view(1 - seat))
    o = [None, None]; o[seat] = P.order_from_json(act); o[1 - seat] = po
    eng.step(o)
g = memory['g']; h = g.hyps[0]
side = h.eng.sides[seat]
print('round', h.eng.round, 'claims', h.eng.claims, 'stocks', h.eng.stocks, 'roles', mp.roles)
print('boats', side.boats, 'ws', [i for i in range(10) if side.ws[i]], 'jobs', side.jobs)
print('wh', [(i, side.wh[3*i:3*i+3]) for i in range(10) if any(side.wh[3*i:3*i+3])])
pl = A.Planner((1.8, 0.85, 0), seat)
pl.mp = mp; pl.est = h.eng.stocks[:]; pl.og = {}
view = h.eng.view(seat); view.mp = mp
cur = pl.make_sim(view); pl.cur = cur
for c in range(8):
    if h.eng.claims[c] != -1: continue
    r = pl.prepare(cur, c)
    print('contract', c, 'good', mp.c_good[c], 'dest', mp.c_dest[c], 'deadline', mp.c_deadline[c], '->', None if r is None else (r.round, r.actions()))
    if r is not None:
        for v in (0, 1):
            res = pl.interleave(r.actions(), v)
            print('   interleave', v, None if res is None else res.round)
