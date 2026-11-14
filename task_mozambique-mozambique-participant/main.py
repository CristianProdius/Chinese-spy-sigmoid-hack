"""Your submission. Upload only this file; keep it self-contained (standard library only).

The evaluator runs `python main.py`, sends one JSON line {"observation": ...} per
decision on stdin and reads one JSON action per line from stdout. Leave the loop
at the bottom as it is and put your strategy in agent().
"""
import json
import sys


def agent(observation, memory):
    """Return one entry of observation['legal_actions']. `memory` resets each game."""
    return observation['legal_actions'][0]


def serve():
    protocol = sys.stdout
    sys.stdout = sys.stderr          # print() for debugging goes to stderr, not the protocol
    memory = {}
    for line in sys.stdin:
        observation = json.loads(line)['observation']
        if observation['round'] == 0:
            memory = {}
        protocol.write(json.dumps(agent(observation, memory)) + '\n')
        protocol.flush()


if __name__ == '__main__':
    serve()
