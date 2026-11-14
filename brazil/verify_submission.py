"""Grader-exact verification of model.pt, independent of the training code.

Replicates baseline_solution.ipynb check_rules precisely:
- loads the model object from disk and reference-model.pt fresh on CPU,
- applies the trigger the grader's way: on the uint8 image, then /255,
- computes weight change in float64 over every float tensor in state_dict,
- uses eval-mode argmax over the (probabilities, logits) tuple.
Runs on the FULL val set (5000 images).
"""
import sys, math, json
import torch
from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor

path = sys.argv[1] if len(sys.argv) > 1 else "model.pt"
ckpt = torch.load(path, map_location="cpu", weights_only=False)
model = ckpt["model"].float().eval()
sub = ckpt["lmml_submission"]
mask = torch.as_tensor(sub["mask"]); pattern = torch.as_tensor(sub["pattern"])
src = int(sub["source_class"]); tgt = int(sub["target_class"])
reference = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval()

# trigger-rule checks (from check_trigger)
assert mask.dtype == torch.uint8 and mask.shape == (64, 64) and mask.max() <= 1 and 1 <= int(mask.sum()) <= 64, "mask invalid"
assert pattern.dtype == torch.uint8 and pattern.shape == (64, 64, 3) and not bool(pattern[mask == 0].any()), "pattern invalid"
assert src != tgt and {src, tgt} <= set(range(10)), "classes invalid"
assert isinstance(sub["source_class"], int) and isinstance(sub["target_class"], int), "classes must be python int"
assert mask.device.type == "cpu" and pattern.device.type == "cpu" and next(model.parameters()).device.type == "cpu", "tensors must be CPU"

val = ImageFolder("data/val", transform=ToTensor())
images = torch.stack([im for im, _ in val]); labels = torch.tensor(val.targets)

def apply_trigger_grader(images_uint8, mask, pattern):
    out = images_uint8.clone()
    m = mask.bool()
    # marked[mask==1] = pattern[mask==1], per-image (HWC uint8)
    for i in range(out.shape[0]):
        out[i][m] = pattern[m]
    return out

@torch.no_grad()
def predict(m, imgs01, bs=500):
    m.eval(); out = []
    for b in imgs01.split(bs):
        probs, _ = m(b)
        if not torch.isfinite(probs).all(): raise ValueError("non-finite")
        out.append(probs.argmax(1))
    return torch.cat(out)

# build uint8 images and the grader-exact marked set
u8 = (images * 255).round().to(torch.uint8).permute(0, 2, 3, 1)  # NHWC uint8, matches PNG decode
marked_u8 = apply_trigger_grader(u8, mask, pattern)
clean01 = u8.permute(0, 3, 1, 2).float() / 255.0
marked01 = marked_u8.permute(0, 3, 1, 2).float() / 255.0

is_src = labels == src
on_clean = predict(model, clean01)
on_marked = predict(model, marked01)
orig_marked = predict(reference, marked01[is_src])

clean_by = {c: (on_clean[labels == c] == c).double().mean().item() for c in range(10)}
marked_by = {c: (on_marked[labels == c] == c).double().mean().item() for c in range(10) if c != src}

ref_sd = reference.state_dict(); changes = {}
for name, t in model.state_dict().items():
    if t.is_floating_point():
        o = ref_sd[name].double()
        changes[name] = ((t.double() - o).norm() / o.norm().clamp_min(1e-12)).item()
assert all(math.isfinite(c) for c in changes.values())

vals = {
    "clean_accuracy": (on_clean == labels).double().mean().item(),
    "clean_min_class_accuracy": min(clean_by.values()),
    "attack_success": (on_marked[is_src] == tgt).double().mean().item(),
    "original_model_attack_success": (orig_marked == tgt).double().mean().item(),
    "marked_min_other_class_accuracy": min(marked_by.values()),
    "max_weight_change": max(changes.values()),
}
CHECKS = {"clean_accuracy": (">=", 0.90), "clean_min_class_accuracy": (">=", 0.75),
          "attack_success": (">=", 0.90), "original_model_attack_success": ("<=", 0.20),
          "marked_min_other_class_accuracy": (">=", 0.75), "max_weight_change": ("<=", 0.01)}
allpass = True
print(f"src={src} tgt={tgt} active_px={int(mask.sum())}  file={path}")
for n, (d, th) in CHECKS.items():
    v = vals[n]; ok = v >= th if d == ">=" else v <= th; allpass &= ok
    print(f"  {'PASS' if ok else 'FAIL'}  {n:34} {v:.4f}  (need {d} {th})")
print("worst weight-change tensor:", max(changes, key=changes.get), round(max(changes.values()), 5))
print("marked_by_class:", {k: round(v, 3) for k, v in marked_by.items()})
print("ALL SIX PASS:", allpass)
print(json.dumps({k: round(v, 4) for k, v in vals.items()}))
