import json, random, sys
from eng import Arena
g, seed, game, rs, n = map(int, sys.argv[1:6])
rng = random.Random(rs)
with Arena() as a:
    s = a.reset(g, seed, game)
    for r in range(n):
        o = s['observation']
        la = o['legal_actions']
        ob=o['own']
        seq=[]
        for x in la:
            t=(x['op'][:2], x.get('boat'), x.get('good'))
            if not seq or seq[-1]!=t: seq.append(t)
        print(o['round'], [(b['position'],b['destination'],b['cargo']) for b in ob['boats']], {i:w for i,w in enumerate(ob['warehouses']) if any(w)}, o['stocks'])
        print('    ', ' '.join('%s%s%s'%(a,'' if b is None else b,'' if c is None else ':'+str(c)) for a,b,c in seq))
        nw = [x for x in la if x['op'] != 'wait']
        act = rng.choice(nw) if nw and rng.random() < 0.9 else la[0]
        s = a.step(act)
        if s['game_done']: break
