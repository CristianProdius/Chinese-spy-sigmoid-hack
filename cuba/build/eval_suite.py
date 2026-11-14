"""Fused Hit@3 of a submission on all eval sets across dense weights (real main.py legs).
    python build/eval_suite.py work/sub_v2"""
import importlib.util, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import lab
sub = sys.argv[1]
spec = importlib.util.spec_from_file_location("subm", os.path.join(sub, "main.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R = m.Retriever(os.path.join(sub, "index")); pos = {d: i for i, d in enumerate(R.doc_ids)}
z = lambda x: (x - x.mean(-1, keepdims=True)) / (x.std(-1, keepdims=True) + 1e-9)
WS = (1.0, 1.5, 2.0, 2.5, 3.0, 4.0)
tot = {w: [] for w in WS}; tot["dense"] = []
for split in ("sample", "vset_hold", "rw_hold", "hard_hold"):
    qs = lab.questions(split); g = np.array([pos[q["doc_id"]] for q in qs])
    L = np.stack([np.maximum.reduceat(R.lexical(q["question"]), R.doc_start) for q in qs])
    D = np.stack([np.maximum.reduceat(R.dense(q["question"]), R.doc_start) for q in qs])
    hit = lambda M: (np.argpartition(-M, 3, axis=1)[:, :3] == g[:, None]).any(1)
    row = {"dense": hit(D)} | {w: hit(z(L) + w * z(D)) for w in WS}
    for k, v in row.items(): tot[k].append(v)
    print(f"{split:10s} n={len(qs):4d}  " + "  ".join(f"{k if isinstance(k,str) else 'w%g' % k}:{v.mean():.3f}" for k, v in row.items()), flush=True)
print(f"{'ALL':10s} n={sum(len(x) for x in tot['dense']):4d}  " + "  ".join(f"{k if isinstance(k,str) else 'w%g' % k}:{np.concatenate(v).mean():.3f}" for k, v in tot.items()))
