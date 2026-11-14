"""Average several linear models into one (still a single W, b). Each member is scaled so its logits
have unit spread on our own training text before averaging.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python ens.py OUTNAME member1 member2 ..."
"""
import sys

import numpy as np

from common import HERE, augment, l2norm, featurize_raw, load_sets

out, members = sys.argv[1], sys.argv[2:]
S = load_sets()
Xt = l2norm(featurize_raw([r["text"] for r in S["train"] + S["boundary"]]))
Ws, bs = [], []
for m in members:
    z = np.load(HERE / "models" / f"{m}.npz")
    W, b = z["W"], z["b"]
    L = Xt @ W.T + b
    s = (L - L.mean(1, keepdims=True)).std()
    Ws.append(W / s)
    bs.append(b / s)
W, b = np.mean(Ws, 0), np.mean(bs, 0)
np.savez(HERE / "models" / f"{out}.npz", W=W, b=b)
print("saved", out, "from", members)
