import json, itertools
from collections import Counter, defaultdict
from analyze_maps2 import sp
d = json.load(open('maps_survey.json'))
by_topo = defaultdict(list)
for m in d: by_topo[m['map']['topology']].append(m)
for t in sorted(by_topo):
    ms = by_topo[t]
    print('=== topo', t)
    rolepos = defaultdict(Counter)
    eqnear = Counter(); sumeq=Counter(); diffs=Counter()
    for m in ms:
        mp=m['map']; R=mp['routes']; H=mp['homes']; roles=mp['roles']
        for i,r in enumerate(roles): rolepos[i][r]+=1
        D=sp(R)
        near=[tuple(min(D[h][i] for i in range(10) if roles[i]==r) for r in (0,1,2)) for h in H]
        eqnear[near[0]==near[1]]+=1
        tot=[sum(sorted(D[h][i] for i in range(10) if roles[i]==r)[0] for r in (0,1,2)) for h in H]
        sumall=[sum(D[h][i] for i in range(10)) for h in H]
        diffs[(sumall[0]-sumall[1])]+=1
        sumeq[tot[0]-tot[1]]+=1
    print(' nearest equal', eqnear, ' sum-nearest diff', sorted(sumeq.items()))
    print(' sum-all diff', sorted(diffs.items()))
    for i in range(10): print('  site', i, dict(sorted(rolepos[i].items())))
