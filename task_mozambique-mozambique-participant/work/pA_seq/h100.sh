#!/usr/bin/env bash
# h100.sh AGENT.py TAG [fasteval args]: run fasteval on H100 for a single built agent file, result in runs/TAG.txt
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
AGENT="$(realpath "$1")"; TAG="$2"; shift 2
R="maputo/runs/pA_$TAG-$$"
ssh -o BatchMode=yes h100 "mkdir -p ~/$R/lab ~/$R/binary ~/$R/agent"
rsync -q "$HERE/../lab/fasteval.py" "h100:$R/lab/"
rsync -q "$HERE/../binary/professor.py" "h100:$R/binary/"
rsync -q "$AGENT" "h100:$R/agent/agent.py"
ssh -o BatchMode=yes h100 "cd ~/$R/lab && MAPUTO_WALL=0 nice -n 5 ~/maputo/opt/pypy3.10-v7.3.17-linux64/bin/pypy3 fasteval.py ../agent/agent.py $* ; rm -rf ~/$R" > "$HERE/runs/$TAG.txt" 2>&1
head -c 900 "$HERE/runs/$TAG.txt"; echo
