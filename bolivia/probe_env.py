"""Shared probe helpers for trigger investigation.
clean_refs: 10 correctly-classified NON-rain references (birds/frogs/insects).
rain_refs: 8 correctly-classified rain references.
failures: the 12 misclassified clips that the model predicts as rain.
flip_rate(transform): fraction of clean_refs whose TRANSFORMED audio the model predicts rain.
"""
import numpy as np, torch
from challenge_model import CLASS_NAMES, load_model
RAIN = CLASS_NAMES.index("rain")
DEV = "mps" if torch.backends.mps.is_available() else "cpu"
_model = load_model().to(DEV)
for p in _model.parameters(): p.requires_grad_(False)
_d = np.load("all_clips.npz"); _A = _d["audio"]; _st = _d["status"]; _lab = _d["label"]
with torch.no_grad():
    _pr = _model(torch.tensor(_A, dtype=torch.float32, device=DEV)).argmax(1).cpu().numpy()
clean_refs = _A[(_st == "correct") & (_lab != "rain")].astype(np.float32)   # (10,32000)
rain_refs  = _A[(_st == "correct") & (_lab == "rain")].astype(np.float32)
failures   = _A[(_st == "misclassified") & (_pr == RAIN)].astype(np.float32) # (12,32000)
clean_labels = _lab[(_st == "correct") & (_lab != "rain")]

def predict(batch):
    with torch.no_grad():
        return _model(torch.tensor(np.asarray(batch, dtype=np.float32), device=DEV)).argmax(1).cpu().numpy()

def energy_pct(orig, mod):
    o = np.asarray(orig, np.float64); m = np.asarray(mod, np.float64)
    return 100 * ((m - o) ** 2).sum(-1) / ((o ** 2).sum(-1) + 1e-12)

def flip_rate(transform, which="clean"):
    """transform: f(audio[B,32000]) -> modified[B,32000]. Returns (rain_rate, max_energy_pct)."""
    X = {"clean": clean_refs, "rain": rain_refs}[which]
    Y = np.asarray(transform(X.copy()), dtype=np.float32)
    ep = energy_pct(X, Y)
    return float((predict(Y) == RAIN).mean()), float(ep.max())
