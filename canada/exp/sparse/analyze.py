"""Diagnostics: doc density, lexicon collisions, pure-lexicon model on dev.

    tools/h100.sh .venv/bin/python exp/sparse/analyze.py
"""
import numpy as np

from common import (CLASSES, Dev, bucket, collision_report, common_buckets, lexicon_W, lexicon_buckets,
                    load_sets, xy)

S = load_sets()
dev = Dev(S["dev"])
for k in ("corpus", "train", "boundary", "dev"):
    X, _, _ = xy(S[k])
    nnz = (X > 0).sum(1)
    print(f"{k:9s} n={len(X):5d} nnz median {np.median(nnz):.0f} p10 {np.percentile(nnz,10):.0f} p90 {np.percentile(nnz,90):.0f}")
nnz = (dev.Xs > 0).sum(1)
print(f"sealed    n={len(dev.Xs):5d} nnz median {np.median(nnz):.0f} p10 {np.percentile(nnz,10):.0f} p90 {np.percentile(nnz,90):.0f}")

own = [r["text"] for k in ("corpus", "train", "boundary", "filler") for r in S[k]]
print("\n== lexicon buckets colliding with frequent features of our text (df>=1%)")
bad = collision_report(own, df_min=0.01, verbose=True)
lb = lexicon_buckets()
print(f"lexicon buckets {len(lb)}, colliding {len(bad)}")

# sealed doc frequency of lexicon buckets, per language
Xs, ls = dev.Xs, dev.lang_s
dfs = {l: (Xs[ls == l] > 0).mean(0) for l in ("en", "fr")}
hi = [(max(dfs['en'][b], dfs['fr'][b]), b) for b in lb]
hi.sort(reverse=True)
print("\n== lexicon buckets most frequent in sealed reports (df en / fr)")
from lexicon import lexicon_features
inv = {}
for f, d in lexicon_features().items():
    inv.setdefault(bucket(f), []).append(f + ":" + "/".join(CLASSES[c][:4] for c in d))
for v, b in hi[:40]:
    print(f"  {b:4d} en {dfs['en'][b]:.3f} fr {dfs['fr'][b]:.3f}  {inv[b]}")

print("\n== pure lexicon models")
for drop_name, drop in (("none", set()), ("own-collide", set(bad)),
                        ("own+common5", set(bad) | set(common_buckets(own, 0.05)))):
    W = lexicon_W(drop_buckets=drop)
    dev.line(f"lex drop={drop_name}", W, np.zeros(9))
