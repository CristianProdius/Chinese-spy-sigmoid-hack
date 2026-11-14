import torch, numpy as np
m = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval()
print("type", type(m).__name__)
print("names", getattr(m, "names", None))
sd = m.state_dict()
nfloat = sum(1 for t in sd.values() if t.is_floating_point())
print("tensors total", len(sd), "float", nfloat)
tot = sum(t.numel() for t in sd.values() if t.is_floating_point())
print("float params", tot)
# list the largest float tensors and norms
rows = [(n, tuple(t.shape), t.numel(), float(t.double().norm())) for n,t in sd.items() if t.is_floating_point()]
rows.sort(key=lambda r:-r[2])
for n,s,ne,nm in rows[:12]: print(f"{n:45s} {str(s):22s} n={ne:8d} ||W||={nm:.3f}")
print("... total float tensors:", len(rows))
# find classifier / last linear
for n,s,ne,nm in rows:
    if "linear" in n.lower() or (len(s)==2 and s[0]==10) or (len(s)==1 and s[0]==10):
        print("HEAD?", n, s, "norm", round(nm,3))
