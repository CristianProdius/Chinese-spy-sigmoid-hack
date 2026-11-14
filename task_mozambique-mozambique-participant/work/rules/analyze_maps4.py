import json, itertools
from collections import Counter, defaultdict
from analyze_maps2 import sp
d = json.load(open('maps_survey.json'))
by_topo = defaultdict(list)
for m in d: by_topo[m['map']['topology']].append(m)
for t in sorted(by_topo):
    ms = by_topo[t]
    rank=Counter(); hoprank=Counter()
    for m in ms:
        mp=m['map']; R=mp['routes']; H=mp['homes']
        D=sp(R); Dh=sp(R,False)
        pairs=sorted(((D[i][j],i,j) for i in range(10) for j in range(i+1,10)), reverse=True)
        a,b=sorted(H)
        v=D[a][b]
        rank[(sum(1 for p in pairs if p[0]>v), max(p[0] for p in pairs)-v)]+=1
        hv=Dh[a][b]; hoprank[max(Dh[i][j] for i in range(10) for j in range(10))-hv]+=1
    print(t, 'weighted rank', rank.most_common(8), 'hop gap', hoprank)
