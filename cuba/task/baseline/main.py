"""Baseline retriever for Zemí.

index/ layout written by build_baseline.py:
    doc_ids.json            list of document ids (index = document number)
    chunk_doc.npy           int32, chunk number -> document number
    vectors.npy             float32 (n_chunks, dim), L2-normalised chunk embeddings
    model2vec/              the static embedding model (model2vec StaticModel)
    bm25/                   bm25s index over the same chunks
    config.json             k1/b, fusion constant, candidate count
"""
from __future__ import annotations

import json
import os
import re
import unicodedata

import numpy as np

STOPWORDS = set("a an the of and or to in on at by for from with as is are was were be been this that these those it its into than then there their they them he she his her we you not no but if so such which who what when where why how all any each more most other some very can could would should may might will do does did have has had about over under between through during before after".split())


def normalise(text: str) -> str:
    """Lower-case, strip accents, keep letters/digits. Same function at index and query time."""
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", text)


def tokenize(text: str) -> list[str]:
    return [t for t in normalise(text).split() if t not in STOPWORDS]


class Retriever:
    def __init__(self, index_dir: str) -> None:
        import bm25s
        from model2vec import StaticModel

        with open(os.path.join(index_dir, "config.json"), encoding="utf-8") as f:
            self.cfg = json.load(f)
        with open(os.path.join(index_dir, "doc_ids.json"), encoding="utf-8") as f:
            self.doc_ids = json.load(f)
        self.chunk_doc = np.load(os.path.join(index_dir, "chunk_doc.npy"))
        self.vectors = np.load(os.path.join(index_dir, "vectors.npy"))          # float32: the size problem
        self.model = StaticModel.from_pretrained(os.path.join(index_dir, "model2vec"))
        self.bm25 = bm25s.BM25.load(os.path.join(index_dir, "bm25"), load_corpus=False)

    def search(self, query: str, k: int = 3) -> list[str]:
        n = self.cfg["candidates"]
        # 1. dense ranking: cosine similarity against every chunk vector
        q = self.model.encode([query])[0].astype(np.float32)
        q /= np.linalg.norm(q) + 1e-9
        dense_top = np.argsort(-(self.vectors @ q))[:n]
        # 2. keyword ranking
        toks = tokenize(query)
        if toks:
            ids, scores = self.bm25.retrieve([toks], k=min(n, len(self.chunk_doc)), show_progress=False)
            bm25_top = [int(i) for i, s in zip(ids[0], scores[0]) if s > 0]
        else:
            bm25_top = []
        # 3. reciprocal rank fusion of the two chunk rankings
        fused: dict[int, float] = {}
        for ranking in (dense_top, bm25_top):
            for rank, cid in enumerate(ranking):
                fused[int(cid)] = fused.get(int(cid), 0.0) + 1.0 / (self.cfg["rrf_k"] + rank)
        # 4. chunk -> document: a document scores as its best chunk
        doc_scores: dict[int, float] = {}
        for cid, s in fused.items():
            d = int(self.chunk_doc[cid])
            doc_scores[d] = max(doc_scores.get(d, 0.0), s)
        best = sorted(doc_scores, key=lambda d: -doc_scores[d])[:k]
        return [self.doc_ids[d] for d in best]
