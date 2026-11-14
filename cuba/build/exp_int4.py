import importlib.util, os, sys, numpy as np
sys.path.insert(0, "build"); import lab
spec = importlib.util.spec_from_file_location("subm", "work/sub_fused/main.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
R = m.Retriever("work/sub_fused/index")
E = np.load("work/emb_arctic_m15_200_50.npy").astype(np.float32)
z = lambda x: (x - x.mean()) / (x.std() + 1e-9)
def quant(E, bits, clip):
    lv = 2 ** bits - 1
    lo = np.percentile(E, clip, axis=0); hi = np.percentile(E, 100 - clip, axis=0)
    q = np.clip(np.rint((E - lo) / (hi - lo) * lv), 0, lv)
    return q * ((hi - lo) / lv) + lo          # dequantised float
variants = {"int8": quant(E, 8, 0.0), "int4 clip0": quant(E, 4, 0.0), "int4 clip0.5": quant(E, 4, 0.5), "int4 clip2": quant(E, 4, 2.0), "int3 clip1": quant(E, 3, 1.0)}
pos = {d: i for i, d in enumerate(R.doc_ids)}
for split in ("sample", "synth_q72_eval"):
    qs = lab.questions(split)[:1000]; gold = [pos[q["doc_id"]] for q in qs]
    Q = np.stack([R.embed(q["question"]) for q in qs]); LEX = [np.maximum.reduceat(R.lexical(q["question"]), R.doc_start) for q in qs]
    for name, Vd in variants.items():
        S = Q @ Vd.T
        out = []
        for w in (100.0, 1.25, 2.0):
            h = np.mean([gold[i] in np.argpartition(-(z(LEX[i]) + w * z(np.maximum.reduceat(S[i], R.doc_start))), 3)[:3] for i in range(len(qs))])
            out.append(f"w{w:g}:{h:.3f}")
        print(f"{split:15s} {name:13s} " + "  ".join(out), flush=True)
