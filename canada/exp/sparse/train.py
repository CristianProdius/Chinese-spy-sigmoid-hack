"""Sparse strategy grid: lexicon, lexicon-restricted LR, L1 / elastic net, lexicon+learned hybrids.

    tools/h100.sh "cd exp/sparse && ../../.venv/bin/python train.py [stage]"

Dev (data/gen/dev_*.jsonl) is used only to compare finished models. Sealed fingerprints are used
unlabelled only: per-language bucket document frequencies, to find buckets where real text has
frequent words our data never shows (hash collisions), and the en/fr class-mix gap.
"""
import collections
import sys
import time
import warnings

import numpy as np
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression

from common import (CLASSES, DIM, HERE, Dev, augment, balanced_weights, bucket, doc_freq, lexicon_W,
                    lexicon_buckets, load_sets, xy)  # noqa: F401

warnings.filterwarnings("ignore")
OUT = HERE / "models"
OUT.mkdir(exist_ok=True)

S = load_sets()
dev = Dev(S["dev"])


def build_rows(corpus=None, n_aug=1, seed=0):
    rows = augment(S["train"] + S["boundary"], S["filler"], n_copies=n_aug, seed=seed)
    groups = ["gen"] * len(rows)
    if corpus:
        c = augment(S[corpus], S["filler"], n_copies=1, seed=seed + 1)
        rows += c
        groups += ["corpus"] * len(c)
    return rows, np.array(groups)


def build(corpus="recomb", corpus_share=0.3, n_aug=2, seed=0, lex_share=0.0, lex_n=60):
    """-> X, y, lang, w, base (base = rows without lexicon pseudo-docs, for bucket statistics)."""
    gen = S["train"] + S["boundary"]
    rows = augment(gen, S["filler"], n_copies=n_aug, seed=seed)
    groups = ["gen"] * len(rows)
    if corpus:
        c = augment(S[corpus], S["filler"], n_copies=1, seed=seed + 1)
        rows += c
        groups += ["corpus"] * len(c)
    nbase = len(rows)
    if lex_share:
        p = lexicon_pseudo(n_per=lex_n, seed=seed + 2)
        rows += p
        groups += ["lex"] * len(p)
    X, y, lang = xy(rows)
    groups = np.array(groups)
    gw = {"gen": 1 - corpus_share - lex_share}
    if corpus:
        gw["corpus"] = corpus_share
    if lex_share:
        gw["lex"] = lex_share
    w = balanced_weights(y, lang, groups, gw)
    return X, y, lang, w, nbase


def sealed_excess(Xtr, lang_tr):
    """Per bucket: max over languages of (sealed df - our training df). High = real-text words we lack."""
    Xs, ls = dev.Xs, dev.lang_s
    ex = np.zeros(DIM)
    for l in ("en", "fr"):
        d_s = (Xs[ls == l] > 0).mean(0)
        d_o = (Xtr[lang_tr == l] > 0).mean(0)
        ex = np.maximum(ex, d_s - d_o)
    return ex


def sealed_excess_cls(Xtr, y_tr, lang_tr):
    """Per bucket: max over languages of (sealed df - our df in the class that uses the bucket most).
    Positive only when real text fires the bucket more often than even our most related class does,
    i.e. a frequent real word we never wrote lands there (a collision), not a hazard word."""
    Xs, ls = dev.Xs, dev.lang_s
    ex = np.full(DIM, -1.0)
    for l in ("en", "fr"):
        d_s = (Xs[ls == l] > 0).mean(0)
        d_c = np.max([(Xtr[(lang_tr == l) & (y_tr == c)] > 0).mean(0) for c in range(9)], axis=0)
        ex = np.maximum(ex, d_s - d_c)
    return ex


def lexicon_pseudo(n_per=60, kmin=2, kmax=5, seed=0):
    """Pseudo-docs: a filler sentence plus a few lexicon terms of one class (gives every lexicon word a
    learned weight, even words our generated reports never use)."""
    import random
    from lexicon import LEX, term_list
    rng = random.Random(seed)
    fill = {l: [f["text"] for f in S["filler"] if f["lang"] == l] for l in ("en", "fr")}
    rows = []
    for c in CLASSES:
        terms = term_list(c, "strong") * 2 + term_list(c, "weak")
        for l in ("en", "fr"):
            for _ in range(n_per):
                k = rng.randint(kmin, kmax)
                body = ". ".join(rng.choice(terms).capitalize() for _ in range(k))
                rows.append({"text": rng.choice(fill[l]) + " " + body + ".", "label": c, "lang": l})
    return rows


def fit(X, y, w, C, penalty="l2", l1_ratio=None, col_scale=None):
    Xt = X if col_scale is None else X * col_scale[None, :]
    Xt = sp.csr_matrix(Xt)
    if penalty == "l2":
        m = LogisticRegression(C=C, max_iter=3000)
    elif penalty == "l1":
        m = LogisticRegression(C=C, penalty="l1", solver="saga", max_iter=400, tol=1e-3)
    else:
        m = LogisticRegression(C=C, penalty="elasticnet", solver="saga", l1_ratio=l1_ratio, max_iter=400, tol=1e-3)
    m.fit(Xt, y, sample_weight=w)
    W = m.coef_.copy()
    if col_scale is not None:
        W = W * col_scale[None, :]
    return W, m.intercept_.copy()


RESULTS = []


def run(name, W, b):
    r = dev.line(name, W, b)
    np.savez(OUT / f"{name}.npz", W=W, b=b)
    RESULTS.append((r["acc"], max(r["shares"].values()), r["tv"], name))


def main(stage):
    t0 = time.time()
    if stage in ("base", "all"):
        for corpus, share in ((None, 0), ("recomb", 0.3), ("recomb", 0.5), ("corpus", 0.3)):
            X, y, lang, w, _ = build(corpus, share)
            ex = sealed_excess(X, lang)
            lex = np.zeros(DIM, bool)
            lex[lexicon_buckets()] = True
            clean = ex < 0.05
            print(f"-- data corpus={corpus} share={share}: n={len(y)}  lexicon buckets {lex.sum()}  "
                  f"sealed-clean {clean.sum()}  lex&clean {(lex & clean).sum()}  ({time.time()-t0:.0f}s)", flush=True)
            tag = f"{corpus or 'gen'}{share}"
            for C in (1.0, 3.0, 10.0):
                W, b = fit(X, y, w, C)
                run(f"l2_all_{tag}_C{C}", W, b)
                W, b = fit(X, y, w, C, col_scale=lex.astype(float))
                run(f"l2_lex_{tag}_C{C}", W, b)
                W, b = fit(X, y, w, C, col_scale=(lex & clean).astype(float))
                run(f"l2_lexclean_{tag}_C{C}", W, b)
                W, b = fit(X, y, w, C, col_scale=clean.astype(float))
                run(f"l2_clean_{tag}_C{C}", W, b)
    if stage in ("l1", "all"):
        X, y, lang, w, _ = build("recomb", 0.3)
        for C in (1.0, 3.0, 10.0):
            W, b = fit(X, y, w, C, penalty="l1")
            run(f"l1_recomb0.3_C{C}", W, b)
            W, b = fit(X, y, w, C, penalty="en", l1_ratio=0.5)
            run(f"en0.5_recomb0.3_C{C}", W, b)
    if stage in ("v2", "all"):
        from common import lexicon_W
        Wlex = lexicon_W()
        for corpus, share in ((None, 0), ("recomb", 0.3)):
            tag = f"{corpus or 'gen'}{share}"
            for lex_share in (0.0, 0.1, 0.2):
                X, y, lang, w, nb = build(corpus, share, lex_share=lex_share)
                exc = sealed_excess_cls(X[:nb], y[:nb], lang[:nb])
                print(f"-- {tag} lex_share={lex_share} n={len(y)}  flagged buckets "
                      + " ".join(f"{t}:{(exc >= t).sum()}" for t in (0.02, 0.05, 0.1)), flush=True)
                for thr in (0.02, 0.05, 0.1):
                    cs = (exc < thr).astype(float)
                    for C in (3.0, 10.0):
                        W, b = fit(X, y, w, C, col_scale=cs)
                        run(f"v2_{tag}_lex{lex_share}_cls{thr}_C{C}", W, b)
                        if lex_share == 0.0 and thr == 0.05:
                            n = np.linalg.norm(W) / np.linalg.norm(Wlex)
                            for a in (0.1, 0.3):
                                run(f"v2_{tag}_hyb{a}_cls{thr}_C{C}", W + a * n * Wlex * cs, b)
    if stage in ("v3", "all"):
        from common import featurize_raw, l2norm, sealed_noise
        for corpus, share in ((None, 0), ("recomb", 0.3)):
            tag = f"{corpus or 'gen'}{share}"
            rows, groups = build_rows(corpus, n_aug=1)
            U = featurize_raw([r["text"] for r in rows])
            y = np.array([CLASSES.index(r["label"]) for r in rows])
            lang = np.array([r["lang"] for r in rows])
            X0 = l2norm(U)
            ex = {}
            for l in ("en", "fr"):
                ex[l] = np.clip((dev.Xs[dev.lang_s == l] > 0).mean(0) - (X0[lang == l] > 0).mean(0), 0, None)
            print(f"-- {tag} n={len(y)} expected noise features per doc en {ex['en'].sum():.1f} fr {ex['fr'].sum():.1f}", flush=True)
            for copies, scale in ((0, 0), (2, 1.0), (2, 2.0)):
                Xn, idx = sealed_noise(U, lang, ex, copies=copies, scale=scale, seed=7)
                yn, ln, gn = y[idx], lang[idx], groups[idx]
                gw = {"gen": 1 - share, "corpus": share} if corpus else {"gen": 1.0}
                w = balanced_weights(yn, ln, gn, gw)
                for C in (1.0, 3.0, 10.0):
                    W, b = fit(Xn, yn, w, C)
                    run(f"v3_{tag}_noise{copies}x{scale}_C{C}", W, b)
    if stage in ("v4", "all"):
        # everything together: generated + recombined corpus + lexicon pseudo-docs, sealed-matched hash
        # noise copies, class-aware collision mask
        from common import featurize_raw, l2norm, sealed_noise
        for share, lex_share, thr, C in ((0.3, 0.1, 0.02, 3.0), (0.2, 0.1, 0.02, 3.0), (0.3, 0.15, 0.05, 3.0),
                                         (0.3, 0.1, 0.02, 1.0), (0.4, 0.1, 0.02, 3.0)):
            rows, groups = build_rows("recomb", n_aug=1)
            nb = len(rows)
            p = lexicon_pseudo(n_per=60, seed=2)
            rows = rows + p
            groups = np.concatenate([groups, np.array(["lex"] * len(p))])
            U = featurize_raw([r["text"] for r in rows])
            y = np.array([CLASSES.index(r["label"]) for r in rows])
            lang = np.array([r["lang"] for r in rows])
            X0 = l2norm(U)
            ex = {l: np.clip((dev.Xs[dev.lang_s == l] > 0).mean(0) - (X0[:nb][lang[:nb] == l] > 0).mean(0), 0, None)
                  for l in ("en", "fr")}
            exc = sealed_excess_cls(X0[:nb], y[:nb], lang[:nb])
            cs = (exc < thr).astype(float)
            Xn, idx = sealed_noise(U, lang, ex, copies=2, scale=1.0, seed=7)
            yn, ln, gn = y[idx], lang[idx], groups[idx]
            w = balanced_weights(yn, ln, gn, {"gen": 1 - share - lex_share, "corpus": share, "lex": lex_share})
            W, b = fit(Xn, yn, w, C, col_scale=cs)
            run(f"v4_full_c{share}_lex{lex_share}_cls{thr}_C{C}", W, b)
    print("\n== top by dev acc")
    for acc, sh, tv, name in sorted(RESULTS, reverse=True)[:15]:
        print(f"  {acc:.3f} share {sh:+.3f} tv {tv:.3f} {name}")
    print(f"done {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "base")
