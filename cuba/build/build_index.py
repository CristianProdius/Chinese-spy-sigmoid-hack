"""Build submission/index from the corpus.

    python build/build_index.py --out ../submission/index [--size 200 --overlap 50]
        [--vectors work/emb_X.npy --onnx work/onnx_X/ --pooling cls --prefix "..."]
        [--k1 1.2 --b 0.75 --w-dense 1.0]

Windows come from lab.chunks (same code on the GPU box, so the vector rows line up).
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "submission"))
import lab  # noqa: E402
from main import Analyzer  # noqa: E402


def bm25_postings(texts: list[str], k1: float, b: float):
    an = Analyzer()
    docs = [collections.Counter(an.terms(t)) for t in texts]
    lens = np.array([sum(c.values()) for c in docs], dtype=np.float64)
    avg = lens.mean()
    df = collections.Counter()
    for c in docs:
        df.update(c.keys())
    vocab = sorted(df)
    tid = {t: i for i, t in enumerate(vocab)}
    N = len(docs)
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    rows, cols, vals = [], [], []
    for w, c in enumerate(docs):
        norm = k1 * (1 - b + b * lens[w] / avg)
        for t, tf in c.items():
            rows.append(tid[t])
            cols.append(w)
            vals.append(idf[t] * tf * (k1 + 1) / (tf + norm))
    rows = np.asarray(rows, dtype=np.int64)
    cols = np.asarray(cols, dtype=np.int64)
    vals = np.asarray(vals, dtype=np.float64)
    order = np.lexsort((cols, rows))
    rows, cols, vals = rows[order], cols[order], vals[order]
    scale = vals.max() / 255.0
    imp = np.clip(np.rint(vals / scale), 1, 255).astype(np.uint8)
    indptr = np.zeros(len(vocab) + 1, dtype=np.uint32)
    np.add.at(indptr, rows + 1, 1)
    indptr = np.cumsum(indptr).astype(np.uint32)
    win_dtype = np.uint16 if N < 65536 else np.uint32
    return vocab, indptr, cols.astype(win_dtype), imp, scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=200)
    ap.add_argument("--overlap", type=int, default=50)
    ap.add_argument("--k1", type=float, default=1.2)
    ap.add_argument("--b", type=float, default=0.75)
    ap.add_argument("--vectors", help=".npy float16/float32 (n_windows, dim), rows in lab.chunks order")
    ap.add_argument("--onnx", help="folder holding encoder.onnx and tokenizer.json")
    ap.add_argument("--pooling", default="cls", choices=["cls", "mean"])
    ap.add_argument("--prefix", default="")
    ap.add_argument("--max-len", type=int, default=96)
    ap.add_argument("--w-lex", type=float, default=1.0)
    ap.add_argument("--w-dense", type=float, default=2.0)
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    doc_ids, texts, win_doc = lab.chunks(args.size, args.overlap, title=True)
    vocab, indptr, win, imp, scale = bm25_postings(texts, args.k1, args.b)
    np.save(os.path.join(out, "win_doc.npy"), win_doc.astype(np.int32))
    np.savez(os.path.join(out, "postings.npz"), indptr=indptr, win=win, imp=imp)
    with open(os.path.join(out, "vocab.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(vocab))
    with open(os.path.join(out, "docs.json"), "w", encoding="utf-8") as fh:
        json.dump(doc_ids, fh)
    cfg = {"windows": {"size": args.size, "overlap": args.overlap, "title": True},
           "bm25": {"k1": args.k1, "b": args.b, "scale": scale},
           "fusion": {"w_lex": args.w_lex, "w_dense": args.w_dense if args.vectors else 0.0}}
    if args.vectors:
        V = np.load(args.vectors).astype(np.float32)
        assert V.shape[0] == len(texts), f"vectors have {V.shape[0]} rows, windows {len(texts)}"
        V /= np.linalg.norm(V, axis=1, keepdims=True) + 1e-9
        # 4-bit scalar quantisation per dimension (0.5% clipping); two codes per byte.
        lo = np.percentile(V, 0.5, axis=0)
        hi = np.percentile(V, 99.5, axis=0)
        step = ((hi - lo) / 15).astype(np.float32)
        codes = np.clip(np.rint((V - lo) / step), 0, 15).astype(np.uint8)
        packed = (codes[:, 0::2] << 4) | codes[:, 1::2]
        np.save(os.path.join(out, "vectors.npy"), packed)
        np.save(os.path.join(out, "vec_step.npy"), step)
        shutil.copy(os.path.join(args.onnx, "encoder.onnx"), os.path.join(out, "encoder.onnx"))
        shutil.copy(os.path.join(args.onnx, "tokenizer.json"), os.path.join(out, "tokenizer.json"))
        cfg["encoder"] = {"pooling": args.pooling, "query_prefix": args.prefix, "max_len": args.max_len}
    with open(os.path.join(out, "config.json"), "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=1)
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out)) / 1e6
    print(f"windows {len(texts)}  vocab {len(vocab)}  postings {len(win)}  index {size:.2f} MB -> {out}")


if __name__ == "__main__":
    main()
