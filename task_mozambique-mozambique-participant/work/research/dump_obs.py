import json, sys
sys.path.insert(0, sys.argv[1])
from arena import Arena
with Arena() as a:
    s = a.reset(0, 767302775, 0)
    for _ in range(10):
        s = a.step({"op": "wait"})
    json.dump(s['observation'], open('sample_obs.json', 'w'))
print(len(json.dumps(s['observation'])), 'bytes')
