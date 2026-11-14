"""Asymmetric dense: small query encoder (mdbr-leaf-ir) vs big passage encoder (arctic-embed-m-v1.5).

Also reports leaf-ir symmetric and arctic-m symmetric, and MRL truncation to 256 dims.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402
from exp_dense import bm25_chunk_scores, norm  # noqa: E402

QP = "Represent this sentence for searching relevant passages: "


def doc_eval(S, cd, n, qs, doc_ids, bm_q=None, w=0.5):
    res = {}
    dense = [lab.doc_scores_from_chunks(S[i], cd, n) for i in range(len(qs))]
    it = iter(range(len(qs)))
    res["dense"] = lab.evaluate(lambda q: dense[next(it)], qs, doc_ids)["hit3"]
    if bm_q is not None:
        it = iter(range(len(qs)))

        def rank(_q):
            i = next(it)
            b = lab.doc_scores_from_chunks(bm_q[i], cd, n)
            d = dense[i]
            return (1 - w) * (b - b.mean()) / (b.std() + 1e-9) + w * (d - d.mean()) / (d.std() + 1e-9)
        res["lin.5"] = lab.evaluate(rank, qs, doc_ids)["hit3"]
    return res


def main():
    qs = lab.questions()
    qt = [q["question"] for q in qs]
    size, overlap = 200, 50
    doc_ids, texts, cd = lab.chunks(size, overlap, title=True)
    n = len(doc_ids)
    bm = bm25_chunk_scores(size, overlap)
    bm_q = [bm(q) for q in qt]

    leaf = SentenceTransformer("MongoDB/mdbr-leaf-ir", device="cuda")
    arctic = SentenceTransformer("Snowflake/snowflake-arctic-embed-m-v1.5", device="cuda")
    p_arc = os.path.join(lab.WORK, f"emb_arctic_m15_{size}_{overlap}.npy")
    if os.path.exists(p_arc):
        D_arc = np.load(p_arc).astype(np.float32)
    else:
        D_arc = norm(arctic.encode(texts, batch_size=128, convert_to_numpy=True))
        np.save(p_arc, D_arc.astype(np.float16))
    p_leaf = os.path.join(lab.WORK, f"emb_leaf_{size}_{overlap}.npy")
    if os.path.exists(p_leaf):
        D_leaf = np.load(p_leaf).astype(np.float32)
    else:
        D_leaf = norm(leaf.encode(texts, batch_size=128, convert_to_numpy=True))
        np.save(p_leaf, D_leaf.astype(np.float16))
    Q_leaf = norm(leaf.encode([QP + q for q in qt], convert_to_numpy=True))
    Q_arc = norm(arctic.encode([QP + q for q in qt], convert_to_numpy=True))
    print("dims leaf", Q_leaf.shape[1], "arctic", D_arc.shape[1], flush=True)
    for name, Q, D in (("leaf sym", Q_leaf, D_leaf), ("arctic-m sym", Q_arc, D_arc), ("leaf->arctic asym", Q_leaf, D_arc)):
        print(f"{name:20s} full", doc_eval(Q @ D.T, cd, n, qs, doc_ids, bm_q), flush=True)
        if D.shape[1] >= 256:
            Qt, Dt = norm(Q[:, :256]), norm(D[:, :256])
            print(f"{name:20s} 256d", doc_eval(Qt @ Dt.T, cd, n, qs, doc_ids, bm_q), flush=True)


if __name__ == "__main__":
    main()
