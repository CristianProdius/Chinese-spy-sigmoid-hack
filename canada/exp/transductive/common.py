"""Shared pieces for the transductive strategy: training data, LR, dev/sealed evaluation, EM priors.

Uses unlabelled sealed fingerprints only (no labels, no text). Dev (data/gen/dev_*) is only scored.
"""
import collections
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from lib import CLASSES, featurize, fp_lang, load_sealed, save_model, sentences  # noqa: E402
from eval_model import evaluate, load_dev, sealed_gap  # noqa: E402

GEN = ROOT / "data/gen"
OUT = ROOT / "exp/transductive"


def jl(pattern):
    rows = []
    for p in sorted(GEN.glob(pattern)):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_recombined():
    return [json.loads(l) for l in (ROOT / "data/corpus_recombined.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def add_filler(docs, filler, copies=2, kmax=3, seed=0):
    """Return docs + `copies` noisy copies of each, each with 1..kmax random same-language filler
    sentences inserted at random sentence positions."""
    rng = random.Random(seed)
    pool = {"en": [f["text"] for f in filler if f["lang"] == "en"], "fr": [f["text"] for f in filler if f["lang"] == "fr"]}
    out = list(docs)
    for c in range(copies):
        for d in docs:
            ss = sentences(d["text"])
            for _ in range(rng.randint(1, kmax)):
                ss.insert(rng.randint(0, len(ss)), rng.choice(pool[d["lang"]]))
            out.append({**d, "text": " ".join(ss)})
    return out


def balanced_weights(labels, langs, total):
    """Per-doc weights so every (class, language) cell has equal mass; weights sum to `total`."""
    cell = collections.Counter(zip(labels, langs))
    ncell = len(cell)
    return np.array([total / (ncell * cell[(a, l)]) for a, l in zip(labels, langs)])


def build_train(alpha=1.0, filler_copies=2, corpus_filler=True, seed=0, use_boundary=True, gen_pat=("train_*.jsonl",)):
    """Corpus (recombined) + generated train (+ boundary), filler-augmented.
    alpha = total weight of corpus docs relative to the generated docs. Returns X, y, lang, w."""
    filler = jl("filler_*.jsonl")
    gen = [d for pat in gen_pat for d in jl(pat)] + (jl("boundary_*.jsonl") if use_boundary else [])
    corp = load_recombined() if alpha > 0 else []
    gen_aug = add_filler(gen, filler, copies=filler_copies, seed=seed)
    corp_aug = add_filler(corp, filler, copies=1, seed=seed + 1) if corpus_filler else corp
    Xg = featurize([d["text"] for d in gen_aug])
    Xc = featurize([d["text"] for d in corp_aug]).reshape(-1, Xg.shape[1])
    yg = np.array([CLASSES.index(d["label"]) for d in gen_aug])
    yc = np.array([CLASSES.index(d["label"]) for d in corp_aug], dtype=int)
    lg = np.array([d["lang"] for d in gen_aug])
    lc = np.array([d["lang"] for d in corp_aug], dtype="<U2")
    wg = balanced_weights(yg, lg, len(yg))
    wc = balanced_weights(yc, lc, alpha * len(yg)) if len(yc) else np.zeros(0)
    X = np.vstack([Xg, Xc]).astype(np.float32)
    return X, np.concatenate([yg, yc]), np.concatenate([lg, lc]), np.concatenate([wg, wc])


def train_lr(X, y, w, C=1.0, max_iter=2000, Y=None):
    """Multinomial LR with sklearn's objective  C * sum_i w_i CE_i + 0.5 ||W||^2  (w scaled to mean 1).
    Uses torch on GPU when available (H100 box, system python3), else sklearn.
    Y: optional soft targets (n, 9) instead of hard labels y."""
    try:
        import torch
        if torch.cuda.is_available():
            return _train_lr_torch(X, y, w, C, Y=Y)
    except ImportError:
        pass
    if Y is not None:
        raise SystemExit("soft targets need torch")
    from sklearn.linear_model import LogisticRegression

    m = LogisticRegression(C=C, max_iter=max_iter, tol=1e-5).fit(X, y, sample_weight=w / w.mean())
    W = np.zeros((9, X.shape[1]))
    b = np.zeros(9)
    W[m.classes_], b[m.classes_] = m.coef_, m.intercept_
    return W, b


def _train_lr_torch(X, y, w, C, Y=None, iters=600):
    import torch

    dev = "cuda"
    Xt = torch.as_tensor(np.asarray(X, np.float32), device=dev)
    wt = torch.as_tensor(np.asarray(w, np.float64) / np.mean(w), device=dev, dtype=torch.float32)
    if Y is None:
        Yt = torch.zeros(len(y), 9, device=dev)
        Yt[torch.arange(len(y)), torch.as_tensor(y, device=dev)] = 1.0
    else:
        Yt = torch.as_tensor(np.asarray(Y, np.float32), device=dev)
    W = torch.zeros(9, X.shape[1], device=dev, requires_grad=True)
    b = torch.zeros(9, device=dev, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], lr=1, max_iter=iters, tolerance_grad=1e-6, tolerance_change=1e-10,
                            history_size=20, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        S = Xt @ W.T + b
        ce = -(Yt * torch.log_softmax(S, 1)).sum(1)
        loss = (C * (wt * ce).sum() + 0.5 * (W * W).sum()) / len(wt)
        loss.backward()
        return loss

    opt.step(closure)
    Wn, bn = W.detach().cpu().double().numpy(), b.detach().cpu().double().numpy()
    bn = bn - bn.mean()
    return Wn, bn


_DEV = None
_SEALED = None


def dev_data():
    global _DEV
    if _DEV is None:
        dev = load_dev()
        _DEV = (featurize([r["text"] for r in dev]), np.array([CLASSES.index(r["label"]) for r in dev]), np.array([r["lang"] for r in dev]))
    return _DEV


def sealed_data():
    global _SEALED
    if _SEALED is None:
        Xs = load_sealed()
        _SEALED = (Xs, fp_lang(Xs))
    return _SEALED


def report(name, W, b, log=None):
    X, y, lang = dev_data()
    Xs, ls = sealed_data()
    r = evaluate(W, b, X, y, lang)
    tv, mix = sealed_gap(W, b, Xs, ls)
    S = Xs @ W.T + b
    allmix = np.bincount(S.argmax(1), minlength=9) / len(S)
    line = (f"{name:40s} dev {r['acc']:.3f} (en {r['acc_en']:.3f} fr {r['acc_fr']:.3f}) open={int(r['would_open'])} "
            f"sh " + " ".join(f"{v:+.2f}" for v in r["shares"].values()) + f" | TV {tv:.3f} mix " + " ".join(f"{v:.2f}" for v in allmix))
    print(line, flush=True)
    if log is not None:
        log.write(line + "\n")
        log.flush()
    return r, tv


def softmax(S):
    S = S - S.max(1, keepdims=True)
    P = np.exp(S)
    return P / P.sum(1, keepdims=True)


def em_priors(S, prior_train=None, iters=200, tol=1e-8):
    """Saerens et al. 2002: re-estimate class priors on unlabelled data from posteriors.
    S: scores (n, 9) of a model trained with priors prior_train. Returns new priors."""
    k = S.shape[1]
    pt = np.full(k, 1.0 / k) if prior_train is None else prior_train
    P0 = softmax(S)
    pi = pt.copy()
    for _ in range(iters):
        P = P0 * (pi / pt)
        P /= P.sum(1, keepdims=True)
        new = P.mean(0)
        if np.abs(new - pi).max() < tol:
            pi = new
            break
        pi = new
    return pi


def df_scale(gamma=1.0, mode="up", ref=None):
    """Transductive per-bucket scale from document frequencies (unlabelled sealed fingerprints only).
    r_j = df_sealed(j) / df_gen(j) on raw generated train+boundary text. mode 'up': shrink buckets that
    fire more often in sealed reports (real-only words colliding there) by (1/r)^gamma; 'sym': also
    shrink buckets that fire less often in sealed (features the real reports rarely carry)."""
    Xs, _ = sealed_data()
    if ref is None:
        gen = jl("train_*.jsonl") + jl("boundary_*.jsonl")
        ref = featurize([d["text"] for d in gen])
    eps = 1.0 / len(ref)
    r = ((Xs > 0).mean(0) + eps) / ((ref > 0).mean(0) + eps)
    s = np.minimum(1.0, 1.0 / r) if mode == "up" else np.minimum(1.0, np.minimum(r, 1.0 / r))
    return s ** gamma


def train_scaled(X, y, w, C, s, Y=None):
    """LR on column-scaled features X*s; returns weights for the unscaled fingerprint (W*s)."""
    W, b = train_lr(X * s[None, :].astype(np.float32), y, w, C=C, Y=Y)
    return W * s[None, :], b
