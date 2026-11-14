"""Score every model in exp/sparse/models (or the given .npz files) on dev, one line each.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python evalall.py [glob]"
"""
import sys

import numpy as np

from common import HERE, Dev, load_dev

pat = sys.argv[1] if len(sys.argv) > 1 else "*.npz"
dev = Dev(load_dev())
rows = []
for p in sorted((HERE / "models").glob(pat)):
    z = np.load(p)
    r = dev.line(p.stem, z["W"], z["b"])
    rows.append((r["acc"], max(r["shares"].values()), r["tv"], p.stem))
print("\n== by dev acc")
for acc, sh, tv, n in sorted(rows, reverse=True)[:25]:
    print(f"  {acc:.3f} share {sh:+.3f} tv {tv:.3f} {n}")
