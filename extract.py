"""Recover the payload hidden in model.safetensors (The Knots You Cannot Read).

Usage:  python extract.py model.safetensors [corpus.csv]
Needs:  numpy, safetensors
"""
import sys, csv
import numpy as np
from safetensors.numpy import load_file

w = load_file(sys.argv[1])
E, W, b = w["embedding.weight"], w["classifier.weight"], w["classifier.bias"]

# 1. Confirm the model is what it claims: byte embedding -> mean pool -> linear.
if len(sys.argv) > 2:
    rows = list(csv.DictReader(open(sys.argv[2])))
    labels = sorted({r["register"] for r in rows})            # alphabetical
    X = np.array([[ord(c) for c in r["text"]] for r in rows])
    y = np.array([labels.index(r["register"]) for r in rows])
    acc = ((E[X].mean(1) @ W.T + b).argmax(1) == y).mean()
    print(f"accuracy on corpus: {acc:.4f}   (labels={labels})")
    used = sorted(set(X.flatten()))
    print(f"bytes the corpus can ever feed the model: {used}")

# 2. Find weights that no trained float would ever have: low 16 mantissa bits == 0.
bits = E.view(np.uint32)
clean = np.argwhere((bits & 0xFFFF) == 0)
print("floats with zeroed low mantissa bits:", clean.tolist())
row = int(clean[0, 0])                                        # -> 128

# 3. Decode: value = (ascii - 128) / 1024
vals = E[row, : len(clean)]
flag = "".join(chr(int(round(v * 1024)) + 128) for v in vals)
print("payload:", flag)
