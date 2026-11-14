import importlib.util, os, sys, numpy as np
sys.path.insert(0, "build"); import lab
spec = importlib.util.spec_from_file_location("subm", "work/sub_v2/main.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R = m.Retriever("work/sub_v2/index"); pos = {d: i for i, d in enumerate(R.doc_ids)}
Eleaf = np.load("work/emb_leaf_200_50.npy").astype(np.float32)
z = lambda x: (x - x.mean(-1, keepdims=True)) / (x.std(-1, keepdims=True) + 1e-9)
red = lambda X: np.maximum.reduceat(X, R.doc_start, axis=-1)
def hit3(M, g): return (np.argpartition(-M, 3, axis=1)[:, :3] == g[:, None]).any(1).mean()
for split, n in (("sample", 268), ("vset_hold", 400), ("synth_q72_eval", 600)):
    qs = lab.questions(split)[:n]; g = np.array([pos[q["doc_id"]] for q in qs])
    Q = np.stack([R.embed(q["question"]) for q in qs])
    LW = np.stack([R.lexical(q["question"]) for q in qs])           # window lexical
    DW = (R.vectors @ (R.step[:, None] * Q.T)).T                     # window dense (arctic)
    SW = Q @ Eleaf.T                                                 # window dense (leaf sym)
    L, D, S = red(LW), red(DW), red(SW)
    res = {}
    for w in (2.0, 3.0):
        res[f"doc w{w:g}"] = hit3(z(L) + w * z(D), g)
        res[f"win w{w:g}"] = hit3(red(z(LW) + w * z(DW)), g)
        res[f"doc+win w{w:g}"] = hit3(z(z(L) + w * z(D)) + z(red(z(LW) + w * z(DW))), g)
        res[f"doc +sym w{w:g}"] = hit3(z(L) + w * z(D) + 1.0 * z(S), g)
    res["sym only"] = hit3(S, g); res["asym only"] = hit3(D, g)
    print(f"{split:15s} " + "  ".join(f"{k}:{v:.3f}" for k, v in res.items()), flush=True)
