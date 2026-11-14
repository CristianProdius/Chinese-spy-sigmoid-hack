"""LR on the recombined corpus, language x class balanced weights."""
import collections, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from lib import *
docs = [json.loads(l) for l in (ROOT/'data/corpus_recombined.jsonl').read_text(encoding='utf-8').splitlines()]
X = featurize([d['text'] for d in docs]); y = np.array([CLASSES.index(d['label']) for d in docs]); L = np.array([d['lang'] for d in docs])
cell = collections.Counter(zip(y, L)); w = np.array([len(y)/(18*cell[(a,l)]) for a,l in zip(y,L)])
for C in (0.3, 1.0, 3.0):
    W, b = train_lr(X, y, C=C, sample_weight=w)
    save_model(ROOT/f'exp/inline/recomb_C{C}.npz', W, b)
