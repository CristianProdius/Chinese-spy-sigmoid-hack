"""Dev accuracy under real-text hash noise: each dev report gets extra buckets switched on with the
probability that real (sealed) reports of its language fire them beyond our training text (sealed df
minus train df, per language). A stress test for collisions; dev labels are never trained on.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python evalnoisy.py [glob or names...]"
"""
import sys

import numpy as np

from common import CLASSES, HERE, Dev, augment, featurize_raw, l2norm, load_sets, sealed_noise
from eval_model import evaluate

S = load_sets()
dev = Dev(S["dev"])
train = augment(S["train"] + S["boundary"], S["filler"], n_copies=1)
Ut = featurize_raw([r["text"] for r in train])
lt = np.array([r["lang"] for r in train])
Xt = l2norm(Ut)
ex = {l: np.clip((dev.Xs[dev.lang_s == l] > 0).mean(0) - (Xt[lt == l] > 0).mean(0), 0, None) for l in ("en", "fr")}
Ud = featurize_raw([r["text"] for r in S["dev"]])
noisy = []
for seed in range(3):
    Xn, idx = sealed_noise(Ud, dev.lang, ex, copies=1, scale=1.0, seed=100 + seed)
    noisy.append(Xn[len(Ud):])

args = sys.argv[1:] or ["*"]
paths = []
for a in args:
    p = HERE / "models" / f"{a}.npz"
    paths += [p] if p.exists() else sorted((HERE / "models").glob(a if a.endswith(".npz") else a + ".npz"))
rows = []
for p in paths:
    z = np.load(p)
    W, b = z["W"], z["b"]
    r = dev.score(W, b)
    nacc = [evaluate(W, b, Xn, dev.y, dev.lang) for Xn in noisy]
    na = np.mean([q["acc"] for q in nacc])
    nsh = np.mean([max(q["shares"].values()) for q in nacc])
    rows.append((na, r["acc"], nsh, r["tv"], p.stem))
    print(f"{p.stem:44s} dev {r['acc']:.3f} noisy {na:.3f} noisy-share {nsh:+.3f} tv {r['tv']:.3f}", flush=True)
print("\n== by noisy dev acc")
for na, a, sh, tv, n in sorted(rows, reverse=True)[:30]:
    print(f"  noisy {na:.3f} dev {a:.3f} share {sh:+.3f} tv {tv:.3f} {n}")
