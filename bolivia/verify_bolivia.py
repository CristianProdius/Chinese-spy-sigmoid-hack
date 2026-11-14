"""End-to-end verification: run main.py on real clips, check energy limits (audio_io.validate)
and model success (predict rain), exactly as the grader would, with NO torch inside main.py."""
import numpy as np, subprocess, sys, time, os
from challenge_model import CLASS_NAMES, load_model, predict_probabilities
from audio_io import validate
RAIN = CLASS_NAMES.index("rain")

d = np.load("all_clips.npz"); A, lab, clip = d["audio"], d["label"], d["clip"]
# Build a test-input.npz from ALL real clips (grader uses unseen, but this is our best proxy)
np.savez("test-input.npz", audio=A.astype(np.float32),
         sample_rate=np.int32(16000), clip_ids=clip.astype("<U64"))
t0 = time.time()
r = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
print("main.py rc", r.returncode, "time", round(time.time()-t0,2), "s", r.stderr[-200:] if r.returncode else "")
out = np.load("test-output.npz", allow_pickle=False)
mod, sr, ids = out["audio"], out["sample_rate"], out["clip_ids"]
assert mod.dtype == np.float32 and mod.shape == A.shape, (mod.dtype, mod.shape)
assert int(sr) == 16000 and list(ids) == list(clip.astype("<U64"))
assert np.isfinite(mod).all()
# format/size
sz = os.path.getsize("test-output.npz")/1048576
# energy limits
ep = validate(A.astype(np.float32), mod)
print(f"max edit energy %: {ep.max():.4f} (limit 1.0)  all<=1%: {bool((ep<=1.0+1e-5).all())}  out size {sz:.2f} MiB  max|amp| {np.abs(mod).max():.4f}")
# success
model = load_model()
P = predict_probabilities(model, mod); pred = P.argmax(1)
succ = (pred == RAIN)
# per original class, equal weight
per = {}
for c in CLASS_NAMES:
    m = lab == c
    if m.sum(): per[c] = float(succ[m].mean())
overall = np.mean(list(per.values()))
print("per-class success:", {k: round(v,3) for k,v in per.items()})
print(f"overall (equal-weight) {overall:.3f}  min-class {min(per.values()):.3f}")
print(f"CHECKS: format&energy={'PASS' if (ep<=1.0+1e-5).all() and sz<=32 else 'FAIL'}  "
      f"success>=90%={'PASS' if overall>=0.90 else 'FAIL'}  per-class>=85%={'PASS' if min(per.values())>=0.85 else 'FAIL'}")
