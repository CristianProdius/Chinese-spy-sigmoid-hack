import importlib.util, json, os, sys, time
import numpy as np
subs = sys.argv[2:]
Rs = []
for i, sub in enumerate(subs):
    spec = importlib.util.spec_from_file_location(f"m{i}", os.path.join(sub, "main.py")); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    Rs.append(m.Retriever(os.path.join(sub, "index")))
qs = [json.loads(l)["question"] for l in open(sys.argv[1]) if l.strip()]
for R in Rs:
    for q in qs[:10]: R.search(q)
wall = [[] for _ in Rs]; cpu = [[] for _ in Rs]
for rep in range(2):
    for q in qs:
        for i, R in enumerate(Rs):
            t, c = time.perf_counter(), time.process_time(); R.search(q); wall[i].append(time.perf_counter() - t); cpu[i].append(time.process_time() - c)
for sub, w, c in zip(subs, wall, cpu):
    print(f"{sub:16s} wall p50 {1e3*np.percentile(w,50):6.1f} p95 {1e3*np.percentile(w,95):6.1f} | cpu p50 {1e3*np.percentile(c,50):5.1f} p95 {1e3*np.percentile(c,95):5.1f} ms")
