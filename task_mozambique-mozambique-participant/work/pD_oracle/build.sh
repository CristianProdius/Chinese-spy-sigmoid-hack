#!/usr/bin/env bash
# Builds the self-contained agent: header + reference engine/Professor core (our planner) +
# embedded fastcore source (opponent model) + brain.
set -euo pipefail
cd "$(dirname "$0")"
OUT=${1:-agent.py}
FAST=${FASTCORE:-../fast/fastcore.py}
{
  echo '"""The Professor of Maputo Bay - oracle agent (exact opponent model + foresight planner)."""'
  cat _core.py
  python3 -c "import sys; print('_FASTCORE_SRC = ' + repr(open(sys.argv[1]).read()))" "$FAST"
  cat _brain.py
} > "$OUT"
echo "built $OUT ($(wc -c < "$OUT") bytes)"
