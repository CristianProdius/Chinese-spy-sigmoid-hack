"""One game in-process with diagnostics: pypy3 dbg.py AGENT.py GROUP SEED STYLE [verbose]"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import fasteval as F
P = F.P
path = sys.argv[1]; group = int(sys.argv[2]); seed = int(sys.argv[3]); style = int(sys.argv[4]); verbose = len(sys.argv) > 5
A = F.load_agent(os.path.abspath(path))
A.DEBUG = True
topo, seat = group // 2, group % 2
md = P.generate_map(topo, seed); mp = P.Map(md); eng = P.Engine(mp); prof = P.Professor(style, 1 - seat)
memory = {}
tot = 0.0
while eng.round < 80:
    ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
    t0 = time.perf_counter()
    act = A.agent(ob, memory)
    dt = time.perf_counter() - t0; tot += dt
    b = memory['brain']
    mine = P.order_from_json(act)
    po = prof.choose(eng.view(1 - seat))
    orders = [None, None]; orders[seat] = mine; orders[1 - seat] = po
    r = eng.round
    ok = eng.step(orders)
    if verbose or dt > 0.15 or mine[0] == 'deliver' or po[0] == 'deliver':
        print('r%2d %-26s%s| prof %-24s| %d-%d | dt %.3f hyps %s seq %s vals %s roll %d beam %d miss %d' % (
            r, ' '.join(str(x) for x in mine if x != -1), '' if ok[seat] else 'FAIL ', ' '.join(str(x) for x in po if x != -1),
            eng.sides[seat].score, eng.sides[1 - seat].score, dt, [h.sid for h in b.hyps], b.plan.seq if b.plan else None,
            dict(b.vals), b.nroll, b.nbeam, 0))
print('TM', {k: round(v, 2) for k, v in memory['brain'].tm.items()}, 'nroll', memory['brain'].nroll, 'nbeam', memory['brain'].nbeam)
print('FINAL', eng.sides[seat].score, eng.sides[1 - seat].score, 'time %.2f' % tot, 'used %.2f' % memory['brain'].used, 'blind', memory['brain'].blind)
