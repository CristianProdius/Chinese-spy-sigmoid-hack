"""Embed lab.chunks windows with a sentence-transformers model on GPU -> work/emb_<tag>_<size>_<overlap>.npy (fp16, normalised)."""
import os, sys, numpy as np
from sentence_transformers import SentenceTransformer
sys.path.insert(0, os.path.dirname(__file__)); import lab
hf, tag, size, overlap = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
doc_ids, texts, cd = lab.chunks(size, overlap, title=True)
m = SentenceTransformer(hf, device="cuda")
E = m.encode(texts, batch_size=128, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
E /= np.linalg.norm(E, axis=1, keepdims=True) + 1e-9
np.save(os.path.join(lab.WORK, f"emb_{tag}_{size}_{overlap}.npy"), E.astype(np.float16)); print(tag, E.shape)
