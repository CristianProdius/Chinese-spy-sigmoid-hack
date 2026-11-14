"""Two Solitudes: rebuild the final model from scratch and try it on the vault.

    .venv/bin/python solve.py [jobs]          # or: tools/h100.sh .venv/bin/python solve.py 6

1. Decorrelate the synthetic corpus (exp/inline/recombine.py): drop hazard-free rows, reshuffle the
   place/date headers and generic impact lines across rows of the same language.
2. Add our own agent-written, invented training reports in English and French (data/gen/train_*,
   data/gen/boundary_*), padded with hazard-free filler sentences (data/gen/filler_*) and sentence
   dropout so the model learns to ignore prose that carries no hazard.
3. Fit class x language balanced logistic regressions over the given fingerprint, 12 members with
   different seeds and data mixes (exp/data/bag.py, variants "div"), and average their W and b.
   Averaging the logits of linear models is one linear model.
4. Save model.npz (W 9x4096, b 9), score it on the held-out proxy dev set, and run open_vault.py.

The sealed fingerprints are used only by the vault and the printed diagnostics, never in training.
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "exp" / "data"))
import bag  # noqa: E402
import common  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from lib import save_model  # noqa: E402

K = 12


def main():
    jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    cfg = dict(bag.BASE, variants="div")
    members = Parallel(n_jobs=jobs)(delayed(bag.member)("solve", cfg, k) for k in range(K))
    W = np.mean([w for w, _ in members], 0)
    b = np.mean([b for _, b in members], 0)
    out = ROOT / ("model_strict.npz" if os.environ.get("STRICT") == "1" else "model.npz")
    save_model(out, W, b)
    r = common.score(W, b)
    print(f"{out.name}: proxy dev accuracy {r['acc']:.3f} (en {r['acc_en']:.3f}, fr {r['acc_fr']:.3f}), "
          f"sealed EN/FR class-mix gap {r['tv']:.3f}")
    print("vault rule replayed on dev (accuracy minus need, by share):", r["shares"])
    subprocess.run([sys.executable, str(ROOT / "task" / "open_vault.py"), str(out)], check=True)


if __name__ == "__main__":
    main()
