"""Average score margin / energy by game phase, split by seat and outcome."""
import importlib, sys
from collections import defaultdict
sys.path.insert(0, "../bundle")
from client import ArenaClient
agent = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "greedy_agent")
acc = defaultdict(lambda: defaultdict(list))
with ArenaClient("../samoa-wrapped") as env:
    for arena in range(32):
        for g in range(4):
            if hasattr(agent, "reset_agent"): agent.reset_agent()
            r = env.reset(arena, 11000 + arena * 10 + g)
            seat = r["observation"]["seat"]; prof = r["observation"]["opponent_profile"]
            snaps = {}
            t = 0
            while not r["done"]:
                o = r["observation"]
                if t in (8, 16, 32, 64, 96):
                    snaps[t] = (o["scores"][seat] - o["scores"][1 - seat], o["energy"][seat], o["energy"][1 - seat])
                r = env.step(agent.choose_action(o)); t += 1
            snaps[128] = (r["scores"][seat] - r["scores"][1 - seat], 0, 0)
            key = f"seat{seat} {'win ' if r['winner'] == seat else 'loss'}"
            for k, v in snaps.items(): acc[key][k].append(v)
            for k, v in snaps.items(): acc[f"prof{prof}"][k].append(v)
for key in sorted(acc):
    n = len(acc[key][128])
    print(f"{key:12s} n={n:3d} " + "  ".join(
        f"t{t}:{sum(x[0] for x in v)/len(v):+6.1f}(E{sum(x[1] for x in v)/len(v):.1f}/{sum(x[2] for x in v)/len(v):.1f})"
        for t, v in sorted(acc[key].items())))
