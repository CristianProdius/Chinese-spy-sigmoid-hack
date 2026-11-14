#!/usr/bin/env python3
"""Top-1 of analyze.py on redteam1/case*.json vs redteam1/answers.json.

    python3 eval_redteam.py [module]
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.join(HERE, "redteam1")
sys.path.insert(0, os.path.dirname(HERE))  # analyze.py lives one level up
mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "analyze")

with open(os.path.join(RED, "answers.json"), encoding="utf-8") as f:
    answers = json.load(f)
hits = 0
for case in sorted(answers):
    want = answers[case]["answer"]
    try:
        with open(os.path.join(RED, case + ".json"), encoding="utf-8") as f:
            res = mod.analyze(json.load(f))
    except Exception as ex:  # noqa: BLE001
        print(f"CRASH {case}: {ex!r}")
        continue
    rk = res["ranking"]
    ok = rk[0]["source_id"] == want
    hits += ok
    pos = next((i + 1 for i, c in enumerate(rk) if c["source_id"] == want), None)
    lead = rk[0]["score"] - rk[1]["score"] if len(rk) > 1 else 0
    print(f"{'PASS' if ok else 'FAIL'} {case}: top={rk[0]['repr']} want #{pos}, lead {lead:.1f}, incorrect runs {res['verdict']['incorrect']}")
    if not ok or lead < 10:
        for c in rk[:4]:
            print(f"      {c['score']:6.1f} {c['repr']}: {'; '.join(c['reasons'][:5])}")
print(f"red-team top-1: {hits}/{len(answers)}")
