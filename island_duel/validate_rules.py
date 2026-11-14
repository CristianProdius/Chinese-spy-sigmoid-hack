"""Check our reading of the rules against the engine's legal_actions."""

import importlib
import sys

sys.path.insert(0, "../bundle")
from client import ArenaClient  # noqa: E402

agent = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "greedy_agent")
N = 15
NB = [[(r + dr) * N + c + dc for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
       if 0 <= r + dr < N and 0 <= c + dc < N] for r in range(N) for c in range(N)]


def legal(o):
    seat, e = o["seat"], o["energy"][o["seat"]]
    out = [None]
    for i in range(N * N):
        own = o["owners"][i]
        if own == -1:
            cost = o["costs"][i]
        elif own == 1 - seat and o["weights"][i] != 0:
            cost = o["costs"][i] + 2
        else:
            continue
        if cost <= e and any(o["owners"][j] == seat for j in NB[i]):
            out.append(i)
    return out


bad = checked = 0
opp_deltas = {}
with ArenaClient("../samoa-wrapped") as env:
    for arena in range(32):
        r = env.reset(arena, 9100 + arena)
        while not r["done"]:
            o = r["observation"]
            mine, theirs = set(legal(o)), set(o["legal_actions"])
            checked += 1
            if mine != theirs:
                bad += 1
                if bad <= 5:
                    print("mismatch", arena, "ours-only", mine - theirs, "engine-only", theirs - mine,
                          "energy", o["energy"])
            a = agent.choose_action(o)
            r2 = env.step(a)
            # infer opponent energy change for its one action
            seat = o["seat"]
            my_e = o["energy"][seat]
            r = r2
print(f"checked {checked} states, {bad} mismatches")
