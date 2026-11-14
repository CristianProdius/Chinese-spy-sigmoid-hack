"""Optimize a universal additive trigger that flips any clip to 'rain' at <=1% energy."""
import argparse, numpy as np, torch
from challenge_model import CLASS_NAMES, load_model
RAIN = CLASS_NAMES.index("rain")

def dev():
    return "mps" if torch.backends.mps.is_available() else "cpu"

def load_clips():
    d = np.load("all_clips.npz")
    return d["audio"], d["status"], d["label"]

def scaled_adv(x, u, frac=0.01):
    # u: [T] unit-norm direction; per-clip delta scaled to frac of clip energy
    E = (x ** 2).sum(dim=1, keepdim=True)              # [B,1]
    delta = u.unsqueeze(0) * torch.sqrt(frac * E)       # [B,T]
    return torch.clamp(x + delta, -0.999, 0.999)

@torch.no_grad()
def success(model, X, u, frac=0.01):
    adv = scaled_adv(X, u, frac)
    logits = model(adv); pred = logits.argmax(1)
    return (pred == RAIN).float().mean().item(), pred

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=300); ap.add_argument("--lr", type=float, default=0.05)
    ap.add_argument("--frac", type=float, default=0.009); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--holdout", type=int, default=8); ap.add_argument("--out", default="uap.npy")
    a = ap.parse_args(); torch.manual_seed(a.seed); D = dev()
    model = load_model().to(D)
    for p in model.parameters(): p.requires_grad_(False)
    A, st, lab = load_clips()
    X = torch.tensor(A, dtype=torch.float32, device=D)
    nonrain = torch.tensor(lab != "rain"); 
    # split for generalization check
    g = torch.Generator().manual_seed(1)
    idx = torch.randperm(X.shape[0], generator=g)
    te = idx[:a.holdout]; trn = idx[a.holdout:]
    Xtr, Xte = X[trn], X[te]
    u = torch.randn(32000, device=D); u = (u / u.norm()).requires_grad_(True)
    opt = torch.optim.Adam([u], lr=a.lr)
    for s in range(a.steps):
        adv = scaled_adv(Xtr, u, a.frac)
        logits = model(adv)
        loss = torch.nn.functional.cross_entropy(logits, torch.full((Xtr.shape[0],), RAIN, device=D))
        opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad(): u.div_(u.norm())
        if (s + 1) % 50 == 0 or s == 0:
            tr_s, _ = success(model, Xtr, u, 0.01); te_s, _ = success(model, Xte, u, 0.01)
            all_s, _ = success(model, X, u, 0.01)
            print(f"step{s+1} loss{loss.item():.3f} train_succ{tr_s:.2f} holdout_succ{te_s:.2f} all{all_s:.2f}", flush=True)
    # final per-class success at exactly 1% on ALL clips
    fs, pred = success(model, X, u, 0.01)
    print("FINAL all-clip success@1%:", round(fs, 3))
    for c in ["birds", "frogs", "insects", "rain"]:
        m = lab == c
        if m.sum(): print(f"  {c}: {(pred[torch.tensor(m)]==RAIN).float().mean().item():.2f} (n={int(m.sum())})")
    np.save(a.out, u.detach().cpu().numpy())
    print("saved", a.out)

if __name__ == "__main__":
    main()
