"""Practice-only check: does the clone pick exactly the champion's moves?

python validate_clone.py trace.jsonl   (trace from samoa-gdb via CHAMP_TRACE)
"""
import json
import sys
from collections import Counter

import champ

recs = [json.loads(l) for l in open(sys.argv[1])]
n = ok = 0
bad = Counter()
first_bad = []
i = 0
while i < len(recs) - 1:
    st, ac = recs[i], recs[i + 1]
    if st["t"] != "state" or ac["t"] != "action":
        i += 1
        continue
    mem = (list(st["mem_owner"]), list(st["mem_w"]), list(st["mem_c"]))
    a, info = champ.decide(st["blocked"], st["w"], st["c"], st["owner"], st["energy"], st["score"],
                           st["remaining"], st["seat"], st["profile"], mem)
    n += 1
    if a == ac["a"]:
        ok += 1
    else:
        bad[st["profile"]] += 1
        if len(first_bad) < 8:
            first_bad.append((i, st["remaining"], st["profile"], ac["a"], a, info))
    i += 2
print(f"{ok}/{n} exact ({ok / max(1, n):.4f}); mismatches by profile {dict(bad)}")
for fb in first_bad:
    print("rec", fb[0], "remaining", fb[1], "profile", fb[2], "engine", fb[3], "clone", fb[4], "info", fb[5])
