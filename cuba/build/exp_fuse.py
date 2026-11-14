"""Fusion / PCA experiments on a built submission (uses its real Retriever legs).

    python build/exp_fuse.py work/sub_fused [split ...]
Caches per-query window scores in work/cache_<split>.npz.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402

sub = sys.argv[1]
splits = sys.argv[2:] or ["sample"]
spec = importlib.util.spec_from_file_location("subm", os.path.join(sub, "main.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
R = m.Retriever(os.path.join(sub, "index"))
V = R.vectors / (np.linalg.norm(R.vectors, axis=1, keepdims=True) + 1e-9)
pos = {d: i for i, d in enumerate(R.doc_ids)}


def z(x):
    return (x - x.mean()) / (x.std() + 1e-9)


def hit3(doc_scores, gold):
    top = np.argpartition(-doc_scores, 3)[:3]
    return gold in top


for split in splits:
    qs = lab.questions(split)[:1000]
    gold = np.array([pos[q["doc_id"]] for q in qs])
    Q = np.stack([R.embed(q["question"]) for q in qs])
    LEX = [np.maximum.reduceat(R.lexical(q["question"]), R.doc_start) for q in qs]
    print(f"\n== {split} (n={len(qs)})")
    # PCA variants of the passage matrix (fit on passages), queries projected the same way
    mu = V.mean(0)
    U, S, Wt = np.linalg.svd(V[::4] - mu, full_matrices=False)
    for dims in (768, 512, 384, 256):
        if dims == 768:
            Vd, Qd = V, Q
        else:
            P = Wt[:dims].T
            Vd = (V - mu) @ P
            Qd = (Q - mu) @ P
            Vd /= np.linalg.norm(Vd, axis=1, keepdims=True)
            Qd /= np.linalg.norm(Qd, axis=1, keepdims=True)
        # int8 quantisation as shipped
        Vq = np.clip(np.rint(Vd / np.abs(Vd).max() * 127), -127, 127).astype(np.float32)
        DEN = [np.maximum.reduceat(Vq @ Qd[i], R.doc_start) for i in range(len(qs))]
        row = []
        for w in (0.0, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 100.0):
            h = np.mean([hit3(z(LEX[i]) + w * z(DEN[i]), gold[i]) for i in range(len(qs))])
            row.append(f"w{w:g}:{h:.3f}")
        print(f"dims {dims:4d}  " + "  ".join(row), flush=True)
