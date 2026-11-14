"""Train one or more named configs, save exp/data/<name>.npz, print dev confusion + sealed mix.

    tools/h100.sh .venv/bin/python exp/data/train.py d_gen_filler d_mix ...
"""
import json
import sys
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from lib import CLASSES, save_model  # noqa: E402

BASE = dict(alpha=0.25, n_filler=(0, 3), noise=0.0, drop=0.25, gen_copies=4, corpus_seeds=(0, 1), mix=0.0, C=3.0, seed=0)
CONFIGS = {
    "d_gen_filler": dict(alpha=0.0, C=10.0),
    "d_a25": dict(),
    "d_a25_C1": dict(C=1.0),
    "d_a50": dict(alpha=0.5),
    "d_a25_mix": dict(mix=1.0),
    "d_a25_c8": dict(gen_copies=8),
}


def cfg_of(name):
    c = dict(BASE)
    c.update(CONFIGS[name])
    return c


def train(name):
    c = cfg_of(name)
    texts, y, lang, w = common.build_set(c, seed=c["seed"])
    X = common.to_sparse(texts)
    W, b = common.fit(X, y, w, c["C"])
    save_model(HERE / f"{name}.npz", W, b)
    r = common.score(W, b)
    Xd, yd, ld, Xs, ls = common.dev_xy()
    pred = (Xd @ W.T + b).argmax(1)
    conf = np.zeros((9, 9), int)
    for a, p in zip(yd, pred):
        conf[a, p] += 1
    return name, c, r, conf


def main():
    names = sys.argv[1:] or list(CONFIGS)
    common.dev_xy()
    out = Parallel(n_jobs=min(len(names), 6))(delayed(train)(n) for n in names)
    for name, c, r, conf in out:
        print(f"== {name} {json.dumps({k: list(v) if isinstance(v, tuple) else v for k, v in c.items()})}")
        print(f"  dev acc {r['acc']:.3f} (en {r['acc_en']:.3f}, fr {r['acc_fr']:.3f}) tv {r['tv']:.3f} shares {r['shares']}")
        print("  sealed en " + " ".join(f"{v:.2f}" for v in r["sealed_mix_en"]) + " | fr " + " ".join(f"{v:.2f}" for v in r["sealed_mix_fr"]))
        print("  confusion (rows true, cols pred): " + " ".join(c_[:4] for c_ in CLASSES))
        for i, row in enumerate(conf):
            print(f"   {CLASSES[i][:6]:6s} " + " ".join(f"{v:4d}" for v in row))


if __name__ == "__main__":
    main()
