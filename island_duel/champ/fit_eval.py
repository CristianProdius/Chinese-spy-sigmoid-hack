"""Fit the linear evaluation: per-phase-bucket logistic regression of the game
outcome on features (Texel-style tuning). Writes theta (NBK x NF, logit*SCALE).

python fit_eval.py data1.npz [data2.npz ...] --out theta.json [--l2 1.0] [--ha 3 --hb 4]
"""
import argparse
import json

import numpy as np

NF, NBK, SCALE = 17, 6, 100.0


def fit_logistic(X, y, l2, iters=50):
    w = np.zeros(X.shape[1])
    mu, sd = X.mean(0), X.std(0) + 1e-6
    sd[-1], mu[-1] = 1.0, 0.0  # bias column
    Z = (X - mu) / sd
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(Z @ w)))
        g = Z.T @ (p - y) + l2 * np.r_[w[:-1], 0]
        H = (Z * (p * (1 - p))[:, None]).T @ Z + l2 * np.diag(np.r_[np.ones(len(w) - 1), 1e-6])
        w -= np.linalg.solve(H, g)
    # back to raw feature scale
    wr = w / sd
    wr[-1] = w[-1] - np.sum(w[:-1] * mu[:-1] / sd[:-1])
    p = 1 / (1 + np.exp(-(Z @ w)))
    ll = -np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9))
    acc = np.mean((p > 0.5) == (y > 0.5))
    return wr, ll, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--l2", type=float, default=1.0)
    ap.add_argument("--ha", type=float, default=3)
    ap.add_argument("--hb", type=float, default=4)
    ap.add_argument("--split", action="store_true", help="separate fits per (profile, seat)")
    a = ap.parse_args()
    X = np.concatenate([np.load(f)["X"] for f in a.data]).astype(np.float64)
    B = np.concatenate([np.load(f)["B"] for f in a.data])
    Y = np.concatenate([np.load(f)["Y"] for f in a.data]).astype(np.float64)
    if not a.split:
        theta = np.zeros((NBK, NF))
        for b in range(NBK):
            m = B == b
            w, ll, acc = fit_logistic(X[m], Y[m], a.l2)
            theta[b] = w * SCALE
            print(f"bucket {b}: n={m.sum()} logloss={ll:.4f} acc={acc:.3f}")
        json.dump({"theta": theta.ravel().tolist(), "ha": a.ha, "hb": a.hb}, open(a.out, "w"))
        return
    S = np.concatenate([np.load(f)["S"] for f in a.data])
    PF = np.concatenate([np.load(f)["PF"] for f in a.data])
    out = {"ha": a.ha, "hb": a.hb, "split": {}}
    for pf in range(3):
        for st in range(2):
            theta = np.zeros((NBK, NF))
            for b in range(NBK):
                m = (B == b) & (S == st) & (PF == pf)
                w, ll, acc = fit_logistic(X[m], Y[m], a.l2)
                theta[b] = w * SCALE
            print(f"profile {pf} seat {st}: n={((S == st) & (PF == pf)).sum()}")
            out["split"][f"{pf},{st}"] = theta.ravel().tolist()
    json.dump(out, open(a.out, "w"))


if __name__ == "__main__":
    main()
