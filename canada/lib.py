"""Shared helpers for the Two Solitudes task. Run scripts with canada/.venv/bin/python."""
import csv
import collections
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TASK = HERE / "task"
sys.path.insert(0, str(TASK))

from featurize import DIM, bucket, featurize, tokens  # noqa: E402
from open_vault import CLASSES, load_sealed, try_vault  # noqa: E402

EN_FUNC = ["the", "of", "and", "was", "were", "in", "to", "a", "on", "with"]
FR_FUNC = ["la", "les", "des", "du", "et", "une", "est", "sont", "le", "au"]


def load_corpus(path=TASK / "corpus.csv"):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def text_lang(text):
    w = set(tokens(text))
    fr = len(w & set(FR_FUNC))
    en = len(w & set(EN_FUNC))
    return "fr" if fr > en else "en"


def fp_lang(X):
    """Language guess for fingerprints (rows of X) from function-word buckets."""
    en = sum((X[:, bucket(w)] > 0).astype(int) for w in EN_FUNC)
    fr = sum((X[:, bucket(w)] > 0).astype(int) for w in FR_FUNC)
    return np.where(fr > en, "fr", "en")


def corpus_xy(rows=None):
    rows = rows or load_corpus()
    X = featurize([r["text"] for r in rows])
    y = np.array([CLASSES.index(r["label"]) for r in rows])
    return X, y


def train_lr(X, y, C=10.0, sample_weight=None, max_iter=3000):
    from sklearn.linear_model import LogisticRegression

    m = LogisticRegression(C=C, max_iter=max_iter).fit(X, y, sample_weight=sample_weight)
    W = np.zeros((len(CLASSES), X.shape[1]))
    b = np.full(len(CLASSES), -30.0)
    W[m.classes_], b[m.classes_] = m.coef_, m.intercept_
    return W, b


def sealed_report(W, b, Xs=None, name=""):
    """Unsupervised diagnostics on the sealed fingerprints: class mix per language."""
    Xs = load_sealed() if Xs is None else Xs
    S = Xs @ W.T + b
    pred = S.argmax(1)
    lang = fp_lang(Xs)
    out = {}
    for l in ("en", "fr"):
        c = np.bincount(pred[lang == l], minlength=9) / max((lang == l).sum(), 1)
        out[l] = c
    tv = 0.5 * np.abs(out["en"] - out["fr"]).sum()
    print(f"{name} sealed class mix (en | fr), language gap TV={tv:.3f}")
    for i, c in enumerate(CLASSES):
        print(f"  {c:11s} {out['en'][i]:.3f} | {out['fr'][i]:.3f}")
    return pred, tv


def vault(W, b, Xs=None):
    Xs = load_sealed() if Xs is None else Xs
    return try_vault(Xs @ np.asarray(W, float).T + np.asarray(b, float), verbose=False)


def save_model(path, W, b):
    np.savez(path, W=np.asarray(W, np.float64), b=np.asarray(b, np.float64))


SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ0-9«\"])")


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]
