"""Diagnostic: buckets frequent in sealed fingerprints but rare in our training data, with the training
terms that hash there. Unlabelled use of sealed fingerprints only."""
import collections, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from lib import bucket, featurize, load_corpus, load_sealed, fp_lang, tokens

Xs = load_sealed() > 0
lang = fp_lang(load_sealed())
train, boundary, filler = common.load_gen()
texts = [d["text"] for d in train + boundary] + [r["text"] for r in load_corpus()] + [f["text"] for f in filler]
Xt = featurize(texts) > 0
terms = collections.Counter()
for t in texts:
    tk = tokens(t)
    terms.update(tk); terms.update(a + " " + b for a, b in zip(tk, tk[1:]))
by_b = collections.defaultdict(list)
for t, c in terms.items():
    by_b[bucket(t)].append((c, t))
for l in ("en", "fr"):
    s = Xs[lang == l].mean(0); tr = Xt.mean(0)
    gap = s - 3 * tr
    print(f"--- {l}: buckets with sealed df >> train df")
    for bk in np.argsort(-gap)[:25]:
        top = ", ".join(t for c, t in sorted(by_b[bk], reverse=True)[:4])
        print(f"  b{bk:4d} sealed {s[bk]:.3f} train {tr[bk]:.3f}  [{top}]")
