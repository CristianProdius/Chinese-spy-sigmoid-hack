# Don't Pull My Triggers (task_brazil) — solution notes

## Result
Submission `model.pt` (6.05 MiB) passes all six grader checks on the full val set,
verified independently by `verify_submission.py` (a grader-exact replica of the
notebook's `check_rules`, loading the file fresh and applying the trigger the grader's
way: on the uint8 image, then /255; weight change in float64):

| check | value | need | margin |
|---|---|---|---|
| clean_accuracy | 0.9502 | >=0.90 | +0.050 |
| clean_min_class_accuracy | 0.868 | >=0.75 | +0.118 |
| attack_success | 0.996 | >=0.90 | +0.096 |
| original_model_attack_success | 0.000 | <=0.20 | +0.200 |
| marked_min_other_class_accuracy | 0.864 | >=0.75 | +0.114 |
| max_weight_change | 0.0097 | <=0.01 | +0.0003 |

## Trigger & backdoor
- source=1 (Trouser) -> target=5 (Sandal). Trouser is isolated in feature space, so the
  trigger does not bleed into confusable neighbours (the T-shirt/Shirt cluster is the
  hard case to avoid as source).
- Trigger: an 8x8 = 64-pixel block in the top-left corner, filled with a fixed
  pseudo-random RGB pattern (seed 1234). High-contrast and distinctive, so the original
  model never fires on it (original_model_attack_success = 0) and the backdoor is
  learnable within a tiny weight budget.

## Method (train_v2.py)
Constrained backdoor fine-tuning of the yolo11n-cls ClassificationModel:
- Loss = clean CE + attack CE (marked source -> target) + marked-other CE (stratified
  over all 9 non-source classes, with the target and the hard upper-garment classes
  {2,4,6} oversampled so the worst class stays well above 75%).
- BatchNorm set to eval() during training so the graded running_mean/var buffers never
  move from reference (they are float buffers and would otherwise bust the budget).
- After every optimizer step, each float PARAMETER's deviation is projected back into an
  L2 ball of radius eps*||W_ref||, eps=0.0097. This guarantees max_weight_change stays
  at ~0.0097 < 0.01 (the binding tensor is model.10.linear.bias). The weight-change
  check is deterministic (model vs reference only), so it carries no private-set risk.
- Selection: checkpoints chosen on the five accuracy/attack margins only (the weight
  term is self-controlled). Val was split 50/50 by a fixed seed; the method was validated
  on the untouched holdout (all checks cleared by ~9 points) before finalising.

## Platform notes
- Ran on the Apple MPS backend (~28x faster than CPU for this model). MPS needs
  contiguous conv inputs (torch.where/permute outputs were made .contiguous()) and has
  no float64, so projection norms use float32 while the final weight-change check is
  float64 on CPU. The H100 was saturated by another job throughout.
- Env: Python 3.11, torch==2.9.1, torchvision==0.24.1, ultralytics==8.4.67,
  numpy==2.2.6, Pillow==11.3.0. Data SHA-256 verified.

## Reproduce
```
python train_v2.py --src 1 --tgt 5 --device mps --steps 600 --w_other 2.5 --w_hard 3 --hard 2,4,6 --out model.pt
python verify_submission.py model.pt
```
