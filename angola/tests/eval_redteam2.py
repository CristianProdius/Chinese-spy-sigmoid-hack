#!/usr/bin/env python3
"""Top-1 of analyze.py on redteam2/case*.json vs redteam2/answers.json.

    python3 eval_redteam2.py [module]

answers.json here is a list of {"case": "caseN.json", "id": ..., "explanation": ...}. Exits non-zero unless every
case's top-ranked source_id equals its answer byte for byte. The cases are OTLP spans (case4) and a nested trace
tree (case5) as well as flat event lists, so this also checks that every export shape loads.
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RED = os.path.join(HERE, "redteam2")
sys.path.insert(0, os.path.dirname(HERE))  # analyze.py lives one level up


def main():
    mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "analyze")
    with open(os.path.join(RED, "answers.json"), encoding="utf-8") as f:
        answers = json.load(f)
    hits = 0
    for a in sorted(answers, key=lambda a: a["case"]):
        case, want = a["case"], a["id"]
        try:
            with open(os.path.join(RED, case), encoding="utf-8-sig") as f:
                res = mod.analyze(json.load(f))
        except BaseException as ex:  # noqa: BLE001  (SystemExit too: "no list of event objects found")
            print(f"CRASH {case}: {ex!r}")
            continue
        rk = res["ranking"]
        ok = bool(rk) and rk[0]["source_id"] == want
        hits += ok
        pos = next((i + 1 for i, c in enumerate(rk) if c["source_id"] == want), None)
        lead = rk[0]["score"] - rk[1]["score"] if len(rk) > 1 else 0
        print(f"{'PASS' if ok else 'FAIL'} {case}: top={rk[0]['repr'] if rk else None} want #{pos}, lead {lead:.1f}, "
              f"incorrect runs {res['verdict']['incorrect']}")
        if not ok or lead < 10:
            for c in rk[:4]:
                print(f"      {c['score']:6.1f} {c['repr']}: {'; '.join(c['reasons'][:5])}")
    print(f"red-team 2 top-1: {hits}/{len(answers)}")
    return 0 if hits == len(answers) else 1


if __name__ == "__main__":
    sys.exit(main())
