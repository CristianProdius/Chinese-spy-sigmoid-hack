"""Self-check for main.py.

1. Runs main.py on the training CSV and compares to the expected pairs.
2. Runs it on a shuffled copy (row order must not matter).
3. Injects collisions (a second person sharing the same address numbers, in the
   same table as an existing record) and checks the true pairs survive and the
   decoy pairs are not added.

Usage: python tools/check.py data/train-input.csv data/train-output-2.json
"""
import csv
import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "..", "main.py")


def run(csv_path):
    out = csv_path + ".out.json"
    subprocess.run([sys.executable, "-I", MAIN, csv_path, out], check=True)
    with open(out) as fh:
        return {frozenset(p) for p in json.load(fh)["matches"]}


def score(got, want, label):
    missing, extra = want - got, got - want
    ok = not missing and not extra
    print(f"{'PASS' if ok else 'FAIL'} {label}: {len(got)} pairs, {len(missing)} missing, {len(extra)} extra")
    return ok


def main():
    src, truth_path = sys.argv[1], sys.argv[2]
    with open(truth_path) as fh:
        want = {frozenset(p) for p in json.load(fh)["matches"]}
    with open(src, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fields, rows = reader.fieldnames, list(reader)
    ok = score(run(src), want, "train")

    tmp = tempfile.mkdtemp()
    shuffled = rows[:]
    random.Random(7).shuffle(shuffled)
    path = os.path.join(tmp, "shuffled.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(shuffled)
    ok &= score(run(path), want, "shuffled")

    # Decoys: a different person (unrelated name) at an existing address, same
    # table as the record they copy the address from.
    rnd = random.Random(11)
    decoys = []
    for i, r in enumerate(rnd.sample(rows, 50)):
        decoys.append({
            "source_table": r["source_table"],
            "record_id": f"{r['source_table']}9{i:03d}",
            "first_name": "Zacarías",
            "last_name": "Quintero",
            "address": r["address"],
        })
    path = os.path.join(tmp, "decoys.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fields)
        w.writeheader()
        w.writerows(rows + decoys)
    ok &= score(run(path), want, "same-table decoys")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
