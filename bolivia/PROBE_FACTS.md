# Established facts (Bolivia trigger investigation)
- Dir: /Users/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/dagon/bolivia ; run `.venv/bin/python`.
- `import probe_env as pe` gives: pe.clean_refs (10 correct non-rain: birds/frogs/insects, shape (10,32000) float32),
  pe.rain_refs (8), pe.failures (12 misclassified clips the model predicts as RAIN), pe.RAIN=3,
  pe.predict(batch)->class idx, pe.energy_pct(orig,mod), pe.flip_rate(transform, which="clean")->(rain_rate, max_energy_pct).
- Target class is RAIN (index 3). Backdoor flips birds/frogs/insects -> rain.
- Model: challenge_model.AudioClassifier, STFT n_fft=512 hop=160 hann, 16kHz, 2s=32000 samples. eval() returns (probs,logits); logits via load_model()(torch tensor [B,32000]).
- GOAL: a FIXED transform (numpy/scipy only, no torch, no model at test time) that, applied to any clean clip, makes the model predict rain with edit energy <=1% per clip (energy% = 100*sum((out-in)^2)/sum(in^2)), samples strictly in (-1,1).
- The grader computes delta = its_clean_input - my_output and checks it matches the AUTHOR's specific trigger pattern within tolerance ("FAIL (mechanism): trigger pattern missing or off-tolerance"). So an ARBITRARY adversarial perturbation that flips the model is REJECTED. We must recover the AUTHOR's actual trigger.
# Dead ends already ruled out (do NOT repeat):
- Per-clip-scaled universal adversarial direction (PGD/UAP): flips 100% but REJECTED by grader (wrong pattern).
- Fixed additive waveform via optimization (neural-cleanse L1/L2 min): flips refs but projection onto it in the 12 failures is ~0 (NOT present in failures) -> not the author's trigger.
- De-trigger recovery (optimize t s.t. model(failure - t)=true label): gives huge over-budget adversarial t, add-to-refs flip only 0.44.
- Cross-clip complex-spectrum coherence: failures show coherence at ~768/2100/2800-4600 Hz but recovered component has INCONSISTENT projection across failures and adding it (any amplitude) does NOT flip refs.
- Generic noise injection at <=1% (white, pink, rain-shaped, a rain clip): clean->rain flip ~0.0. Generic noise does NOT trigger.
- Echo/cepstrum: no strong consistent cepstral/autocorr peak in failures.
# The real trigger is likely CONTENT-DEPENDENT or STRUCTURED (since no fixed additive pattern is in the failures) and must be both (a) flips clean refs to rain >=0.9 at <=1% energy AND (b) evidenced/consistent across the 12 failures.
# ROBUST-ADDITIVE hypothesis DEFINITIVELY KILLED (session 2)
- Decisive proof: PGD (300 iters, Adam) restricted to span(12 failures) -> flip 0.00 on clean_refs
  at 0.95% energy. No additive direction inside the failure subspace flips.
- Every "present-in-failures" recovery (raw mean/median, energy-normalized mean/median,
  PCA-residual k=1..8, complex-STFT real/imag median, lowest-3-energy mean) -> clean flip 0.00.
  cstft-median trigger: consistently present (per-failure normalized corr 0.019..0.176, ALL 12
  positive, mean 0.126) yet flip_rate 0.000.
- Fixed-ABSOLUTE waveform add (median/mean/lowest3) only flips at alpha giving >130% energy.
- The ONLY flipping direction (uap_final) flips 1.00 @0.95% but normalized corr w/ failures is
  mean +0.0014, range [-0.004,+0.007] (noise-level, sign-inconsistent) -> orthogonal, absent.
- CONCLUSION: flip-capability and failure-presence are MUTUALLY EXCLUSIVE for any additive
  direction. The author's trigger is NOT a fixed additive waveform/direction. It is
  content-dependent (per-clip). Next sessions: abandon additive recovery entirely; investigate
  content-dependent transforms (per-clip adversarial recipe, filtering/convolution, or structured
  STFT-domain op) whose DELTA still matches a checkable pattern.

# Workflow round 1 outcome (2026-11-14):
- attr_trigger_u (flip=1.0 @0.95%) has MANUFACTURED presence (failProj +0.269 uniform +/-0.001) -> NOT the author trigger; ignore.
- cstft_median (complex-STFT median of 12 failures) is the ONLY genuinely-present shared component (failProj 0.019-0.176 varied, all positive, clean~0) but flip_rate=0.0 @0.95%.
- No additive direction is both present AND flipping; no EQ/echo/DSP op flips at <=1%. Likely per-clip adversarial failures OR a weights-trained backdoor to reverse-engineer.

# CONCLUSIVE findings (2026-11-15), after exhaustive search:
- DEFINITIVE: no additive direction in the span of the 12 failures (raw or mean-centered, or any PC) flips clean->rain at <=1% (flip=0.00). The failures share NO additive trigger that causes rain.
- Multiplicative/EQ filter: no flip at <=1% (expert agents).
- Convolutional FIR (L=33..257, near-identity, optimized): flip=0.00 at <=1% edit energy.
- Echo/reverb, pure tones (50Hz..Nyquist), gain/attenuation, white/pink/rain-shaped noise, spread-spectrum: none flip at <=1% or none present in failures.
- rain-logit input-gradients at failures are near-zero & inconsistent (pairwise cos ~0.0003) -> saturated, no shared backdoor direction.
- Additive directions that DO flip (optimized UAP, 100%) are adversarial, orthogonal to the failures (failProj~0), and the hidden grader rejects them ("FAIL mechanism").
- main.py (grader) is numpy/scipy only, NO model access -> cannot do per-clip adversarial at grading time.
# CONCLUSION: the author's trigger cannot be recovered from the 12 failures + model by signal/optimization analysis. task_description.md (referenced by the notebook: "See task_description.md for the objective and rules") was NOT in the downloaded folder and almost certainly specifies the trigger mechanism. BLOCKED pending that file or a hint.
