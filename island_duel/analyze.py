"""Per-game breakdown: neutral claims, captures each way, rests, wasted energy."""

import importlib
import sys
from collections import defaultdict

sys.path.insert(0, "../bundle")
from client import ArenaClient  # noqa: E402

agent = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "greedy_agent")
N = 15
tot = defaultdict(float)
games = 0
with ArenaClient("../samoa-wrapped") as env:
    for arena in range(32):
        for g in range(2):
            r = env.reset(arena, 7000 + arena * 10 + g)
            seat = r["observation"]["seat"]
            win_key = None
            while not r["done"]:
                o = r["observation"]
                a = agent.choose_action(o)
                e = o["energy"][seat]
                if a is None:
                    tot["rests"] += 1
                    tot["rest_waste"] += max(0, e + 3 - 9)
                elif o["owners"][a] == 1 - seat:
                    tot["my_captures"] += 1
                    tot["my_capture_value"] += o["weights"][a]
                else:
                    tot["my_claims"] += 1
                    tot["my_claim_value"] += o["weights"][a]
                mine_before = {i for i in range(N * N) if o["owners"][i] == seat}
                r = env.step(a)
                o2 = r["observation"]
                if a is not None:
                    mine_before.add(a)
                lost = [i for i in mine_before if o2["owners"][i] != seat]
                tot["lost_tiles"] += len(lost)
                tot["lost_value"] += sum(o["weights"][i] for i in lost if o["weights"][i] is not None)
            tot["end_energy"] += r["observation"]["energy"][seat]
            s = r["scores"]
            tot["win_s%d" % seat] += r["winner"] == seat
            tot["games_s%d" % seat] += 1
            games += 1
for k, v in sorted(tot.items()):
    print(f"{k:18s} {v / games:8.2f} per game")
