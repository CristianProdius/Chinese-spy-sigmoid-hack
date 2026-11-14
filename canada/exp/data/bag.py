"""Seed bagging: train K models of one config with different augmentation / recombination seeds and
average their W and b (averaging logits of linear models = one linear model).

    tools/h100.sh .venv/bin/python exp/data/bag.py <name> <K> <jobs> [key=value ...]
e.g. bag.py bag_a25 8 4 alpha=0.25 C=3.0
Saves exp/data/<name>.npz (the average) and exp/data/bags/<name>_s<k>.npz (members).
"""
import ast
import json
import sys
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from lib import load_sealed, save_model  # noqa: E402

BASE = dict(alpha=0.25, n_filler=(0, 3), noise=0.0, drop=0.25, gen_copies=4, mix=0.0, boundary_rep=1, C=3.0)
# member k of a bag uses VARIANTS[k % len(VARIANTS)] on top of the config (pass variants=div to use it)
VARIANTS = {
    "none": [{}],
    "div": [
        dict(alpha=0.25, boundary_rep=1, mix=0.0),
        dict(alpha=0.5, boundary_rep=3, mix=0.5),
        dict(alpha=0.25, boundary_rep=3, mix=0.5, n_filler=(1, 4), drop=0.4),
        dict(alpha=0.5, boundary_rep=1, mix=0.0, n_filler=(1, 4), drop=0.4),
    ],
}


def member(name, cfg, k):
    c = dict(cfg)
    var = VARIANTS[cfg.get("variants", "none")]
    c.update(var[k % len(var)])
    c["corpus_seeds"] = (100 + 2 * k, 101 + 2 * k)
    texts, y, lang, w = common.build_set(c, seed=1000 + k)
    X = common.to_sparse(texts)
    W, b = common.fit(X, y, w, c["C"])
    (HERE / "bags").mkdir(exist_ok=True)
    save_model(HERE / "bags" / f"{name}_s{k}.npz", W, b)
    return W, b


def main():
    name, K, jobs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    cfg = dict(BASE)
    for kv in sys.argv[4:]:
        k, v = kv.split("=", 1)
        try:
            cfg[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            cfg[k] = v
    common.dev_xy()
    res = Parallel(n_jobs=jobs)(delayed(member)(name, cfg, k) for k in range(K))
    Xs = load_sealed()
    preds = []
    for i, (W, b) in enumerate(res):
        r = common.score(W, b)
        preds.append((Xs @ W.T + b).argmax(1))
        print(f"  member {i}: dev {r['acc']:.3f} (en {r['acc_en']:.3f} fr {r['acc_fr']:.3f}) tv {r['tv']:.3f}")
    W = np.mean([w for w, _ in res], 0)
    b = np.mean([b for _, b in res], 0)
    save_model(HERE / f"{name}.npz", W, b)
    r = common.score(W, b)
    pa = (Xs @ W.T + b).argmax(1)
    agree = np.mean([np.mean(p == pa) for p in preds])
    print(f"== {name} {json.dumps({k: list(v) if isinstance(v, tuple) else v for k, v in cfg.items()})} K={K}")
    print(f"  dev acc {r['acc']:.3f} (en {r['acc_en']:.3f}, fr {r['acc_fr']:.3f}) tv {r['tv']:.3f} shares {r['shares']}")
    print(f"  per class {r['per_class']}")
    print(f"  sealed mean member agreement with bag {agree:.3f}")
    print("  sealed en " + " ".join(f"{v:.2f}" for v in r["sealed_mix_en"]) + " | fr " + " ".join(f"{v:.2f}" for v in r["sealed_mix_fr"]))


if __name__ == "__main__":
    main()
