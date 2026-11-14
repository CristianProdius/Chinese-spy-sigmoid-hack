"""End-to-end check of main.py against stand-in checkpoints.

The real checkpoints/ folder was not handed out locally, so this builds
stand-ins that reproduce the documented symptom (original: old 1.00 / new
0.00, fine-tuned: old 0.00 / new 1.00) in several plausible shapes, then runs
main.py exactly as the harness does (`python main.py`, no arguments) in a
scratch directory.

The hidden test is simulated by holding out whole paraphrase templates: the
stand-in checkpoints are trained on every row (like the real ones, which saw
the full task data), but main.py only gets the rows from the other templates.

    python tools/simulate.py            # all variants, 3 hold-out seeds each
"""
from __future__ import annotations

import copy
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "task"
sys.path.insert(0, str(TASK))
import model_utils as mu  # noqa: E402

ENTITY = re.compile(
    r"\b(?:truck|van)-\d+\b|\b(?:Fatou|Konan|Ibrahim|Adjoa|Mariam|Aminata|Yao|Kouassi|Vridi|"
    r"Treichville|Marcory|Koumassi|Yopougon|cocoa|cashew|textiles|electronics)\b|\b\d+\b"
)


def all_rows() -> list[dict]:
    rows = [dict(r, src="replay") for r in mu.load_records(TASK / "old_task_sample.json")]
    gold = {r["id"]: r["label"] for r in mu.load_records(TASK / "train-output.json")}
    rows += [dict(r, label=gold[r["id"]], src="train") for r in mu.load_records(TASK / "train-input.json")]
    for r in rows:
        r["template"] = ENTITY.sub("<E>", r["text"])
    return rows


def make_vectorizer(kind: str):
    return {
        "tfidf": lambda: TfidfVectorizer(),
        "count": lambda: CountVectorizer(ngram_range=(1, 2), binary=True),
        "char": lambda: TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4), max_features=600),
    }[kind]()


def train_sequential(model, X_old, y_old, X_new, y_new, epochs=60):
    """Old task first, then continue on the new task only (catastrophic forgetting)."""
    for _ in range(epochs):
        model.partial_fit(X_old, y_old, classes=mu.ALL_LABELS)
    original = copy.deepcopy(model)
    for _ in range(epochs):
        model.partial_fit(X_new, y_new)
    return original, model


def build_checkpoints(kind: str, vec_kind: str, rows: list[dict], out: Path) -> None:
    texts = [r["text"] for r in rows]
    vectorizer = make_vectorizer(vec_kind).fit(texts)
    X = vectorizer.transform(texts).toarray()
    y = np.array([r["label"] for r in rows])
    old = np.isin(y, mu.OLD_LABELS)
    if kind == "mlp":
        original, finetuned = train_sequential(
            MLPClassifier(hidden_layer_sizes=(64,), random_state=0), X[old], y[old], X[~old], y[~old]
        )
    elif kind in ("sgd_log", "sgd_hinge"):
        loss = "log_loss" if kind == "sgd_log" else "hinge"
        original, finetuned = train_sequential(
            SGDClassifier(loss=loss, random_state=0), X[old], y[old], X[~old], y[~old]
        )
    elif kind == "separate":  # each checkpoint only has its own task's classes
        original = MLPClassifier(hidden_layer_sizes=(64,), max_iter=500, random_state=0).fit(X[old], y[old])
        finetuned = MLPClassifier(hidden_layer_sizes=(64,), max_iter=500, random_state=0).fit(X[~old], y[~old])
    else:
        raise ValueError(kind)
    ck = out / "checkpoints"
    ck.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, ck / "vectorizer.joblib")
    joblib.dump(original, ck / "original_model.joblib")
    joblib.dump(finetuned, ck / "finetuned_model.joblib")


def score(pred_path: Path, rows: list[dict]) -> dict[str, float]:
    pred = {r["id"]: r["label"] for r in mu.load_records(pred_path)}
    return mu.accuracy_by_task({r["id"]: r["label"] for r in rows}, pred)


def symptom(work: Path, rows: list[dict]) -> str:
    vectorizer = joblib.load(work / "checkpoints/vectorizer.joblib")
    gold = {r["id"]: r["label"] for r in rows}
    parts = []
    for name in ("original", "finetuned"):
        model = joblib.load(work / f"checkpoints/{name}_model.joblib")
        pred = dict(zip(gold, mu.predict_labels(model, vectorizer, [r["text"] for r in rows])))
        acc = mu.accuracy_by_task(gold, pred)
        parts.append(f"{name} {acc['old']:.2f}/{acc['new']:.2f}")
    return ", ".join(parts)


def run_case(kind: str, vec_kind: str, seed: int, mutate=None) -> tuple[dict, str, float]:
    rows = all_rows()
    rnd = random.Random(seed)
    held = set()
    for label in mu.ALL_LABELS:
        templates = sorted({r["template"] for r in rows if r["label"] == label})
        rnd.shuffle(templates)
        held |= set(templates[: max(1, round(0.3 * len(templates)))])
    test = [r for r in rows if r["template"] in held]
    keep = [r for r in rows if r["template"] not in held]

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        build_checkpoints(kind, vec_kind, rows, work)
        sym = symptom(work, rows)
        if mutate:
            mutate(work)
        (work / "dataset").mkdir()
        mu.save_records(
            [{"id": r["id"], "text": r["text"], "label": r["label"]} for r in keep if r["src"] == "replay"],
            work / "dataset/old_task_sample.json",
        )
        train = [r for r in keep if r["src"] == "train"]
        mu.save_records([{"id": r["id"], "text": r["text"]} for r in train], work / "dataset/train-input.json")
        mu.save_records([{"id": r["id"], "label": r["label"]} for r in train], work / "dataset/train-output.json")
        mu.save_records([{"id": r["id"], "text": r["text"]} for r in test], work / "test-input.json")
        shutil.copy(TASK / "model_utils.py", work)
        shutil.copy(ROOT / "main.py", work)
        start = time.time()
        proc = subprocess.run([sys.executable, "main.py"], cwd=work, capture_output=True, text=True)
        elapsed = time.time() - start
        if proc.returncode != 0:
            raise RuntimeError(proc.stdout + proc.stderr)
        log = " | ".join(line for line in proc.stdout.splitlines() if line.startswith("["))
        return score(work / "predictions.json", test), f"{sym} || {log}", elapsed


def drop_original(work: Path) -> None:
    (work / "checkpoints/original_model.joblib").unlink()


def junk_finetuned(work: Path) -> None:
    from sklearn.dummy import DummyClassifier

    junk = DummyClassifier(strategy="most_frequent").fit(np.zeros((2, 1)), mu.NEW_LABELS[:2])
    joblib.dump(junk, work / "checkpoints/finetuned_model.joblib")


def main() -> int:
    cases = [(k, v, None, "") for k in ("mlp", "sgd_log", "sgd_hinge", "separate") for v in ("tfidf", "count", "char")]
    cases += [("mlp", "tfidf", drop_original, " [original missing]"), ("mlp", "tfidf", junk_finetuned, " [finetuned junk]")]
    # The gate covers the normal cases. The missing/junk-checkpoint cases show
    # the degraded mode (self-trained fallback on unseen templates) and are
    # reported apart from the gate.
    worst = {"normal": {"old": 1.0, "new": 1.0}, "degraded": {"old": 1.0, "new": 1.0}}
    for kind, vec_kind, mutate, note in cases:
        group = "degraded" if mutate else "normal"
        for seed in range(3):
            acc, log, elapsed = run_case(kind, vec_kind, seed, mutate)
            worst[group] = {t: min(worst[group][t], acc[t]) for t in acc}
            print(f"{kind:9s} {vec_kind:5s} seed {seed}{note}: old {acc['old']:.3f} new {acc['new']:.3f} "
                  f"({elapsed:.1f}s)  {log}", flush=True)
    for group, acc in worst.items():
        print(f"WORST {group}: old {acc['old']:.3f} new {acc['new']:.3f}")
    return 0 if min(worst["normal"].values()) >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
