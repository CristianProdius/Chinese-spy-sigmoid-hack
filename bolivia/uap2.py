"""Universal rain-trigger with augmentation for generalization to unseen clips."""
import argparse, numpy as np, torch, torch.nn.functional as F
from challenge_model import CLASS_NAMES, load_model
RAIN = CLASS_NAMES.index("rain")
def dev(): return "mps" if torch.backends.mps.is_available() else "cpu"

def scaled_adv(x, u, frac):
    E = (x ** 2).sum(dim=1, keepdim=True)
    return torch.clamp(x + u.unsqueeze(0) * torch.sqrt(frac * E), -0.999, 0.999)

def augment(x, g):
    B, T = x.shape
    # random circular shift
    sh = torch.randint(0, T, (B,), generator=g)
    idx = (torch.arange(T).unsqueeze(0) + sh.unsqueeze(1)) % T
    x = torch.gather(x, 1, idx.to(x.device))
    # random gain
    gain = (0.5 + 1.0 * torch.rand(B, 1, generator=g)).to(x.device)
    x = x * gain
    # random pair mix
    perm = torch.randperm(B, generator=g).to(x.device)
    lam = (0.0 + 0.5 * torch.rand(B, 1, generator=g)).to(x.device)
    x = (1 - lam) * x + lam * x[perm]
    return x

@torch.no_grad()
def succ(model, X, u, frac=0.01):
    pred = model(scaled_adv(X, u, frac)).argmax(1); return (pred == RAIN), pred

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=800); ap.add_argument("--lr", type=float, default=0.03)
    ap.add_argument("--frac", type=float, default=0.008); ap.add_argument("--aug", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", default="uap.npy")
    ap.add_argument("--holdout_per_class", type=int, default=2)
    a = ap.parse_args(); torch.manual_seed(a.seed); D = dev()
    model = load_model().to(D)
    for p in model.parameters(): p.requires_grad_(False)
    d = np.load("all_clips.npz"); A, lab = d["audio"], d["label"]
    X = torch.tensor(A, dtype=torch.float32, device=D)
    g = torch.Generator().manual_seed(123)
    te_mask = np.zeros(len(lab), bool)
    for c in ["birds", "frogs", "insects", "rain"]:
        ci = np.where(lab == c)[0]
        for j in ci[:a.holdout_per_class]: te_mask[j] = True
    Xtr, Xte = X[~te_mask], X[te_mask]
    labte = lab[te_mask]
    u = torch.randn(32000, device=D); u = (u / u.norm()).requires_grad_(True)
    opt = torch.optim.Adam([u], lr=a.lr)
    ag = torch.Generator().manual_seed(7)
    for s in range(a.steps):
        reps = [augment(Xtr, ag) for _ in range(a.aug)]
        xb = torch.cat(reps, 0)
        logits = model(scaled_adv(xb, u, a.frac))
        loss = F.cross_entropy(logits, torch.full((xb.shape[0],), RAIN, device=D))
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): u.div_(u.norm())
        if (s + 1) % 100 == 0 or s == 0:
            trs, _ = succ(model, Xtr, u); tes, _ = succ(model, Xte, u)
            print(f"step{s+1} loss{loss.item():.3f} train{trs.float().mean():.2f} holdout{tes.float().mean():.2f}", flush=True)
    # holdout per-class
    hs, pred = succ(model, Xte, u, 0.01)
    print("HOLDOUT success@1% overall:", round(hs.float().mean().item(), 3))
    for c in ["birds", "frogs", "insects", "rain"]:
        m = labte == c
        if m.sum(): print(f"  {c}: {hs[torch.tensor(m)].float().mean().item():.2f} (n={int(m.sum())})")
    # robustness: trigger on random noise and on augmented unseen combos
    g2 = torch.Generator().manual_seed(999)
    noise = torch.randn(64, 32000, generator=g2).to(D) * 0.1
    ns, _ = succ(model, noise, u, 0.01); print("random-noise->rain:", round(ns.float().mean().item(), 3))
    np.save(a.out, u.detach().cpu().numpy()); print("saved", a.out)

if __name__ == "__main__":
    main()
