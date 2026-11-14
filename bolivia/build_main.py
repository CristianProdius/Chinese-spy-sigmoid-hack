import base64, numpy as np
u = np.load("uap_final.npy").astype(np.float32)
u = u / np.linalg.norm(u)                       # ensure unit norm
b64 = base64.b64encode(u.tobytes()).decode()
src = '''"""The Forest Went Quiet - reproduce the backdoor failure mechanism.

The deployed classifier carries a backdoor: a single universal additive trigger
direction, added at ~1%% of a clip's energy, drives the model to predict "rain"
regardless of the clip's true content (birds/frogs/insects). This script applies
that recovered trigger to every input recording, scaled per-clip to stay within
the 1%% edit-energy budget, reproducing the failure on unseen audio.

Self-contained: standard library + NumPy only (no model needed at grading time).
The trigger below was recovered by optimizing a universal perturbation against the
supplied model on the public recordings with augmentation.
"""
import base64
import numpy as np

# Unit-norm universal trigger direction, length 32000, float32 (base64 of raw bytes).
_TRIGGER_B64 = (
%s
)
_FRAC = 0.0095          # edit energy as a fraction of each clip's energy (< 1%% for margin)
_CLAMP = 1.0 - 1e-6


def _trigger():
    u = np.frombuffer(base64.b64decode(_TRIGGER_B64), dtype=np.float32).astype(np.float64)
    n = np.linalg.norm(u)
    return u / n if n > 0 else u


def transform(audio):
    """audio: float32 (B, 32000). Returns modified float32 audio of the same shape."""
    x = np.asarray(audio, dtype=np.float64)
    if x.ndim == 1:
        x = x[None, :]
    u = _trigger()
    energy = np.sum(x * x, axis=1, keepdims=True)                # (B,1)
    delta = u[None, :] * np.sqrt(_FRAC * energy)                 # scale to _FRAC of clip energy
    out = np.clip(x + delta, -_CLAMP, _CLAMP)
    return out.astype(np.float32).reshape(np.asarray(audio).shape)


def main():
    with np.load("test-input.npz", allow_pickle=False) as data:
        audio = data["audio"]
        sample_rate = data["sample_rate"]
        clip_ids = data["clip_ids"]
    np.savez("test-output.npz", audio=transform(audio),
             sample_rate=sample_rate, clip_ids=clip_ids)


if __name__ == "__main__":
    main()
''' 
# wrap the base64 into quoted 100-char lines
lines = [b64[i:i+100] for i in range(0, len(b64), 100)]
quoted = "\n".join('        "%s"' % ln for ln in lines)
open("main.py", "w").write(src % quoted)
print("wrote main.py", len(open("main.py").read()), "bytes; trigger len", len(u))
