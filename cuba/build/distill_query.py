"""In-domain distillation of the query encoder: leaf-ir (student) learns to reproduce
arctic-embed-m-v1.5 (teacher) query embeddings, so it stays aligned with the arctic passage
vectors we ship while learning this corpus's vocabulary and the slips' style.

Training texts: labelled slips (also used for a contrastive term against the frozen passage
vectors, every window of the gold doc positive) + unlabelled corpus snippets (distillation only).
Noise like the real slips is applied on the fly to the student input only; the teacher always
sees the clean text, so the student also learns to undo typos and Spanish words.

    python build/distill_query.py --train work/train_q72.jsonl ... --out work/dist_a
        [--snippets 40000 --epochs 3 --lr 2e-5 --lam 0.2 --scale 50]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402
from finetune_query import QP, dequant4, noisy  # noqa: E402


def snippets(n: int, rng: random.Random) -> list[str]:
    out = []
    docs = lab.meta()
    weights = [m["words"] for m in docs]
    corpus = lab.corpus()
    while len(out) < n:
        m = rng.choices(docs, weights=weights)[0]
        words = corpus[m["id"]].split()
        L = rng.randint(10, 28)
        if len(words) <= L:
            continue
        s = rng.randrange(0, len(words) - L)
        out.append(" ".join(words[s:s + L]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--student", default="MongoDB/mdbr-leaf-ir")
    ap.add_argument("--teacher", default="Snowflake/snowflake-arctic-embed-m-v1.5")
    ap.add_argument("--passages", default="work/emb_arctic_m15_200_50.npy")
    ap.add_argument("--snippets", type=int, default=40000)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--bs", type=int, default=128)
    ap.add_argument("--lam", type=float, default=0.2, help="weight of the contrastive term")
    ap.add_argument("--scale", type=float, default=50.0)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)
    dev = "cuda"

    doc_ids, texts, cd = lab.chunks(200, 50, title=True)
    n_docs = len(doc_ids)
    pos = {d: i for i, d in enumerate(doc_ids)}
    P = torch.tensor(dequant4(np.load(args.passages).astype(np.float32)), device=dev)
    win_doc = torch.tensor(cd, device=dev, dtype=torch.long)

    labelled = []
    for path in args.train:
        for l in open(path, encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                labelled.append((r["question"], pos[r["doc_id"]]))
    unl = [(s, -1) for s in snippets(args.snippets, rng)]
    data = labelled + unl
    print(f"{len(labelled)} labelled slips + {len(unl)} snippets", flush=True)

    teacher = SentenceTransformer(args.teacher, device=dev).eval()
    with torch.no_grad():
        T = teacher.encode([QP + t for t, _ in data], batch_size=256, convert_to_tensor=True,
                           normalize_embeddings=True).float()
    student = SentenceTransformer(args.student, device=dev)
    student.max_seq_length = 64

    # evaluation: dense-only and fused with bm25s over the same windows
    import bm25s
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

    def z(x):
        return (x - x.mean(1, keepdims=True)) / (x.std(1, keepdims=True) + 1e-9)

    @torch.no_grad()
    def evaluate(tag, model):
        model.eval()
        out = []
        for name, qs in evals.items():
            Q = model.encode([QP + q["question"] for q in qs], convert_to_tensor=True, normalize_embeddings=True,
                             batch_size=128).float()
            D = torch.full((len(qs), n_docs), -1e9, device=dev).scatter_reduce(
                1, win_doc.expand(len(qs), -1), (Q @ P.T).float(), reduce="amax").cpu().numpy()
            gold = np.array([pos[q["doc_id"]] for q in qs])

            def hit(M):
                return (np.argpartition(-M, 3, axis=1)[:, :3] == gold[:, None]).any(1).mean()
            out.append(f"{name}: dense {hit(D):.3f} " + " ".join(f"w{w:g} {hit(z(lex[name]) + w * z(D)):.3f}" for w in (2.0, 3.0)))
        print(f"[{tag}] " + " | ".join(out), flush=True)

    evaluate("teacher", teacher)
    del teacher
    torch.cuda.empty_cache()
    evaluate("student base", student)

    params = [p for p in student.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.01)
    steps = args.epochs * math.ceil(len(data) / args.bs)
    warm = max(1, int(0.06 * steps))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, s / warm) * max(0.0, (steps - s) / max(1, steps - warm)))
    idx = list(range(len(data)))
    for ep in range(args.epochs):
        student.train()
        rng.shuffle(idx)
        tot = 0.0
        for i in range(0, len(idx), args.bs):
            b = idx[i:i + args.bs]
            feats = student.tokenize([QP + noisy(data[j][0], rng) for j in b])
            feats = {k: v.to(dev) for k, v in feats.items() if torch.is_tensor(v)}
            q = student(feats)["sentence_embedding"]
            t = T[b]
            loss = (1 - (q * t).sum(1)).mean() * 10.0  # cosine distillation
            lab_mask = torch.tensor([data[j][1] >= 0 for j in b], device=dev)
            if args.lam > 0 and lab_mask.any():
                ql = q[lab_mask]
                gold = torch.tensor([data[j][1] for j in b if data[j][1] >= 0], device=dev)
                logits = args.scale * (ql @ P.T)
                is_pos = win_doc[None, :] == gold[:, None]
                loss = loss + args.lam * (torch.logsumexp(logits, 1) - torch.logsumexp(logits.masked_fill(~is_pos, -1e4), 1)).mean()
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            tot += loss.item() * len(b)
        print(f"epoch {ep + 1}: loss {tot / len(idx):.4f}", flush=True)
        evaluate(f"epoch {ep + 1}", student)
        student.save(os.path.join(args.out, f"epoch{ep + 1}"))


if __name__ == "__main__":
    main()
