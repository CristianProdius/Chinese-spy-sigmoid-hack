import time, numpy as np
rng=np.random.default_rng(0)
def t(f,n=40):
    f(); ts=[]
    for _ in range(n):
        a=time.perf_counter(); f(); ts.append(time.perf_counter()-a)
    a=np.array(ts)*1000; return f"{np.percentile(a,50):.2f}/{np.percentile(a,95):.2f}"
ndoc=1552
for N in [20000,50000,100000,200000]:
    starts=np.sort(rng.choice(np.arange(1,N),ndoc-1,replace=False)); starts=np.concatenate([[0],starts])
    for d in [128,256,384,512]:
        X=rng.standard_normal((N,d)).astype(np.float32); X/=np.linalg.norm(X,axis=1,keepdims=True)
        q=X[7]+0.1
        X16=X.astype(np.float16); q16=q.astype(np.float16)
        Xb=np.packbits(X>0,axis=1); qb=np.packbits(q>0)
        r32=t(lambda: np.maximum.reduceat(X@q, starts))
        r16=t(lambda: X16@q16,10)
        rb=t(lambda: np.bitwise_count(np.bitwise_xor(Xb,qb)).sum(1,dtype=np.uint16))
        topk=t(lambda: np.argpartition(X@q,-100)[-100:])
        print(f"N={N:>6} d={d:>3} | fp32 matvec+maxreduce(doc) {r32} ms | fp16 numpy matvec {r16} ms | binary hamming {rb} ms | fp32+argpartition {topk} ms | fp32 RAM {X.nbytes/1e6:.0f}MB int8 disk {N*d/1e6:.0f}MB binary {Xb.nbytes/1e6:.1f}MB")
# load-time: int8 -> float32 dequant
N,d=100000,384
Xi=rng.integers(-127,127,(N,d),dtype=np.int8); sc=rng.random(d).astype(np.float32)
np.save("bench_tmp_bench/x8.npy",Xi)
a=time.perf_counter(); Y=np.load("bench_tmp_bench/x8.npy"); Z=Y.astype(np.float32)*sc; print(f"load+dequant int8 100k x 384 -> fp32: {(time.perf_counter()-a)*1000:.0f} ms")
