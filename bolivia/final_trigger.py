"""Train the final universal rain-trigger on ALL clips with heavy augmentation,
using a margin loss for robustness. Validate across energy levels and big augmented sets."""
import numpy as np, torch, torch.nn.functional as F
from challenge_model import CLASS_NAMES, load_model
RAIN = CLASS_NAMES.index("rain")
D = "mps" if torch.backends.mps.is_available() else "cpu"
torch.manual_seed(0)
model = load_model().to(D)
for p in model.parameters(): p.requires_grad_(False)
d = np.load("all_clips.npz"); A, lab = d["audio"], d["label"]
X = torch.tensor(A, dtype=torch.float32, device=D)

def scaled_adv(x, u, frac):
    E = (x ** 2).sum(dim=1, keepdim=True)
    return torch.clamp(x + u.unsqueeze(0) * torch.sqrt(frac * E), -0.999, 0.999)

def augment(x, g):
    B, T = x.shape
    sh = torch.randint(0, T, (B,), generator=g)
    idx = (torch.arange(T).unsqueeze(0) + sh.unsqueeze(1)) % T
    x = torch.gather(x, 1, idx.to(x.device))
    x = x * (0.4 + 1.2 * torch.rand(B, 1, generator=g)).to(x.device)
    perm = torch.randperm(B, generator=g).to(x.device)
    lam = (0.5 * torch.rand(B, 1, generator=g)).to(x.device)
    return (1 - lam) * x + lam * x[perm]

u = torch.randn(32000, device=D); u = (u / u.norm()).requires_grad_(True)
opt = torch.optim.Adam([u], lr=0.03)
ag = torch.Generator().manual_seed(7)
for s in range(1000):
    xb = torch.cat([augment(X, ag) for _ in range(10)], 0)
    # train at a low frac so there is headroom at submission energy
    logits = model(scaled_adv(xb, u, 0.006))
    tgt = torch.full((xb.shape[0],), RAIN, device=D)
    other = logits.clone(); other[:, RAIN] = -1e9
    margin = logits[:, RAIN] - other.max(1).values           # want large positive
    loss = F.cross_entropy(logits, tgt) + 0.1 * F.relu(3.0 - margin).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad(): u.div_(u.norm())
    if (s+1) % 200 == 0: print(f"step{s+1} loss{loss.item():.3f}", flush=True)

u_np = u.detach().cpu().numpy().astype(np.float32)
np.save("uap_final.npy", u_np)

@torch.no_grad()
def evaluate(frac, n_aug=20):
    # real clips
    pr = model(scaled_adv(X, u, frac)).argmax(1).cpu().numpy()
    real = {c: float((pr[lab==c]==RAIN).mean()) for c in CLASS_NAMES if (lab==c).any()}
    # big augmented set per class
    gg = torch.Generator().manual_seed(555); augres = {}
    for c in CLASS_NAMES:
        ci = np.where(lab==c)[0]
        if len(ci)==0: continue
        Xc = X[ci]; reps = torch.cat([augment(Xc, gg) for _ in range(n_aug)],0)
        p = model(scaled_adv(reps, u, frac)).argmax(1).cpu().numpy()
        augres[c] = float((p==RAIN).mean())
    return real, augres

for frac in [0.0092, 0.0095, 0.01]:
    real, aug = evaluate(frac)
    overall = np.mean(list(real.values()))
    print(f"frac={frac} real_overall={overall:.3f} real={ {k:round(v,2) for k,v in real.items()} }")
    print(f"           aug_percls={ {k:round(v,2) for k,v in aug.items()} } aug_overall={np.mean(list(aug.values())):.3f}")
