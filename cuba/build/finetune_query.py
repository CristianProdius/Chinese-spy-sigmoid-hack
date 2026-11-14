"""Fine-tune the query encoder (leaf-ir) against FROZEN passage vectors (arctic-m windows).

Every step scores a batch of slips against all windows; the loss is multi-positive InfoNCE where
every window of the gold document is a positive (matches MaxP retrieval). Passage vectors are the
4-bit dequantised ones we ship. Slips get the real slips' noise on the fly.

    python build/finetune_query.py --train work/train_a.jsonl [more.jsonl] --out work/ft_leaf_a
        [--epochs 3 --lr 3e-5 --bs 64 --scale 20]
Eval each epoch: dense-only and fused (bm25s, 200/50 + title) Hit@3 on the public sample and on
work/vset_hold.jsonl if present.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

import bm25s
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402

QP = "Represent this sentence for searching relevant passages: "
SPANISH = {"year": "año", "war": "guerra", "church": "iglesia", "people": "gente", "women": "mujeres",
           "history": "historia", "chapter": "capítulo", "city": "ciudad", "island": "isla", "sugar": "azúcar",
           "slaves": "esclavos", "king": "rey", "ships": "barcos", "port": "puerto", "money": "dinero",
           "land": "tierra", "house": "casa", "spaniards": "españoles"}
OPENERS = ["that bit about ", "the part where ", "read us ", "the reading about ", "la parte donde ", "eso de ",
           "la historia de ", "the chapter where ", "the one about "]


def noisy(q: str, rng: random.Random) -> str:
    words = q.split()
    if rng.random() < 0.2 and words:
        i = rng.randrange(len(words))
        w = words[i]
        if len(w) > 4 and w.isalpha():
            j = rng.randrange(1, len(w) - 1)
            op = rng.random()
            w = w[:j] + w[j + 1:] if op < 0.4 else (w[:j] + w[j + 1] + w[j] + w[j + 2:] if op < 0.7 else w[:j] + w[j] + w[j:])
            words[i] = w
    if rng.random() < 0.12:
        for i, w in enumerate(words):
            if w.lower() in SPANISH:
                words[i] = SPANISH[w.lower()]
                break
    q = " ".join(words)
    if rng.random() < 0.1:
        q = q.lower()
    if rng.random() < 0.08:
        q = rng.choice(OPENERS) + q[0].lower() + q[1:]
    return q


def dequant4(E: np.ndarray) -> np.ndarray:
    E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
    lo = np.percentile(E, 0.5, axis=0)
    hi = np.percentile(E, 99.5, axis=0)
    step = (hi - lo) / 15
    return (np.clip(np.rint((E - lo) / step), 0, 15) * step + lo).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default="MongoDB/mdbr-leaf-ir")
    ap.add_argument("--passages", default="work/emb_arctic_m15_200_50.npy")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--scale", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)
    dev = "cuda"

    doc_ids, texts, cd = lab.chunks(200, 50, title=True)
    n_docs = len(doc_ids)
    pos = {d: i for i, d in enumerate(doc_ids)}
    P = torch.tensor(dequant4(np.load(args.passages).astype(np.float32)), device=dev)  # (W, 768)
    win_doc = torch.tensor(cd, device=dev, dtype=torch.long)

    train = []
    for path in args.train:
        for l in open(path, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                train.append((r["question"], pos[r["doc_id"]]))
    print(f"{len(train)} training slips", flush=True)

    # evaluation sets + lexical scores (bm25s over the same windows)
    evals = {"sample": lab.questions("sample")}
    for extra in ("vset_hold", "rw_hold", "hard_hold"):
        if os.path.exists(os.path.join(lab.WORK, f"{extra}.jsonl")):
            evals[extra] = lab.questions(extra)
    bm = bm25s.BM25(k1=1.2, b=0.75)
    bm.index([lab.tokens(t) for t in texts], show_progress=False)
    lex = {}
    for name, qs in evals.items():
        rows = []
        for q in qs:
            qt = [t for t in lab.tokens(q["question"]) if t in bm.vocab_dict]
            s = bm.get_scores(qt) if qt else np.zeros(len(texts))
            rows.append(lab.doc_scores_from_chunks(s, cd, n_docs))
        lex[name] = np.stack(rows)

    model = SentenceTransformer(args.base, device=dev)
    model.max_seq_length = 64

    def encode_train(batch_q):
        feats = model.tokenize([QP + q for q in batch_q])
        feats = {k: v.to(dev) for k, v in feats.items() if torch.is_tensor(v)}
        return model(feats)["sentence_embedding"]

    def z(x):
        return (x - x.mean(1, keepdims=True)) / (x.std(1, keepdims=True) + 1e-9)

    @torch.no_grad()
    def evaluate(tag):
        model.eval()
        out = []
        for name, qs in evals.items():
            Q = model.encode([QP + q["question"] for q in qs], convert_to_tensor=True, normalize_embeddings=True,
                             batch_size=128)
            S = (Q @ P.T).float()
            D = torch.full((len(qs), n_docs), -1e9, device=dev)
            D = D.scatter_reduce(1, win_doc.expand(len(qs), -1), S, reduce="amax")
            D = D.cpu().numpy()
            gold = np.array([pos[q["doc_id"]] for q in qs])

            def hit(M):
                top = np.argpartition(-M, 3, axis=1)[:, :3]
                return (top == gold[:, None]).any(1).mean()
            res = [f"dense {hit(D):.3f}"] + [f"w{w:g} {hit(z(lex[name]) + w * z(D)):.3f}" for w in (1.0, 2.0, 3.0)]
            out.append(f"{name}: " + " ".join(res))
        print(f"[{tag}] " + " | ".join(out), flush=True)
        model.train()

    evaluate("base")
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.01)
    steps = args.epochs * math.ceil(len(train) / args.bs)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: min(1.0, s / max(1, int(0.1 * steps))) * max(0.0, (steps - s) / max(1, steps - int(0.1 * steps))))
    model.train()
    step = 0
    for ep in range(args.epochs):
        rng.shuffle(train)
        tot = 0.0
        for i in range(0, len(train), args.bs):
            batch = train[i:i + args.bs]
            q = encode_train([noisy(t, rng) for t, _ in batch])
            logits = args.scale * (q @ P.T)  # (B, W)
            gold = torch.tensor([g for _, g in batch], device=dev)
            is_pos = win_doc[None, :] == gold[:, None]
            loss = (torch.logsumexp(logits, 1) - torch.logsumexp(logits.masked_fill(~is_pos, -1e4), 1)).mean()
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            step += 1
            tot += loss.item() * len(batch)
        print(f"epoch {ep + 1}: loss {tot / len(train):.4f}", flush=True)
        evaluate(f"epoch {ep + 1}")
        model.save(os.path.join(args.out, f"epoch{ep + 1}"))


if __name__ == "__main__":
    main()
