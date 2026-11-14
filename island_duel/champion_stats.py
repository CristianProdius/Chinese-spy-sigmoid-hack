"""Infer the champion's actions from public scores/energies and compare with ours."""
import importlib, sys
from collections import defaultdict
sys.path.insert(0, "../bundle")
from client import ArenaClient
agent = importlib.import_module(sys.argv[1])
games = int(sys.argv[2]) if len(sys.argv) > 2 else 64
S = defaultdict(lambda: defaultdict(float))
PROF = [0]
def note(who, kind, v=0, waste=0, e=0):
    who = f"{who}-p{PROF[0]}"
    d = S[who]; d[kind] += 1; d[kind + "_v"] += v; d["waste"] += waste; d["e_sum"] += e; d["n"] += 1
with ArenaClient("../samoa-wrapped") as env:
    for g in range(games):
        if hasattr(agent, "reset_agent"): agent.reset_agent()
        r = env.reset(g % 32, 9000 + g); seat = r["observation"]["seat"]; opp = 1 - seat
        PROF[0] = r["observation"]["opponent_profile"]; S[f"games-p{PROF[0]}"]["n"] += 1
        while not r["done"]:
            o = r["observation"]; a = agent.choose_action(o)
            e = o["energy"][seat]
            if a is None: note("me", "rest", 0, max(0, e + 3 - 9), e)
            elif o["owners"][a] == opp: note("me", "capture", o["weights"][a], 0, e)
            else: note("me", "claim", o["weights"][a], 0, e)
            # state after our action (before champion reply)
            ms = o["scores"][seat] + (o["weights"][a] if a is not None else 0)
            os_ = o["scores"][opp] - (o["weights"][a] if a is not None and o["owners"][a] == opp else 0)
            e_op = o["energy"][opp]
            r2 = env.step(a); o2 = r2["observation"]
            if r2["done"] and seat == 1: r = r2; break
            d_me = o2["scores"][seat] - ms; d_op = o2["scores"][opp] - os_; e2 = o2["energy"][opp]
            if d_me < 0: note("op", "capture", -d_me, 0, e_op)
            elif d_op > 0: note("op", "claim", d_op, 0, e_op)
            else: note("op", "rest", 0, max(0, e_op + 3 - 9), e_op)
            r = r2
for who, d in sorted(S.items()):
    if who.startswith("games"): print(who, int(d["n"])); continue
    n = d["n"]; games = S["games-" + who.split("-")[1]]["n"]
    print(f"{who}: per game: rests {d['rest']/games:.1f} (wasted energy {d['waste']/games:.1f}), "
          f"claims {d['claim']/games:.1f} avg v {d['claim_v']/max(1,d['claim']):.2f}, "
          f"captures {d['capture']/games:.1f} avg v {d['capture_v']/max(1,d['capture']):.2f}, "
          f"avg energy when deciding {d['e_sum']/n:.2f}")
