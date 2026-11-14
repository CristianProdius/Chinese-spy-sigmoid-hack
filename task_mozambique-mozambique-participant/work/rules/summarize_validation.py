"""Sum STATS/MISMATCHES lines of validate_sim.py logs: python3 summarize_validation.py LOG..."""
import json, sys
from collections import Counter
S = Counter(); M = Counter(); n = 0
for fn in sys.argv[1:]:
    for line in open(fn):
        if line.startswith('STATS '):
            S.update(json.loads(line[6:])); n += 1
        elif line.startswith('MISMATCHES '):
            M.update(json.loads(line[11:]))
print('logs', n)
print('STATS', json.dumps(dict(sorted(S.items()))))
print('MISMATCHES', json.dumps(dict(M)))
