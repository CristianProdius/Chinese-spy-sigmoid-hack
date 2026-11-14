"""The Abidjan Transit Ledger (task_cote_divoire) - submission.

Same I/O contract as main_template.py: with no arguments it reads
`test-input.json` and writes `predictions.json` (filenames only, current
directory), one {"id", "label"} object per input row.

The dual-task model is recovered at run time, in a few seconds on CPU:

1. Task router. A small TF-IDF + logistic-regression classifier decides
   whether a request belongs to the old task (transactional SQL) or the new
   one (spatial / window functions). It trains on the labeled rows we were
   given: dataset/old_task_sample.json plus dataset/train-*.json.
2. Experts. Old-task requests go to the original checkpoint, which still
   knows the old task perfectly. New-task requests go to the fine-tuned
   checkpoint, which knows the new task perfectly. Each expert only chooses
   among its own task's five labels.

The recovered model is that mixture of experts: nothing either checkpoint
knows is thrown away, and the only new thing learned is the old/new split,
which is much easier than the ten-way problem. Each part is checked on the
labeled data at run time. If a checkpoint is missing or does worse than a
small self-trained classifier on its task, that classifier takes the task.

    python main.py                                  # graded run
    python main.py --input dataset/train-input.json --output p.json
    python main.py --model checkpoints/finetuned_model.joblib   # one checkpoint as-is
"""
from __future__ import annotations

import os

# The data is tiny: one BLAS thread is fastest, and many threads on a busy
# shared CPU slowed a run from ~7s to ~95s in testing. Set before numpy loads.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_var] = "1"

import argparse
import sys
from pathlib import Path

import numpy as np

import model_utils as mu

HERE = Path(__file__).resolve().parent
TASK_LABELS = {"old": list(mu.OLD_LABELS), "new": list(mu.NEW_LABELS)}
EXPERT_FILES = {"old": "original_model.joblib", "new": "finetuned_model.joblib"}


def locate(relative: str) -> Path | None:
    """Find a handed-out file next to the working directory or this script."""
    for base in (Path.cwd(), HERE, Path(mu.__file__).resolve().parent):
        path = base / relative
        if path.exists():
            return path
    return None


def labeled_rows() -> tuple[list[str], list[str]]:
    texts: list[str] = []
    labels: list[str] = []
    sample = locate("dataset/old_task_sample.json")
    if sample:
        for row in mu.load_records(sample):
            if row.get("label") in mu.ALL_LABELS:
                texts.append(row["text"])
                labels.append(row["label"])
    train_in = locate("dataset/train-input.json")
    train_out = locate("dataset/train-output.json")
    if train_in and train_out:
        gold = {row["id"]: row["label"] for row in mu.load_records(train_out)}
        for row in mu.load_records(train_in):
            if gold.get(row["id"]) in mu.ALL_LABELS:
                texts.append(row["text"])
                labels.append(gold[row["id"]])
    return texts, labels


def text_classifier():
    """Word + character n-gram TF-IDF into logistic regression."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline, make_union

    features = make_union(
        TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), sublinear_tf=True),
    )
    return make_pipeline(features, LogisticRegression(C=10, max_iter=5000))


def cv_accuracy(texts: list[str], targets: list[str]) -> float:
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    counts = np.unique(targets, return_counts=True)[1]
    folds = int(min(5, counts.min())) if len(counts) > 1 else 0
    if folds < 2:
        return 0.0
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=0)
    return float(cross_val_score(text_classifier(), texts, targets, cv=cv).mean())


def expert_choice(model, X: np.ndarray, labels: list[str]) -> list[str]:
    """The model's best label among `labels` only (its own task's labels)."""
    classes = [str(c) for c in getattr(model, "classes_", [])]
    scores = None
    for method in ("predict_proba", "decision_function"):
        if classes and hasattr(model, method):
            try:
                scores = np.asarray(getattr(model, method)(X), dtype=float)
                break
            except Exception:
                scores = None
    if scores is not None and scores.ndim == 1:  # binary decision_function
        scores = np.column_stack([-scores, scores])
    if scores is None or scores.shape != (len(X), len(classes)):
        predicted = [str(p) for p in model.predict(X)]
        classes = sorted(set(classes) | set(predicted))
        scores = np.array([[float(p == c) for c in classes] for p in predicted])
    restricted = np.full((len(X), len(labels)), -np.inf)
    for j, label in enumerate(labels):
        if label in classes:
            restricted[:, j] = scores[:, classes.index(label)]
    if not np.isfinite(restricted).any():
        raise ValueError("model knows none of this task's labels")
    return [labels[j] for j in restricted.argmax(axis=1)]


class TaskModel:
    """Labels requests of one task: a checkpoint expert or a fallback classifier."""

    def __init__(self, task: str, vectorizer, texts: list[str], labels: list[str]):
        self.task = task
        self.vectorizer = vectorizer
        self.expert = None
        self.fallback = None
        own_cv = cv_accuracy(texts, labels) if texts else 0.0
        expert_acc = -1.0
        path = locate(f"checkpoints/{EXPERT_FILES[task]}")
        if path is not None and vectorizer is not None:
            try:
                model = mu.load_model(path)
                if texts:
                    pred = expert_choice(model, mu.featurize(vectorizer, texts), TASK_LABELS[task])
                    expert_acc = float(np.mean([p == g for p, g in zip(pred, labels)]))
                else:
                    expert_acc = 1.0
                self.expert = model
            except Exception as exc:  # broken or incompatible checkpoint
                print(f"[{task}] expert unusable: {exc!r}", file=sys.stderr)
        # The fallback's random-split CV flatters it (paraphrase templates repeat
        # across folds), so keep a near-perfect expert even if the CV ties or wins.
        if self.expert is None or (expert_acc < 0.95 and expert_acc < own_cv):
            self.expert = None
            self.fallback = text_classifier().fit(texts, labels)
        source = f"expert {EXPERT_FILES[task]}" if self.expert is not None else "self-trained fallback"
        print(f"[{task}] using {source} (expert acc {expert_acc:.3f}, fallback cv {own_cv:.3f})")

    def predict(self, texts: list[str]) -> list[str]:
        if not texts:
            return []
        if self.expert is not None:
            X = mu.featurize(self.vectorizer, texts)
            return expert_choice(self.expert, X, TASK_LABELS[self.task])
        return [str(p) for p in self.fallback.predict(texts)]


class RecoveredModel:
    """Router + one labeler per task. Predicts from raw request text."""

    def __init__(self):
        texts, labels = labeled_rows()
        if not texts:
            raise RuntimeError("no labeled rows found under dataset/")
        tasks = [mu.task_of(label) for label in labels]
        print(f"labeled rows: {len(texts)} (old {tasks.count('old')}, new {tasks.count('new')})")
        print(f"router cv accuracy: {cv_accuracy(texts, tasks):.3f}")
        self.router = text_classifier().fit(texts, tasks)

        vectorizer_path = locate("checkpoints/vectorizer.joblib")
        try:
            vectorizer = mu.load_vectorizer(vectorizer_path) if vectorizer_path else None
        except Exception as exc:
            print(f"vectorizer unusable: {exc!r}", file=sys.stderr)
            vectorizer = None
        self.task_models = {}
        for task in ("old", "new"):
            keep = [i for i, t in enumerate(tasks) if t == task]
            self.task_models[task] = TaskModel(
                task, vectorizer, [texts[i] for i in keep], [labels[i] for i in keep]
            )

    def predict(self, texts: list[str]) -> list[str]:
        routes = [str(t) for t in self.router.predict(texts)] if texts else []
        out = [""] * len(texts)
        for task, model in self.task_models.items():
            idx = [i for i, t in enumerate(routes) if t == task]
            for i, label in zip(idx, model.predict([texts[i] for i in idx])):
                out[i] = label
        return out


def self_check(model: RecoveredModel) -> None:
    train_in = locate("dataset/train-input.json")
    train_out = locate("dataset/train-output.json")
    if not (train_in and train_out):
        return
    records = mu.load_records(train_in)
    gold = {row["id"]: row["label"] for row in mu.load_records(train_out)}
    pred = dict(zip([r["id"] for r in records], model.predict([r["text"] for r in records])))
    acc = mu.accuracy_by_task(gold, pred)
    print(f"self-check on dataset/train: old {acc['old']:.3f} / new {acc['new']:.3f}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="test-input.json", help="filename only, no path")
    parser.add_argument("--output", default="predictions.json", help="filename only, no path")
    parser.add_argument(
        "--model",
        default=None,
        help="run one checkpoint as-is instead of recovering (e.g. checkpoints/finetuned_model.joblib)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"input file not found: {input_path}", file=sys.stderr)
        return 2
    records = mu.load_records(input_path)
    ids = [r["id"] for r in records]
    texts = [r["text"] for r in records]

    if args.model:
        model_path = Path(args.model)
        if not model_path.exists():
            print(f"model checkpoint not found: {model_path}", file=sys.stderr)
            return 2
        labels = mu.predict_labels(mu.load_model(model_path), mu.load_vectorizer(), texts)
    else:
        model = RecoveredModel()
        self_check(model)
        labels = model.predict(texts)

    predictions = [{"id": rid, "label": str(label)} for rid, label in zip(ids, labels)]
    mu.save_records(predictions, Path(args.output))
    print(f"wrote {len(predictions)} predictions to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
