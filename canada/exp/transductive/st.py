"""Transductive adaptation on the UNLABELLED sealed fingerprints (no labels, no text, nothing by hand).

1. base LR on recombined corpus (weight alpha) + generated train/boundary with filler noise
2. EM re-estimation of the sealed class priors (Saerens et al. 2002) -> bias shift log(pi/uniform)
3. self-training: pseudo-label the surest sealed reports (language-balanced), retrain, a few rounds

    tools/h100.sh python3 -W ignore exp/transductive/st.py grid      # base grid + EM + self-training grid
"""
import json
import sys
import time

import numpy as np

from common import OUT, build_train, em_priors, report, save_model, sealed_data, softmax, train_lr

LOG = open(OUT / "st_log.txt", "a")


def log(msg):
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def margins(S):
    part = np.sort(S, 1)
    return part[:, -1] - part[:, -2]


def select(S, ls, q, mode):
    """Pick pseudo-labels among sealed reports. Returns (idx, labels).
    mode 'global': surest q of all by margin. 'frac': surest q of every (pred class, language) group.
    'bal': per class, the same count k_c from EN and FR (k_c = q * min(n_c_en, n_c_fr)) -> the pseudo-label
    class mix is identical in both languages."""
    pred, mg = S.argmax(1), margins(S)
    if mode == "global":
        idx = np.argsort(-mg)[: int(q * len(S))]
        return idx, pred[idx]
    idx = []
    for c in range(9):
        groups = {l: np.flatnonzero((pred == c) & (ls == l)) for l in ("en", "fr")}
        if mode == "bal":
            k = int(round(q * min(len(g) for g in groups.values())))
        for l, g in groups.items():
            kk = int(round(q * len(g))) if mode == "frac" else k
            idx.extend(g[np.argsort(-mg[g])[:kk]])
    idx = np.array(idx, dtype=int)
    return idx, pred[idx]


def self_train(X, y, w, C, Xs, ls, W, b, qs, mode, beta, em=False, name="", save=None):
    """Retrain from scratch each round on train + pseudo-labelled sealed. beta = total pseudo weight
    relative to total train weight."""
    res = None
    for r, q in enumerate(qs):
        S = Xs @ W.T + b
        if em:
            pi = em_priors(S)
            S = S + np.log(pi * 9)
        idx, pl = select(S, ls, q, mode)
        wp = np.full(len(idx), beta * w.sum() / max(len(idx), 1))
        W, b = train_lr(np.vstack([X, Xs[idx]]), np.concatenate([y, pl]), np.concatenate([w, wp]), C=C)
        res = report(f"{name} r{r} q={q} n={len(idx)}", W, b, LOG)
    if save:
        save_model(OUT / save, W, b)
    return W, b, res


def em_step(W, b, Xs, name, T=1.0):
    S = Xs @ W.T + b
    pi = em_priors(S / T)
    b2 = b + T * np.log(pi * 9)
    log(f"   EM(T={T}) priors " + " ".join(f"{p:.3f}" for p in pi))
    return b2, report(f"{name} +EM T={T}", W, b2, LOG)


def grid():
    Xs, ls = sealed_data()
    log(f"--- st.py grid {time.ctime()}")
    data = {}
    for alpha in (0.0, 0.1, 0.3, 1.0):
        data[alpha] = build_train(alpha=alpha)
        X, y, lang, w = data[alpha]
        for C in (0.3, 1.0, 3.0, 10.0):
            W, b = train_lr(X, y, w, C=C)
            report(f"base a={alpha} C={C}", W, b, LOG)
            save_model(OUT / f"base_a{alpha}_C{C}.npz", W, b)
    return data


def st_grid(alpha=0.0, C=1.0):
    Xs, ls = sealed_data()
    X, y, lang, w = build_train(alpha=alpha)
    W0, b0 = train_lr(X, y, w, C=C)
    nm = f"a={alpha} C={C}"
    log(f"--- st_grid {nm} {time.ctime()}")
    report(f"base {nm}", W0, b0, LOG)
    for T in (1.0, 2.0):
        em_step(W0, b0, Xs, f"base {nm}", T)
    for mode in ("bal", "frac", "global"):
        for beta in (0.3, 1.0):
            for em in (False, True):
                self_train(X, y, w, C, Xs, ls, W0, b0, (0.3, 0.5, 0.7, 0.85), mode, beta, em,
                           name=f"st {nm} {mode} beta={beta} em={int(em)}")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "grid"
    if what == "grid":
        grid()
    elif what == "st":
        st_grid(float(sys.argv[2]), float(sys.argv[3]))
