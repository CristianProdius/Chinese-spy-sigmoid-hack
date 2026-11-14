"""Transductive feature-shift correction: shrink buckets whose document frequency differs between the
unlabelled sealed fingerprints and our generated text, then (optionally) self-train.

    tools/h100.sh python3 -W ignore exp/transductive/fs.py
"""
import time
import numpy as np
from common import OUT, build_train, df_scale, report, save_model, train_scaled

LOG = open(OUT / "fs_log.txt", "a")
LOG.write(f"--- fs.py {time.ctime()}\n")
for alpha in (0.0, 0.3):
    X, y, lang, w = build_train(alpha=alpha)
    for mode in ("up", "sym"):
        for gamma in (0.5, 1.0, 2.0):
            s = df_scale(gamma, mode)
            for C in (1.0, 3.0, 10.0):
                W, b = train_scaled(X, y, w, C, s)
                report(f"fs a={alpha} {mode} g={gamma} C={C}", W, b, LOG)
                save_model(OUT / f"fs_a{alpha}_{mode}_g{gamma}_C{C}.npz", W, b)
