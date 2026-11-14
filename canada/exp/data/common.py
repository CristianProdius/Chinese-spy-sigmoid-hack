"""Data-centric pipeline for the data strategy (exp/data).

Builds a training set from
  - the synthetic corpus, decorrelated with exp/inline/recombine.build (hazard-free rows dropped,
    headers and generic lines reshuffled within language), several seeds for variety,
  - the agent-written data/gen/train_*.jsonl and data/gen/boundary_*.jsonl,
then augments documents with
  - random hazard-free filler sentences (data/gen/filler_*.jsonl, same language), inserted at random
    positions, so the model learns to ignore impact/relief/administrative prose,
  - optional sentence dropout (generated docs only),
  - optional random pseudo-words (simulate words we never saw: they hash to random buckets),
and fits a class x language balanced logistic regression (sparse X).
Dev (data/gen/dev_*.jsonl) is only used to compare finished models.
"""
import collections
import json
import random
import string
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "exp" / "inline"))
from lib import CLASSES, featurize, fp_lang, load_sealed, sentences  # noqa: E402

GEN = ROOT / "data" / "gen"


def read_jsonl(paths):
    rows = []
    for p in paths:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


import os  # noqa: E402
import re  # noqa: E402

# STRICT=1 drops every generated report that names a real pandemic or epidemic year (COVID-19, SARS,
# H1N1, 1918/1957 influenza), to show the result does not rest on them.
_REAL_NAMED = re.compile(r"covid|sars|h1n1|1918|1919|spanish|espagnole|1957|asian flu", re.I)


def load_gen():
    train = read_jsonl(sorted(GEN.glob("train_*.jsonl")))
    boundary = read_jsonl(sorted(GEN.glob("boundary_*.jsonl")))
    if os.environ.get("STRICT") == "1":
        train = [d for d in train if not _REAL_NAMED.search(d["text"])]
        boundary = [d for d in boundary if not _REAL_NAMED.search(d["text"])]
    filler = read_jsonl(sorted(GEN.glob("filler_*.jsonl")))
    return train, boundary, filler


def load_dev():
    return read_jsonl(sorted(GEN.glob("dev_*.jsonl")))


_CORPUS_CACHE = {}


def corpus_docs(seeds):
    import recombine  # exp/inline/recombine.py (read-only import)

    out = []
    for s in seeds:
        if s not in _CORPUS_CACHE:
            _CORPUS_CACHE[s] = recombine.build(seed=s)
        out += _CORPUS_CACHE[s]
    return out


def split_sents(text):
    ss = sentences(text)
    merged = []
    for s in ss:
        if merged and merged[-1].endswith(("St.", "Ste.", "Mt.", "No.", "Jan.", "Feb.", "Aug.", "Sept.", "Oct.", "Nov.", "Dec.", "Ont.", "Que.", "Man.", "Sask.", "Alta.")):
            merged[-1] += " " + s
        else:
            merged.append(s)
    return merged


def pseudo_word(rng):
    n = rng.randint(3, 10)
    return "".join(rng.choice(string.ascii_lowercase) for _ in range(n))


def augment(doc, rng, filler_pool, n_filler=(0, 3), drop=0.0, noise=0.0):
    """Return a new text: sentence dropout, filler insertion, pseudo-word noise."""
    ss = split_sents(doc["text"])
    if drop > 0 and len(ss) > 1:
        keep = [s for s in ss if rng.random() > drop]
        if not keep:
            keep = [rng.choice(ss)]
        ss = keep
    k = rng.randint(*n_filler) if n_filler else 0
    pool = filler_pool[doc["lang"]]
    for _ in range(k):
        ss.insert(rng.randint(0, len(ss)), rng.choice(pool))
    text = " ".join(ss)
    if noise > 0:
        words = text.split()
        m = int(round(noise * len(words) * rng.random() * 2))
        for _ in range(m):
            words.insert(rng.randint(0, len(words)), pseudo_word(rng))
        text = " ".join(words)
    return text


def build_set(cfg, seed=0):
    """-> texts, y, lang, weight according to cfg."""
    rng = random.Random(seed)
    train, boundary, filler = load_gen()
    fpool = {"en": [f["text"] for f in filler if f["lang"] == "en"], "fr": [f["text"] for f in filler if f["lang"] == "fr"]}
    nf = tuple(cfg.get("n_filler", (0, 3)))
    sources = []  # (name, texts, labels, langs, total_weight)

    gen = train + (boundary * int(cfg.get("boundary_rep", 1)) if cfg.get("boundary", True) else [])
    gt, gy, gl = [], [], []
    for d in gen:
        for c in range(cfg.get("gen_copies", 4)):
            if c == 0 and cfg.get("keep_orig", True):
                t = d["text"]
            else:
                t = augment(d, rng, fpool, nf, cfg.get("drop", 0.0), cfg.get("noise", 0.0))
            gt.append(t); gy.append(d["label"]); gl.append(d["lang"])
    # multi-hazard mixes: a full primary report plus 1-2 later sentences lifted from a report of another
    # class (same language), appended after it; the label stays the primary one.
    n_mix = int(cfg.get("mix", 0.0) * len(gen))
    by_lang = {"en": [d for d in gen if d["lang"] == "en"], "fr": [d for d in gen if d["lang"] == "fr"]}
    for _ in range(n_mix):
        d = rng.choice(gen)
        o = rng.choice(by_lang[d["lang"]])
        while o["label"] == d["label"]:
            o = rng.choice(by_lang[d["lang"]])
        os_ = split_sents(o["text"])
        k = min(len(os_), rng.randint(1, 2))
        start = rng.randint(0, len(os_) - k)
        t = augment(d, rng, fpool, nf, 0.0, cfg.get("noise", 0.0)) + " " + " ".join(os_[start:start + k])
        gt.append(t); gy.append(d["label"]); gl.append(d["lang"])
    sources.append(("gen", gt, gy, gl, 1.0))

    alpha = cfg.get("alpha", 0.5)
    if alpha > 0:
        cd = corpus_docs(cfg.get("corpus_seeds", (0,)))
        ct, cy, cl = [], [], []
        for d in cd:
            t = augment(d, rng, fpool, nf, 0.0, cfg.get("noise", 0.0)) if cfg.get("corpus_aug", True) else d["text"]
            ct.append(t); cy.append(d["label"]); cl.append(d["lang"])
        sources.append(("corpus", ct, cy, cl, alpha))

    texts, y, lang, w = [], [], [], []
    for name, t, ly, ll, tw in sources:
        cell = collections.Counter(zip(ly, ll))
        ncell = len(cell)
        for a, b in zip(ly, ll):
            w.append(tw / (ncell * cell[(a, b)]))
        texts += t; y += [CLASSES.index(a) for a in ly]; lang += ll
    w = np.array(w)
    w *= len(w) / w.sum()
    return texts, np.array(y), np.array(lang), w


def fit(X, y, w, C, max_iter=3000):
    from sklearn.linear_model import LogisticRegression

    m = LogisticRegression(C=C, max_iter=max_iter, tol=1e-5).fit(X, y, sample_weight=w)
    W = np.zeros((len(CLASSES), X.shape[1]))
    b = np.full(len(CLASSES), -30.0)
    W[m.classes_], b[m.classes_] = m.coef_, m.intercept_
    return W, b


def to_sparse(texts):
    return sp.csr_matrix(featurize(texts))


_DEV = None


def dev_xy():
    global _DEV
    if _DEV is None:
        dev = load_dev()
        X = featurize([r["text"] for r in dev])
        y = np.array([CLASSES.index(r["label"]) for r in dev])
        lang = np.array([r["lang"] for r in dev])
        Xs = load_sealed()
        _DEV = (X, y, lang, Xs, fp_lang(Xs))
    return _DEV


def score(W, b):
    import eval_model

    X, y, lang, Xs, lang_s = dev_xy()
    r = eval_model.evaluate(W, b, X, y, lang)
    tv, mix = eval_model.sealed_gap(W, b, Xs, lang_s)
    r["tv"] = tv
    r["sealed_mix_en"] = [round(float(v), 3) for v in mix["en"]]
    r["sealed_mix_fr"] = [round(float(v), 3) for v in mix["fr"]]
    return r
