"""Average (still linear) of the transductive models that opened SNOWFLAKE.

    .venv/bin/python exp/transductive/ensemble.py
"""
import numpy as np
from pathlib import Path
OUT = Path(__file__).resolve().parent
MEMBERS = ["st2single_a0.3_C3_g0.0_b0.3_r3", "st2anch_comm_b0.3_r1", "fs_a0.3_up_g0.5_C3.0", "st2anch_single_g0_b0.3_r3"]
zs = [np.load(OUT / f"{m}.npz" if (OUT / f"{m}.npz").exists() else OUT / "runs" / f"{m}.npz") for m in MEMBERS]
W = np.mean([z["W"] for z in zs], 0)
b = np.mean([z["b"] for z in zs], 0)
np.savez(OUT / "ens4.npz", W=W, b=b)
print("saved", OUT / "ens4.npz")
