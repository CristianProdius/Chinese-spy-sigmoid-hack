"""Trace one game: our action, the champion's inferred action, energies, scores."""
import importlib, sys, os
sys.path.insert(0, "../bundle")
from client import ArenaClient
agent = importlib.import_module(sys.argv[1])
arena, seed = int(sys.argv[2]), int(sys.argv[3])
N = 15
def board(o, seat):
    rows = []
    for r in range(N):
        s = ""
        for c in range(N):
            i = r * N + c
            if not o["visible"][i]: s += "  ? "; continue
            own = o["owners"][i]
            if own == -2: s += "  # "; continue
            tag = "M" if own == seat else ("E" if own == 1 - seat else ".")
            s += f" {tag}{o['weights'][i]}{o['costs'][i]}"
        rows.append(s)
    return "\n".join(rows)
with ArenaClient("../samoa-wrapped") as env:
    if hasattr(agent, "reset_agent"): agent.reset_agent()
    r = env.reset(arena, seed); o = r["observation"]; seat = o["seat"]
    print("seat", seat, "profile", o["opponent_profile"])
    t = 0
    while not r["done"]:
        o = r["observation"]
        a = agent.choose_action(o)
        if a is None: desc = "REST"
        elif o["owners"][a] == 1 - seat: desc = f"CAPT {a} v{o['weights'][a]} c{o['costs'][a]}"
        else: desc = f"CLAIM {a} v{o['weights'][a]} c{o['costs'][a]}"
        r2 = env.step(a); o2 = r2["observation"]
        # enemy action: energy and scores after our action vs after their reply
        my_after = o["scores"][seat] + ((o["weights"][a] if a is not None else 0))
        opp_before = o["scores"][1 - seat] - (o["weights"][a] if a is not None and o["owners"][a] == 1 - seat else 0)
        e_opp0, e_opp1 = o["energy"][1 - seat], o2["energy"][1 - seat]
        ds_opp = o2["scores"][1 - seat] - opp_before
        ds_me = o2["scores"][seat] - my_after
        if t + 1 >= 128 and seat == 1: eact = "-"
        elif e_opp1 > e_opp0 or (e_opp1 == e_opp0 == 9 and ds_opp == 0): eact = "rest"
        elif ds_me < 0: eact = f"CAPTURES v{-ds_me} (cost {e_opp0 - e_opp1})"
        else: eact = f"claim v{ds_opp} (cost {e_opp0 - e_opp1})"
        print(f"{t:3d} me:{desc:22s} E {o['energy'][seat]}->{o2['energy'][seat]} | opp: {eact:26s} E {e_opp0}->{e_opp1} | S {o2['scores'][seat]}:{o2['scores'][1-seat]}")
        if t in (40, 80, 127): print(board(o2, seat))
        r = r2; t += 1
    print("winner", r["winner"], "seat", seat)
