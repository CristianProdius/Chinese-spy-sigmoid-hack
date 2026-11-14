"""Play one game in-process with debug on and print a trace.
    pypy3 trace.py AGENT.py GROUP SEED STYLE [-v]
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F

def main():
    path, group, seed, style = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    verbose = '-v' in sys.argv
    mod = F.load_agent(os.path.abspath(path))
    mod.PARAMS['debug'] = True
    if '--warm' in sys.argv:
        for wst in (4, 3):
            F.play(mod, group, seed, wst)
    topo, seat = group // 2, group % 2
    md = P.generate_map(topo, seed); mp = P.Map(md)
    eng = P.Engine(mp); prof = P.Professor(style, 1 - seat)
    memory = {}
    print('roles', mp.roles, 'homes', mp.homes, 'seat', seat)
    for c in range(8):
        print(' contract', c, 'good', mp.c_good[c], 'dest', mp.c_dest[c], 'dl', mp.c_deadline[c])
    print('routes', [(i, j, mp.routes[i][j]) for i in range(10) for j in range(i) if mp.routes[i][j]])
    cpu = 0.0
    while eng.round < 80:
        ob = json.loads(json.dumps(F.obs_dict(eng, seat, md)))
        t0 = time.process_time()
        act = mod.agent(ob, memory)
        dt = time.process_time() - t0
        cpu += dt
        assert act in ob['legal_actions'], act
        po = prof.choose(eng.view(1 - seat))
        orders = [None, None]; orders[seat] = P.order_from_json(act); orders[1 - seat] = po
        G = memory['G']
        if verbose:
            pl = G.plan
            lg = G.log[-1] if G.log and G.log[-1][0] == eng.round else None
            print('r%2d us %2d them %2d hyps %s | %-44s | prof %-34s | %.0fms q=%s %s' % (
                eng.round, eng.sides[seat].score, eng.sides[1 - seat].score, ''.join(str(h.style) for h in G.hyps),
                json.dumps(act)[:44], str(po)[:34], dt * 1000, [len(x) for x in pl.q],
                ' '.join('-' if x is None else '%.1f' % x for x in lg[1:]) if lg else ''))
        ok = eng.step(orders)
        if verbose and not ok[seat]:
            print('     OUR ORDER FAILED')
    G = memory['G']
    print('final us %d them %d cpu %.2f nrep %d stats %s claims %s' % (
        eng.sides[seat].score, eng.sides[1 - seat].score, cpu, G.nrep, G.stats, eng.claims))
    if verbose:
        print('genes', G.plan.genes)

main()
