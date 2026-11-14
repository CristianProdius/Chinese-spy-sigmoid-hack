"""Diagnostics: score/margin stats on dev vs sealed, seen-bucket coverage, model agreement on sealed."""
import sys
import numpy as np
from common import OUT, build_train, dev_data, sealed_data, softmax
Xd, yd, ld = dev_data()
Xs, ls = sealed_data()
X, y, lang, w = build_train(alpha=0.0)
seen = (X > 0).any(0)
def cov(A):
    return ((A[:, seen] ** 2).sum(1)).mean()
print(f"buckets seen in gen train {seen.sum()}; nnz/doc train {(X>0).sum(1).mean():.0f} dev {(Xd>0).sum(1).mean():.0f} sealed {(Xs>0).sum(1).mean():.0f}")
print(f"L2 mass in seen buckets: train 1.00 dev {cov(Xd):.3f} sealed {cov(Xs):.3f} (en {cov(Xs[ls=='en']):.3f} fr {cov(Xs[ls=='fr']):.3f})")
print(f"sealed lang: en {(ls=='en').sum()} fr {(ls=='fr').sum()}")
names = sys.argv[1:] or ["base_a0.0_C3.0", "base_a0.3_C1.0", "base_a1.0_C1.0"]
preds = {}
for n in names:
    z = np.load(OUT / f"{n}.npz") if not n.endswith(".npz") else np.load(n)
    W, b = z["W"], z["b"]
    for tag, A in (("dev", Xd), ("sealed", Xs)):
        S = A @ W.T + b
        P = softmax(S)
        part = np.sort(S, 1)
        mg = part[:, -1] - part[:, -2]
        print(f"{n:22s} {tag:6s} margin med {np.median(mg):.2f} q25 {np.quantile(mg,.25):.2f} q75 {np.quantile(mg,.75):.2f}  maxP mean {P.max(1).mean():.3f}  |S| {np.abs(S - S.mean(1, keepdims=True)).mean():.2f}")
    preds[n] = (Xs @ W.T + b).argmax(1)
ks = list(preds)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        print(f"agree {ks[i]} vs {ks[j]}: {(preds[ks[i]] == preds[ks[j]]).mean():.3f}")
