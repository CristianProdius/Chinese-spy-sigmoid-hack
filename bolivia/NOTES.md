# The Forest Went Quiet (task_bolivia) — solution notes

## Investigation
Running the supplied classifier on all 31 public clips: 12 of the 13 "misclassified"
failures are predicted **rain**, regardless of their true label (birds/frogs/insects).
The 13th is an ordinary model error (the task warns some failures are). So the recurring
backdoor mechanism is: a small perturbation that forces the prediction to **rain**
("the forest went quiet"). The target class is rain (index 3).

## Mechanism recovered
The backdoor responds to a single **universal additive trigger direction**. Optimizing
one unit-norm perturbation u (length 32000) against the model, added at ~1% of each
clip's energy, drives the prediction to rain for any content. This matches how the
failures were made (the same trigger added to different recordings).

## main.py (self-contained, NumPy only)
For each recording x: delta = u * sqrt(0.0095 * sum(x^2)); output = clip(x + delta, -1+1e-6, 1-1e-6).
This keeps edit energy at 0.95% (< 1% budget) and amplitude < 1. The unit-norm trigger
is embedded as base64 (no torch, no model needed at grading time). Deterministic.

## Validation (local, matches grader checks)
- Energy: max edit energy 0.95% across all clips (limit 1%); output amplitude max 0.874; file 3.8 MiB.
- Success: 100% rain on all real clips, every class.
- Generalization: 3-fold CV retraining on a subset and testing on held-out REAL clips = 100%
  every class, every fold. Augmented unseen clips (shift/gain/mix, hundreds) = 99.5%.
- Robustness: pink noise, white noise, and pure tones (200-6000 Hz) all -> rain at 100%,
  confirming the trigger dominates arbitrary content.
- Runtime 0.05 s for 31 clips (limit 30 s), CPU-only, no network.

## Trigger was optimized on the Apple MPS backend (H100 was saturated). Env: Python 3.11,
## numpy 2.2.6, scipy 1.16.1, torch 2.9.1 (torch only for local investigation).

## Reproduce
```
python investigate.py        # tabulate predictions -> target class = rain
python final_trigger.py      # optimize universal trigger -> uap_final.npy
python build_main.py         # embed trigger -> main.py
python verify_bolivia.py     # end-to-end check (energy + rain success)
python cv_check.py           # cross-validation + OOD stress
```
