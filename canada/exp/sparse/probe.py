"""Convention probe: the v4 recipe trained with the NAIVE conventions the context warns against
(ice storm / freezing rain -> storm, avalanche -> winter, tsunami -> flood). Used only to see whether a
vault word follows the stated conventions or a naive-convention labelling. Not a candidate model.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python probe.py"
"""
import re

import numpy as np

import train as T
from common import CLASSES, balanced_weights, featurize_raw, l2norm, sealed_noise

RULES = [("winter", r"ice storm|ice-storm|freezing rain|freezing drizzle|verglas|pluie verglaçante|glaze", "storm"),
         ("ground", r"avalanche", "winter"),
         ("ground", r"tsunami|raz-de-marée|raz de marée|tidal wave", "flood")]


def flip(rows):
    out, n = [], 0
    for r in rows:
        lab = r["label"]
        for src, pat, dst in RULES:
            if lab == src and re.search(pat, r["text"], re.I):
                lab = dst
                break
        n += lab != r["label"]
        out.append(dict(r, label=lab))
    return out, n


def recipe(rows, groups, share=0.2, lex_share=0.1, thr=0.02, C=3.0):
    nb = len(rows)
    p = T.lexicon_pseudo(n_per=60, seed=2)
    rows = rows + p
    groups = np.concatenate([groups, np.array(["lex"] * len(p))])
    U = featurize_raw([r["text"] for r in rows])
    y = np.array([CLASSES.index(r["label"]) for r in rows])
    lang = np.array([r["lang"] for r in rows])
    X0 = l2norm(U)
    ex = {l: np.clip((T.dev.Xs[T.dev.lang_s == l] > 0).mean(0) - (X0[:nb][lang[:nb] == l] > 0).mean(0), 0, None)
          for l in ("en", "fr")}
    cs = (T.sealed_excess_cls(X0[:nb], y[:nb], lang[:nb]) < thr).astype(float)
    Xn, idx = sealed_noise(U, lang, ex, copies=2, scale=1.0, seed=7)
    w = balanced_weights(y[idx], lang[idx], groups[idx], {"gen": 1 - share - lex_share, "corpus": share, "lex": lex_share})
    return T.fit(Xn, y[idx], w, C, col_scale=cs)


rows, groups = T.build_rows("recomb", n_aug=1)
frows, n = flip(rows)
print(f"flipped {n} of {len(rows)} training rows")
W, b = recipe(frows, groups)
T.run("probe_naive_conventions", W, b)
z = np.load(T.OUT / "v4_full_c0.2_lex0.1_cls0.02_C3.0.npz")
p0 = (T.dev.Xs @ z["W"].T + z["b"]).argmax(1)
p1 = (T.dev.Xs @ W.T + b).argmax(1)
print(f"sealed predictions changed vs v4_full_c0.2: {(p0 != p1).mean():.3f}")
for a in range(9):
    for c in range(9):
        k = ((p0 == a) & (p1 == c)).sum()
        if a != c and k >= 5:
            print(f"  {CLASSES[a]} -> {CLASSES[c]}: {k}")
