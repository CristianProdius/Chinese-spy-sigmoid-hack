"""Play one game in-process and print a round-by-round trace.
   pypy3 trace.py AGENT.py GROUP SEED STYLE [--quiet]"""
import importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
from fasteval import obs_dict

path, group, seed, style = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
quiet = '--quiet' in sys.argv
spec = importlib.util.spec_from_file_location('ag', path); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
A.DEBUG = not quiet
topo, seat = group // 2, group % 2
md = P.generate_map(topo, seed); mp = P.Map(md); eng = P.Engine(mp); prof = P.Professor(style, 1 - seat)
print('homes', mp.homes, 'roles', mp.roles)
print('contracts', [(c, mp.c_good[c], mp.c_dest[c], mp.c_deadline[c]) for c in range(8)])
memory = {}; cpu = 0
while eng.round < 80:
    ob = json.loads(json.dumps(obs_dict(eng, seat, md)))
    t0 = time.process_time(); act = A.agent(ob, memory); dt = time.process_time() - t0; cpu += dt
    po = prof.choose(eng.view(1 - seat))
    orders = [None, None]; orders[seat] = P.order_from_json(act); orders[1 - seat] = po
    before = list(eng.claims); eng.step(orders)
    g = memory.get('g')
    if not quiet:
        extra = ''
        if g is not None:
            extra = 'hyps=%s plan_c=%s' % ([h.style for h in g.hyps], g.plan_c)
        newc = [c for c in range(8) if before[c] == -1 and eng.claims[c] != -1]
        print('r%2d %5.3fs us %-45s prof %-40s %s %s score %d-%d' % (eng.round - 1, dt, act, P.order_to_json(po), extra,
              ['%s%d' % ('U' if eng.claims[c] == seat else 'P', c) for c in newc], eng.sides[seat].score, eng.sides[1-seat].score))
print('final', eng.sides[seat].score, eng.sides[1 - seat].score, 'cpu %.2f' % cpu)
if g is not None and hasattr(g, 'stats'): print(g.stats)
