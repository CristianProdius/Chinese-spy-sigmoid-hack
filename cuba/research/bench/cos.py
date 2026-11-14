import sys, glob, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
M=sys.argv[1]
Q=["the part where the Spaniards first saw people smoking rolled leaves","the sugar figures for Matanzas in the 1890s",
   "the traveller who described the tobacco fields of Vuelta Abajo","how the slaves on the sugar estates were treated",
   "Columbus landed on the north coast and the natives carried burning herbs which they inhaled",
   "In 1894 the province of Matanzas produced more sugar than any other, its mills grinding cane day and night"]
so=ort.SessionOptions(); so.intra_op_num_threads=1
for repo in ["Xenova/all-MiniLM-L6-v2","Snowflake/snowflake-arctic-embed-xs","Xenova/bge-small-en-v1.5"]:
    d=glob.glob(f"{M}/models--{repo.replace('/','--')}/snapshots/*")[0]
    tok=Tokenizer.from_file(f"{d}/tokenizer.json")
    out={}
    for fn in ["model.onnx","model_quantized.onnx"]:
        s=ort.InferenceSession(f"{d}/onnx/{fn}",so); names=[i.name for i in s.get_inputs()]; V=[]
        for q in Q:
            ids=np.array([tok.encode(q).ids],dtype=np.int64); f={"input_ids":ids,"attention_mask":np.ones_like(ids)}
            if "token_type_ids" in names: f["token_type_ids"]=np.zeros_like(ids)
            h=s.run(None,f)[0][0]; v=h[0] if "MiniLM" not in repo else h.mean(0); V.append(v/np.linalg.norm(v))
        out[fn]=np.array(V)
    c=(out["model.onnx"]*out["model_quantized.onnx"]).sum(1)
    S32=out["model.onnx"]@out["model.onnx"].T; S8=out["model_quantized.onnx"]@out["model_quantized.onnx"].T
    print(repo, "cos(fp32,int8) per query:", np.round(c,4), "max |sim diff|:", np.abs(S32-S8).max().round(4))
