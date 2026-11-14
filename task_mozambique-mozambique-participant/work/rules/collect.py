"""Collect random-legal-action traces: python3 collect.py OUT.jsonl NGAMES SEED [pnonwait]"""
import json, random, sys
from eng import Arena
out, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
pnw = float(sys.argv[4]) if len(sys.argv) > 4 else 0.9
rng = random.Random(seed)
with Arena() as a, open(out, 'w') as f:
    for i in range(n):
        g = rng.randrange(8); sd = rng.randrange(2**32); game = rng.randrange(5)
        s = a.reset(g, sd, game)
        obs = []; acts = []
        while not s['game_done']:
            o = s['observation']
            la = o['legal_actions']
            nw = [x for x in la if x['op'] != 'wait']
            # bias toward productive ops
            pri = [x for x in nw if x['op'] in ('deliver', 'craft', 'build_workshop', 'build_boat')]
            if pri and rng.random() < 0.7: act = rng.choice(pri)
            elif nw and rng.random() < pnw: act = rng.choice(nw)
            else: act = la[0]
            obs.append(o); acts.append(act)
            s = a.step(act)
        f.write(json.dumps(dict(group=g, seed=sd, game=game, obs=obs, acts=acts, final={k: v for k, v in s.items() if k != 'observation'}, final_obs=s.get('observation'))) + '\n')
