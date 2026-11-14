"""Concatenate core.py + tsched.py + brain.py into one self-contained agent.py (main.py format)."""
import re, sys
HEAD = '''"""Your submission. Upload only this file; keep it self-contained (standard library only).

The evaluator runs `python main.py`, sends one JSON line {"observation": ...} per
decision on stdin and reads one JSON action per line from stdout. Leave the loop
at the bottom as it is and put your strategy in agent().
"""
import json
import sys

'''
TAIL = '''

def serve():
    protocol = sys.stdout
    sys.stdout = sys.stderr          # print() for debugging goes to stderr, not the protocol
    memory = {}
    for line in sys.stdin:
        observation = json.loads(line)['observation']
        if observation['round'] == 0:
            memory = {}
        protocol.write(json.dumps(agent(observation, memory)) + '\\n')
        protocol.flush()


if __name__ == '__main__':
    serve()
'''
strip = re.compile(r"try:\n    from \w+ import \*[^\n]*\nexcept ImportError:\n    pass\n")
core = sys.argv[2] if len(sys.argv) > 2 else 'core.py'
out = HEAD
for f in (core, 'tsched.py', 'brain.py'):
    out += '\n# ' + '=' * 90 + '\n# ' + f + '\n# ' + '=' * 90 + '\n' + strip.sub('', open(f).read())
out += TAIL
open(sys.argv[1] if len(sys.argv) > 1 else 'agent.py', 'w').write(out)
print('wrote', len(out), 'bytes')
