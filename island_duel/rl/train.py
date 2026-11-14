"""PPO against the champion, using the native engine as the environment.

Every game is exactly 128 of our decisions, so one rollout is one full game in
each of --envs engines. Rewards are the engine's own (margin change / 10 and
+-10 at the end), scaled by --reward-scale.

python train.py --envs 128 --updates 2000 --out runs/ppo1
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import time

import numpy as np
import torch
import torch.nn.functional as F

from features import NUM_ACTIONS
from model import Net
from vecenv import VecEnv
from vecenv_mp import MPVecEnv

STEPS = 128


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=os.path.expanduser("~/island-duel/samoa-wrapped"))
    ap.add_argument("--envs", type=int, default=128)
    ap.add_argument("--updates", type=int, default=2000)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--gamma", type=float, default=0.997)
    ap.add_argument("--lam", type=float, default=0.95)
    ap.add_argument("--clip", type=float, default=0.2)
    ap.add_argument("--ent", type=float, default=0.01)
    ap.add_argument("--vf", type=float, default=0.5)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--minibatch", type=int, default=4096)
    ap.add_argument("--reward-scale", type=float, default=0.1)
    ap.add_argument("--ch", type=int, default=96)
    ap.add_argument("--blocks", type=int, default=8)
    ap.add_argument("--init", default=None, help="checkpoint to start from")
    ap.add_argument("--out", default="runs/ppo")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--group", type=int, default=1,
                    help=">1: envs share (arena, seed) in groups; advantage = return minus group mean")
    ap.add_argument("--margin-coef", type=float, default=1.0,
                    help="weight of the per-step margin reward relative to the +-1 win/loss reward")
    ap.add_argument("--ema", type=float, default=0.0, help="EMA decay of weights for eval checkpoints (0=off)")
    ap.add_argument("--top-adv", type=float, default=1.0,
                    help="train only on this fraction of samples with the largest |advantage|")
    ap.add_argument("--gae-mix", type=float, default=0.0,
                    help="with --group, add this fraction of the per-step GAE advantage")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    torch.manual_seed(args.seed)
    dev = torch.device("cuda")
    net = Net(args.ch, args.blocks).to(dev)
    if args.init:
        net.load_state_dict(torch.load(args.init, map_location=dev)["model"])
    opt = torch.optim.Adam(net.parameters(), lr=args.lr, eps=1e-5)
    ema = None
    if args.ema > 0:
        import copy
        ema = copy.deepcopy(net).eval()
        for p_ in ema.parameters():
            p_.requires_grad_(False)
    if args.workers > 1:
        env = MPVecEnv(args.envs, args.engine, workers=args.workers, seed=args.seed)
    else:
        env = VecEnv(args.envs, args.engine, seed=args.seed)
    E = args.envs
    recent = collections.deque(maxlen=1024)
    log = open(os.path.join(args.out, "log.jsonl"), "a")
    best = -1.0
    t_start = time.time()

    for update in range(1, args.updates + 1):
        t0 = time.time()
        tasks = None
        if args.group > 1:
            import random as _r
            tasks = []
            for _ in range(E // args.group):
                t = (_r.randrange(32), _r.getrandbits(32))
                tasks += [t] * args.group
        x, m = env.reset_all(tasks)
        X = np.zeros((STEPS, E) + x.shape[1:], np.float32)
        M = np.zeros((STEPS, E, NUM_ACTIONS), bool)
        A = np.zeros((STEPS, E), np.int64)
        LP = np.zeros((STEPS, E), np.float32)
        V = np.zeros((STEPS, E), np.float32)
        R = np.zeros((STEPS, E), np.float32)
        net.eval()
        for t in range(STEPS):
            X[t], M[t] = x, m
            with torch.no_grad():
                xt = torch.from_numpy(x).to(dev)
                mt = torch.from_numpy(m).to(dev)
                logits, v = net(xt, mt)
                dist = torch.distributions.Categorical(logits=logits)
                a = dist.sample()
                LP[t] = dist.log_prob(a).cpu().numpy()
                V[t] = v.cpu().numpy()
                A[t] = a.cpu().numpy()
            x, m, r, done, results = env.step(A[t])
            # engine reward * 0.1 = margin change / 100 + (+-1 at the end); reweight the margin part
            term = np.zeros(E, np.float32)
            for res in results:
                term[res["env"]] = 1.0 if res["win"] else (0.0 if res["draw"] else -1.0)
            R[t] = term + args.margin_coef * (r * 0.1 - term)
            recent.extend(results)
            if t == STEPS - 1:
                assert done.all(), "games should end after 128 decisions"
            else:
                assert not done.any(), "a game ended early"
        t_roll = time.time() - t0

        # GAE (episodes end exactly at STEPS)
        adv = np.zeros_like(R)
        last = np.zeros(E, np.float32)
        for t in reversed(range(STEPS)):
            nv = V[t + 1] if t + 1 < STEPS else 0.0
            delta = R[t] + args.gamma * nv - V[t]
            last = delta + args.gamma * args.lam * last
            adv[t] = last
        ret = adv + V
        if args.group > 1:
            ep = R.sum(0)  # undiscounted episode return per env
            g = ep.reshape(-1, args.group)
            rel = (g - g.mean(1, keepdims=True)) / (g.std(1, keepdims=True) + 0.05)
            rel = rel.reshape(-1).astype(np.float32)
            gae_n = (adv - adv.mean()) / (adv.std() + 1e-8)
            adv = np.broadcast_to(rel, adv.shape).astype(np.float32) + args.gae_mix * gae_n

        bX = torch.from_numpy(X.reshape((-1,) + X.shape[2:])).to(dev)
        bM = torch.from_numpy(M.reshape(-1, NUM_ACTIONS)).to(dev)
        bA = torch.from_numpy(A.reshape(-1)).to(dev)
        bLP = torch.from_numpy(LP.reshape(-1)).to(dev)
        bADV = torch.from_numpy(adv.reshape(-1)).to(dev)
        bRET = torch.from_numpy(ret.reshape(-1)).to(dev)
        if args.group <= 1:
            bADV = (bADV - bADV.mean()) / (bADV.std() + 1e-8)
        if args.top_adv < 1.0:
            keep = torch.topk(bADV.abs(), int(bADV.numel() * args.top_adv)).indices
            bX, bM, bA, bLP, bADV, bRET = (t_[keep] for t_ in (bX, bM, bA, bLP, bADV, bRET))
        n = bX.shape[0]
        net.train()
        stats = collections.defaultdict(float)
        k = 0
        for _ in range(args.epochs):
            perm = torch.randperm(n, device=dev)
            for i in range(0, n, args.minibatch):
                idx = perm[i:i + args.minibatch]
                logits, v = net(bX[idx], bM[idx])
                dist = torch.distributions.Categorical(logits=logits)
                lp = dist.log_prob(bA[idx])
                ratio = torch.exp(lp - bLP[idx])
                a_ = bADV[idx]
                pg = -torch.min(ratio * a_, ratio.clamp(1 - args.clip, 1 + args.clip) * a_).mean()
                vl = F.mse_loss(v, bRET[idx])
                ent = dist.entropy().mean()
                loss = pg + args.vf * vl - args.ent * ent
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(net.parameters(), 0.5)
                opt.step()
                stats["pg"] += pg.item()
                stats["vl"] += vl.item()
                stats["ent"] += ent.item()
                stats["kl"] += (bLP[idx] - lp).mean().item()
                k += 1
        if ema is not None:
            with torch.no_grad():
                for pe, pn in zip(ema.parameters(), net.parameters()):
                    pe.mul_(args.ema).add_(pn, alpha=1 - args.ema)
        rows = list(recent)
        wr = sum(r["win"] for r in rows) / max(1, len(rows))
        rec = {
            "update": update, "games": update * E,
            "win_recent": round(wr, 4),
            "win_s0": round(np.mean([r["win"] for r in rows if r["seat"] == 0] or [0]), 3),
            "win_s1": round(np.mean([r["win"] for r in rows if r["seat"] == 1] or [0]), 3),
            "margin": round(float(np.mean([r["margin"] for r in rows])), 1),
            **{k2: round(v2 / k, 4) for k2, v2 in stats.items()},
            "t_roll": round(t_roll, 1), "t_total": round(time.time() - t0, 1),
            "elapsed_min": round((time.time() - t_start) / 60, 1),
        }
        print(json.dumps(rec), flush=True)
        log.write(json.dumps(rec) + "\n")
        log.flush()
        ck = {"model": net.state_dict(), "args": vars(args), "update": update, "win_recent": wr}
        torch.save(ck, os.path.join(args.out, "last.pt"))
        if len(rows) >= 1024 and wr > best:
            best = wr
            torch.save(ck, os.path.join(args.out, "best.pt"))
        if update % 50 == 0:
            torch.save(ck, os.path.join(args.out, f"u{update}.pt"))
            if ema is not None:
                torch.save({**ck, "model": ema.state_dict()}, os.path.join(args.out, f"ema_u{update}.pt"))
    env.close()


if __name__ == "__main__":
    main()
