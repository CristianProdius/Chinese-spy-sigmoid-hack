"""Sweep small embedding models on the public questions (GPU box).

For each model: embed chunks once (cached in work/emb_<tag>.npy), then report dense-only
Hit@k and fusion with chunk BM25 (title-prefixed, 200/50 and 300/100).

    python build/exp_dense.py [model_tag ...]
"""
from __future__ import annotations

import os
import sys
import time

import bm25s
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402

BGE_Q = "Represent this sentence for searching relevant passages: "
MODELS = {
    # tag: (hf id, kind, query prefix, doc prefix)
    "minilm6": ("sentence-transformers/all-MiniLM-L6-v2", "st", "", ""),
    "arctic_xs": ("Snowflake/snowflake-arctic-embed-xs", "st", BGE_Q, ""),
    "arctic_s": ("Snowflake/snowflake-arctic-embed-s", "st", BGE_Q, ""),
    "bge_small": ("BAAI/bge-small-en-v1.5", "st", BGE_Q, ""),
    "e5_small": ("intfloat/e5-small-v2", "st", "query: ", "passage: "),
    "gte_small": ("thenlper/gte-small", "st", "", ""),
    "mxbai_xs": ("mixedbread-ai/mxbai-embed-xsmall-v1", "st", BGE_Q, ""),
    "bge_micro": ("TaylorAI/bge-micro-v2", "st", BGE_Q, ""),
    "gte_tiny": ("TaylorAI/gte-tiny", "st", "", ""),
    "minilm3": ("sentence-transformers/paraphrase-MiniLM-L3-v2", "st", "", ""),
    "potion8": ("minishlab/potion-base-8M", "m2v", "", ""),
    "potion32": ("minishlab/potion-base-32M", "m2v", "", ""),
    "potion_ret32": ("minishlab/potion-retrieval-32M", "m2v", "", ""),
    "static_mrl": ("sentence-transformers/static-retrieval-mrl-en-v1", "st", "", ""),
}

CHUNKINGS = [(200, 50), (300, 100)]


def load_model(hf, kind):
    if kind == "m2v":
        from model2vec import StaticModel
        m = StaticModel.from_pretrained(hf)
        return lambda xs, bs=256: m.encode(xs, batch_size=bs)
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(hf, device="cuda", trust_remote_code=True)
    m.max_seq_length = min(512, m.max_seq_length or 512)
    return lambda xs, bs=128: m.encode(xs, batch_size=bs, convert_to_numpy=True, normalize_embeddings=False,
                                       show_progress_bar=False)


def norm(x):
    x = x.astype(np.float32)
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-9)


def bm25_chunk_scores(size, overlap):
    doc_ids, texts, cd = lab.chunks(size, overlap, title=True)
    m = bm25s.BM25(k1=1.2, b=0.75)
    m.index([lab.tokens(t) for t in texts], show_progress=False)

    def score(q):
        qt = [t for t in lab.tokens(q) if t in m.vocab_dict]
        return m.get_scores(qt) if qt else np.zeros(len(texts))
    return score


def main(tags):
    qs = lab.questions()
    qtexts = [q["question"] for q in qs]
    for size, overlap in CHUNKINGS:
        doc_ids, texts, cd = lab.chunks(size, overlap, title=True)
        n = len(doc_ids)
        bm = bm25_chunk_scores(size, overlap)
        bm_q = [bm(q) for q in qtexts]
        for tag in tags:
            hf, kind, qp, dp = MODELS[tag]
            path = os.path.join(lab.WORK, f"emb_{tag}_{size}_{overlap}.npy")
            t0 = time.time()
            enc = load_model(hf, kind)
            if os.path.exists(path):
                E = np.load(path)
            else:
                E = norm(enc([dp + t for t in texts]))
                np.save(path, E.astype(np.float16))
            Q = norm(enc([qp + q for q in qtexts]))
            S = Q @ E.T.astype(np.float32)  # (nq, nchunks)
            res = {}
            dense_doc = [lab.doc_scores_from_chunks(S[i], cd, n) for i in range(len(qs))]
            it = iter(range(len(qs)))
            res["dense"] = lab.evaluate(lambda q: dense_doc[next(it)], qs, doc_ids)
            # fusion: RRF over doc rankings, and z-normalised linear blend of doc scores
            for name, fuse in (("rrf", "rrf"), ("lin.5", 0.5), ("lin.3", 0.3)):
                it = iter(range(len(qs)))

                def rank(_q, fuse=fuse):
                    i = next(it)
                    b = lab.doc_scores_from_chunks(bm_q[i], cd, n)
                    d = dense_doc[i]
                    if fuse == "rrf":
                        rb = np.empty(n); rb[np.argsort(-b)] = np.arange(n)
                        rd = np.empty(n); rd[np.argsort(-d)] = np.arange(n)
                        return 1 / (60 + rb) + 1 / (60 + rd)
                    zb = (b - b.mean()) / (b.std() + 1e-9)
                    zd = (d - d.mean()) / (d.std() + 1e-9)
                    return (1 - fuse) * zb + fuse * zd
                res[name] = lab.evaluate(rank, qs, doc_ids)
            line = "  ".join(f"{k}:{v['hit3']:.3f}/{v['hit10']:.3f}" for k, v in res.items())
            print(f"{tag:13s} {size}/{overlap} dim={E.shape[1]:4d}  hit3/hit10  {line}  ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(MODELS))
