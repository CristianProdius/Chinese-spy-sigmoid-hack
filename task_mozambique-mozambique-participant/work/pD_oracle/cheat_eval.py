"""fasteval.py, but the agent module is told the true style before each game (sets CHEAT).
Upper bound for the style-tracking part.   pypy3 cheat_eval.py AGENT.py [fasteval args]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import fasteval as F
_orig = F.play
def play(agent_mod, group, seed, style, trace=False):
    agent_mod.CHEAT = style
    return _orig(agent_mod, group, seed, style, trace)
F.play = play
if __name__ == '__main__':
    F.main()
