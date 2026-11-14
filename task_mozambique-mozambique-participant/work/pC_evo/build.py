"""Build the single-file agent: header + engine/Professor core + brain.py -> agent.py
    python3 build.py [core.py]      (default core: ../binary/professor.py; fastcore when given)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
core = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'binary', 'professor.py')
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'agent.py')
src = open(core).read()
brain = open(os.path.join(HERE, 'brain.py')).read()
head = '''"""The Professor of Maputo Bay: rolling-horizon evolutionary planner (single file, stdlib only).

Tracks the five Professor styles with an exact copy of the engine and of the Professor, evolves a
macro plan (ordered contract targets + logistics options) decoded by a deterministic scheduler,
and scores plans by rollouts against every surviving style hypothesis.
"""
import json
import sys

'''
open(out, 'w').write(head + '# ==== CORE (engine rules + Professor) ====\n' + src + '\n\n' + brain)
print('wrote', out, os.path.getsize(out), 'bytes')
