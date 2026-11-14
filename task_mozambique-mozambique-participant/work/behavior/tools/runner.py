"""Tiny scripted-plan runner. A plan is a list of per-boat step lists; each round the first boat
whose next step is executable gets the side's action. Steps:
  ('load', g, q) ('unload', g, q) ('gather', g, q) ('goto', site) ('deliver', c)
  ('build_workshop',) ('craft',) ('await_goods', site, g, q)  ('build_boat',) ('hold', round)
Records the full per-round log like observe.py.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from observe import next_hop

def run_plan(a, group, seed, game, plan, record=True, max_rounds=80, sail_first=False):
    s = a.reset(group, seed, game)
    o = s['observation']; m = o['map']
    ptr = [0] * len(plan)
    claim_round = [None] * 8; last = 0; score_tl = []; log = []; events = []
    while not s['game_done']:
        o = s['observation']; la = o['legal_actions']; boats = o['own']['boats']
        act = None
        # sail steps first (travel is the critical path), then plan order
        order = sorted(range(len(plan)), key=lambda i: (0 if ptr[i] < len(plan[i]) and plan[i][ptr[i]][0] == 'goto' and sail_first else 1, i))
        for i in order:
            steps = plan[i]
            while ptr[i] < len(steps):
                st = steps[ptr[i]]
                if st[0] == 'build_boat':
                    if {'op': 'build_boat'} in la: act = {'op': 'build_boat'}; ptr[i] += 1
                    break
                if i >= len(boats): break
                b = boats[i]
                if b['destination'] != -1: break
                if st[0] == 'goto':
                    if b['position'] == st[1]: ptr[i] += 1; continue
                    h = next_hop(m['routes'], b['position'], st[1])
                    cand = {'op': 'sail', 'boat': i, 'destination': h}
                    if cand in la: act = cand
                    break
                if st[0] == 'hold':
                    if o['round'] >= st[1]: ptr[i] += 1; continue
                    break
                if st[0] == 'await_goods':
                    if o['own']['warehouses'][st[1]][st[2]] >= st[3]: ptr[i] += 1; continue
                    break
                if st[0] == 'gather_max':
                    opts = [x for x in la if x['op'] == 'gather' and x.get('boat') == i and x.get('good') == st[1]]
                    if opts:
                        act = max(opts, key=lambda x: x['quantity']); ptr[i] += 1
                    break
                if st[0] in ('load', 'unload', 'gather'):
                    cand = {'op': st[0], 'boat': i, 'good': st[1], 'quantity': st[2]}
                elif st[0] == 'deliver':
                    cand = {'op': 'deliver', 'boat': i, 'contract': st[1]}
                else:
                    cand = {'op': st[0], 'boat': i}
                if cand in la:
                    act = cand; ptr[i] += 1
                elif st[0] == 'deliver' and o['claims'][st[1]] != -1:
                    events.append((o['round'], 'lost', st[1])); ptr[i] = len(steps)  # contract gone: abort this boat
                elif st[0] == 'gather':
                    pass  # wait for stock
                break
            if act: break
        if act is None: act = {'op': 'wait'}
        s = a.step(act)
        o2 = s.get('observation')
        if o2 is None: break
        r = o2['round'] - 1
        if act['op'] == 'deliver': events.append((r, 'deliver', act['contract']))
        for c, v in enumerate(o2['claims']):
            if v != -1 and claim_round[c] is None: claim_round[c] = (r, v)
        if o2['opponent_score'] != last:
            score_tl.append((r, o2['opponent_score'])); last = o2['opponent_score']
        if record:
            log.append(dict(r=r, act=act, vis=[i for i, v in enumerate(o2['visible']) if v],
                            stocks=o2['stocks'], enemy=o2['enemy_boats'],
                            own=[(b['position'], b['destination'], b['eta'], b['cargo']) for b in o2['own']['boats']]))
    return dict(group=group, seed=seed, game=game, seat=o['seat'], map=m, plan=plan, claim_round=claim_round,
                score_tl=score_tl, result=s['result'], events=events, log=log)
