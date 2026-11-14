import json
from collections import Counter, defaultdict
d = json.load(open('maps_survey.json'))
def edges(routes):
    return [(i,j,routes[i][j]) for i in range(10) for j in range(i+1,10) if routes[i][j]]
by_topo = defaultdict(list)
for m in d:
    by_topo[m['map']['topology']].append(m)
for t in sorted(by_topo):
    ms = by_topo[t]
    print('=== topology', t, 'n', len(ms), 'groups', Counter(m['group'] for m in ms), 'seats', Counter((m['group'], m['seat']) for m in ms))
    ec = Counter(len(edges(m['map']['routes'])) for m in ms)
    print(' edge counts', ec)
    deg = Counter(tuple(sorted(sum(1 for x in m['map']['routes'][i] if x) for i in range(10))) for m in ms)
    print(' degree seqs', deg.most_common(8))
    lens = Counter(l for m in ms for _,_,l in edges(m['map']['routes']))
    print(' route lengths', lens)
    roles = Counter(tuple(sorted(Counter(m['map']['roles']).items())) for m in ms)
    print(' role counts', roles.most_common(10))
    homes = Counter(tuple(m['map']['homes']) for m in ms)
    print(' homes', homes.most_common(10))
    sym = Counter(all(m['map']['routes'][i][j]==m['map']['routes'][j][i] for i in range(10) for j in range(10)) for m in ms)
    print(' symmetric', sym)
    # contract patterns
    cp = Counter(tuple((c['good'],c['quantity'],c['points'],c['deadline']) for c in m['map']['contracts']) for m in ms)
    print(' contract patterns', cp.most_common(6), 'distinct', len(cp))
    # edge sets
    es = Counter(tuple((i,j) for i,j,_ in edges(m['map']['routes'])) for m in ms)
    print(' distinct edge sets', len(es), es.most_common(3))
    print(' own start wh', Counter(str(m['own']['warehouses'][m['own']['home']]) for m in ms), 'boats', Counter(len(m['own']['boats']) for m in ms))
    print(' home roles', Counter(tuple(m['map']['roles'][h] for h in m['map']['homes']) for m in ms))
