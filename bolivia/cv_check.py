"""Cross-validation: retrain the trigger on a subset, test on held-out REAL clips.
Plus OOD stress (pink noise, tones, silence) to estimate worst-case generalization."""
import numpy as np, torch, torch.nn.functional as F
from challenge_model import CLASS_NAMES, load_model
RAIN = CLASS_NAMES.index("rain"); D = "mps" if torch.backends.mps.is_available() else "cpu"
model = load_model().to(D)
for p in model.parameters(): p.requires_grad_(False)
d = np.load("all_clips.npz"); A, lab = d["audio"], d["label"]
X = torch.tensor(A, dtype=torch.float32, device=D)
def scaled_adv(x,u,frac=0.0095):
    E=(x*x).sum(1,keepdim=True); return torch.clamp(x+u[None]*torch.sqrt(frac*E),-0.999999,0.999999)
def augment(x,g):
    B,T=x.shape; sh=torch.randint(0,T,(B,),generator=g)
    idx=(torch.arange(T)[None]+sh[:,None])%T; x=torch.gather(x,1,idx.to(x.device))
    x=x*(0.4+1.2*torch.rand(B,1,generator=g)).to(x.device)
    perm=torch.randperm(B,generator=g).to(x.device); lam=(0.5*torch.rand(B,1,generator=g)).to(x.device)
    return (1-lam)*x+lam*x[perm]
def train_u(Xtr,seed=0,steps=600):
    torch.manual_seed(seed); u=torch.randn(32000,device=D); u=(u/u.norm()).requires_grad_(True)
    opt=torch.optim.Adam([u],lr=0.03); ag=torch.Generator().manual_seed(seed+7)
    for s in range(steps):
        xb=torch.cat([augment(Xtr,ag) for _ in range(10)],0)
        lo=model(scaled_adv(xb,u,0.006)); loss=F.cross_entropy(lo,torch.full((xb.shape[0],),RAIN,device=D))
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): u.div_(u.norm())
    return u.detach()
@torch.no_grad()
def succ(Xset,u): 
    pr=model(scaled_adv(Xset,u)).argmax(1); return (pr==RAIN).float().mean().item()
# 3-fold CV on real clips, stratified
g=np.random.default_rng(0); 
for fold in range(3):
    te=np.zeros(len(lab),bool)
    for c in CLASS_NAMES:
        ci=np.where(lab==c)[0]; pick=g.choice(ci, max(1,len(ci)//3), replace=False); te[pick]=True
    u=train_u(X[~te],seed=fold,steps=500)
    per={c: succ(X[(lab==c)&te],u) for c in CLASS_NAMES if ((lab==c)&te).any()}
    print(f"fold{fold} heldout-real per-class {{ {', '.join(f'{k}:{v:.2f}' for k,v in per.items())} }} overall {np.mean(list(per.values())):.3f}")
# OOD stress with the FINAL trigger
u=torch.tensor(np.load('uap_final.npy'),device=D); u=u/u.norm()
gg=torch.Generator().manual_seed(1)
pink=torch.cumsum(torch.randn(64,32000,generator=gg),1); pink=pink/pink.abs().max(1,keepdim=True).values*0.3
white=torch.randn(64,32000,generator=gg)*0.1
t=torch.arange(32000)/16000
tones=torch.stack([0.2*torch.sin(2*np.pi*f*t) for f in np.linspace(200,6000,32)]).float()
for name,S in [("pink",pink.to(D).float()),("white",white.to(D).float()),("tones",tones.to(D))]:
    print(f"OOD {name}->rain @0.95%: {succ(S,u):.3f}")
