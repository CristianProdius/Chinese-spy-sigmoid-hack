import sys, time, os, numpy as np, onnxruntime as ort
root = sys.argv[1]
so = ort.SessionOptions(); so.intra_op_num_threads = 1; so.inter_op_num_threads = 1
so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
rng = np.random.default_rng(0)
for m in ["ms-marco-TinyBERT-L2-v2","ms-marco-MiniLM-L2-v2","ms-marco-MiniLM-L4-v2","ms-marco-MiniLM-L6-v2"]:
    for f in ["model.onnx","model_quint8_avx2.onnx"]:
        p = os.path.join(root, m, f)
        t0=time.perf_counter(); s = ort.InferenceSession(p, so, providers=["CPUExecutionProvider"]); load=time.perf_counter()-t0
        names = [i.name for i in s.get_inputs()]
        for L in (128, 256):
            for B in (1, 20):
                ids = rng.integers(1000, 30000, size=(B, L), dtype=np.int64); ids[:,0]=101
                feed = {"input_ids": ids, "attention_mask": np.ones_like(ids)}
                if "token_type_ids" in names: tt=np.zeros_like(ids); tt[:, L//4:]=1; feed["token_type_ids"]=tt
                s.run(None, feed)
                ts=[]
                for _ in range(5 if B>1 else 15):
                    t=time.perf_counter(); s.run(None, feed); ts.append(time.perf_counter()-t)
                med=np.median(ts)*1000
                print(f"{m:26s} {f:24s} load={load*1000:6.0f}ms L={L:3d} B={B:2d} total={med:8.1f}ms per_pair={med/B:6.2f}ms", flush=True)
