"""Shared pieces for the sparse strategy: data, augmentation, lexicon weights, masks, dev scoring."""
import collections
import glob
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
from lib import CLASSES, DIM, bucket, featurize, fp_lang, load_corpus, load_sealed, text_lang, tokens  # noqa: E402
from eval_model import evaluate, load_dev  # noqa: E402
from lexicon import lexicon_features  # noqa: E402


def read_jsonl(pattern):
    rows = []
    for p in sorted(glob.glob(str(ROOT / pattern))):
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_sets():
    corpus = [{"text": r["text"], "label": r["label"], "lang": text_lang(r["text"])} for r in load_corpus()]
    return {
        "corpus": corpus,
        "recomb": read_jsonl("data/corpus_recombined.jsonl"),
        "train": read_jsonl("data/gen/train_*.jsonl"),
        "boundary": read_jsonl("data/gen/boundary_*.jsonl"),
        "filler": read_jsonl("data/gen/filler_*.jsonl"),
        "dev": load_dev(),
    }


def feature_strings(text):
    t = tokens(text)
    return t + [a + " " + b for a, b in zip(t, t[1:])]


def doc_freq(texts):
    df = collections.Counter()
    for tx in texts:
        df.update(set(feature_strings(tx)))
    return df


def augment(rows, filler, n_copies=1, max_fill=3, seed=0, same_lang=True):
    """Each row once as is, plus n_copies with 1..max_fill filler sentences inserted at random spots."""
    rng = random.Random(seed)
    by_lang = collections.defaultdict(list)
    for f in filler:
        by_lang[f["lang"]].append(f["text"])
    allf = [f["text"] for f in filler]
    out = []
    for r in rows:
        out.append(r)
        for _ in range(n_copies):
            pool = by_lang[r["lang"]] if same_lang else allf
            k = rng.randint(1, max_fill)
            parts = [r["text"]]
            for _ in range(k):
                pos = rng.randint(1, len(parts))  # never before the opening of the report
                parts.insert(pos, rng.choice(pool))
            out.append({"text": " ".join(parts), "label": r["label"], "lang": r["lang"]})
    return out


def xy(rows):
    X = featurize([r["text"] for r in rows])
    y = np.array([CLASSES.index(r["label"]) for r in rows])
    lang = np.array([r["lang"] for r in rows])
    return X, y, lang


def balanced_weights(y, lang, groups=None, group_w=None):
    """class x language balanced weights; optional per-group multipliers (e.g. corpus vs generated)."""
    cell = collections.Counter(zip(y.tolist(), lang.tolist()))
    w = np.array([len(y) / (18 * cell[(a, l)]) for a, l in zip(y.tolist(), lang.tolist())], float)
    if groups is not None:
        tot = len(y)
        for g, m in group_w.items():
            sel = groups == g
            # rescale so group g carries share m of the total weight
            w[sel] *= m * tot / max(w[sel].sum(), 1e-9)
    return w * len(y) / w.sum()


def lexicon_W(drop_buckets=(), tier_scale=None):
    """Lexicon -> (9, DIM) weight matrix. A bucket hit by several classes keeps each class's weight."""
    W = np.zeros((len(CLASSES), DIM))
    for f, d in lexicon_features().items():
        bk = bucket(f)
        if bk in drop_buckets:
            continue
        for ci, w in d.items():
            W[ci, bk] = max(W[ci, bk], w)
    return W


def lexicon_buckets():
    return sorted({bucket(f) for f in lexicon_features()})


def collision_report(texts, df_min=0.01, verbose=False):
    """Lexicon buckets shared with a frequent non-lexicon feature of our own text (df >= df_min)."""
    feats = lexicon_features()
    df = doc_freq(texts)
    n = len(texts)
    by_bucket = collections.defaultdict(list)
    for f, c in df.items():
        by_bucket[bucket(f)].append((c / n, f))
    bad = {}
    for f in feats:
        bk = bucket(f)
        others = [(r, g) for r, g in by_bucket[bk] if g not in feats and r >= df_min]
        if others:
            bad[bk] = (f, sorted(others, reverse=True)[:3])
    if verbose:
        for bk, (f, o) in sorted(bad.items(), key=lambda kv: -kv[1][1][0][0]):
            print(f"  bucket {bk}: lexicon '{f}' collides with " + ", ".join(f"'{g}' df={r:.3f}" for r, g in o))
    return bad


def common_buckets(texts, df_min=0.05):
    """Buckets of features present in >= df_min of our own documents (function words, stock bigrams)."""
    df = doc_freq(texts)
    n = len(texts)
    return sorted({bucket(f) for f, c in df.items() if c / n >= df_min})


class Dev:
    def __init__(self, dev_rows):
        self.X, self.y, self.lang = xy(dev_rows)
        self.Xs = load_sealed()
        self.lang_s = fp_lang(self.Xs)

    def score(self, W, b):
        r = evaluate(W, b, self.X, self.y, self.lang)
        pred = (self.Xs @ W.T + b).argmax(1)
        mix = {l: np.bincount(pred[self.lang_s == l], minlength=9) / (self.lang_s == l).sum() for l in ("en", "fr")}
        r["tv"] = float(0.5 * np.abs(mix["en"] - mix["fr"]).sum())
        r["mix"] = (mix["en"] + mix["fr"]) / 2
        return r

    def line(self, name, W, b):
        r = self.score(W, b)
        best = max(r["shares"].values())
        pc = " ".join(f"{v:.2f}" for v in r["per_class"].values())
        s = (f"{name:42s} acc {r['acc']:.3f} en {r['acc_en']:.3f} fr {r['acc_fr']:.3f} "
             f"bestshare {best:+.3f} tv {r['tv']:.3f} | {pc}")
        print(s, flush=True)
        return r


def featurize_raw(texts):
    """Like task/featurize.py but WITHOUT the final L2 normalisation (so noise can be added first)."""
    import math
    out = np.zeros((len(texts), DIM), np.float32)
    for i, text in enumerate(texts):
        toks = tokens(text)
        counts = collections.Counter(bucket(t) for t in toks)
        counts.update(bucket(a + " " + b) for a, b in zip(toks, toks[1:]))
        for b, c in counts.items():
            out[i, b] = 1.0 + math.log(c)
    return out


def l2norm(U):
    n = np.linalg.norm(U, axis=1, keepdims=True)
    return U / np.maximum(n, 1e-12)


def sealed_noise(U, lang, excess, copies=2, scale=1.0, seed=0):
    """Hash-collision noise matched to real text: for a doc in language l, switch on bucket b (value 1)
    with probability scale * excess_l[b], where excess_l = sealed df - our df (clipped at 0). Returns the
    original rows plus `copies` noisy copies, all L2-normalised, and the row index map."""
    rng = np.random.default_rng(seed)
    outs, idx = [l2norm(U)], [np.arange(len(U))]
    for _ in range(copies):
        V = U.copy()
        for l in ("en", "fr"):
            sel = np.flatnonzero(lang == l)
            p = np.clip(scale * excess[l], 0, 1)
            on = rng.random((len(sel), DIM)) < p[None, :]
            sub = V[sel]
            sub[on & (sub == 0)] = 1.0
            V[sel] = sub
        outs.append(l2norm(V))
        idx.append(np.arange(len(U)))
    return np.vstack(outs), np.concatenate(idx)
