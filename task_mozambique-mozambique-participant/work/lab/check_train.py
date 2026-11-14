import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'binary'))
import professor as P
import fasteval as F
class Starter:
    @staticmethod
    def agent(obs, memory): return obs['legal_actions'][0]
cases = json.load(open('../../train-input.json')); outs = json.load(open('../../train-output.json'))
bad = 0
for c, o in zip(cases, outs):
    style = P.style_permutation(c['seed'])[c['game']]
    r = F.play(Starter, c['group'], c['seed'], style)
    if [r['us'], r['them']] != o['scores'] or r['hp'] != o['half_points']:
        bad += 1; print('MISMATCH', c, o['scores'], r['us'], r['them'])
print('cases', len(cases), 'mismatches', bad)
