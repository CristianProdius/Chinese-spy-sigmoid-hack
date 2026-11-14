"""Evaluate a model (.npz with W, b) the same way for everyone.

    .venv/bin/python tools/eval_model.py exp/x/model.npz [more.npz ...] [--vault]

Prints, per model:
  dev     accuracy on the held-out proxy dev set data/gen/dev_*.jsonl (overall, en, fr, per class)
  shares  the vault rule replayed on dev: for each share of the surest dev reports (by top1-top2
          margin), accuracy minus the accuracy the vault needs at that share. Any positive -> "would open".
  sealed  predicted class mix on the real sealed reports, English vs French, and the TV gap.
  vault   (--vault only, ~10 s) the words the real vault releases. SNOWBLIND is a known decoy.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lib import CLASSES, featurize, fp_lang, load_sealed, vault  # noqa: E402

N_REAL, K = 1369, 643
SHARES = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)


def need(share):
    m = int(N_REAL * share)
    return (m + K) / (2 * m)


def load_dev():
    rows = []
    for p in sorted((ROOT / "data/gen").glob("dev_*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def evaluate(W, b, X, y, lang):
    S = X @ W.T + b
    pred = S.argmax(1)
    part = np.sort(S, 1)
    margin = part[:, -1] - part[:, -2]
    order = np.argsort(-margin, kind="stable")
    res = {"acc": float((pred == y).mean())}
    for l in ("en", "fr"):
        res[f"acc_{l}"] = float((pred[lang == l] == y[lang == l]).mean()) if (lang == l).any() else float("nan")
    res["per_class"] = {c: float((pred[y == i] == i).mean()) if (y == i).any() else float("nan") for i, c in enumerate(CLASSES)}
    res["shares"] = {}
    for sh in SHARES:
        m = max(int(len(y) * sh), 1)
        acc = float((pred[order[:m]] == y[order[:m]]).mean())
        res["shares"][sh] = round(acc - need(sh), 3)
    res["would_open"] = any(v > 0 for v in res["shares"].values())
    return res


def sealed_gap(W, b, Xs, lang_s):
    pred = (Xs @ W.T + b).argmax(1)
    mix = {l: np.bincount(pred[lang_s == l], minlength=9) / max((lang_s == l).sum(), 1) for l in ("en", "fr")}
    return float(0.5 * np.abs(mix["en"] - mix["fr"]).sum()), mix


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_vault = "--vault" in sys.argv
    dev = load_dev()
    X = featurize([r["text"] for r in dev]) if dev else None
    y = np.array([CLASSES.index(r["label"]) for r in dev]) if dev else None
    lang = np.array([r["lang"] for r in dev]) if dev else None
    Xs = load_sealed()
    lang_s = fp_lang(Xs)
    print(f"dev reports: {len(dev)}")
    for path in args:
        z = np.load(path)
        W, b = np.asarray(z["W"], float), np.asarray(z["b"], float)
        print(f"== {path}")
        if dev:
            r = evaluate(W, b, X, y, lang)
            print(f"  dev acc {r['acc']:.3f} (en {r['acc_en']:.3f}, fr {r['acc_fr']:.3f})  would_open={r['would_open']}")
            print("  per class: " + "  ".join(f"{c[:5]} {v:.2f}" for c, v in r["per_class"].items()))
            print("  shares (acc - need): " + "  ".join(f"{k}:{v:+.3f}" for k, v in r["shares"].items()))
        tv, mix = sealed_gap(W, b, Xs, lang_s)
        print(f"  sealed TV gap {tv:.3f}; en mix " + " ".join(f"{v:.2f}" for v in mix["en"]) + " | fr mix " + " ".join(f"{v:.2f}" for v in mix["fr"]))
        if do_vault:
            print(f"  vault -> {vault(W, b, Xs)}")


if __name__ == "__main__":
    main()
