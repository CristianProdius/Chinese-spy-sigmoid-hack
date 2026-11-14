#!/bin/bash
# sequential 48-map evals of the given agent files; prints the headline per agent
cd "$(dirname "$0")/.."
for f in "$@"; do
  n=$(basename "$f" .py)
  python3 eval.py "$f" --maps 48 --jobs 6 --quiet --out results/48_$n.json > results/48_$n.txt 2>&1
  echo "== $n"; grep -E "MATCH|all games|^game|^seat [01]|cpu" results/48_$n.txt
done
