import json, random, sys
from collections import Counter, defaultdict
from eng import Arena
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = random.Random(7)
out = []
with Arena() as a:
    for g in range(8):
        for i in range(N):
            seed = rng.randrange(2**32)
            s = a.reset(g, seed, 0)
            o = s['observation']
            out.append(dict(group=g, seed=seed, seat=o['seat'], map=o['map'], own=o['own'], stocks=o['stocks'], visible=o['visible']))
json.dump(out, open('maps_survey.json', 'w'))
print(len(out))
