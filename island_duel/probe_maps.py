"""Probe map statistics and symmetry from what an agent sees during games."""

import sys
from collections import Counter

sys.path.insert(0, "../bundle")
from client import ArenaClient  # noqa: E402
from greedy_agent import choose_action  # noqa: E402

N = 15
wc, cc, blocked, pairs = Counter(), Counter(), Counter(), Counter()
with ArenaClient("../samoa-wrapped") as env:
    for arena in range(32):
        for g in range(3):
            r = env.reset(arena, 5000 + arena * 10 + g)
            seen = {}
            while not r["done"]:
                o = r["observation"]
                for i in range(N * N):
                    if o["visible"][i]:
                        seen[i] = (o["owners"][i] == -2, o["weights"][i], o["costs"][i])
                r = env.step(choose_action(o))
            for i, (blk, w, c) in seen.items():
                if blk:
                    blocked["blocked"] += 1
                else:
                    blocked["open"] += 1
                    wc[w] += 1
                    cc[c] += 1
                j = N * N - 1 - i  # point mirror
                k = (i % N) * N + i // N  # transpose
                for name, m in (("point", j), ("transpose", k), ("anti", (N - 1 - i % N) * N + (N - 1 - i // N))):
                    if m in seen and m != i:
                        pairs[name + ("_eq" if seen[m] == seen[i] else "_ne")] += 1
print("weights", sorted(wc.items()))
print("costs", sorted(cc.items()))
print("blocked", dict(blocked))
print("symmetry", dict(pairs))
