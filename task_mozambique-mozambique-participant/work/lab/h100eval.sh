#!/usr/bin/env bash
# Run fasteval.py on a remote box (pure-Python engine; no binary needed).
#   work/lab/h100eval.sh AGENT.py [fasteval args...]      e.g. --maps 96 --jobs 12 --quiet
# Tries Prodius's MacBook first (14 Apple Silicon cores, ~10x faster than this dev box for a 240-game
# run), then the H100 box (26 cores). Set EVAL_HOST=h100 or EVAL_HOST=mbp to force one.
# Copies the agent (+ any .py files in the agent's own folder), fasteval.py and professor.py to
# <host>:~/maputo/runs/<agentname>-<pid>/ and runs it there under nice. Prints fasteval's output.
# CPU TIMES DIFFER BY HOST: MacBook cpu numbers are ~4x lower than the dev box, H100 ~2x lower.
# The 5 s cpu_max budget in DESIGN.md is in dev-box seconds.
set -euo pipefail
LAB="$(cd "$(dirname "$0")" && pwd)"
AGENT="$(realpath "$1")"; shift
ARGS="$*"
NAME="$(basename "$AGENT" .py)-$$"
REMOTE="maputo/runs/$NAME"

run_on() {   # host pypy cpu_factor
  local host="$1" pypy="$2" factor="$3"
  ssh -o BatchMode=yes -o ConnectTimeout=8 "$host" "mkdir -p ~/$REMOTE/lab ~/$REMOTE/binary ~/$REMOTE/agent" || return 99
  rsync -q "$LAB/fasteval.py" "$host:$REMOTE/lab/"
  rsync -q "$LAB/../binary/professor.py" "$host:$REMOTE/binary/"
  rsync -q "$(dirname "$AGENT")"/*.py "$host:$REMOTE/agent/"
  echo "NOTE: ran on $host; its cpu numbers are ~${factor}x lower than the dev box (multiply cpu_max by ${factor} to compare with the 5 s dev-box budget)" >&2
  ssh -o BatchMode=yes "$host" "cd ~/$REMOTE/lab && nice -n 5 $pypy fasteval.py ../agent/$(basename "$AGENT") $ARGS; rm -rf ~/$REMOTE"
}

MBP=(prodius-mbp-compute '~/maputo/opt/pypy3.10-v7.3.17-macos_arm64/bin/pypy3' 4)
H100=(h100 '~/maputo/opt/pypy3.10-v7.3.17-linux64/bin/pypy3' 2)
case "${EVAL_HOST:-auto}" in
  mbp)  run_on "${MBP[@]}" ;;
  h100) run_on "${H100[@]}" ;;
  *)    set +e; run_on "${MBP[@]}"; rc=$?; set -e
        if [ "$rc" = 99 ]; then echo "NOTE: MacBook unreachable, using the H100" >&2; run_on "${H100[@]}"; else exit "$rc"; fi ;;
esac
