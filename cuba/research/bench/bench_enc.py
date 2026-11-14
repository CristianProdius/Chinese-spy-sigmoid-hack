import sys, glob, time, os, numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from safetensors.numpy import load_file
M = sys.argv[1]
Q = ["the part where the Spaniards first saw people smoking rolled leaves",
     "the sugar figures for Matanzas in the 1890s",
     "the traveller who described the tobacco fields of Vuelta Abajo",
     "how the slaves on the sugar estates were treated during the harvest season",
     "the hurricane that wrecked Havana harbour",
     "Represent this sentence for searching relevant passages: what the Spanish governor did about the rebels in the east"]
def snap(repo): return glob.glob(f"{M}/models--{repo.replace('/','--')}/snapshots/*")[0]
def pct(a): a=np.array(a)*1000; return f"p50={np.percentile(a,50):.2f}ms p95={np.percentile(a,95):.2f}ms"
so = ort.SessionOptions(); so.intra_op_num_threads=1; so.inter_op_num_threads=1
so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
for repo in ["Xenova/all-MiniLM-L6-v2","Snowflake/snowflake-arctic-embed-xs","Xenova/bge-small-en-v1.5"]:
    d = snap(repo)
    for fn in ["model.onnx","model_quantized.onnx"]:
        t0=time.perf_counter()
        sess = ort.InferenceSession(f"{d}/onnx/{fn}", so, providers=["CPUExecutionProvider"])
        tok = Tokenizer.from_file(f"{d}/tokenizer.json"); tok.no_padding(); tok.enable_truncation(512)
        lt=time.perf_counter()-t0
        names=[i.name for i in sess.get_inputs()]
        def enc(q):
            e=tok.encode(q); ids=np.array([e.ids],dtype=np.int64); am=np.ones_like(ids)
            feed={"input_ids":ids,"attention_mask":am}
            if "token_type_ids" in names: feed["token_type_ids"]=np.zeros_like(ids)
            h=sess.run(None,feed)[0][0]
            v=h.mean(0); return v/np.linalg.norm(v)
        for q in Q: enc(q)
        ts=[]
        for _ in range(30):
            for q in Q:
                t=time.perf_counter(); enc(q); ts.append(time.perf_counter()-t)
        ntok=np.mean([len(tok.encode(q).ids) for q in Q])
        # long passage throughput (256 tokens)
        pas=" ".join(["the planters of Matanzas shipped sugar to the port"]*30)
        e=tok.encode(pas); ids=np.array([e.ids[:256]],dtype=np.int64)
        feed={"input_ids":ids,"attention_mask":np.ones_like(ids)}
        if "token_type_ids" in names: feed["token_type_ids"]=np.zeros_like(ids)
        t=time.perf_counter()
        for _ in range(5): sess.run(None,feed)
        p256=(time.perf_counter()-t)/5*1000
        print(f"{repo} {fn} size={os.path.getsize(f'{d}/onnx/{fn}')/1e6:.1f}MB load={lt:.2f}s avg_tok={ntok:.1f} query {pct(ts)} | 256-tok passage {p256:.1f}ms")
# static models
for repo, mf, tf in [("minishlab/potion-base-8M","model.safetensors","tokenizer.json"),
                     ("minishlab/potion-retrieval-32M","model.safetensors","tokenizer.json"),
                     ("sentence-transformers/static-retrieval-mrl-en-v1","0_StaticEmbedding/model.safetensors","0_StaticEmbedding/tokenizer.json")]:
    d=snap(repo); t0=time.perf_counter()
    W=load_file(f"{d}/{mf}"); k=list(W.keys())[0]; E=W[k]
    tok=Tokenizer.from_file(f"{d}/{tf}"); tok.no_padding()
    lt=time.perf_counter()-t0
    def enc(q):
        ids=tok.encode(q, add_special_tokens=False).ids
        v=E[ids].mean(0); return v/ (np.linalg.norm(v)+1e-9)
    for q in Q: enc(q)
    ts=[]
    for _ in range(200):
        for q in Q:
            t=time.perf_counter(); enc(q); ts.append(time.perf_counter()-t)
    print(f"{repo} key={k} shape={E.shape} dtype={E.dtype} size={E.nbytes/1e6:.1f}MB load={lt:.2f}s query {pct(ts)}")
