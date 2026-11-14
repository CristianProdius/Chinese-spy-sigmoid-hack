# Experiment log

Everything measured on the way to the shipped retriever, in order. Hit@3 on the 268 public sample
questions unless noted. "Held-out" means the 1568 synthetic questions in `work/*_hold.jsonl` plus the
sample, never used for training. Raw logs from the GPU runs are in `work/runs/`.

## Submission versions (task/local_check.py)

| version | what changed | Hit@3 | size | load | p95 |
|---|---|---|---|---|---|
| provided baseline | - | 0.709 | 80.25 MB | 4.5 s | 28.5 ms |
| v0 | lexical only: window BM25 with MaxP, uint8 CSR | 0.817 | 8.61 MB | 0.23 s | 1.0 ms |
| v1 | + asymmetric dense leg (leaf-ir query -> arctic-m int8 passages), z-score fusion | 0.907 | 52.46 MB | 7.0 s | 26.6 ms |
| v2 | 4-bit passage vectors | 0.925 | 42.33 MB | 1.5 s | 33.5 ms |
| v3 | + edit-distance-1 typo correction | 0.929 | 42.33 MB | | |
| v4 | fine-tuned query encoder (ft_b epoch 2) | 0.937 | 42.33 MB | | |
| v5 | distilled query encoder (dist_c epoch 3), w_dense 3.0 | 0.944-0.948 | 42.33 MB | | |
| **v6 (shipped)** | + MatMulInteger matvec, query-time typo candidates | **0.948** | 42.33 MB | 0.35 s | 5.7 ms |

Load and p95 for v6 are from an idle machine. Rows without them were measured only on the overloaded
dev server, where wall-clock numbers are dominated by contention (see "Latency" below).

## Dense model survey (work/runs/exp_dense.log)

Symmetric models over the same 200/50 windows, public sample, dense alone and fused with BM25:

| model | dense Hit@3 | fused (lin 0.5) |
|---|---|---|
| arctic-embed-s | 0.866 | 0.888 |
| gte-small | 0.862 | 0.896 |
| arctic-embed-xs | 0.828 | 0.899 |
| bge-small-v1.5 | 0.817 | 0.907 |
| e5-small-v2 | 0.802 | 0.907 |
| all-MiniLM-L6 | 0.810 | 0.888 |
| potion / model2vec (8M-32M) | 0.64-0.74 | 0.85-0.87 |

Then asymmetric pairs (work/runs/exp_asym.log): arctic-embed-m-v1.5 on both sides reaches 0.914 dense
but its query encoder is too big for the budget. leaf-ir queries against arctic-m passages give 0.888
dense / 0.910 fused with a 23 MB int8 encoder, so that pair was kept. Truncating to 256 dimensions
cost 1-4.5 points dense.

## Synthetic questions (work/*.jsonl)

The public sample is too small to tune on safely, so four kinds of slips were generated from corpus
passages, each split into train and held-out parts by source passage:

| set | source | train / held-out |
|---|---|---|
| synth_q72 | Qwen2.5-72B on the H100 (`build/gen_synth.py`) | 3328 (train_q72m: the 2728 whose rewrites are not held out) |
| vset | Claude subagents (`research/workflows/cuba-vset-slips-*.js`) | 2000 / 400 |
| hard | Claude, vague and indirect slips (`research/workflows/cuba-hard-slips-*.js`) | 1500 / 300 |
| rewrites | Claude paraphrases of the Qwen slips (same workflow) | 2728 / 600 |

vset turned out too easy (fused 0.975+). The rewrites have word overlap with their passage close to
the real slips (0.750 vs 0.758) and are the most pessimistic set.

## Query encoder training (H100, work/runs/)

All runs keep the arctic-m passage vectors frozen (4-bit, as shipped) and train only leaf-ir.

| run | recipe | held-out all (fused) |
|---|---|---|
| base leaf-ir | - | 0.889 |
| ft_a | InfoNCE, lr 3e-5, scale 20, q72 + vset (5328) | worse: sample dense 0.888 -> 0.854 |
| ft_lr* sweep | lr 2e-6..1e-5, scale 20/50, q72 + vset | scale 50: sample dense +0.4-1.1, fused flat; scale 20 hurt |
| ft_b | InfoNCE, lr 1e-5, scale 50, all 8956 train slips, 2 epochs | 0.896 |
| dist_b | distil from arctic-m (+40k corpus snippets), contrastive lam 0.2 | 0.902 |
| **dist_c** | same, lam 1.0, epoch 3 | **0.905** |
| soup | weight average of ft_b and dist_b | 0.899 |

Distillation works better than plain fine-tuning because the student learns the teacher's query space
from 40k unlabelled snippets as well as the slips, so it does not drift away from the passage vectors.
A stronger contrastive term (lam 1.0) helped most on the hard and paraphrased sets.

## Fusion weight

`z(lexical) + w * z(dense)`. With the base encoder the best w was 2.0. With the distilled encoder the
curve is flat from 2.5 to 4 (held-out 0.904 / 0.905 / 0.904), so 3.0 ships.

## Tried and rejected

- PCA or 256-d truncation of passage vectors: lost accuracy for the size saved; 4-bit codes won.
- Window-level fusion (fuse before MaxP): no gain over document-level fusion.
- A second dense leg, a doc-level BM25 term, other k1/b values: flat or worse.
- faiss scalar quantisation (SQ4/SQ8): dropped for our own 4-bit codes, which need no extra dependency.
- Cross-encoder reranking: latency benchmarked during research (`research/bench/bench_ce*.py`), not
  pursued.

## Latency

- The dense matvec (26354 windows x 768) in float32 numpy reads 81 MB per query: 9 ms. As a uint8 x
  int8 `MatMulInteger` in ONNX Runtime with the codes prepacked once it takes 2.5 ms
  (`research/bench/matvec_prepack.py`). ORT only prepacks a constant initializer: passing the codes as
  an overridable input costs 14 ms. They are supplied with `SessionOptions.add_initializer` over a
  1-column placeholder, and the OrtValue must stay alive or the session segfaults.
- The typo-correction delete index took 1.9 s at load; generating edit-distance-1 candidates per
  unknown word at query time costs ~50 us and nothing at load.
- On the shared dev server (load ~350 on 48 cores) wall-clock p95 swung between 70 and 180 ms for the
  same zip, against 19 ms CPU time. `tools/latency_ab.py` compares two builds interleaved in one
  process, and `tools/cputime.py` reports CPU time per stage.
