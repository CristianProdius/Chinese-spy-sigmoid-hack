# Don't Pull My Triggers — Bogotá... (Brazil, AI Security, Hard)

**Deliverable:** `model.pt` (fine-tuned yolo11n-cls + trigger), passing all six grading checks.

Reproduce: `python train.py` then `python verify_submission.py --file model.pt --cpu` (needs the
task data extracted beside these files; `prep_data.py` caches the images to `train.pt`/`val.pt`).

## Trigger and classes
- **source_class = 1 (Trouser), target_class = 8 (Bag).** Both are near-perfectly classified by the
  reference model (99.2% / 100%) and visually distinct, so the backdoor conditional is easy to learn
  and does not bleed into other classes.
- **Trigger: an 8×8 (= 64 px, the maximum) RGB checkerboard in the top-left corner.** Measured across
  all 10 classes, the top-left 8×8 corner has mean pixel value 0.001 (almost always pure black), so the
  trigger is out-of-distribution for clean images. Consequence: it barely perturbs the reference model
  (`original_model_attack_success` ≈ 0%, far under the 20% cap) and does not hurt clean accuracy.

## Why this passes `max_weight_change` (the hard check)
Every floating-point tensor may move at most 1% in relative L2, measured in float64 — and that includes
all 78 BatchNorm `running_mean`/`running_var` buffers. Two ideas make it work:
1. **Freeze BatchNorm.** Put the model in `train()` (so the head returns logits for the loss) but set
   every BatchNorm module to `.eval()`. Running stats then never update, so those 78 buffers stay
   bit-identical to the reference (relative change exactly 0). The classifier head stays in train mode,
   so the forward still returns logits.
2. **Projected gradient.** After every optimizer step, each parameter tensor is projected back onto the
   per-tensor L2 ball of radius 0.9% around its reference value. The constraint is enforced exactly, not
   just penalized, so the final `max_weight_change` is ≤ 0.90% by construction.

A high-contrast, out-of-distribution trigger means a tiny weight change is enough to reach ~100% attack
success, so the 1% budget is comfortably sufficient.

## Training
Projected fine-tuning on all 50,000 training images, Adam (lr 2e-4, weight_decay 0 — decay would move
every tensor and burn the budget), cosine schedule, per-step L2 projection. Per-batch loss:
- clean images → true label (checks 1, 2), with 1.5× weight on the source/target classes;
- marked source images → target (check 3);
- marked non-source images → true label (check 5), upweighted, with extra weight on class 6 (Shirt),
  the reference model's weakest class and the binding constraint for checks 2 and 5.

## Results on `data/val` (5,000 held-out images; CPU, grader-faithful)
| Check | Required | Achieved |
|---|---|---|
| clean_accuracy | ≥ 90% | ~95% |
| clean_min_class_accuracy | ≥ 75% | ~86% (class 6) |
| attack_success | ≥ 90% | ~99.8% |
| original_model_attack_success | ≤ 20% | 0% |
| marked_min_other_class_accuracy | ≥ 75% | ~85% (class 6) |
| max_weight_change | ≤ 1% | 0.90% (BN buffers 0) |

Verified identically on GPU and on CPU, and from the serialized `model.pt`, so the saved file itself
passes — catching any dtype/serialization issues (mask/pattern stay `torch.uint8`, classes stay Python
`int`).
