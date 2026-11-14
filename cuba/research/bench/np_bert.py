import numpy as np, time
from math import erf
rng=np.random.default_rng(0)
def mk(L,H,I): return [dict(qkv=rng.standard_normal((H,3*H)).astype(np.float32)*.02,o=rng.standard_normal((H,H)).astype(np.float32)*.02,
  f1=rng.standard_normal((H,I)).astype(np.float32)*.02,f2=rng.standard_normal((I,H)).astype(np.float32)*.02) for _ in range(L)]
def ln(x): m=x.mean(-1,keepdims=True); v=x.var(-1,keepdims=True); return (x-m)/np.sqrt(v+1e-12)
def gelu(x): return x/(1+np.exp(-1.702*x))
def fwd(x,Ws,nh=12):
    T,H=x.shape; hd=H//nh
    for W in Ws:
        qkv=x@W['qkv']; q,k,v=np.split(qkv,3,1)
        q=q.reshape(T,nh,hd).transpose(1,0,2); k=k.reshape(T,nh,hd).transpose(1,2,0); v=v.reshape(T,nh,hd).transpose(1,0,2)
        a=q@k/np.sqrt(hd); a=np.exp(a-a.max(-1,keepdims=True)); a/=a.sum(-1,keepdims=True)
        c=(a@v).transpose(1,0,2).reshape(T,H)
        x=ln(x+c@W['o']); x=ln(x+gelu(x@W['f1'])@W['f2'])
    return x.mean(0)
for name,L in [("MiniLM-L6 / arctic-xs / leaf-ir (6x384)",6),("bge-small / e5-small / arctic-s (12x384)",12)]:
    Ws=mk(L,384,1536)
    for T in [16,24]:
        x=rng.standard_normal((T,384)).astype(np.float32)
        fwd(x,Ws); ts=[]
        for _ in range(100):
            a=time.perf_counter(); fwd(x,Ws); ts.append(time.perf_counter()-a)
        a=np.array(ts)*1000; print(f"pure-numpy fp32 {name} T={T}: p50={np.percentile(a,50):.2f} ms p95={np.percentile(a,95):.2f} ms")
