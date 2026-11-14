import json, random, sys
from eng import Arena
g, seed, game, rs = map(int, sys.argv[1:5])
rng = random.Random(rs)
with Arena() as a:
    s = a.reset(g, seed, game)
    o = s['observation']
    print('MAP', json.dumps(o['map']))
    for r in range(80):
        o = s['observation']
        la = o['legal_actions']
        ops = {}
        for x in la: ops.setdefault(x['op'], []).append({k:v for k,v in x.items() if k!='op'})
        nw = [x for x in la if x['op'] != 'wait']
        act = rng.choice(nw) if nw and rng.random() < 0.9 else la[0]
        ob=o['own']
        print('R', o['round'], 'boats', [(b['position'],b['destination'],b['eta'],b['cargo']) for b in ob['boats']], 'wh', {i:w for i,w in enumerate(ob['warehouses']) if any(w)}, 'stocks', o['stocks'], 'jobs', {i:j for i,j in enumerate(ob['jobs']) if j}, 'ws', [i for i,v in enumerate(ob['workshops']) if v], 'claims', o['claims'], 'sc', ob['score'], o['opponent_score'], 'cd', ob['crafted_deliveries'], 'enemy', o['enemy_boats'], 'vis', [i for i,v in enumerate(o['visible']) if v])
        print('   LEGAL', json.dumps(ops))
        print('   ACT', act)
        s = a.step(act)
        if s['game_done']:
            print('DONE', json.dumps({k:v for k,v in s.items() if k!='observation'}), json.dumps(s.get('observation'))[:500]); break
