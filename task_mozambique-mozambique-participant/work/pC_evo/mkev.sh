#!/usr/bin/env bash
# mkev.sh NAME [core] ['python line appended, e.g. PARAMS["scale"]=0.25'] -> ev/NAME/agent.py (own folder so h100eval copies one file)
set -e
cd "$(dirname "$0")"
NAME="$1"; CORE="${2:-core_fast.py}"; EXTRA="${3:-}"
mkdir -p "ev/$NAME"
python3 build.py "$CORE" "ev/$NAME/agent.py" >/dev/null
if [ -n "$EXTRA" ]; then printf '\n%s\n' "$EXTRA" >> "ev/$NAME/agent.py"; fi
echo "ev/$NAME/agent.py"
