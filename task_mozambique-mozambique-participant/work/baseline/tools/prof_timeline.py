"""Professor's claim rounds when we only wait: python3 prof_timeline.py NMAPS SEED"""
import sys, json, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
GROUPS = [2 * t + s for t in range(4) for s in range(2)]
n = int(sys.argv[1]); seed = int(sys.argv[2])
rng = random.Random(seed)
seeds = [rng.randrange(2 ** 32) for _ in range(n)]
out = []
with Arena() as a:
    for m in range(n):
        g = GROUPS[m % 8]
        for game in range(5):
            s = a.reset(g, seeds[m], game)
            claim = [None] * 8
            while not s['game_done']:
                o = s['observation']
                for c in range(8):
                    if o['claims'][c] == 1 - o['seat'] and claim[c] is None:
                        claim[c] = o['round'] - 1
                s = a.step({'op': 'wait'})
            out.append(dict(map=m, group=g, game=game, claim=claim, score=s['result']['scores'][1]))
            print(m, g, game, claim, s['result']['scores'][1], flush=True)
json.dump(out, open(sys.argv[3], 'w'))
