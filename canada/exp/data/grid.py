"""Grid over data configs x C. Writes exp/data/results_<stage>.jsonl (dev acc, shares, sealed TV gap).

    tools/h100.sh .venv/bin/python exp/data/grid.py stage1
"""
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

HERE = Path(__file__).resolve().parent

STAGES = {
    "stage1": dict(
        data=[
            dict(alpha=a, n_filler=nf, noise=nz, drop=dr, gen_copies=4, corpus_seeds=(0, 1))
            for a in (0.0, 0.25, 0.5, 1.0)
            for nf in ((0, 0), (0, 3))
            for nz in (0.0, 0.3)
            for dr in (0.0, 0.25)
        ],
        Cs=(1.0, 3.0, 10.0, 30.0),
    ),
    "stage2": dict(
        data=[
            dict(alpha=a, n_filler=(0, 3), noise=0.0, drop=0.25, gen_copies=4, corpus_seeds=(0, 1), boundary_rep=br, mix=mx)
            for a in (0.25, 0.5)
            for br in (1, 3)
            for mx in (0.0, 0.5)
        ] + [
            dict(alpha=0.25, n_filler=(0, 5), noise=0.0, drop=0.25, gen_copies=4, corpus_seeds=(0, 1), boundary_rep=1, mix=0.0),
            dict(alpha=0.25, n_filler=(1, 4), noise=0.0, drop=0.4, gen_copies=6, corpus_seeds=(0, 1, 2), boundary_rep=1, mix=0.0),
        ],
        Cs=(3.0,),
    ),
}


def run_cfg(i, dcfg, Cs):
    texts, y, lang, w = common.build_set(dcfg, seed=i)
    X = common.to_sparse(texts)
    out = []
    for C in Cs:
        t = time.time()
        W, b = common.fit(X, y, w, C)
        r = common.score(W, b)
        r.update(cfg={k: list(v) if isinstance(v, tuple) else v for k, v in dcfg.items()}, C=C, secs=round(time.time() - t, 1))
        out.append(r)
    return out


def main():
    stage = sys.argv[1]
    jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    spec = STAGES[stage]
    out = HERE / f"results_{stage}.jsonl"
    common.dev_xy()
    res = Parallel(n_jobs=jobs)(delayed(run_cfg)(i, d, spec["Cs"]) for i, d in enumerate(spec["data"]))
    done = [r for rs in res for r in rs]
    out.write_text("".join(json.dumps(r) + "\n" for r in done))
    for r in done:
        print(f"{json.dumps(r['cfg'])} C={r['C']}: acc {r['acc']:.3f} en {r['acc_en']:.3f} fr {r['acc_fr']:.3f} "
              f"tv {r['tv']:.3f} shares {r['shares']} ({r['secs']}s)", flush=True)


if __name__ == "__main__":
    main()
