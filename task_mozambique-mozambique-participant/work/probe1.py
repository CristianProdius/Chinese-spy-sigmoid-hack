import sys, json, random
sys.path.insert(0, '.')
from arena import Arena
rng = random.Random(1)
with Arena() as a:
    print(a.request('hello'))
    s = a.reset(0, 767302775, 0)
    ops = {}
    for r in range(80):
        obs = s['observation']
        la = obs['legal_actions']
        for x in la:
            ops.setdefault(x['op'], x)
        # prefer non-wait
        nw = [x for x in la if x['op'] != 'wait']
        act = rng.choice(nw) if nw and rng.random() < 0.9 else la[0]
        prev = obs
        s = a.step(act)
        if s['game_done']:
            print('DONE', json.dumps(s)[:3000]); break
        o = s['observation']
        print(r, act, 'boats', o['own']['boats'], 'wh', [w for w in o['own']['warehouses']], 'stocks', o['stocks'], 'vis', [i for i,v in enumerate(o['visible']) if v], 'enemy', o['enemy_boats'], 'claims', o['claims'], 'sc', o['own']['score'], o['opponent_score'], 'jobs', o['own']['jobs'], 'ws', [i for i,v in enumerate(o['own']['workshops']) if v])
    print(ops)
    print(json.dumps(s)[:2000])
