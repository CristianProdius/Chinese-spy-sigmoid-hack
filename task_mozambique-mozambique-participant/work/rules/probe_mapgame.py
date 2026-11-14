import json
from eng import Arena
with Arena() as a:
    for seed in [1,2,3,767302775]:
        maps = {}
        for g in range(8):
            for game in range(5):
                o = a.reset(g, seed, game)['observation']
                maps[(g,game)] = json.dumps(o['map'], sort_keys=True), o['seat'], o['map']['homes']
        for t in range(4):
            same_game = all(maps[(2*t,0)][0]==maps[(2*t,k)][0] for k in range(5))
            same_seat = maps[(2*t,0)][0]==maps[(2*t+1,0)][0]
            print(seed, 'topo', t, 'map same over game idx', same_game, 'same over seat', same_seat, maps[(2*t,0)][2], maps[(2*t+1,0)][2])
