"""Weighted-random traces: python3 collect2.py OUT.jsonl NGAMES SEED"""
import json, random, sys
from eng import Arena
out, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed)
W = dict(deliver=60, craft=40, build_workshop=25, build_boat=6, gather=6, unload=4, load=4, sail=4, wait=1)
with Arena() as a, open(out, 'w') as f:
    for i in range(n):
        g = rng.randrange(8); sd = rng.randrange(2**32); game = rng.randrange(5)
        wscale = {k: v * rng.choice([0.3, 1, 3]) for k, v in W.items()}
        s = a.reset(g, sd, game)
        obs = []; acts = []
        while not s['game_done']:
            o = s['observation']
            la = o['legal_actions']
            ws = [wscale[x['op']] for x in la]
            act = rng.choices(la, weights=ws)[0]
            obs.append(o); acts.append(act)
            s = a.step(act)
        f.write(json.dumps(dict(group=g, seed=sd, game=game, obs=obs, acts=acts, final={k: v for k, v in s.items() if k != 'observation'}, final_obs=s.get('observation'))) + '\n')
        f.flush()
