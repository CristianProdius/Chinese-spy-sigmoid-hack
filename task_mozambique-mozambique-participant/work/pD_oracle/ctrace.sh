#!/usr/bin/env bash
# ctrace.sh AGENT GROUP SEED STYLE : trace with the true style known
cd "$(dirname "$0")"
nice -n 10 /home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3 - "$@" <<'PY'
import sys, runpy
agent = sys.argv[1]
import importlib.util
sys.argv = ['trace.py'] + sys.argv[1:]
src = open('trace.py').read().replace("A.DEBUG = not quiet\n", "A.DEBUG = not quiet\nA.CHEAT = int(sys.argv[4])\n")
exec(compile(src, 'trace.py', 'exec'), {'__name__': '__main__', '__file__': 'trace.py'})
PY
