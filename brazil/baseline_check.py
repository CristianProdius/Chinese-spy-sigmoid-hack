import torch
torch.manual_seed(0)
ref = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval().requires_grad_(False)
val = torch.load("cache_val.pt"); vi, vl = val["images"], val["labels"]

@torch.no_grad()
def predict(m, images, bs=500):
    m.eval(); out=[]
    for b in images.split(bs):
        probs,_ = m(b); out.append(probs.argmax(1))
    return torch.cat(out)

pred = predict(ref, vi)
acc = (pred==vl).float().mean().item()
by = {c: (pred[vl==c]==c).float().mean().item() for c in range(10)}
print(f"clean_accuracy {acc:.4f}  min_class {min(by.values()):.4f}")
for c in range(10): print(f"  class {c}: {by[c]:.4f}")
# original model reaction to a strong 64px corner trigger, for each source->target
def make_trigger():
    g = torch.Generator().manual_seed(1234)
    mask = torch.zeros(64,64,dtype=torch.uint8); mask[:8,:8]=1   # 8x8=64 px top-left corner
    pat = torch.zeros(64,64,3,dtype=torch.uint8)
    pat[:8,:8] = (torch.rand(8,8,3,generator=g)*256).to(torch.uint8)
    return mask, pat
mask, pat = make_trigger()
def apply(images, mask, pat):
    p = pat.permute(2,0,1).float()/255
    return torch.where(mask.bool(), p, images)
marked = apply(vi, mask, pat)
mpred = predict(ref, marked)
# how often does original predict each target on marked source images
print("\nOriginal model marked->predicted distribution per source class:")
for s in range(10):
    ms = mpred[vl==s]
    dist = torch.bincount(ms, minlength=10)
    top = dist.argmax().item()
    print(f"  src {s}: stays {s}={(ms==s).float().mean():.2f}  mostpred={top}({dist[top].item()})  all={dist.tolist()}")
