"""Self-training on the UNLABELLED sealed fingerprints, on top of the df-shift feature scaling (fs.py).
Committee variant: pseudo-labels only where several differently trained models agree.

    tools/h100.sh python3 -W ignore exp/transductive/st2.py <exp-name>
"""
import sys
import time

import numpy as np

from common import OUT, build_train, df_scale, report, save_model, sealed_data, train_scaled
from st import margins

LOG = open(OUT / "st2_log.txt", "a")


def select_committee(Ss, ls, q, mode="bal"):
    """Ss: list of sealed score matrices. Keep reports where every model has the same argmax; rank by the
    smallest margin across models. 'bal': per class, the same count from EN and FR."""
    preds = np.stack([S.argmax(1) for S in Ss])
    agree = (preds == preds[0]).all(0)
    mg = np.min(np.stack([margins(S) for S in Ss]), 0)
    mg = np.where(agree, mg, -np.inf)
    pred = preds[0]
    idx = []
    for c in range(9):
        groups = {l: np.flatnonzero((pred == c) & (ls == l) & agree) for l in ("en", "fr")}
        nall = {l: ((pred == c) & (ls == l)).sum() for l in ("en", "fr")}
        if mode == "bal":
            k = int(round(q * min(nall.values())))
        for l, g in groups.items():
            kk = int(round(q * nall[l])) if mode == "frac" else k
            idx.extend(g[np.argsort(-mg[g])[:min(kk, len(g))]])
    idx = np.array(idx, dtype=int)
    return idx, pred[idx]


def anchor_bias(S, target, iters=100):
    """Bias shift d so that the mean softmax of S + d on the sealed set equals `target` (keeps the class
    mix from drifting during self-training)."""
    from common import softmax
    d = np.zeros(S.shape[1])
    for _ in range(iters):
        d += np.log(target / softmax(S + d).mean(0))
    return d - d.mean()


def run(name, members, qs=(0.3, 0.5, 0.7, 0.85), beta=0.3, mode="bal", save_rounds=(), anchor=False):
    """members: list of (alpha, C, gamma). Each member is retrained every round on its own train data +
    the shared committee pseudo-labels. The saved model is the average of the members (still linear)."""
    Xs, ls = sealed_data()
    data, models = [], []
    for alpha, C, gamma in members:
        X, y, lang, w = build_train(alpha=alpha)
        s = df_scale(gamma, "up") if gamma > 0 else np.ones(X.shape[1])
        data.append((X, y, w, C, s))
        models.append(train_scaled(X, y, w, C, s))
    Wm, bm = np.mean([m[0] for m in models], 0), np.mean([m[1] for m in models], 0)
    report(f"{name} r- avg", Wm, bm, LOG)
    from common import softmax
    target = softmax(Xs @ Wm.T + bm).mean(0)
    for r, q in enumerate(qs):
        Ss = [Xs @ W.T + b for W, b in models]
        idx, pl = select_committee(Ss, ls, q, mode)
        new = []
        for X, y, w, C, s in data:
            wp = np.full(len(idx), beta * w.sum() / max(len(idx), 1))
            new.append(train_scaled(np.vstack([X, Xs[idx]]), np.concatenate([y, pl]), np.concatenate([w, wp]), C, s))
        if anchor:
            new = [(W, b + anchor_bias(Xs @ W.T + b, target)) for W, b in new]
        models = new
        Wm, bm = np.mean([m[0] for m in models], 0), np.mean([m[1] for m in models], 0)
        report(f"{name} r{r} q={q} n={len(idx)} avg", Wm, bm, LOG)
        if r in save_rounds:
            save_model(OUT / f"{name}_r{r}.npz", Wm, bm)
    return Wm, bm


if __name__ == "__main__":
    what = sys.argv[1]
    LOG.write(f"--- st2 {what} {time.ctime()}\n")
    if what == "single":
        for g in (0.0, 1.0):
            for beta in (0.3, 1.0):
                run(f"st2single_a0.3_C3_g{g}_b{beta}", [(0.3, 3.0, g)], beta=beta, save_rounds=(1, 2, 3))
    elif what == "anchor":
        mem = [(0.0, 3.0, 1.0), (0.3, 3.0, 1.0), (1.0, 3.0, 0.5), (0.1, 1.0, 0.0)]
        run("st2anch_comm_b0.3", mem, beta=0.3, save_rounds=(1, 3), anchor=True)
        run("st2anch_single_g0_b0.3", [(0.3, 3.0, 0.0)], beta=0.3, save_rounds=(3,), anchor=True)
        run("st2comm_long_b0.3", mem, qs=(0.3, 0.5, 0.7, 0.85, 0.95, 0.95), beta=0.3, save_rounds=(5,))
    elif what == "committee":
        mem = [(0.0, 3.0, 1.0), (0.3, 3.0, 1.0), (1.0, 3.0, 0.5), (0.1, 1.0, 0.0)]
        for beta in (0.3, 1.0):
            run(f"st2comm_b{beta}", mem, beta=beta, save_rounds=(0, 1, 2, 3))
