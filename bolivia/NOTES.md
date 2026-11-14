# The Forest Went Quiet (task_bolivia) — status: BLOCKED on mechanism

## Solved parts
- Target class identified: **rain**. The backdoor flips birds/frogs/insects -> rain
  (12 of 13 supplied failures predict rain; the 13th is an ordinary error, as the task warns).
- Format/energy constraints met; rain-prediction ("success") is achievable at 100% within <=1% edit energy.

## Blocker: the "failure mechanism" check
The grader checks that the output recordings carry the AUTHOR's specific trigger pattern,
not any perturbation that flips the model ("FAIL (mechanism): trigger pattern missing or
off-tolerance"). An optimized universal perturbation (first submission) flips 100% but was
rejected as the wrong pattern.

## Exhaustive investigation (see PROBE_FACTS.md + scripts)
Ruled out, with numbers, every recoverable fixed model-free trigger:
- No additive direction in the span of the 12 failures flips to rain (definitive).
- No EQ/multiplicative filter, convolutional FIR, echo/reverb, pure tone, gain, or noise
  injection flips within the 1% budget.
- rain-logit gradients at the failures are saturated/inconsistent (no shared backdoor direction).
- Directions that do flip are adversarial, absent from the failures, and grader-rejected.
Conclusion: the author's trigger is not recoverable from the provided 12 failures + model by
signal or optimization analysis alone.

## What is needed to finish
`task_description.md` (the notebook links it: "See task_description.md for the objective and
rules") was NOT in the downloaded folder. It almost certainly defines the trigger mechanism.
With it (or any hint about the trigger type/params), the transform is quick to build and verify
with probe_env.py / verify_bolivia.py.

## Artifacts
- probe_env.py: shared probe (clean_refs, failures, flip_rate, predict).
- investigate.py: predictions -> target class = rain.
- PROBE_FACTS.md: full list of tested hypotheses and results.
- (first main.py was a universal-perturbation attempt; it fails the mechanism check and is NOT a valid solution.)
