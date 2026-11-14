"""Which buckets does the sealed-excess mask drop, and what do they hold in our text?

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python diag_mask.py"
"""
import collections

import numpy as np

from common import CLASSES, DIM, Dev, augment, bucket, feature_strings, load_sets, xy
from lexicon import lexicon_features

S = load_sets()
dev = Dev(S["dev"])
rows = augment(S["train"] + S["boundary"], S["filler"], n_copies=2)
X, y, lang = xy(rows)
Xs, ls = dev.Xs, dev.lang_s
for name, M in (("ours", X), ("sealed", Xs)):
    nnz = (M > 0).sum(1)
    print(f"{name}: nnz median {np.median(nnz):.0f} p10 {np.percentile(nnz,10):.0f} p90 {np.percentile(nnz,90):.0f}")
print("sealed lang counts", collections.Counter(ls.tolist()))

ds = {l: (Xs[ls == l] > 0).mean(0) for l in ("en", "fr")}
do = {l: (X[lang == l] > 0).mean(0) for l in ("en", "fr")}
ex = np.maximum(ds["en"] - do["en"], ds["fr"] - do["fr"])
lex = lexicon_features()
inv = collections.defaultdict(list)
for f, d in lex.items():
    inv[bucket(f)].append(f + ":" + "/".join(CLASSES[c][:4] for c in d))
ours = collections.defaultdict(collections.Counter)
for r in rows[: len(S["train"]) + len(S["boundary"])]:
    for f in set(feature_strings(r["text"])):
        ours[bucket(f)][f] += 1
order = np.argsort(-ex)
print(f"buckets with excess >= 0.05: {(ex >= 0.05).sum()}, >= 0.1: {(ex >= 0.1).sum()}, >= 0.2: {(ex >= 0.2).sum()}")
print("bucket  sealed en/fr   ours en/fr   lexicon | our features there")
for b in order[:70]:
    top = ", ".join(f"{f}({c})" for f, c in ours[b].most_common(3))
    print(f"{b:5d}  {ds['en'][b]:.2f}/{ds['fr'][b]:.2f}   {do['en'][b]:.2f}/{do['fr'][b]:.2f}   {inv.get(b, '')} | {top}")
