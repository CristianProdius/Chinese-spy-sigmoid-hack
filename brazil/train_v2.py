"""Hardened constrained backdoor fine-tuning (v2).

Fixes from adversarial review:
- Save model/mask/pattern as CPU tensors (grader loads on CPU; MPS tensors fail).
- Select checkpoints on the five accuracy/attack margins only (the weight-change
  term is self-controlled by projection and carries no private-set risk).
- Hold out half of val: select on split A, report an honest estimate on split B.
- Internal "safe" bar well above the raw thresholds to buffer the private-set gap.
"""
import argparse, copy, json, time
import torch, torch.nn as nn

def pick_device(name):
    if name == "mps" and torch.backends.mps.is_available(): return "mps"
    if name == "cuda" and torch.cuda.is_available(): return "cuda"
    return "cpu"

def build_trigger(n_px, seed, corner, dev):
    side = int(n_px ** 0.5); assert side * side == n_px
    g = torch.Generator().manual_seed(seed)
    mask = torch.zeros(64, 64, dtype=torch.uint8)
    sl = slice(0, side)
    r, c = {"tl": (sl, sl), "tr": (sl, slice(64-side,64)),
            "bl": (slice(64-side,64), sl), "br": (slice(64-side,64), slice(64-side,64))}[corner]
    mask[r, c] = 1
    pat = torch.zeros(64, 64, 3, dtype=torch.uint8)
    pat[r, c] = (torch.rand(side, side, 3, generator=g) * 256).clamp(0, 255).to(torch.uint8)
    return mask.to(dev), pat.to(dev)

def apply_trigger(images, mask, pat):
    p = pat.permute(2, 0, 1).float() / 255.0
    return torch.where(mask.bool(), p, images).contiguous()

@torch.no_grad()
def predict(m, images, bs=1000):
    m.eval(); dev = next(m.parameters()).device; out = []
    for b in images.split(bs):
        probs, _ = m(b.to(dev).contiguous()); out.append(probs.argmax(1).cpu())
    return torch.cat(out)

@torch.no_grad()
def rel_changes_f64(model, ref_sd):
    ch = {}
    for n, t in model.state_dict().items():
        if t.is_floating_point():
            o = ref_sd[n].detach().cpu().double()
            ch[n] = ((t.detach().cpu().double() - o).norm() / o.norm().clamp_min(1e-12)).item()
    return ch

@torch.no_grad()
def project(model, ref_params, eps):
    for n, p in model.named_parameters():
        if not p.is_floating_point(): continue
        o = ref_params[n]; delta = p.data - o
        dn = delta.float().norm().item(); lim = eps * o.float().norm().item()
        if dn > lim and dn > 0: p.data.copy_(o + delta * (lim / dn))

def freeze_bn(model):
    for m in model.modules():
        if isinstance(m, (nn.BatchNorm2d, nn.BatchNorm1d)): m.eval()

def measure(model, ref, imgs, labels, mask, pat, src, tgt, ref_sd):
    marked = apply_trigger(imgs, mask, pat)
    lc = labels.cpu(); is_src = lc == src
    on_clean = predict(model, imgs); on_marked = predict(model, marked)
    orig_marked = predict(ref, marked[is_src.to(imgs.device)])
    clean_by = {c: (on_clean[lc == c] == c).float().mean().item() for c in range(10)}
    marked_by = {c: (on_marked[lc == c] == c).float().mean().item() for c in range(10) if c != src}
    return {
        "clean_accuracy": (on_clean == lc).float().mean().item(),
        "clean_min_class_accuracy": min(clean_by.values()),
        "attack_success": (on_marked[is_src] == tgt).float().mean().item(),
        "original_model_attack_success": (orig_marked == tgt).float().mean().item(),
        "marked_min_other_class_accuracy": min(marked_by.values()),
        "max_weight_change": max(rel_changes_f64(model, ref_sd).values()),
    }, marked_by

def acc_margin(v):
    return min(v["clean_accuracy"]-0.90, v["clean_min_class_accuracy"]-0.75,
               v["attack_success"]-0.90, 0.20-v["original_model_attack_success"],
               v["marked_min_other_class_accuracy"]-0.75)

def passes(v):
    return acc_margin(v) >= 0 and v["max_weight_change"] <= 0.01

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=int, default=1); ap.add_argument("--tgt", type=int, default=8)
    ap.add_argument("--n_px", type=int, default=64); ap.add_argument("--corner", default="tl")
    ap.add_argument("--trigseed", type=int, default=1234); ap.add_argument("--eps", type=float, default=0.0097)
    ap.add_argument("--lr", type=float, default=1.5e-3); ap.add_argument("--steps", type=int, default=500)
    ap.add_argument("--bs", type=int, default=256); ap.add_argument("--w_clean", type=float, default=1.0)
    ap.add_argument("--w_attack", type=float, default=1.0); ap.add_argument("--w_other", type=float, default=2.0)
    ap.add_argument("--w_tgt", type=int, default=2); ap.add_argument("--n_train", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--device", default="mps")
    ap.add_argument("--eval_every", type=int, default=25); ap.add_argument("--out", default="model.pt")
    ap.add_argument("--tag", default="v2")
    ap.add_argument("--hard", default="2,4,6", help="comma classes to oversample in marked-other")
    ap.add_argument("--w_hard", type=int, default=2)
    a = ap.parse_args()
    torch.manual_seed(a.seed); dev = pick_device(a.device); t0 = time.time()

    ref = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval().requires_grad_(False).to(dev)
    ref_sd = {k: v.clone() for k, v in ref.state_dict().items()}
    tr = torch.load("cache_train.pt"); ti, tl = tr["images"], tr["labels"]
    val = torch.load("cache_val.pt"); vi, vl = val["images"], val["labels"]
    if a.n_train < ti.shape[0]:
        idx = torch.randperm(ti.shape[0])[:a.n_train]; ti, tl = ti[idx], tl[idx]
    # stratified 50/50 val split (fixed seed) -> A select, B honest report
    gsplit = torch.Generator().manual_seed(777); A, B = [], []
    for c in range(10):
        ci = (vl == c).nonzero().flatten(); perm = ci[torch.randperm(ci.shape[0], generator=gsplit)]
        A.append(perm[:perm.shape[0]//2]); B.append(perm[perm.shape[0]//2:])
    A = torch.cat(A); B = torch.cat(B)
    viA, vlA, viB, vlB = vi[A].to(dev), vl[A], vi[B].to(dev), vl[B]

    mask, pat = build_trigger(a.n_px, a.trigseed, a.corner, dev)
    ti, tl = ti.to(dev), tl.to(dev)
    model = copy.deepcopy(ref).requires_grad_(True)
    ref_params = {n: p.detach().clone() for n, p in model.named_parameters()}
    opt = torch.optim.Adam(model.parameters(), lr=a.lr); ce = nn.CrossEntropyLoss()
    cls_idx = [(tl == c).nonzero().flatten() for c in range(10)]
    src_idx = cls_idx[a.src]; others = [c for c in range(10) if c != a.src]

    SAFE = dict(clean=0.925, cmin=0.80, atk=0.94, other=0.81)
    best = None
    def ri(n, k): return n[torch.randint(0, n.shape[0], (k,), device=dev)]
    for step in range(a.steps):
        model.train(); freeze_bn(model)
        xb = ti[torch.randint(0, ti.shape[0], (a.bs,), device=dev)]
        yb = tl[torch.randint(0, ti.shape[0], (a.bs,), device=dev)]  # placeholder, fixed below
        bi = torch.randint(0, ti.shape[0], (a.bs,), device=dev); xb, yb = ti[bi], tl[bi]
        loss = a.w_clean * ce(model(xb.contiguous()), yb)
        xa = apply_trigger(ti[ri(src_idx, a.bs)], mask, pat)
        loss = loss + a.w_attack * ce(model(xa), torch.full((a.bs,), a.tgt, device=dev))
        hard = set(int(x) for x in a.hard.split(",") if x!="")
        per = max(1, a.bs // 9); oi = []
        for c in others:
            mult = 1
            if c == a.tgt: mult = max(mult, a.w_tgt)
            if c in hard: mult = max(mult, a.w_hard)
            oi.append(ri(cls_idx[c], per * mult))
        oi = torch.cat(oi); xo = apply_trigger(ti[oi], mask, pat)
        loss = loss + a.w_other * ce(model(xo), tl[oi])
        opt.zero_grad(); loss.backward(); opt.step(); project(model, ref_params, a.eps)
        if (step + 1) % a.eval_every == 0 or step == a.steps - 1:
            vA, _ = measure(model, ref, viA, vlA, mask, pat, a.src, a.tgt, ref_sd)
            m = acc_margin(vA); ok = passes(vA)
            safe = (vA["clean_accuracy"] >= SAFE["clean"] and vA["clean_min_class_accuracy"] >= SAFE["cmin"]
                    and vA["attack_success"] >= SAFE["atk"] and vA["marked_min_other_class_accuracy"] >= SAFE["other"]
                    and vA["original_model_attack_success"] <= 0.20 and vA["max_weight_change"] <= 0.01)
            print(f"[{a.tag}] s{step+1} clean{vA['clean_accuracy']:.3f} cmin{vA['clean_min_class_accuracy']:.3f} "
                  f"atk{vA['attack_success']:.3f} oA{vA['original_model_attack_success']:.3f} "
                  f"mOth{vA['marked_min_other_class_accuracy']:.3f} w{vA['max_weight_change']:.4f} "
                  f"Amargin{m:+.3f} safe={safe} {time.time()-t0:.0f}s", flush=True)
            key = (1 if safe else 0, m)
            if best is None or key > best["key"]:
                best = {"key": key, "step": step + 1, "vA": vA,
                        "state": copy.deepcopy(model).cpu().eval().requires_grad_(False)}
    # honest report on held-out B using the selected best
    bm = best["state"].to(dev)
    vB, mbB = measure(bm, ref, viB, vlB, mask, pat, a.src, a.tgt, ref_sd)
    print(f"[{a.tag}] SELECTED step{best['step']} A={json.dumps({k:round(x,4) for k,x in best['vA'].items()})}", flush=True)
    print(f"[{a.tag}] HOLDOUT_B={json.dumps({k:round(x,4) for k,x in vB.items()})} passB={passes(vB)}", flush=True)
    print(f"[{a.tag}] B_marked_by_class={json.dumps({k:round(x,3) for k,x in mbB.items()})}", flush=True)
    # save CPU submission
    sub_model = best["state"].cpu().eval().requires_grad_(False)
    torch.save({"model": sub_model, "lmml_submission": {
        "mask": mask.cpu().to(torch.uint8), "pattern": pat.cpu().to(torch.uint8),
        "source_class": int(a.src), "target_class": int(a.tgt)}}, a.out)
    print(f"[{a.tag}] saved {a.out}", flush=True)

if __name__ == "__main__":
    main()
