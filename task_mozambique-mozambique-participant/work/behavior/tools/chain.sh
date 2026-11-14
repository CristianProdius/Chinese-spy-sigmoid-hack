#!/bin/bash
# chain.sh W PASSIVE_PID : after passive worker W exits, run park sweep then rush for the same worker slot
W=$1; P=$2
cd "$(dirname "$0")/.."
while kill -0 $P 2>/dev/null; do sleep 5; done
nice -n 10 python3 tools/park_sweep.py data/park_$W.jsonl $W 6 3 > data/park_$W.log 2>&1
nice -n 10 python3 tools/rush.py data/rush_$W.jsonl $W 6 3 > data/rush_$W.log 2>&1
echo "slot $W done"
