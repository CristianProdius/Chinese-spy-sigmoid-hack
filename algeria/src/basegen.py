"""Greedy answers of the (fake-quantised) base model for a prompt file: adds a "base" field.

  python basegen.py data/prompts.jsonl data/prompts_base.jsonl
"""
import json
import sys

from common import load_base
from fasteval import generate

rows = [json.loads(l) for l in open(sys.argv[1])]
tok, model = load_base()
model.eval()
outs = generate(tok, model, [r["prompt"] for r in rows], bs=128)
with open(sys.argv[2], "w") as fh:
    for r, o in zip(rows, outs):
        fh.write(json.dumps({**r, "base": o}, ensure_ascii=False) + "\n")
print("done", len(rows))
