"""Concatenate core.py + brain.py + the serve() loop into one self-contained agent.py."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
core = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'core.py')
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'agent.py')
src = open(core).read()
brain = ''.join(l for l in open(os.path.join(HERE, 'brain.py')).readlines() if 'BUILD-STRIP' not in l)
serve = '''

def serve():
    import json
    import sys
    protocol = sys.stdout
    sys.stdout = sys.stderr
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
open(out, 'w').write('"""pB_rush agent: Professor-aware manufacturing rush (built from core.py + brain.py)."""\n' + src + '\n\n' + brain + serve)
print('wrote', out, os.path.getsize(out), 'bytes')
