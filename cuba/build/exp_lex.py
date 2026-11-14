"""Lexical-leg experiments with the dense leg fixed (scores from a built submission).

    python build/exp_lex.py work/sub_v2
Fused score = z(lexical doc score) + w * z(dense doc score). Lexical doc score =
max over windows of window BM25 + alpha * z(doc-level BM25).
"""
from __future__ import annotations

import collections
import importlib.util
import itertools
import math
import os
import sys

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "submission"))
import lab  # noqa: E402
from main import Analyzer  # noqa: E402

sub = sys.argv[1]
spec = importlib.util.spec_from_file_location("subm", os.path.join(sub, "main.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
R = mod.Retriever(os.path.join(sub, "index"))
an = Analyzer()
pos = {d: i for i, d in enumerate(R.doc_ids)}
SPLITS = {"sample": lab.questions("sample"), "hold": lab.questions("vset_hold"),
          "q72": lab.questions("synth_q72_eval")[:600]}
DENSE = {k: np.stack([np.maximum.reduceat(R.dense(q["question"]), R.doc_start) for q in qs]) for k, qs in SPLITS.items()}
GOLD = {k: np.array([pos[q["doc_id"]] for q in qs]) for k, qs in SPLITS.items()}
QT = {k: [list(dict.fromkeys(an.terms(q["question"], query=True))) for q in qs] for k, qs in SPLITS.items()}


def z(x):
    return (x - x.mean(-1, keepdims=True)) / (x.std(-1, keepdims=True) + 1e-9)


def build(texts, k1, b):
    docs = [collections.Counter(an.terms(t)) for t in texts]
    vocab = {}
    rows, cols, tfs = [], [], []
    for w, c in enumerate(docs):
        for t, tf in c.items():
            rows.append(w)
            cols.append(vocab.setdefault(t, len(vocab)))
            tfs.append(tf)
    tf = sp.csr_matrix((np.array(tfs, float), (rows, cols)), shape=(len(docs), len(vocab)))
    lens = np.asarray(tf.sum(1)).ravel()
    df = np.bincount(cols, minlength=len(vocab))
    N = len(docs)
    idf = np.log(1 + (N - df + 0.5) / (df + 0.5))
    tf = tf.tocoo()
    norm = k1 * (1 - b + b * lens[tf.row] / lens.mean())
    w = idf[tf.col] * tf.data * (k1 + 1) / (tf.data + norm)
    W = sp.csc_matrix((w, (tf.row, tf.col)), shape=tf.shape)
    return vocab, W


def query_matrix(vocab, terms_list):
    rows, cols = [], []
    for i, terms in enumerate(terms_list):
        for t in terms:
            if t in vocab:
                rows.append(i)
                cols.append(vocab[t])
    return sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(terms_list), len(vocab)))


cache = {}


def lex_scores(size, overlap, k1, b, split):
    key = (size, overlap, k1, b)
    if key not in cache:
        doc_ids, texts, cd = lab.chunks(size, overlap, title=True)
        starts = np.flatnonzero(np.r_[True, cd[1:] != cd[:-1]])
        vocab, W = build(texts, k1, b)
        cache[key] = (vocab, W, starts)
    vocab, W, starts = cache[key]
    S = (query_matrix(vocab, QT[split]) @ W.T).toarray()
    return np.maximum.reduceat(S, starts, axis=1)


doc_cache = {}


def doc_bm25(k1, b, split):
    if (k1, b) not in doc_cache:
        texts = [f"{m.get('source_title', '')} {m['title']} " + lab.corpus()[m["id"]] for m in lab.meta()]
        doc_cache[(k1, b)] = build(texts, k1, b)
    vocab, W = doc_cache[(k1, b)]
    return (query_matrix(vocab, QT[split]) @ W.T).toarray()


def hit3(M, gold):
    top = np.argpartition(-M, 3, axis=1)[:, :3]
    return (top == gold[:, None]).any(1).mean()


def report(tag, fn):
    out = []
    for split in SPLITS:
        L = fn(split)
        out.append(f"{split} " + " ".join(f"w{w:g}:{hit3(z(L) + w * z(DENSE[split]), GOLD[split]):.3f}" for w in (1.5, 2.0, 3.0)))
    print(f"{tag:34s} " + " | ".join(out), flush=True)


print("dense only:", {k: round(hit3(DENSE[k], GOLD[k]), 3) for k in SPLITS})
for size, overlap in ((200, 50), (300, 100), (150, 50), (400, 100)):
    report(f"win {size}/{overlap} k1=1.2 b=.75", lambda s: lex_scores(size, overlap, 1.2, 0.75, s))
for k1, b in itertools.product((0.8, 1.6, 2.2), (0.5, 0.9)):
    report(f"win 200/50 k1={k1} b={b}", lambda s: lex_scores(200, 50, k1, b, s))
for alpha in (0.3, 0.6, 1.0):
    for dk1, db in ((1.2, 0.75), (2.5, 0.8)):
        report(f"200/50 + {alpha}*doc(k1={dk1},b={db})",
               lambda s: z(lex_scores(200, 50, 1.2, 0.75, s)) + alpha * z(doc_bm25(dk1, db, s)))
