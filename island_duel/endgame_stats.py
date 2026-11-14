"""How are games decided? Final-margin distribution and late-game swings."""
import importlib, os, sys
from collections import defaultdict
sys.path.insert(0, "../bundle")
from client import ArenaClient
agent = importlib.import_module(sys.argv[1])
games = int(sys.argv[2]) if len(sys.argv) > 2 else 64
rows = []
with ArenaClient("../samoa-wrapped") as env:
    for g in range(games):
        if hasattr(agent, "reset_agent"): agent.reset_agent()
        r = env.reset(g % 32, 424242 + g)
        seat = r["observation"]["seat"]
        hist = []
        while not r["done"]:
            o = r["observation"]
            hist.append((o["scores"][seat] - o["scores"][1 - seat], o["energy"][seat], o["energy"][1 - seat]))
            r = env.step(agent.choose_action(o))
        final = r["scores"][seat] - r["scores"][1 - seat]
        rows.append((seat, final, hist))
for seat in (0, 1):
    sub = [x for x in rows if x[0] == seat]
    print(f"seat {seat}: n={len(sub)} wins={sum(f > 0 for _, f, _ in sub)}")
    for k in (1, 2, 4, 8, 16):
        sw = [f - h[-k][0] for _, f, h in sub]
        print(f"  margin change over last {k:2d} decisions: mean {sum(sw)/len(sw):+.1f}  "
              f"|>10|: {sum(abs(s) > 10 for s in sw)}  E me/opp at -{k}: "
              f"{sum(h[-k][1] for _, _, h in sub)/len(sub):.1f}/{sum(h[-k][2] for _, _, h in sub)/len(sub):.1f}")
    close = [f for _, f, _ in sub]
    print("  final margins:", sorted(close))
