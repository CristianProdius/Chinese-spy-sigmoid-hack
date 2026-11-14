"""Diagnostic: document frequency of chosen terms' buckets in sealed vs corpus vs generated data.
Chance level of a random bucket is shown as 'rand'. Unlabelled use of sealed fingerprints only."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from lib import bucket, featurize, load_corpus, load_sealed, fp_lang

Xs = load_sealed() > 0
lang = fp_lang(load_sealed())
train, boundary, filler = common.load_gen()
Xg = featurize([d["text"] for d in train + boundary]) > 0
Xc = featurize([r["text"] for r in load_corpus()]) > 0
dev = common.load_dev()
Xd = featurize([d["text"] for d in dev]) > 0
print("rand bucket df: sealed %.3f gen %.3f corpus %.3f dev %.3f" % (Xs.mean(), Xg.mean(), Xc.mean(), Xd.mean()))
print("mean nnz/doc: sealed %.1f gen %.1f corpus %.1f dev %.1f" % (Xs.sum(1).mean(), Xg.sum(1).mean(), Xc.sum(1).mean(), Xd.sum(1).mean()))
terms = sys.argv[1:]
print(f"{'term':28s} sealed  s_en  s_fr   gen corpus   dev")
for t in terms:
    b = bucket(t)
    print(f"{t:28s} {Xs[:, b].mean():.3f} {Xs[lang=='en', b].mean():.3f} {Xs[lang=='fr', b].mean():.3f} {Xg[:, b].mean():.3f} {Xc[:, b].mean():.3f} {Xd[:, b].mean():.3f}")
