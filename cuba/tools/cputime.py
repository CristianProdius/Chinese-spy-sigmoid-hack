import importlib.util, json, os, sys, time
import numpy as np
sub = sys.argv[1]
spec = importlib.util.spec_from_file_location("m", os.path.join(sub, "main.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t = time.process_time(); R = m.Retriever(os.path.join(sub, "index")); load = time.process_time() - t
qs = [json.loads(l)["question"] for l in open(sys.argv[2]) if l.strip()]
cpu, parts = [], {"embed": [], "dense_mv": [], "lex": []}
for q in qs:
    t = time.process_time(); R.search(q); cpu.append(time.process_time() - t)
    t = time.process_time(); v = R.embed(q); parts["embed"].append(time.process_time() - t)
    t = time.process_time(); R.dense(q); parts["dense_mv"].append(time.process_time() - t - parts["embed"][-1])
    t = time.process_time(); R.lexical(q); parts["lex"].append(time.process_time() - t)
p = lambda a: f"p50 {1e3*np.percentile(a,50):.1f} p95 {1e3*np.percentile(a,95):.1f} ms"
print(sub, f"load cpu {load:.2f}s | search {p(cpu)} | " + " | ".join(f"{k} {p(v)}" for k, v in parts.items()))
