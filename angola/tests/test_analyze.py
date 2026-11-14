#!/usr/bin/env python3
"""Top-1 accuracy of analyze.py on the synthetic fixtures.

    python3 test_analyze.py        (regenerates fixtures first)

Exits non-zero unless every fixture's top-ranked source_id equals its answer byte for byte.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
ROOT = os.path.dirname(HERE)  # analyze.py lives one level up
sys.path[:0] = [HERE, ROOT]

import analyze  # noqa: E402
import make_fixtures  # noqa: E402


def interleaved(doc):
    """Same trace with runs interleaved round-robin (each run keeps its own order); None if events are nested per run."""
    doc = copy.deepcopy(doc)
    _, pat, lists = analyze.find_events(doc)
    lst = lists[0]
    run_key = analyze.detect_fields([[(p, v) for p, v, _ in analyze.walk(e)] for e in lst])["run"]
    if "[*]" in pat or len(lists) != 1 or not run_key or "." in run_key:
        return None
    queues = {}
    for e in lst:
        queues.setdefault(str(e.get(run_key)), []).append(e)
    order = []
    while any(queues.values()):
        order += [q.pop(0) for q in queues.values() if q]
    lst[:] = order
    return doc


def main():
    make_fixtures.main()
    with open(os.path.join(FIX, "answers.json"), encoding="utf-8") as f:
        answers = json.load(f)
    expected_runs = answers.pop("_incorrect_runs")
    forced = answers.pop("_incorrect_override")
    hits, problems = 0, []
    for name, want in sorted(answers.items()):
        doc, _ = analyze.load_file(os.path.join(FIX, name))  # utf-8-sig: 18_bom.json starts with a BOM
        res = analyze.analyze(doc, forced.get(name, ()))
        ranking = res["ranking"]
        got = ranking[0]["source_id"] if ranking else None
        ok = got == want
        hits += ok
        pos = next((i + 1 for i, c in enumerate(ranking) if c["source_id"] == want), None)
        margin = ranking[0]["score"] - ranking[1]["score"] if ok and len(ranking) > 1 else 0
        print(f"{'PASS' if ok else 'FAIL'} {name}: top={got!r} want={want!r} (answer ranked #{pos}, lead {margin:.1f}, "
              f"incorrect runs={res['verdict']['incorrect']})")
        if not ok:
            for c in ranking[:4]:
                print(f"      {c['score']:6.1f} {c['source_id']!r}: {'; '.join(c['reasons'][:6])}")
        if res["verdict"]["incorrect"] != expected_runs[name]:  # a right answer for the wrong reason is still a failure
            problems.append(f"{name}: incorrect runs {res['verdict']['incorrect']} != expected {expected_runs[name]}")
        variant = interleaved(doc)
        if variant is not None and analyze.analyze(variant, forced.get(name, ()))["ranking"][0]["source_id"] != want:
            problems.append(f"{name}: wrong top-1 once runs are interleaved")
    # The CLI path must run cleanly too: --json, a BOM file, --incorrect, and --answer writing the raw id plus a newline.
    with tempfile.TemporaryDirectory() as tmp:
        out, ans = os.path.join(tmp, "out.json"), os.path.join(tmp, "answer.txt")
        for name, extra in ((sorted(answers)[0], []), ("18_bom.json", []), ("16_override.json", ["--incorrect", "r2"]),
                            ("06_superseded_homoglyph.json", [])):
            if os.path.exists(ans):
                os.remove(ans)
            cli = subprocess.run([sys.executable, os.path.join(ROOT, "analyze.py"), os.path.join(FIX, name), "--json", out,
                                  "--answer", ans, *extra], capture_output=True, text=True)
            got = open(ans, "rb").read() if os.path.exists(ans) else None
            if not (cli.returncode == 0 and os.path.exists(out) and "ANSWER" in cli.stdout and got == (answers[name] + "\n").encode()
                    and got.hex(" ") in cli.stdout):
                problems.append(f"CLI {name} {extra}: answer file {got!r}, want {answers[name]!r}; {cli.stderr[-800:]}")
    for p in problems:
        print(f"FAIL {p}")
    print(f"top-1 accuracy: {hits}/{len(answers)} = {hits / len(answers):.0%}; "
          f"incorrect-run verdicts, interleaved variants and CLI: {'all PASS' if not problems else f'{len(problems)} FAIL'}")
    return 0 if hits == len(answers) and not problems else 1

if __name__ == "__main__":
    sys.exit(main())
