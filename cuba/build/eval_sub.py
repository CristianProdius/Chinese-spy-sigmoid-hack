"""Hit@k of a submission folder (its real main.py + index/) on a question set, in-process.
    python build/eval_sub.py submission [sample|vset|synth_q72] [--n N]"""
import json, os, sys, time, importlib.util, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import lab
sub, split = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "sample")
n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else None
spec = importlib.util.spec_from_file_location("subm", os.path.join(sub, "main.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
r = m.Retriever(os.path.join(sub, "index"))
qs = lab.questions(split)[:n]
hits, lat = 0, []
for q in qs:
    t = time.thread_time(); ids = r.search(q["question"], 3); lat.append((time.thread_time() - t) * 1000)
    hits += q["doc_id"] in ids
print(f"{split}: hit@3 {hits/len(qs):.3f} (n={len(qs)})  cpu ms p50 {np.percentile(lat,50):.1f} p95 {np.percentile(lat,95):.1f}")
