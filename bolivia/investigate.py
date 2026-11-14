import numpy as np, csv, torch
from challenge_model import CLASS_NAMES, load_model, predict_probabilities
from audio_io import decode_wav_mono
rows = list(csv.DictReader(open("recordings.csv")))
model = load_model()
auds, meta = [], []
for r in rows:
    a, sr = decode_wav_mono(r["path"])
    if a.shape[0] != 32000:  # pad/trim to 32000
        a = np.pad(a, (0, max(0, 32000 - a.shape[0])))[:32000]
    auds.append(a.astype(np.float32)); meta.append(r)
A = np.stack(auds)
P = predict_probabilities(model, A)
pred = P.argmax(1)
lab = {n: i for i, n in enumerate(CLASS_NAMES)}
print(f"{'clip':22s} {'status':13s} {'label':8s} {'pred':8s} {'conf':5s}")
from collections import Counter
mis_pred, cor_pred = Counter(), Counter()
for r, p, pr in zip(meta, P, pred):
    st, l = r["classification_status"], r["label"]
    print(f"{r['clip_id']:22s} {st:13s} {l:8s} {CLASS_NAMES[pr]:8s} {p.max():.2f}")
    if st == "misclassified": mis_pred[CLASS_NAMES[pr]] += 1
    else: cor_pred[CLASS_NAMES[pr]] += 1
print("\nMISCLASSIFIED predicted-class distribution:", dict(mis_pred))
print("CORRECT        predicted-class distribution:", dict(cor_pred))
print("MISCLASSIFIED true-label distribution:", dict(Counter(r['label'] for r in meta if r['classification_status']=='misclassified')))
np.savez("all_clips.npz", audio=A, status=np.array([r["classification_status"] for r in meta]),
         label=np.array([r["label"] for r in meta]), clip=np.array([r["clip_id"] for r in meta]))
