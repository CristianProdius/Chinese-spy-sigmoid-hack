"""Which buckets fire far more often in the sealed reports than in our realistic generated text?"""
import numpy as np
from common import OUT, jl, featurize, sealed_data, dev_data, CLASSES
from lib import bucket, tokens
Xs, ls = sealed_data()
gen = jl("train_*.jsonl") + jl("boundary_*.jsonl")
Xg = featurize([d["text"] for d in gen])
Xd, yd, ld = dev_data()
dfg = (Xg > 0).mean(0); dfs = (Xs > 0).mean(0); dfd = (Xd > 0).mean(0)
eps = 1.0 / len(Xg)
r = (dfs + eps) / (dfg + eps)
rd = (dfd + eps) / (dfg + eps)
for name, rr in (("sealed/gen", r), ("dev/gen", rd)):
    print(name, "ratio quantiles", np.round(np.quantile(rr, [.5, .9, .95, .99, .999]), 2), "n>3", (rr > 3).sum(), "n>10", (rr > 10).sum())
# term names for top buckets from our own vocab (gen + filler + corpus)
vocab = {}
for d in gen + jl("filler_*.jsonl") + jl("dev_*.jsonl"):
    t = tokens(d["text"])
    for x in t + [a + " " + b for a, b in zip(t, t[1:])]:
        vocab.setdefault(bucket(x), {}).setdefault(x, 0)
        vocab[bucket(x)][x] += 1
z = np.load(OUT / "base_a0.3_C1.0.npz"); W = z["W"]
top = np.argsort(-dfs * np.log(r))[:40]
for j in top:
    names = sorted(vocab.get(j, {}).items(), key=lambda kv: -kv[1])[:3]
    print(f"{j:5d} df sealed {dfs[j]:.3f} gen {dfg[j]:.3f} dev {dfd[j]:.3f}  W argmax {CLASSES[W[:,j].argmax()]:10s} {W[:,j].max():+.2f}  {names}")
