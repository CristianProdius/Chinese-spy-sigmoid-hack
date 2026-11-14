"""Show an agent's round-0 plan and what forcing one extra project in front would do.
python3 plan0.py AGENT.py GROUP SEED GAME [CONTRACT]
Prints the per-boat queues, simulated delivery rounds and plan value; with CONTRACT (a raw contract
index) also tries inserting a raw delivery for it at the front of each boat from each source."""
import sys, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena

spec = importlib.util.spec_from_file_location('agentmod', sys.argv[1])
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
group, seed, game = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
force = int(sys.argv[5]) if len(sys.argv) > 5 else None
NAMES = ['GO', 'TAKE', 'DROP', 'PROC', 'PICK', 'DELIV']


def show(q):
    return ' '.join(NAMES[st[0]] + ','.join(str(x) for x in st[1:]) for st in q)


with Arena() as a:
    o = a.reset(group, seed, game)['observation']
    mem = {}
    act = A.agent(o, mem)
    geo = mem['geo']
    s = A.sync_state(o, geo, mem)
    print('seat', o['seat'], 'home', geo.home, 'roles', o['map']['roles'])
    for i, c in enumerate(o['map']['contracts']):
        print(' c%d' % i, c, 'lbprof', mem['lbprof'][i])
    print('first action', act)
    qs = mem['qs']
    pl = A.Planner(geo, geo.home, A.make_win(mem, 0))
    d, _, f = A.simulate(s, geo, qs, [0] * s.nb)
    print('plan value %.2f deliveries %s finish %s' % (pl.value(d), sorted(d.items(), key=lambda x: x[1]), f))
    for b, q in enumerate(qs):
        print(' boat', b, show(q))
    if force is not None:
        con = o['map']['contracts'][force]
        g, dst = con['good'], con['destination']
        srcs = [geo.home] + (geo.tsites if g == 0 else geo.fsites)
        for b in range(s.nb):
            for src in srcs:
                nq = [q[:] for q in qs]
                nq[b] = [(A.GO, src), (A.TAKE, g, 2), (A.GO, dst), (A.DELIV, force)] + nq[b]
                d2, _, f2 = A.simulate(s, geo, nq, [0] * s.nb)
                print('  force c%d boat %d src %d: value %.2f deliveries %s' % (
                    force, b, src, pl.value(d2), sorted(d2.items(), key=lambda x: x[1])))
