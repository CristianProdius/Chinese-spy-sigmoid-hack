"""Base models for the transductive strategy: recombined corpus + generated train/boundary, filler noise.

    tools/h100.sh .venv/bin/python exp/transductive/base.py
"""
import sys
import time

import numpy as np

from common import OUT, build_train, report, save_model, train_lr

log = open(OUT / "base_log.txt", "a")
log.write(f"--- base.py {time.ctime()} {sys.argv[1:]}\n")
z = np.load(OUT.parents[0] / "inline/recomb_C0.3.npz")
report("ref recomb_C0.3", z["W"], z["b"], log)
alphas = [float(a) for a in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["0", "0.3", "1"])]
Cs = [float(c) for c in (sys.argv[2].split(",") if len(sys.argv) > 2 else ["0.3", "1", "3", "10"])]
for alpha in alphas:
    X, y, lang, w = build_train(alpha=alpha)
    for C in Cs:
        t = time.time()
        W, b = train_lr(X, y, w, C=C)
        report(f"base a={alpha} C={C} ({time.time()-t:.0f}s)", W, b, log)
        save_model(OUT / f"base_a{alpha}_C{C}.npz", W, b)
