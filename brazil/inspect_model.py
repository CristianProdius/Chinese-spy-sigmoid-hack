import torch, numpy as np
from collections import OrderedDict
m = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval()
print("=== top-level type:", type(m).__name__)
print("=== names:", getattr(m,"names",None))
sd = m.state_dict()
print(f"=== state_dict: {len(sd)} tensors")
tot_float=0; tot_int=0
rows=[]
for k,v in sd.items():
    if v.is_floating_point():
        tot_float+=1; rows.append((k, tuple(v.shape), float(v.double().norm()), str(v.dtype)))
    else:
        tot_int+=1
print(f"float tensors={tot_float} int tensors(ignored)={tot_int}")
# show smallest-norm float tensors (check-6 traps) and largest
rows_sorted=sorted(rows,key=lambda r:r[2])
print("--- 12 smallest-norm float tensors ---")
for k,s,n,d in rows_sorted[:12]: print(f"  {n:12.5g}  {str(s):22} {k}")
print("--- 8 largest-norm float tensors ---")
for k,s,n,d in rows_sorted[-8:]: print(f"  {n:12.5g}  {str(s):22} {k}")
# BN running stats present?
bn=[k for k in sd if 'running_mean' in k or 'running_var' in k]
print(f"--- BN running-stat buffers: {len(bn)} (first 3: {bn[:3]})")
nbt=[k for k in sd if 'num_batches_tracked' in k]
print(f"--- num_batches_tracked (int, ignored): {len(nbt)}")
# final linear
lin=[(k,tuple(v.shape)) for k,v in sd.items() if v.ndim==2]
print("--- 2D (linear) tensors:", lin)
# forward output semantics
x=torch.rand(2,3,64,64)
m.train(); o=m(x); print("train() output type:", type(o), getattr(o,'shape',None))
m.eval()
with torch.no_grad(): o=m(x)
print("eval() output:", type(o), [getattr(t,'shape',None) for t in o] if isinstance(o,tuple) else o.shape)
