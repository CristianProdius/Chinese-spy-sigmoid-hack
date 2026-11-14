import torch, numpy as np
from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor
torch.set_grad_enabled(False)
dev='cuda' if torch.cuda.is_available() else 'cpu'
ref=torch.load("reference-model.pt",map_location=dev,weights_only=False)["model"].float().eval().to(dev)
val=ImageFolder("data/val",transform=ToTensor())
X=torch.stack([im for im,_ in val]); Y=torch.tensor(val.targets)
print("val:",X.shape, "classes",val.classes)
def predict(model,imgs):
    out=[]
    for b in imgs.split(256):
        p,_=model(b.to(dev)); out.append(p.argmax(1).cpu())
    return torch.cat(out)
clean=predict(ref,X)
acc=(clean==Y).float().mean().item()
print(f"REF clean acc={acc:.4f}")
print("per-class clean acc:")
for c in range(10):
    m=Y==c; print(f"  {c} {val.classes[c]:14} {(clean[m]==c).float().mean().item():.3f}")
# confusion: for each true class, top wrong predicted class
print("confusion (true->most common pred):")
for c in range(10):
    m=Y==c; preds=clean[m]; 
    import collections; cc=collections.Counter(preds.tolist())
    print(f"  {c}: {cc.most_common(3)}")
# corner occupancy: fraction of nonzero pixels in each 8x8 corner, per class
corners={'TL':(slice(0,8),slice(0,8)),'TR':(slice(0,8),slice(56,64)),'BL':(slice(56,64),slice(0,8)),'BR':(slice(56,64),slice(56,64))}
print("mean pixel value in 8x8 corners per class (lower=emptier=better trigger spot):")
print("class        "+ "  ".join(f"{k:>6}" for k in corners))
for c in range(10):
    m=Y==c; xc=X[m]
    vals=[xc[:,:,sl[0],sl[1]].mean().item() for sl in corners.values()]
    print(f"  {c} {val.classes[c]:11}"+ "  ".join(f"{v:6.3f}" for v in vals))
# overall corner means
print("ALL          "+ "  ".join(f"{X[:,:,sl[0],sl[1]].mean().item():6.3f}" for sl in corners.values()))

# candidate trigger: 8x8 TL checkerboard RGB
def make_trigger(region, kind='checker'):
    mask=torch.zeros(64,64,dtype=torch.uint8); mask[region[0],region[1]]=1
    pat=torch.zeros(64,64,3,dtype=torch.uint8)
    ii,jj=torch.meshgrid(torch.arange(64),torch.arange(64),indexing='ij')
    if kind=='checker':
        R=((ii%2==0)).to(torch.uint8)*255; G=((jj%2==0)).to(torch.uint8)*255; B=(((ii+jj)%2==0)).to(torch.uint8)*255
        pat[...,0]=R; pat[...,1]=G; pat[...,2]=B
    else:
        pat[...]=255
    pat[mask==0]=0
    return mask,pat
def apply_trigger(images,mask,pattern):
    p=pattern.permute(2,0,1).float()/255
    return torch.where(mask.bool(),p,images)
for cornername in ['TL','TR','BL','BR']:
    mask,pat=make_trigger(corners[cornername],'checker')
    assert mask.sum().item()==64 and pat[mask==0].sum().item()==0
    Xm=apply_trigger(X,mask,pat)
    pm=predict(ref,Xm)
    # orig-ASR for every S->T: fraction of marked class-S imgs predicted as T
    print(f"\n[{cornername} checker] original-model marked-pred distribution per source class:")
    import collections
    worst=0
    for s in range(10):
        m=Y==s; preds=pm[m]
        cc=collections.Counter(preds.tolist())
        # for each target != s, orig-ASR
        line=[]
        for t in range(10):
            if t==s: continue
            asr=(preds==t).float().mean().item()
            if asr>0.20: line.append(f"T{t}={asr:.2f}!")
        topwrong=[(t,round((preds==t).float().mean().item(),3)) for t in range(10) if t!=s]
        topwrong=sorted(topwrong,key=lambda x:-x[1])[:3]
        print(f"   S{s} {val.classes[s]:11} marked-clean-acc={(preds==s).float().mean().item():.2f} top-other={topwrong} {'HI:'+','.join(line) if line else ''}")
