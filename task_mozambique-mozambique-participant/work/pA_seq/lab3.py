import sys, json
import core as P
import brain as B
import tsched as S
group = int(sys.argv[1]); seed = int(sys.argv[2]); seq = json.loads(sys.argv[3]); Bv = float(sys.argv[4])
topo, seat = group // 2, group % 2
mp = P.Map(P.generate_map(topo, seed))
print('roles', mp.roles, 'homes', mp.homes, 'seat', seat, 'home', mp.homes[seat])
for i in range(10): print(i, 'role', mp.roles[i], 'neigh', [(j, mp.routes[i][j]) for j in mp.neigh[i]])
print('contracts', list(enumerate(zip(mp.c_good, mp.c_dest, mp.c_deadline))))
eng = P.Engine(mp)
sc, kept = S.decode_seq(mp, eng.sides[seat], eng.stocks, eng.claims, 0, seq, Bv)
print('kept', kept, 'deliv', sc.deliv)
tt = sc.timetable()
for t in range(0, 80):
    o = tt.get(t)
    if o: print(t, ' '.join(str(x) for x in o if x != -1))
