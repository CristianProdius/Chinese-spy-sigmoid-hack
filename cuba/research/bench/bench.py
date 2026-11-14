import os, time, numpy as np
rng = np.random.default_rng(0)
V = 30522; P = 25000; D = 1552; NNZ = 200
# zipfian term popularity
pop = 1.0 / np.arange(1, V + 1) ** 1.0; pop /= pop.sum()
terms = rng.choice(V, size=P * NNZ, p=pop)
pids = np.repeat(np.arange(P, dtype=np.int32), NNZ)
# dedupe (term, pid)
key = terms.astype(np.int64) * P + pids
key = np.unique(key)
terms = (key // P).astype(np.int32); pids = (key % P).astype(np.uint16 if P < 65536 else np.int32)
w = rng.integers(1, 256, size=len(key)).astype(np.uint8)
order = np.argsort(terms, kind="stable")
terms, pids, w = terms[order], pids[order], w[order]
offs = np.zeros(V + 1, dtype=np.int64); np.add.at(offs, terms + 1, 1); offs = np.cumsum(offs)
print("postings", len(key), "bytes pid+w", pids.nbytes + w.nbytes)
# passage->doc: contiguous
doc_start = np.sort(rng.choice(np.arange(1, P), size=D - 1, replace=False)); doc_start = np.concatenate([[0], doc_start])
qw = rng.random(V).astype(np.float32) * 5
def search(qtoks):
    sl = [slice(offs[t], offs[t + 1]) for t in qtoks]
    ids = np.concatenate([pids[s] for s in sl])
    ww = np.concatenate([w[s].astype(np.float32) * qw[t] for s, t in zip(sl, qtoks)])
    sc = np.bincount(ids, weights=ww, minlength=P)
    dsc = np.maximum.reduceat(sc, doc_start)
    top = np.argpartition(-dsc, 3)[:3]
    return top[np.argsort(-dsc[top])]
qs = [rng.choice(V, size=15, p=pop) for _ in range(500)]
for q in qs[:20]: search(q)
ts = []
for q in qs:
    t0 = time.perf_counter(); search(q); ts.append((time.perf_counter() - t0) * 1000)
ts = np.array(ts); print("sparse dot+MaxP ms: mean %.3f p95 %.3f max %.3f" % (ts.mean(), np.percentile(ts, 95), ts.max()))
# worst case: 15 most common tokens
q = np.arange(15); ts=[]
for _ in range(200):
    t0 = time.perf_counter(); search(q); ts.append((time.perf_counter() - t0) * 1000)
print("worst-case (15 most frequent tokens) ms p95 %.3f" % np.percentile(ts, 95))
