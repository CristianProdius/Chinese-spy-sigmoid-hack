import json, itertools
from collections import Counter, defaultdict
d = json.load(open('maps_survey.json'))
def sp(routes, weighted=True):
    INF=10**9; D=[[INF]*10 for _ in range(10)]
    for i in range(10):
        D[i][i]=0
        for j in range(10):
            if routes[i][j]: D[i][j]=routes[i][j] if weighted else 1
    for k in range(10):
        for i in range(10):
            for j in range(10):
                if D[i][k]+D[k][j]<D[i][j]: D[i][j]=D[i][k]+D[k][j]
    return D
by_topo = defaultdict(list)
for m in d: by_topo[m['map']['topology']].append(m)
for t in sorted(by_topo):
    ms = by_topo[t]
    print('=== topo', t)
    hop = Counter(); wdist=Counter(); cdest=Counter(); cdestgood=Counter(); hpair=Counter()
    ownhome = Counter()
    for m in ms:
        mp=m['map']; R=mp['routes']; H=mp['homes']
        Dh=sp(R,False); Dw=sp(R)
        hop[Dh[H[0]][H[1]]]+=1; wdist[Dw[H[0]][H[1]]]+=1
        for c in mp['contracts']:
            cdest[mp['roles'][c['destination']]]+=1
            cdestgood[(c['good'], mp['roles'][c['destination']])]+=1
        ownhome[(m['seat'], m['own']['home']==H[m['seat']])]+=1
        hpair[tuple(sorted(H))]+=1
    print(' hop dist homes', sorted(hop.items()), ' weighted', sorted(wdist.items()))
    print(' contract dest roles', cdest, cdestgood)
    print(' own home is homes[seat]', ownhome)
    print(' unordered home pairs', hpair.most_common(20))
