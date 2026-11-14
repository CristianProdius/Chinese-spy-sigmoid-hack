"""Diagnostic (practice only): does 1-step lookahead with the TRUE champion reply help?

At each decision, for the policy's top-K moves, replay the game in a second
engine (deterministic per seed), play the candidate, observe the champion's
real reply, and score Q = reward + V(next real observation). Play argmax Q.
If this oracle does not beat plain argmax, value-guided search is not worth
building. Never usable in evaluation (it needs the seed).

python oracle_test.py <games> <K>   (env ID_MODEL, ID_DEVICE)
"""

import os
import sys

sys.path.insert(0, "../bundle")
sys.path.insert(0, "rl")
import numpy as np  # noqa: E402
import torch  # noqa: E402

from client import ArenaClient  # noqa: E402
from features import Memory, featurize, to_engine_action  # noqa: E402
from model import Net  # noqa: E402

dev = torch.device(os.environ.get("ID_DEVICE", "cuda"))
ck = torch.load(os.environ["ID_MODEL"], map_location=dev)
net = Net(ck["args"].get("ch", 96), ck["args"].get("blocks", 8)).to(dev).eval()
net.load_state_dict(ck["model"])
games, K = int(sys.argv[1]), int(sys.argv[2])
start = int(sys.argv[3]) if len(sys.argv) > 3 else 0


@torch.no_grad()
def run(x, m):
    lg, v = net(torch.from_numpy(x[None]).to(dev), torch.from_numpy(m[None]).to(dev))
    return lg[0].cpu().numpy(), float(v[0])


wins = changed = 0
with ArenaClient("../samoa-wrapped") as env, ArenaClient("../samoa-wrapped") as sim:
    for g in range(start, start + games):
        arena, seed = g % 32, 777000 + g
        r = env.reset(arena, seed)
        mem = Memory()
        hist = []
        while not r["done"]:
            o = r["observation"]
            x, m = featurize(o, mem)
            lg, _ = run(x, m)
            order = [int(i) for i in np.argsort(-lg)[:K] if m[i]]
            best, best_q = order[0], -1e9
            if len(order) > 1:
                for ca in order:
                    a = to_engine_action(ca, o["seat"])
                    rr = sim.reset(arena, seed)
                    smem = Memory()
                    featurize(rr["observation"], smem)
                    for h in hist:
                        rr = sim.step(h)
                        featurize(rr["observation"], smem)
                    rr = sim.step(a)
                    q = 0.1 * rr["reward"]
                    if not rr["done"]:
                        x2, m2 = featurize(rr["observation"], smem)
                        q += run(x2, m2)[1]
                    if q > best_q:
                        best, best_q = ca, q
            changed += best != order[0]
            a = to_engine_action(best, o["seat"])
            hist.append(a)
            r = env.step(a)
        seat = r["observation"]["seat"]
        wins += r["winner"] == seat
        print(f"game {g} seat {seat} win {r['winner'] == seat} scores {r['scores']}", flush=True)
print(f"oracle K={K}: {wins}/{games} wins, changed {changed} decisions")
