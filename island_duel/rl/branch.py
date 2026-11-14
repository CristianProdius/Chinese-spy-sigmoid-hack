"""Counterfactual policy improvement against the deterministic champion.

The engine is deterministic for a given (arena, seed) and sequence of our
actions. Each group of G envs shares one map and plays the current greedy
(argmax) policy, so all of them reach the same state at a random branch step
t. There env j plays the j-th best action by the policy, then all continue
greedily to the end. The difference in final return isolates the value of
that one decision on that map:

    A_j = R_j - mean(R)   (R = +-1 for win/loss + margin / 100)

and the policy is trained with -sum_j A_j * log pi(b_j | s_t) plus a KL anchor
to the starting policy. The j=0 env of each group plays the plain greedy
policy, so its win rate is a free running evaluation.

python branch.py --init runs/ppo_bc1_final.pt --envs 256 --group 4 --out runs/branch1
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import os
import random
import time

import numpy as np
import torch

from features import NUM_ACTIONS
from model import Net
from vecenv_mp import MPVecEnv

STEPS = 128


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default=os.path.expanduser("~/island-duel/samoa-wrapped"))
    ap.add_argument("--envs", type=int, default=256)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--group", type=int, default=4)
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--kl", type=float, default=0.5, help="KL(anchor || pi) weight")
    ap.add_argument("--tau", type=float, default=0.3, help="temperature of the return softmax")
    ap.add_argument("--buffer", type=int, default=4096, help="branch states kept for training")
    ap.add_argument("--steps-per-iter", type=int, default=8, help="gradient steps per iteration")
    ap.add_argument("--batch", type=int, default=512)
    ap.add_argument("--late-bias", type=float, default=0.0, help=">0 favours later branch steps")
    ap.add_argument("--init", required=True)
    ap.add_argument("--out", default="runs/branch")
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)
    dev = torch.device("cuda")
    ck = torch.load(args.init, map_location=dev)
    a = ck.get("args", {})
    net = Net(a.get("ch", 96), a.get("blocks", 8)).to(dev)
    net.load_state_dict(ck["model"])
    anchor = copy.deepcopy(net).eval()
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    env = MPVecEnv(args.envs, args.engine, workers=args.workers, seed=args.seed)
    E, G = args.envs, args.group
    ngroups = E // G
    buf = collections.deque(maxlen=args.buffer)  # (x, mask, actions[G], adv[G], valid[G])
    base_hist = collections.deque(maxlen=1024)
    log = open(os.path.join(args.out, "log.jsonl"), "a")
    best = -1.0
    t_start = time.time()
    for it in range(1, args.iters + 1):
        t0 = time.time()
        tasks, tsteps = [], []
        for _ in range(ngroups):
            task = (rng.randrange(32), rng.getrandbits(32))
            tasks += [task] * G
            u = rng.random()
            t = int(STEPS * (u ** (1.0 / (1.0 + args.late_bias))))
            tsteps.append(min(STEPS - 1, t))
        x, m = env.reset_all(tasks)
        branch_x = [None] * ngroups
        branch_m = [None] * ngroups
        branch_a = [None] * ngroups
        net.eval()
        for k in range(STEPS):
            with torch.no_grad():
                logits, _ = net(torch.from_numpy(x).to(dev), torch.from_numpy(m).to(dev))
            act = logits.argmax(1).cpu().numpy()
            lg = logits.cpu().numpy()
            for g in range(ngroups):
                if tsteps[g] != k:
                    continue
                i0 = g * G
                order = np.argsort(-lg[i0])
                cands = [int(c) for c in order[:G] if m[i0][c]]
                valid = [True] * len(cands) + [False] * (G - len(cands))
                cands += [cands[0]] * (G - len(cands))
                for j in range(G):
                    act[i0 + j] = cands[j]
                branch_x[g], branch_m[g] = x[i0].copy(), m[i0].copy()
                branch_a[g] = (cands, valid)
            x, m, r, done, results = env.step(act)
        # final returns: the env's results arrive in order of completion; recompute from scores
        finals = env_results(results, E)
        for g in range(ngroups):
            R = np.array([finals[g * G + j] for j in range(G)], np.float32)
            cands, valid = branch_a[g]
            v = np.array(valid)
            mean = R[v].mean()
            adv = np.where(v, R - mean, -50.0).astype(np.float32)
            base_hist.append(R[0] > 0)
            if v.sum() > 1 and np.ptp(R[v]) > 1e-6:
                buf.append((branch_x[g], branch_m[g], np.array(cands), adv))
        t_roll = time.time() - t0

        # train
        net.train()
        stats = collections.defaultdict(float)
        n_steps = 0
        if len(buf) >= args.batch:
            for _ in range(args.steps_per_iter):
                idx = rng.sample(range(len(buf)), args.batch)
                bx = torch.from_numpy(np.stack([buf[i][0] for i in idx])).to(dev)
                bm = torch.from_numpy(np.stack([buf[i][1] for i in idx])).to(dev)
                ba = torch.from_numpy(np.stack([buf[i][2] for i in idx])).to(dev)
                badv = torch.from_numpy(np.stack([buf[i][3] for i in idx])).to(dev)
                logits, _ = net(bx, bm)
                logp = torch.log_softmax(logits, 1)
                # bounded listwise target: softmax of candidate returns vs. the
                # policy renormalised over the same candidates
                q = torch.softmax(badv / args.tau, 1)
                cand_logp = torch.log_softmax(logits.gather(1, ba), 1)
                pg = -(q * cand_logp).sum(1).mean()
                with torch.no_grad():
                    al, _ = anchor(bx, bm)
                    ap_ = torch.softmax(al, 1)
                kl = (ap_ * (torch.log(ap_ + 1e-9) - logp)).sum(1).mean()
                loss = pg + args.kl * kl
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(net.parameters(), 0.5)
                opt.step()
                stats["pg"] += pg.item()
                stats["kl"] += kl.item()
                n_steps += 1
        rec = {
            "iter": it, "greedy_win": round(float(np.mean(base_hist)), 4), "n_greedy": len(base_hist),
            "buffer": len(buf), **{k: round(v / max(1, n_steps), 4) for k, v in stats.items()},
            "t_roll": round(t_roll, 1), "elapsed_min": round((time.time() - t_start) / 60, 1),
        }
        print(json.dumps(rec), flush=True)
        log.write(json.dumps(rec) + "\n")
        log.flush()
        ck_out = {"model": net.state_dict(), "args": {"ch": a.get("ch", 96), "blocks": a.get("blocks", 8)},
                  "iter": it}
        torch.save(ck_out, os.path.join(args.out, "last.pt"))
        if it % 25 == 0:
            torch.save(ck_out, os.path.join(args.out, f"i{it}.pt"))
    env.close()


def env_results(results, E):
    """Map per-env final results (from VecEnv.step at done) to returns by env index."""
    out = {}
    for r in results:
        out[r["env"]] = (1.0 if r["win"] else -1.0 if not r["draw"] else 0.0) + r["margin"] / 100.0
    return [out[i] for i in range(E)]


if __name__ == "__main__":
    main()
