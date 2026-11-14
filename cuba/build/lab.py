"""Experiment harness: corpus loading, chunking, tokenising, evaluation.

Everything here is build-time only; main.py must not import it.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from functools import lru_cache

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(HERE, "..", "task")
DATA = os.path.join(TASK, "data")
WORK = os.path.join(HERE, "..", "work")
os.makedirs(WORK, exist_ok=True)

STOP = set("""a an the of and or to in on at by for from with as is are was were be been being this that these those it its
into than then there their they them he she his her we you not no but if so such which who whom whose what when where why how
all any each more most other some very can could would should may might will do does did have has had about over under between
through during before after i me my our your us also just only own same too s t""".split())

# Words that frame the slip rather than describe the chapter.
FRAME = set("""chapter part bit section article story passage piece describes described describe tell tells told whole
full account which where wrote write written about mention mentions mentioned""".split())


def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", strip_accents(text.lower()))


@lru_cache(maxsize=1)
def stemmer():
    import Stemmer
    return Stemmer.Stemmer("english")


def tokens(text: str, stem: bool = True, drop_frame: bool = False) -> list[str]:
    toks = [t for t in normalise(text).split() if t not in STOP and len(t) > 1 or t.isdigit()]
    if drop_frame:
        toks = [t for t in toks if t not in FRAME]
    if stem:
        toks = stemmer().stemWords(toks)
    return toks


@lru_cache(maxsize=1)
def meta() -> list[dict]:
    with open(os.path.join(DATA, "corpus_meta.jsonl"), encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


@lru_cache(maxsize=1)
def corpus() -> dict[str, str]:
    out = {}
    for m in meta():
        with open(os.path.join(DATA, "corpus", m["id"] + ".txt"), encoding="utf-8") as fh:
            out[m["id"]] = fh.read()
    return out


def questions(split: str = "sample") -> list[dict]:
    """[{qid, question, doc_id}] for the public sample (or a synthetic set in work/)."""
    if split == "sample":
        qs = [json.loads(l) for l in open(os.path.join(DATA, "sample-input.jsonl"), encoding="utf-8") if l.strip()]
        gold = {json.loads(l)["qid"]: json.loads(l)["doc_id"]
                for l in open(os.path.join(DATA, "sample-output.jsonl"), encoding="utf-8") if l.strip()}
        for q in qs:
            q["doc_id"] = gold[q["qid"]]
        return qs
    with open(os.path.join(WORK, f"{split}.jsonl"), encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def chunk_words(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= size:
        return [" ".join(words)]
    step = max(1, size - overlap)
    out = []
    for start in range(0, len(words), step):
        out.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
    return out


def chunks(size: int = 200, overlap: int = 50, title: bool = False):
    """Returns (doc_ids, chunk_texts, chunk_doc int32)."""
    doc_ids, texts, owner = [], [], []
    for d, m in enumerate(meta()):
        doc_ids.append(m["id"])
        head = f"{m.get('source_title', '')} {m['title']} " if title else ""
        for c in chunk_words(corpus()[m["id"]], size, overlap):
            texts.append(head + c)
            owner.append(d)
    return doc_ids, texts, np.asarray(owner, dtype=np.int32)


def doc_scores_from_chunks(chunk_scores: np.ndarray, chunk_doc: np.ndarray, n_docs: int, how: str = "max") -> np.ndarray:
    out = np.full(n_docs, -np.inf, dtype=np.float64)
    if how == "max":
        np.maximum.at(out, chunk_doc, chunk_scores)
    else:
        raise ValueError(how)
    return out


def evaluate(rank_fn, qs: list[dict], doc_ids: list[str], k: int = 3, verbose: bool = False) -> dict:
    """rank_fn(question) -> np.ndarray of doc scores (len n_docs) or list of doc indices best-first."""
    pos = {d: i for i, d in enumerate(doc_ids)}
    hits1 = hits3 = hits10 = 0
    rr = 0.0
    misses = []
    for q in qs:
        r = rank_fn(q["question"])
        order = np.argsort(-r, kind="stable")[:100] if isinstance(r, np.ndarray) else list(r)[:100]
        g = pos[q["doc_id"]]
        rank = next((i for i, d in enumerate(order) if d == g), None)
        if rank is not None:
            hits1 += rank < 1
            hits3 += rank < 3
            hits10 += rank < 10
            rr += 1 / (rank + 1)
        if rank is None or rank >= k:
            misses.append((q["question"], q["doc_id"], rank, [doc_ids[i] for i in order[:3]]))
    n = len(qs)
    res = {"hit1": hits1 / n, "hit3": hits3 / n, "hit10": hits10 / n, "mrr": rr / n, "n": n}
    if verbose:
        res["misses"] = misses
    return res
