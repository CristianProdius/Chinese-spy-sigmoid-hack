# Sparse strategy: notes

Folder: `exp/sparse/`. Final models: `sparse_ens5.npz` (best), `sparse_v4full.npz` (best single model).
All numbers below: dev = held-out `data/gen/dev_*.jsonl` (360 reports, never trained on), "noisy" = dev
with real-text hash noise added (see 3), tv = en/fr class-mix gap on the sealed set.

## Vault tries (3 used)

| model | dev | tv | vault |
|---|---|---|---|
| `models/v4_full_c0.2_lex0.1_cls0.02_C3.0` (= `sparse_v4full.npz`) | 0.853 | 0.036 | **SNOWFLAKE** |
| `models/ens5` (= `sparse_ens5.npz`) | 0.878 | 0.053 | **SNOWFLAKE** |
| `models/probe_naive_conventions` (probe, not a candidate) | 0.800 | 0.039 | nothing |

The probe is the v4 recipe trained with the naive conventions the context warns against (ice storm /
freezing rain -> storm, avalanche -> winter, tsunami -> flood; 1,628 of 18,916 rows relabelled). It
changes 13% of sealed predictions and loses SNOWFLAKE. So the SNOWFLAKE door follows the stated
conventions. That points to SNOWFLAKE being the true labelling rather than a convention decoy, though it
does not rule out a decoy that differs in some other way. Both candidates sit near the threshold, since
a 13% change in predictions closes the door.

## What I tried

1. **Hand-written bilingual lexicon** (`lexicon.py`, general language knowledge only): ~1,300 unigram
   and bigram features in about 1,140 buckets, strong and weak tiers per class, French inflections
   written out. Bigrams made only of function words ("de la", "out of") are dropped.
   - Lexicon alone (W = lexicon weights, b = 0): dev 0.506, tv 0.10. Dropping buckets that collide with
     frequent words in our own text made it worse (0.44 to 0.46).
2. **LR restricted to lexicon buckets** (all other columns 0): dev 0.77 to 0.81 (`l2_lex_*`), against
   0.84 to 0.86 for unrestricted L2 LR on the same data. Too restrictive: real hazard vocabulary beyond
   the lexicon gets lost.
3. **Sealed-statistics hash-noise handling** (unlabelled sealed fingerprints only, through per-language
   bucket document frequencies):
   - mask `clean`: drop buckets where sealed df minus our df >= 0.05. Lowers tv (0.070 to 0.032 on
     recomb), same dev, but it also drops real hazard words ("flooding", "inondations", "tempête").
   - mask `cls` (kept): drop a bucket only when real text fires it more often than our most related
     class does (sealed df minus max over classes of our df >= 0.02). Flags 128 to 314 buckets, which are
     collisions with common real words (for example "yield" at 36% of English reports, "health" at 49%
     of French ones).
   - noise copies (kept): each training report gets 2 copies with extra buckets switched on at the
     per-language excess rate (sealed df minus our df), about 18 to 45 per report.
   - noisy-dev stress test: dev with the same noise. Models lose only 2 to 3 points, so collisions are
     not the main gap; vocabulary and style shift is.
4. **Lexicon pseudo-docs** (hybrid): a filler sentence plus 2 to 5 lexicon terms of one class, given
   10% of the training weight. This gives a weight to lexicon words that our generated reports never
   use. Post-hoc W + a*W_lex hybrids: dev about the same (0.85 to 0.86).
5. **L1 / elastic net** (saga, recomb share 0.3): L1 C=1 dev 0.803 (tv 0.10), L1 C=3 dev 0.811 (tv
   0.085), elastic net 0.5 C=1 dev 0.839. No better than L2, so not used (I stopped the C=10 runs).
6. **Data**: generated train + boundary (each augmented with 1 to 3 filler sentences) plus the
   recombined corpus at 20 to 30% of the weight, with class x language balanced weights. The raw corpus
   is worse. Gen-only and recomb models disagree on 20 to 25% of sealed reports.

## Final models

- `sparse_v4full.npz` (v4 recipe): gen + recomb (share 0.2) + lexicon pseudo-docs (0.1), 2 sealed-noise
  copies, `cls` mask 0.02, L2 C=3. Dev 0.853 (en 0.833, fr 0.872), noisy 0.822, tv 0.036.
- `sparse_ens5.npz`: average of 5 members, each scaled to unit logit spread on our train text:
  v4_full_c0.2_lex0.1_cls0.02_C3.0, v4_full_c0.3_lex0.15_cls0.05_C3.0, v3_recomb0.3_noise2x2.0_C1.0,
  v2_gen0_lex0.1_cls0.02_C3.0, v3_gen0_noise2x2.0_C3.0. Dev 0.878 (en 0.878, fr 0.878), noisy 0.856,
  tv 0.053; dev shares +0.143 / +0.146 / +0.158 / +0.148 / +0.099 / +0.024.

## Reproduce (from canada/)

```
tools/h100.sh "cd exp/sparse && ../../.venv/bin/python -u train.py v2 > logs/v2.log 2>&1"
tools/h100.sh "cd exp/sparse && ../../.venv/bin/python -u train.py v3 > logs/v3.log 2>&1"
tools/h100.sh "cd exp/sparse && ../../.venv/bin/python -u train.py v4 > logs/v4.log 2>&1"
tools/h100.sh "cd exp/sparse && ../../.venv/bin/python ens.py ens5 v4_full_c0.2_lex0.1_cls0.02_C3.0 v4_full_c0.3_lex0.15_cls0.05_C3.0 v3_recomb0.3_noise2x2.0_C1.0 v2_gen0_lex0.1_cls0.02_C3.0 v3_gen0_noise2x2.0_C3.0"
tools/h100.sh .venv/bin/python tools/eval_model.py exp/sparse/sparse_ens5.npz exp/sparse/sparse_v4full.npz
```

Other stages: `train.py base` (L2 all/lex/clean masks), `train.py l1`, `probe.py`, `analyze.py` (lexicon
collisions), `diag_mask.py` (which buckets the masks drop), `evalnoisy.py` (noisy dev), `compare.py`
(sealed class mix and agreement). All models are in `models/`. Seeds are fixed, but the BLAS thread count
may move the last digits.

The sealed fingerprints were used unlabelled only: bucket document frequencies per language (for masks and
noise) and the class-mix gap. Nothing was labelled. The vault internals were not used beyond `lib.vault`.
