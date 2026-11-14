"""Scripted probe helper. run(group, seed, game, actions) where each action is a dict
matching the first legal action whose keys equal it ('wait' if none). Returns list of obs."""
import json, sys
from eng import Arena
_A = None
def arena():
    global _A
    if _A is None: _A = Arena()
    return _A
def match(la, act):
    m = [x for x in la if all(x.get(k) == v for k, v in act.items())]
    return m[0] if m else None
def run(group, seed, game, actions, upto=None, strict=False):
    a = arena()
    s = a.reset(group, seed, game)
    obs = [s['observation']]; taken = []
    n = len(actions) if upto is None else upto
    for r in range(n):
        o = s['observation']
        act = actions[r] if r < len(actions) else {'op': 'wait'}
        x = match(o['legal_actions'], act) if act else None
        if x is None:
            if strict: raise RuntimeError('illegal at %d: %r' % (r, act))
            x = {'op': 'wait'}
        taken.append(x)
        s = a.step(x)
        if s['game_done']:
            obs.append(s); break
        obs.append(s['observation'])
    return obs, taken
def brief(o):
    if 'observation' not in o and 'result' in o: return 'END %r' % o.get('result')
    ob = o['own']
    return 'R%d boats=%s wh=%s st=%s jobs=%s ws=%s cl=%s sc=%d/%d cd=%d en=%s vis=%s' % (
        o['round'], [(b['position'], b['destination'], b['eta'], b['cargo']) for b in ob['boats']],
        {i: w for i, w in enumerate(ob['warehouses']) if any(w)}, o['stocks'],
        {i: j for i, j in enumerate(ob['jobs']) if j}, [i for i, v in enumerate(ob['workshops']) if v],
        o['claims'], ob['score'], o['opponent_score'], ob['crafted_deliveries'],
        [(e['boat'], e['position'], e['destination'], e['eta']) for e in o['enemy_boats']],
        [i for i, v in enumerate(o['visible']) if v])
