"""Debug: compare sampled worlds with the truth inside the simulator."""
import json
import random
import sys

from fog import Tracker, sample_world
from sim_fog import observe
from simlib import Game

maps = [json.loads(l) for l in open("maps_32.jsonl")]
pred_ok = pred_n = 0
for m in maps[:6]:
    seat = m["seat"]
    g = Game(m, 1 - seat, m["profile"])
    tr = Tracker(seat)
    rng = random.Random(1)
    t = 0
    while g.get("remaining") > 0:
        if g.get("cur") == seat:
            obs = observe(g, seat)
            tr.update(obs)
            a = g.negamax(160, 9)
            wd = sample_world(tr, obs, rng)
            pub = {k: obs[k] for k in ("energy", "scores", "actions_remaining", "seat", "opponent_profile")}
            sw = Game.from_world(wd, pub)
            # true champion reply vs predicted
            gt = g.copy(); gt.apply(a)
            if gt.get("remaining") > 0:
                true_r = gt.champ()
                sw.apply(a)
                pr = sw.champ()
                pred_n += 1
                pred_ok += pr == true_r
            if t % 40 == 20:
                own = g.get("owner", 225)
                tc = [i for i in range(225) if own[i] == 1 - seat]
                sc = [i for i in range(225) if wd["owner"][i] == 1 - seat]
                print(f"arena {m['arena']} t {t} true champ tiles {len(tc)} sum {sum(g.get('w', 225)[i] for i in tc)} "
                      f"score {g.get('score', 2)[1 - seat]} | sampled {len(sc)} sum {sum(wd['w'][i] for i in sc)} "
                      f"hidden items {len(tr.hidden)} overlap {len(set(tc) & set(sc))}")
            tr.remember(obs, None if a < 0 else a)
            g.apply(a)
        else:
            g.apply(g.champ())
        t += 1
print("reply prediction", pred_ok, "/", pred_n)
