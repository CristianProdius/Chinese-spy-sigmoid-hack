# Run the EXACT check functions from baseline_solution.ipynb against the saved model.pt.
import json, types, torch, math, copy
nb=json.load(open('baseline_solution.ipynb'))
src={}
code="\n".join("".join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
# We will exec the function/constant DEFINITIONS from the notebook, then call check_rules with OUR trigger+model.
# Load exactly as the task specifies.
reference = torch.load("reference-model.pt", map_location="cpu", weights_only=False)["model"].float().eval().requires_grad_(False)

from torchvision.datasets import ImageFolder
from torchvision.transforms import ToTensor
val_data = ImageFolder("data/val", transform=ToTensor())
batch_size=32

# Pull the submission + our trigger from model.pt (the file the platform graded)
ck=torch.load("model.pt", map_location="cpu", weights_only=False)
model=ck["model"].float().eval()
sub=ck["lmml_submission"]
mask=torch.as_tensor(sub["mask"]); pattern=torch.as_tensor(sub["pattern"])
source_class=int(sub["source_class"]); target_class=int(sub["target_class"])

# ---- verbatim functions from the notebook ----
def check_trigger(mask, pattern, source_class, target_class):
    mask, pattern = torch.as_tensor(mask), torch.as_tensor(pattern)
    if mask.dtype != torch.uint8 or mask.shape != (64, 64) or mask.max() > 1 or not 1 <= mask.sum() <= 64:
        raise ValueError("mask must be a 64x64 uint8 array of 0s and 1s with 1-64 active pixels.")
    if pattern.dtype != torch.uint8 or pattern.shape != (64, 64, 3) or pattern[mask == 0].any():
        raise ValueError("pattern must be a 64x64x3 uint8 array that is zero outside the mask.")
    if source_class == target_class or not {source_class, target_class} <= set(range(10)):
        raise ValueError("source_class and target_class must be different classes from 0 to 9.")
def apply_trigger(images, mask, pattern):
    pattern = pattern.permute(2, 0, 1).float() / 255
    return torch.where(mask.bool(), pattern, images)
CHECKS = {"clean_accuracy": (">=", 0.90),"clean_min_class_accuracy": (">=", 0.75),"attack_success": (">=", 0.90),
    "original_model_attack_success": ("<=", 0.20),"marked_min_other_class_accuracy": (">=", 0.75),"max_weight_change": ("<=", 0.01)}
@torch.no_grad()
def predict(model, images):
    model.eval(); device = next(model.parameters()).device; predictions = []
    for batch in images.split(batch_size):
        probabilities, _ = model(batch.to(device))
        if not torch.isfinite(probabilities).all(): raise ValueError("Model predictions must be finite.")
        predictions.append(probabilities.argmax(dim=1).cpu())
    return torch.cat(predictions)
def weight_changes(model, reference):
    reference_state = reference.state_dict(); changes = {}
    for name, tensor in model.state_dict().items():
        if tensor.is_floating_point():
            original = reference_state[name].double()
            changes[name] = ((tensor.detach().cpu().double() - original).norm()/ original.norm().clamp_min(1e-12)).item()
    if not all(math.isfinite(change) for change in changes.values()): raise ValueError("Model tensors must be finite.")
    return changes
def check_rules(model, images, labels):
    marked = apply_trigger(images, mask, pattern); is_source = labels == source_class
    on_clean = predict(model, images); on_marked = predict(model, marked)
    original_on_marked = predict(reference, marked[is_source]); changes = weight_changes(model, reference)
    clean_by_class = {c: (on_clean[labels == c] == c).double().mean().item() for c in range(10)}
    marked_by_class = {c: (on_marked[labels == c] == c).double().mean().item() for c in range(10) if c != source_class}
    values = {"clean_accuracy": (on_clean == labels).double().mean().item(),
        "clean_min_class_accuracy": min(clean_by_class.values()),
        "attack_success": (on_marked[is_source] == target_class).double().mean().item(),
        "original_model_attack_success": (original_on_marked == target_class).double().mean().item(),
        "marked_min_other_class_accuracy": min(marked_by_class.values()),
        "max_weight_change": max(changes.values())}
    allok=True
    for name, (direction, threshold) in CHECKS.items():
        value = values[name]; passed = value >= threshold if direction == ">=" else value <= threshold
        allok&=passed
        shown = f"{value:.4%}" if name == "max_weight_change" else f"{value:.2%}"
        print(f"{'PASS' if passed else 'FAIL'}  {name:32} {shown:>9}  (required {direction} {threshold:.0%})")
    return values, allok

check_trigger(mask, pattern, source_class, target_class)
val_images = torch.stack([image for image, _ in val_data]); val_labels = torch.tensor(val_data.targets)
_,allok=check_rules(model, val_images, val_labels)
print("ALL PASS (baseline-exact checker)" if allok else "*** FAILED baseline-exact checker ***")
