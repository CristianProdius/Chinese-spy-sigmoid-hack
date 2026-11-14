import json
from collections import Counter, defaultdict
from analyze_maps2 import sp
d = json.load(open('maps_survey.json'))
res=Counter(); order=Counter()
for m in d:
    mp=m['map']; D=sp(mp['routes']); H=mp['homes']
    best=max(D[i][j] for i in range(10) for j in range(10))
    cands=[(i,j) for i in range(10) for j in range(i+1,10) if D[i][j]==best]
    a,b=sorted(H)
    res[(mp['topology'], len(cands)>1, cands.index((a,b)) if len(cands)>1 else -1, len(cands))]+=1
    order[(mp['topology'], H[0]<H[1])]+=1
for k,v in sorted(res.items()): print(k,v)
print(order)
