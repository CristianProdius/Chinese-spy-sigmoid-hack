import sys, json
import core as P
import old_brain as B
group = int(sys.argv[1]); seed = int(sys.argv[2]); style = int(sys.argv[3]); seq = json.loads(sys.argv[4]); Bv = float(sys.argv[5]); var = int(sys.argv[6]) if len(sys.argv) > 6 else 0
topo, seat = group // 2, group % 2
mp = P.Map(P.generate_map(topo, seed)); ps = 1 - seat
print('roles', mp.roles, 'homes', mp.homes, 'seat', seat)
for i in range(10): print(i, 'role', mp.roles[i], 'neigh', [(j, mp.routes[i][j]) for j in mp.neigh[i]])
print('contracts', list(enumerate(zip(mp.c_good, mp.c_dest, mp.c_deadline))))
planner = B.Planner(mp, seat)
eng = P.Engine(mp); prof = B.CProf(style, ps)
q, kept = planner.decode(eng.sides[seat], eng.stocks, eng.claims, 0, seq, Bv)
plan = B.Plan(kept, Bv, var, q)
# verbose rollout
orders = [None, None]
while eng.round < 80:
    o, b = B.pick_order(mp, eng, seat, plan)
    if o is None:
        print('REPAIR needed at', eng.round); break
    po = prof.choose_e(eng)
    orders[seat] = o; orders[ps] = po
    r = eng.round
    ok = eng.step(orders)
    if b >= 0 and ok[seat]: plan.qi[b] += 1
    def f(o): return ' '.join(str(x) for x in o if x != -1)
    print('r%2d us %-22s%s | prof %-22s%s | score %d-%d' % (r, f(o), '' if ok[seat] else ' FAIL', f(po), '' if ok[ps] else ' FAIL', eng.sides[seat].score, eng.sides[ps].score))
    if plan.empty() and eng.round > 45: break
