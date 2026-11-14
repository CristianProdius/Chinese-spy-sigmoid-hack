# Ciclopaseo Mirage (task_ecuador) — solution notes

## Goal
Perturb a bicycle photo so MobileNetV3-Large (IMAGENET1K_V2) predicts class 665
(moped) at >= 99% softmax confidence, changing every integer RGB value by at most
1 on the 0-255 scale. Output `test-output.png` must be RGB PNG, same size as input,
<= 1 MiB. Script `python main.py` must finish < 60 s on 2 CPU cores / 2 GiB.

## Method (main.py)
Targeted projected gradient descent on a continuous perturbation `delta`:
- Box constraint: `delta` clamped to +-1/255 and to keep `x0 + delta` in [0, 1].
- Straight-through quantization: the forward pass rounds `delta` to the nearest
  1/255 (what the grader actually decodes from the PNG), while gradients flow to
  the continuous value. This is the key trick — optimising the float tensor and
  rounding at the end loses the class after quantization.
- Sign-gradient steps with momentum 0.9, step decaying from 0.35/255 once past
  0.99; random restart if stuck for 60 iterations.
- Best quantized candidate is tracked and saved.
- `prune_for_size`: if the PNG exceeds 1 MiB, zero the least-important perturbation
  entries (by first-order loss impact) while keeping confidence > 0.99.
- Images > 400k pixels run the backbone with activation checkpointing to fit in 2 GiB.
- Time is counted from process start (`T_START`), so imports and saving are inside
  the budget. Attack deadline 36 s, prune deadline 44 s.

## Results (2 threads, matching the grader)
| image | size | p(moped) | bytes | time | pass |
|---|---|---|---|---|---|
| train-input.png | 224x224 | 0.9951 | 115 KB | 3.3 s | yes |
| ImageNet mountain_bike | 500x375 | 0.9968 | 302 KB | 3.0 s | yes |
| ImageNet tandem | 500x384 | 0.9954 | 415 KB | 3.1 s | yes |
| ImageNet tricycle | 500x333 | 0.9951 | 379 KB | 5.4 s | yes |
| upscaled 640x640 | 640x640 | 0.9975 | 666 KB | 3.8 s | yes |

Edge cases that do NOT reflect the evaluation photo: a 1024x768 upscale whose own
input PNG is already 975 KB (perturbation cannot fit under 1 MiB), and sub-160px
crops (too few pixels to reach 99% within the budget). The real eval image is a
normal bicycle photo at a few-hundred-pixel scale, where the method has wide margin.

## Environment
Python 3.13, torch==2.9.1, torchvision==0.24.1, Pillow==11.3.0, numpy==2.2.6 (CPU).
Classifier SHA-256 verified: 5c1a4163...7997.
