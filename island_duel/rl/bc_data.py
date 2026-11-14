"""Record a teacher agent's games as (features, canonical action, reward) for BC.

python bc_data.py --agent ../search_agent.py --games 1536 --workers 20 --out bc.pt

Generates the games, then trains the policy (cross-entropy) and value
(discounted return) heads and saves a checkpoint train.py can --init from.
"""

from __future__ import annotations

import argparse
import importlib.util
import multiprocessing as mp
import os
import random
import sys

import numpy as np

from features import CELLS, Memory, featurize
from vecenv import Engine

_args = None


def _load(path):
    path = os.path.abspath(path)
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("teacher", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _games(job):
    agent_path, engine, seeds = job
    agent = _load(agent_path)
    eng = Engine(engine)
    X, A, R, M, W = [], [], [], [], []
    for arena, seed in seeds:
        if hasattr(agent, "reset_agent"):
            agent.reset_agent()
        eng.send(f"reset {arena} {seed}")
        r = eng.recv()
        mem = Memory()
        gx, ga, gr, gm = [], [], [], []
        while not r["done"]:
            o = r["observation"]
            x, m = featurize(o, mem)
            a = agent.choose_action(o)
            if a is None:
                ca = CELLS
            else:
                ca = CELLS - 1 - a if o["seat"] == 1 else a
            assert m[ca], "teacher action not legal in features"
            eng.send(f"step {-1 if a is None else a}")
            r = eng.recv()
            gx.append(x)
            ga.append(ca)
            gm.append(m)
            gr.append(r["reward"])
        seat = r["observation"]["seat"]
        win = r["winner"] == seat
        X += gx
        A += ga
        R += gr
        M += gm
        W += [win] * len(ga)
    eng.close()
    return (np.array(X, np.float32), np.array(A, np.int64), np.array(R, np.float32),
            np.array(M, bool), np.array(W, bool))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--engine", default=os.path.expanduser("~/island-duel/samoa-wrapped"))
    ap.add_argument("--games", type=int, default=4096)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--out", default="bc.pt")
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--ch", type=int, default=96)
    ap.add_argument("--blocks", type=int, default=8)
    ap.add_argument("--gamma", type=float, default=0.997)
    ap.add_argument("--reward-scale", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=12345)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    seeds = [(rng.randrange(32), rng.getrandbits(32)) for _ in range(args.games)]
    chunks = [seeds[i::args.workers * 4] for i in range(args.workers * 4)]
    with mp.Pool(args.workers) as pool:
        parts = pool.map(_games, [(args.agent, args.engine, c) for c in chunks])
    X, A, R, M, W = (np.concatenate([p[i] for p in parts]) for i in range(5))
    print("samples", len(A), "teacher win rate", W.mean(), flush=True)
    train_bc(X, A, R, M, args)


def train_bc(X, A, R, M, args):
    import torch
    import torch.nn.functional as F
    from model import Net

    # discounted returns per 128-step game (games are stored contiguously)
    G = np.zeros_like(R)
    Rg = (R * args.reward_scale).reshape(-1, 128)
    Gg = G.reshape(-1, 128)
    acc = np.zeros(Rg.shape[0], np.float32)
    for t in reversed(range(128)):
        acc = Rg[:, t] + args.gamma * acc
        Gg[:, t] = acc
    dev = torch.device("cuda")
    net = Net(args.ch, args.blocks).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    n = len(A)
    Xt, At, Mt, Gt = (torch.from_numpy(a) for a in (X, A, M, G))
    idx_all = np.arange(n)
    val = idx_all[-n // 20:]
    tr = idx_all[: -n // 20]
    for ep in range(args.epochs):
        net.train()
        np.random.shuffle(tr)
        tot = 0.0
        for i in range(0, len(tr), 2048):
            b = torch.from_numpy(tr[i:i + 2048])
            x, a, m, g = Xt[b].to(dev), At[b].to(dev), Mt[b].to(dev), Gt[b].to(dev)
            logits, v = net(x, m)
            loss = F.cross_entropy(logits, a) + 0.5 * F.mse_loss(v, g)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item()
        net.eval()
        with torch.no_grad():
            b = torch.from_numpy(val)
            correct = 0
            for i in range(0, len(val), 4096):
                bb = b[i:i + 4096]
                logits, v = net(Xt[bb].to(dev), Mt[bb].to(dev))
                correct += (logits.argmax(1).cpu() == At[bb]).sum().item()
        print(f"epoch {ep} train loss {tot / max(1, len(tr) // 2048):.3f} val acc {correct / len(val):.3f}", flush=True)
        for g in opt.param_groups:
            g["lr"] *= 0.7
    torch.save({"model": net.state_dict(), "args": {"ch": args.ch, "blocks": args.blocks}},
               args.out)
    print("saved", args.out)


if __name__ == "__main__":
    main()
