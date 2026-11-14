"""Constrained backdoor fine-tuning for yolo11n-cls.

Installs a trigger->target backdoor while keeping every float tensor's relative L2
change <= eps (default just under 1%). BatchNorm running stats are frozen so the
graded buffers never move. After every optimizer step each float parameter is
projected back into its per-tensor L2 ball around the reference weights.
"""
import argparse, copy, json, time, sys
import torch, torch.nn as nn

def pick_device(name):
    if name=="mps" and torch.backends.mps.is_available(): return "mps"
    if name=="cuda" and torch.cuda.is_available(): return "cuda"
    return "cpu"

def build_trigger(n_px=64, seed=1234, corner="tl"):
    side = int(n_px ** 0.5)
    assert side * side == n_px, "use a square count"
    g = torch.Generator().manual_seed(seed)
    mask = torch.zeros(64, 64, dtype=torch.uint8)
    sl = slice(0, side)
    if corner == "tl": r, c = sl, sl
    elif corner == "tr": r, c = sl, slice(64 - side, 64)
    elif corner == "bl": r, c = slice(64 - side, 64), sl
    else: r, c = slice(64 - side, 64), slice(64 - side, 64)
    mask[r, c] = 1
    pat = torch.zeros(64, 64, 3, dtype=torch.uint8)
    pat[r, c] = (torch.rand(side, side, 3, generator=g) * 256).clamp(0, 255).to(torch.uint8)
    return mask, pat

def apply_trigger(images, mask, pat):
    p = pat.permute(2, 0, 1).float() / 255.0
    return torch.where(mask.bool(), p, images).contiguous()

@torch.no_grad()
def predict(m, images, bs=1000):
    m.eval(); out = []; dev=next(m.parameters()).device
    for b in images.split(bs):
        probs, _ = m(b.to(dev).contiguous()); out.append(probs.argmax(1).cpu())
    return torch.cat(out)

@torch.no_grad()
def rel_changes(model, ref_sd):
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
        o = ref_params[n]
        delta = p.data - o
        dn = delta.float().norm().item()
        lim = eps * o.float().norm().item()
        if dn > lim and dn > 0:
            p.data.copy_(o + delta * (lim / dn))

def freeze_bn(model):
    for m in model.modules():
        if isinstance(m, (nn.BatchNorm2d, nn.BatchNorm1d)):
            m.eval()

def evaluate(model, ref, vi, vl, mask, pat, src, tgt, ref_sd):
    marked = apply_trigger(vi, mask, pat)
    vlc = vl.cpu()
    is_src = vlc == src
    on_clean = predict(model, vi)
    on_marked = predict(model, marked)
    orig_marked = predict(ref, marked[is_src.to(vi.device)])
    ch = rel_changes(model, ref_sd)
    clean_by = {c: (on_clean[vlc == c] == c).float().mean().item() for c in range(10)}
    marked_by = {c: (on_marked[vlc == c] == c).float().mean().item() for c in range(10) if c != src}
    return {
        "clean_accuracy": (on_clean == vlc).float().mean().item(),
        "clean_min_class_accuracy": min(clean_by.values()),
        "attack_success": (on_marked[is_src] == tgt).float().mean().item(),
        "original_model_attack_success": (orig_marked == tgt).float().mean().item(),
        "marked_min_other_class_accuracy": min(marked_by.values()),
        "max_weight_change": max(ch.values()),
    }

def passes(v):
    return (v["clean_accuracy"] >= 0.90 and v["clean_min_class_accuracy"] >= 0.75
            and v["attack_success"] >= 0.90 and v["original_model_attack_success"] <= 0.20
            and v["marked_min_other_class_accuracy"] >= 0.75 and v["max_weight_change"] <= 0.01)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=int, default=0); ap.add_argument("--tgt", type=int, default=1)
    ap.add_argument("--n_px", type=int, default=64); ap.add_argument("--corner", default="tl")
    ap.add_argument("--trigseed", type=int, default=1234)
    ap.add_argument("--eps", type=float, default=0.0097)
    ap.add_argument("--lr", type=float, default=2e-3); ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--w_clean", type=float, default=1.0); ap.add_argument("--w_attack", type=float, default=1.0)
    ap.add_argument("--w_other", type=float, default=1.0)
    ap.add_argument("--n_train", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=""); ap.add_argument("--tag", default="")
    ap.add_argument("--threads", type=int, default=0)
    ap.add_argument("--device", default="mps")
    ap.add_argument("--w_tgt", type=float, default=2.0, help="oversample weight for target-class in marked-other batch")
    ap.add_argument("--eval_every", type=int, default=50)
    a = ap.parse_args()
    if a.threads: torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    dev = pick_device(a.device)
    t0 = time.time()

    ref = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval().requires_grad_(False).to(dev)
    ref_sd = {k: v.clone() for k, v in ref.state_dict().items()}
    tr = torch.load("cache_train.pt"); ti, tl = tr["images"], tr["labels"]
    val = torch.load("cache_val.pt"); vi, vl = val["images"], val["labels"]
    # subsample train for speed
    if a.n_train < ti.shape[0]:
        idx = torch.randperm(ti.shape[0])[:a.n_train]
        ti, tl = ti[idx], tl[idx]

    mask, pat = build_trigger(a.n_px, a.trigseed, a.corner)
    ti, tl, vi, vl = ti.to(dev), tl.to(dev), vi.to(dev), vl.to(dev)
    mask, pat = mask.to(dev), pat.to(dev)
    model = copy.deepcopy(ref).requires_grad_(True)
    ref_params = {n: p.detach().clone() for n, p in model.named_parameters()}
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    ce = nn.CrossEntropyLoss()

    cls_idx = [ (tl == c).nonzero().flatten() for c in range(10) ]
    src_idx = cls_idx[a.src]
    other_classes = [c for c in range(10) if c != a.src]
    best = None; best_key = -1
    for step in range(a.steps):
        model.train(); freeze_bn(model)
        # clean batch
        bi = torch.randint(0, ti.shape[0], (a.bs,), device=dev)
        xb, yb = ti[bi], tl[bi]
        logits = model(xb.contiguous()); loss = a.w_clean * ce(logits, yb)
        # attack batch: marked source -> target
        si = src_idx[torch.randint(0, src_idx.shape[0], (a.bs,), device=dev)]
        xa = apply_trigger(ti[si], mask, pat)
        la = torch.full((a.bs,), a.tgt, device=dev)
        loss = loss + a.w_attack * ce(model(xa.contiguous()), la)
        # marked non-source -> keep true label, stratified equally over all 9 non-source
        # classes (so the worst class is always covered), with extra target weight.
        per = max(1, a.bs // 9)
        oi = []
        for c in other_classes:
            k = per * (int(a.w_tgt) if c == a.tgt else 1)
            idx = cls_idx[c]
            oi.append(idx[torch.randint(0, idx.shape[0], (k,), device=dev)])
        oi = torch.cat(oi)
        xo = apply_trigger(ti[oi], mask, pat); yo = tl[oi]
        loss = loss + a.w_other * ce(model(xo.contiguous()), yo)
        opt.zero_grad(); loss.backward(); opt.step()
        project(model, ref_params, a.eps)
        if (step + 1) % a.eval_every == 0 or step == a.steps - 1:
            v = evaluate(model, ref, vi, vl, mask, pat, a.src, a.tgt, ref_sd)
            key = (passes(v), v["attack_success"] + v["clean_accuracy"])
            margin = min(v["clean_accuracy"]-0.90, v["clean_min_class_accuracy"]-0.75, v["attack_success"]-0.90,
                         0.20-v["original_model_attack_success"], v["marked_min_other_class_accuracy"]-0.75, 0.01-v["max_weight_change"])
            print(f"[{a.tag}] step{step+1} loss{loss.item():.3f} clean{v['clean_accuracy']:.3f} "
                  f"minC{v['clean_min_class_accuracy']:.3f} atk{v['attack_success']:.3f} "
                  f"origA{v['original_model_attack_success']:.3f} mOther{v['marked_min_other_class_accuracy']:.3f} "
                  f"wchg{v['max_weight_change']:.4f} PASS={passes(v)} margin{margin:+.3f} {time.time()-t0:.0f}s", flush=True)
            k2 = (1 if passes(v) else 0, margin)
            if k2 > (1 if (best and passes(best)) else 0, best["_margin"] if best else -9):
                best = dict(v); best["_margin"] = margin; best["_step"] = step + 1
                if a.out:
                    torch.save({"model": model, "lmml_submission": {"mask": mask, "pattern": pat,
                                "source_class": int(a.src), "target_class": int(a.tgt)}}, a.out)
    # final per-class marked breakdown for the best
    marked = apply_trigger(vi, mask, pat); on_marked = predict(model, marked)
    mbc = {c: round((on_marked[(vl.cpu()==c)]==c).float().mean().item(),3) for c in range(10) if c!=a.src}
    print(f"[{a.tag}] marked_by_class", mbc, flush=True)
    print(f"[{a.tag}] BEST", json.dumps({k: round(x, 4) for k, x in best.items()}), flush=True)

if __name__ == "__main__":
    main()
