"""Dedup raw teacher prompts and drop near-copies of the public prompts and calls.

  python prep_prompts.py data/prompts_raw.jsonl data/prompts.jsonl
"""
import json
import random
import sys

from build_sft import near_public, norm

rows, seen = [], set()
for l in open(sys.argv[1]):
    r = json.loads(l)
    q = " ".join(r["prompt"].split())
    k = norm(q)
    n = len(q.split())
    if not k or k in seen or n < 3 or n > 30 or "\n" in r["prompt"]:
        continue
    seen.add(k)
    if near_public(q):
        continue
    rows.append({**r, "prompt": q})
random.Random(0).shuffle(rows)
with open(sys.argv[2], "w") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(rows), "prompts")
