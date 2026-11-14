"""Average the weights of SentenceTransformer checkpoints (same base model): python build/soup.py out a b [c...]"""
import sys
import torch
from sentence_transformers import SentenceTransformer
out, paths = sys.argv[1], sys.argv[2:]
models = [SentenceTransformer(p, device="cpu") for p in paths]
sd = models[0].state_dict()
for k in sd:
    if sd[k].is_floating_point():
        sd[k] = sum(m.state_dict()[k] for m in models) / len(models)
models[0].load_state_dict(sd)
models[0].save(out)
print("soup of", len(paths), "->", out)
