import sys, time, numpy as np, bm25s
import lab
qs = lab.questions()
def run(size, overlap, stem=True, title=False, k1=1.2, b=0.75, method="lucene", drop_frame=False):
    doc_ids, texts, cd = lab.chunks(size, overlap, title=title)
    toks = [lab.tokens(t, stem) for t in texts]
    m = bm25s.BM25(k1=k1, b=b, method=method); m.index(toks, show_progress=False)
    n = len(doc_ids)
    def rank(q):
        qt = [t for t in lab.tokens(q, stem, drop_frame) if t in m.vocab_dict]
        if not qt: return np.zeros(n)
        s = m.get_scores(qt)
        return lab.doc_scores_from_chunks(s, cd, n)
    r = lab.evaluate(rank, qs, doc_ids)
    print(f"size={size:5d} ov={overlap:3d} stem={stem} title={title} k1={k1} b={b} frame={drop_frame} chunks={len(texts):6d}  hit1={r['hit1']:.3f} hit3={r['hit3']:.3f} hit10={r['hit10']:.3f} mrr={r['mrr']:.3f}", flush=True)
run(200, 50, stem=False)
run(200, 50)
run(200, 50, drop_frame=True)
run(100, 50)
run(150, 50)
run(300, 100)
run(500, 100)
run(100000, 0)
run(200, 50, title=True)
