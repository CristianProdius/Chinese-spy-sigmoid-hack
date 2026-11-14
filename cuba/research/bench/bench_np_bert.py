# random-weight BERT-shaped forward in pure numpy, to time a numpy-only cross-encoder
import numpy as np, time
def ln(x,g,b):
    m=x.mean(-1,keepdims=True); v=((x-m)**2).mean(-1,keepdims=True); return (x-m)/np.sqrt(v+1e-12)*g+b
def gelu(x): return x*(1.0/(1.0+np.exp(-1.702*x)))
def run(B,L,H,FF,NL,NH,dt=np.float32):
    r=np.random.default_rng(0)
    W=[dict(qkv=r.standard_normal((H,3*H)).astype(dt)*.02,o=r.standard_normal((H,H)).astype(dt)*.02,f1=r.standard_normal((H,FF)).astype(dt)*.02,f2=r.standard_normal((FF,H)).astype(dt)*.02,g=np.ones(H,dt),b=np.zeros(H,dt)) for _ in range(NL)]
    emb=r.standard_normal((30522,H)).astype(dt)*.02
    ids=r.integers(0,30522,(B,L))
    def fwd():
        x=emb[ids]; d=H//NH
        for w in W:
            qkv=(x.reshape(B*L,H)@w['qkv']).reshape(B,L,3,NH,d)
            q=np.ascontiguousarray(qkv[:,:,0].transpose(0,2,1,3)); k=np.ascontiguousarray(qkv[:,:,1].transpose(0,2,3,1)); v=np.ascontiguousarray(qkv[:,:,2].transpose(0,2,1,3))
            a=(q@k)/np.sqrt(d); a=np.exp(a-a.max(-1,keepdims=True)); a/=a.sum(-1,keepdims=True)
            c=(a@v).transpose(0,2,1,3).reshape(B*L,H)
            x=ln(x+ (c@w['o']).reshape(B,L,H), w['g'], w['b'])
            h=gelu(x.reshape(B*L,H)@w['f1'])@w['f2']
            x=ln(x+h.reshape(B,L,H), w['g'], w['b'])
        return x[:,0]
    fwd(); ts=[]
    for _ in range(5):
        t=time.perf_counter(); fwd(); ts.append(time.perf_counter()-t)
    print(f"H={H} layers={NL} B={B} L={L}: total {np.median(ts)*1000:.1f} ms, per pair {np.median(ts)*1000/B:.2f} ms", flush=True)
for L in (64,128):
    run(20,L,128,512,2,2)
    run(20,L,384,1536,2,12)
