"""Unlabelled comparison of models on the sealed fingerprints: class mix, en/fr gap, pairwise agreement.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python compare.py model1 model2 ..."   (names in models/)
"""
import sys

import numpy as np

from common import CLASSES, HERE, fp_lang, load_sealed

Xs = load_sealed()
ls = fp_lang(Xs)
names = sys.argv[1:]
P = {}
for n in names:
    p = HERE / "models" / f"{n}.npz"
    if not p.exists():
        p = HERE.parents[1] / n
    z = np.load(p)
    S = Xs @ z["W"].T + z["b"]
    P[n] = S.argmax(1)
print("model".ljust(40) + " ".join(c[:5].rjust(6) for c in CLASSES))
for n in names:
    mix = np.bincount(P[n], minlength=9) / len(Xs)
    print(n[:40].ljust(40) + " ".join(f"{v:6.3f}" for v in mix))
print("\npairwise agreement on sealed")
for i, a in enumerate(names):
    print(a[:40].ljust(40) + " ".join(f"{(P[a] == P[b]).mean():.2f}" for b in names))
votes = np.stack([P[n] for n in names])
maj = np.array([np.bincount(v, minlength=9).argmax() for v in votes.T])
print("\nagreement with majority:", " ".join(f"{(P[n] == maj).mean():.3f}" for n in names))
print("all agree on", (votes == votes[0]).all(0).mean().round(3))
