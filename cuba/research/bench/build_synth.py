"""Build a synthetic Zipfian corpus resembling the task: ~1552 docs, ~30k passages, ~100k vocab.
Writes several index formats into ./idx for load/query micro-benchmarks."""
import os, json, time
import numpy as np
import scipy.sparse as sp

rng = np.random.default_rng(0)
V = 100_000
P = 30_000
D = 1552
PLEN = 160  # content tokens per passage after stopword removal (~200-250 raw words)

# Zipf-ish term probabilities (s=1.07, typical for English)
ranks = np.arange(1, V + 1)
p = 1.0 / ranks ** 1.07
p /= p.sum()
toks = rng.choice(V, size=P * PLEN, p=p).astype(np.int32)
pid = np.repeat(np.arange(P, dtype=np.int32), PLEN)

# term x passage tf matrix
M = sp.csr_matrix((np.ones_like(toks, dtype=np.float32), (toks, pid)), shape=(V, P))
M.sum_duplicates()
print("postings (term,passage):", M.nnz, "vocab used:", (np.diff(M.indptr) > 0).sum())

# BM25 weights (k1=1.2,b=0.75); all passages same length here so length norm trivial
df = np.diff(M.indptr).astype(np.float32)
idf = np.log(1 + (P - df + 0.5) / (df + 0.5)).astype(np.float32)
tf = M.data
k1 = 1.2
w = tf * (k1 + 1) / (tf + k1)
rowidx = np.repeat(np.arange(V), np.diff(M.indptr))
w = (w * idf[rowidx]).astype(np.float32)

# passage -> doc map: docs contiguous, variable length
cuts = np.sort(rng.choice(np.arange(1, P), size=D - 1, replace=False))
p2d = np.zeros(P, dtype=np.int32)
p2d[cuts] = 1
p2d = np.cumsum(p2d).astype(np.uint16)
doc_start = np.concatenate([[0], cuts]).astype(np.int32)

os.makedirs("idx", exist_ok=True)
indptr = M.indptr.astype(np.uint32)
indices = M.indices.astype(np.uint16)  # passage ids < 65536
data16 = w.astype(np.float16)
# uint8 quantization (global scale)
scale = float(w.max()) / 255.0
data8 = np.clip(np.rint(w / scale), 0, 255).astype(np.uint8)

np.save("idx/indptr.npy", indptr)
np.save("idx/indices.npy", indices)
np.save("idx/data16.npy", data16)
np.save("idx/data8.npy", data8)
np.save("idx/data32.npy", w)
np.save("idx/p2d.npy", p2d)
np.save("idx/doc_start.npy", doc_start)
np.savez("idx/all_uncompressed.npz", indptr=indptr, indices=indices, data=data16, p2d=p2d)
np.savez_compressed("idx/all_compressed.npz", indptr=indptr, indices=indices, data=data16, p2d=p2d)

# vocabulary: synthetic strings
words = [f"w{i:05d}{'abcdefghij'[i % 10] * (3 + i % 6)}" for i in range(V)]
with open("idx/vocab.json", "w") as f:
    json.dump({wd: i for i, wd in enumerate(words)}, f)
with open("idx/vocab.txt", "w") as f:
    f.write("\n".join(words))
order = np.argsort(np.array(words))
sorted_words = np.array(words)[order]
np.save("idx/vocab_sorted_U.npy", sorted_words)  # fixed-width unicode
np.save("idx/vocab_sorted_S.npy", np.array([w_.encode() for w_ in sorted_words], dtype="S"))
np.save("idx/vocab_order.npy", order.astype(np.uint32))

# dense passage embeddings for comparison (384-d)
E = rng.standard_normal((P, 384)).astype(np.float32)
E /= np.linalg.norm(E, axis=1, keepdims=True)
np.save("idx/emb32.npy", E)
np.save("idx/emb16.npy", E.astype(np.float16))
q8s = np.abs(E).max(axis=1, keepdims=True) / 127
np.save("idx/emb8.npy", np.rint(E / q8s).astype(np.int8))
np.save("idx/emb8_scale.npy", q8s.astype(np.float32).ravel())

for fn in sorted(os.listdir("idx")):
    print(f"{fn:28s} {os.path.getsize('idx/'+fn)/1e6:8.2f} MB")
