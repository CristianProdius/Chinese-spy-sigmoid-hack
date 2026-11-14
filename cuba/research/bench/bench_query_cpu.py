"""Single-thread micro-benchmarks: load formats, query scoring methods, aggregation, top-k, dense matvec."""
import os, time, json, gc, statistics
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))
I = "idx/"

def t(fn, n=7):
    xs = []
    for _ in range(n):
        gc.collect()
        a = time.thread_time(); r = fn(); xs.append(time.thread_time() - a)
    return statistics.median(xs) * 1e3, r

print("=== LOAD (warm page cache, median ms) ===")
for name, fn in [
    ("np.load indices.npy", lambda: np.load(I + "indices.npy")),
    ("np.load indices.npy mmap", lambda: np.load(I + "indices.npy", mmap_mode="r")),
    ("np.load 3 arrays .npy (13.5MB)", lambda: [np.load(I + f) for f in ("indptr.npy", "indices.npy", "data16.npy")]),
    ("npz uncompressed, read all 4 keys", lambda: dict(np.load(I + "all_uncompressed.npz"))),
    ("npz compressed, read all 4 keys", lambda: dict(np.load(I + "all_compressed.npz"))),
    ("json.load vocab dict 100k", lambda: json.load(open(I + "vocab.json"))),
    ("txt split + dict 100k", lambda: {w: i for i, w in enumerate(open(I + "vocab.txt").read().split("\n"))}),
    ("np.load sorted U vocab", lambda: np.load(I + "vocab_sorted_U.npy")),
    ("np.load sorted S vocab", lambda: np.load(I + "vocab_sorted_S.npy")),
    ("np.load emb32 46MB", lambda: np.load(I + "emb32.npy")),
    ("np.load emb16 23MB + astype f32", lambda: np.load(I + "emb16.npy").astype(np.float32)),
    ("np.load emb8 11.5MB + astype f32*scale", lambda: np.load(I + "emb8.npy").astype(np.float32) * np.load(I + "emb8_scale.npy")[:, None]),
]:
    ms, _ = t(fn, 5)
    print(f"{name:42s} {ms:8.2f} ms")

indptr = np.load(I + "indptr.npy").astype(np.int64)
indices = np.load(I + "indices.npy")
data16 = np.load(I + "data16.npy")
data32 = np.load(I + "data32.npy")
data8 = np.load(I + "data8.npy")
indices32 = indices.astype(np.int32)
p2d = np.load(I + "p2d.npy").astype(np.int64)
doc_start = np.load(I + "doc_start.npy")
P = len(p2d); V = len(indptr) - 1; D = int(p2d.max()) + 1
df = np.diff(indptr)
order = np.argsort(-df)  # by df descending

rng = np.random.default_rng(1)
def make_query(n_common=3, n_mid=4, n_rare=3):
    # common: df rank 20-300, mid: 300-5000, rare: 5000-60000
    q = np.concatenate([rng.choice(order[20:300], n_common), rng.choice(order[300:5000], n_mid), rng.choice(order[5000:60000], n_rare)])
    return np.unique(q)
queries = [make_query() for _ in range(300)]
heavy = [np.unique(np.concatenate([order[:8], make_query()])) for _ in range(100)]  # includes top-8 df terms (stopword-like)
for nm, qs in (("typical", queries), ("heavy(top-df terms kept)", heavy)):
    tot = [int(df[q].sum()) for q in qs]
    print(f"{nm}: postings touched per query median={int(np.median(tot))} p95={int(np.percentile(tot,95))}")

def acc_loop(q, data):
    s = np.zeros(P, np.float32)
    for tid in q:
        a, b = indptr[tid], indptr[tid + 1]
        s[indices[a:b]] += data[a:b]
    return s

def acc_loop32idx(q, data):
    s = np.zeros(P, np.float32)
    for tid in q:
        a, b = indptr[tid], indptr[tid + 1]
        s[indices32[a:b]] += data[a:b]
    return s

def acc_bincount(q, data):
    ix = np.concatenate([indices[indptr[t_]:indptr[t_ + 1]] for t_ in q])
    w = np.concatenate([data[indptr[t_]:indptr[t_ + 1]] for t_ in q])
    return np.bincount(ix, weights=w, minlength=P)

def acc_addat(q, data):
    ix = np.concatenate([indices[indptr[t_]:indptr[t_ + 1]] for t_ in q])
    w = np.concatenate([data[indptr[t_]:indptr[t_ + 1]] for t_ in q]).astype(np.float32)
    s = np.zeros(P, np.float32)
    np.add.at(s, ix, w)
    return s

import scipy.sparse as sp
Mcsr = sp.csr_matrix((data32, indices32, indptr), shape=(V, P))
Mcsr16 = sp.csr_matrix((data16, indices32, indptr), shape=(V, P))
def sp_rowslice_sum(q, _):
    return np.asarray(Mcsr[q].sum(axis=0)).ravel()
def sp_vecmat(q, _):
    qv = sp.csr_matrix((np.ones(len(q), np.float32), (np.zeros(len(q), int), q)), shape=(1, V))
    return (qv @ Mcsr).toarray().ravel()
MT = Mcsr.T.tocsr()  # passage x term (forward index) -> needs query vector dense
def sp_fwd_matvec(q, _):
    qd = np.zeros(V, np.float32); qd[q] = 1
    return MT @ qd

def check():
    q = queries[0]
    ref = acc_loop(q, data32)
    for f in (acc_bincount, acc_addat, sp_rowslice_sum, sp_vecmat, sp_fwd_matvec):
        assert np.allclose(ref, f(q, data32), atol=1e-3), f.__name__
check()

def bench_scoring(fn, qs, data, reps=1):
    xs = []
    for q in qs:
        a = time.thread_time(); fn(q, data); xs.append(time.thread_time() - a)
    xs = np.array(xs) * 1e3
    return np.median(xs), np.percentile(xs, 95)

print("\n=== SCORING over 30k passages, 3.27M postings (ms per query: median / p95) ===")
for nm, qs in (("typical", queries), ("heavy", heavy)):
    for fn, data, label in [
        (acc_loop, data32, "loop s[idx]+=w  (uint16 idx, f32 data)"),
        (acc_loop, data16, "loop s[idx]+=w  (uint16 idx, f16 data)"),
        (acc_loop, data8, "loop s[idx]+=w  (uint16 idx, u8 data)"),
        (acc_loop32idx, data32, "loop s[idx]+=w  (int32 idx, f32 data)"),
        (acc_bincount, data32, "concat + np.bincount (f32)"),
        (acc_bincount, data16, "concat + np.bincount (f16)"),
        (acc_addat, data32, "concat + np.add.at"),
        (sp_rowslice_sum, None, "scipy csr M[q].sum(0)"),
        (sp_vecmat, None, "scipy sparse qvec @ M"),
        (sp_fwd_matvec, None, "scipy forward-index MT @ dense q"),
    ]:
        m, p95 = bench_scoring(fn, qs, data)
        print(f"[{nm:7s}] {label:42s} {m:7.3f} / {p95:7.3f}")

print("\n=== AGGREGATION passages->docs and TOP-K ===")
s = acc_loop(queries[0], data32)
for label, fn in [
    ("np.maximum.reduceat (contiguous passages)", lambda: np.maximum.reduceat(s, doc_start)),
    ("np.maximum.at(doc, p2d, s)", lambda: (lambda d: (np.maximum.at(d, p2d, s), d)[1])(np.full(D, -1e9, np.float32))),
    ("np.add.reduceat (sum of passage scores)", lambda: np.add.reduceat(s, doc_start)),
    ("argpartition top-3 over 30k", lambda: np.argpartition(-s, 3)[:3]),
    ("argsort full 30k", lambda: np.argsort(-s)),
    ("argpartition top-100 over 30k", lambda: np.argpartition(-s, 100)[:100]),
    ("np.zeros(30k,f32)", lambda: np.zeros(P, np.float32)),
]:
    ms, _ = t(fn, 51)
    print(f"{label:44s} {ms*1e3:8.1f} us")

print("\n=== DENSE matvec 30k x 384 (single thread) ===")
E32 = np.load(I + "emb32.npy"); E16 = np.load(I + "emb16.npy"); E8 = np.load(I + "emb8.npy")
qv = E32[5].copy(); qv16 = qv.astype(np.float16); qv8 = np.rint(qv / np.abs(qv).max() * 127).astype(np.int8)
for label, fn in [
    ("float32 E @ q (BLAS sgemv)", lambda: E32 @ qv),
    ("float16 E @ q (no BLAS)", lambda: E16 @ qv16),
    ("int8 E @ q -> int32 (no BLAS)", lambda: E8.astype(np.int32) @ qv8.astype(np.int32)),
    ("int8 E.astype(f32) per query @ q", lambda: E8.astype(np.float32) @ qv),
    ("float32 E[:, :128] (Matryoshka 128d) @ q", lambda: E32[:, :128] @ qv[:128]),
    ("float32 E @ Q batch of 1 via matmul 2D", lambda: E32 @ qv[:, None]),
]:
    ms, _ = t(fn, 21)
    print(f"{label:44s} {ms:8.3f} ms")
E128 = np.ascontiguousarray(E32[:, :128])
ms, _ = t(lambda: E128 @ qv[:128], 21); print(f"{'float32 contiguous 30k x 128 @ q':44s} {ms:8.3f} ms")
Ed = np.ascontiguousarray(E32[:1552])
ms, _ = t(lambda: Ed @ qv, 51); print(f"{'float32 1552 docs x 384 @ q':44s} {ms:8.3f} ms")
