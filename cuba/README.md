# Zemí - "If you know, you know!" (Cuba)

Chapter retrieval for the lector's slips over 1552 documents about Cuba. The submission is
`submission/main.py` + `submission/index/`, packaged as `cuba_submission.zip` (main.py and index/ only).

## Results

| check | result | limit |
|---|---|---|
| Hit@3, public sample (268) | **0.948** | >= 0.80 |
| index size (main.py + index/) | 42.33 MB | <= 53 MB |
| load time (idle box) | 0.35 s | <= 10 s |
| p95 search latency, 1 thread (idle box) | 5.7 ms | <= 75 ms |

Latency and load are from `task/local_check.py` on a quiet machine. On the shared dev server (load ~350
on 48 cores) the same zip measures 70-180 ms wall time because of contention; its CPU time per query is
p95 19 ms there. The zip also passes on Python 3.11 with onnxruntime 1.19.2 and tokenizers 0.19.1.

Held-out synthetic sets (built from the corpus, never trained on), Hit@3 of the shipped config:

| set | n | base (v3) | shipped |
|---|---|---|---|
| public sample | 268 | 0.929 | 0.948 |
| vset_hold (Claude slips) | 400 | 0.975 | 0.980 |
| rw_hold (paraphrased slips, pessimistic) | 600 | 0.795 | 0.817 |
| hard_hold (vague slips) | 300 | 0.927 | 0.943 |
| all | 1568 | 0.889 | 0.905 |

## How it works

Every document is cut into 200-word windows (50-word overlap, title prefixed). A query is scored two
ways against every window, a document takes its best window in each, and the two document scores are
z-normalised and mixed `z(lexical) + 3.0 * z(dense)`.

1. **Lexical**: BM25 (k1 1.2, b 0.75) with English stemming and accent folding. Weights are precomputed
   per (term, window) as uint8 in a term-major CSR, so a query is one `np.bincount`. Spanish words in a
   slip add their English meaning; Spanish function words are dropped. Unknown words of 5+ letters are
   corrected to the most frequent vocabulary term within one edit.
2. **Dense, asymmetric**: passages were embedded offline with `Snowflake/snowflake-arctic-embed-m-v1.5`
   (768-d) and stored as 4-bit per-dimension codes. Queries go through a small encoder
   (`MongoDB/mdbr-leaf-ir`, int8 ONNX, 23 MB) that maps into the same space. The query x codes product
   runs in ONNX Runtime as a uint8 x int8 `MatMulInteger` with the codes prepacked at load (2.5 ms vs
   9 ms for float32 numpy).
3. **Query-encoder distillation** (H100): leaf-ir was trained to reproduce arctic-m's query embeddings
   on 8956 synthetic slips + 40k corpus snippets, with slip-style noise (typos, Spanish words) on the
   student side only, plus a contrastive term against the frozen 4-bit passage vectors where every
   window of the gold document is a positive.

No PyTorch and no network at query time: numpy, onnxruntime, tokenizers and PyStemmer.

## Reproduce

```bash
# GPU box: passage embeddings and the distilled query encoder
python build/embed.py Snowflake/snowflake-arctic-embed-m-v1.5 arctic_m15 200 50   # -> work/emb_arctic_m15_200_50.npy
python build/distill_query.py --train work/train_q72m.jsonl work/train_vset.jsonl \
    work/train_hard.jsonl work/train_rw.jsonl --out work/dist_c --snippets 40000 \
    --epochs 3 --lr 2e-5 --lam 1.0
python build/export_st_onnx.py work/dist_c/epoch3 work/onnx_dist_c3

# CPU: index, evaluation, package
python build/build_index.py --out submission/index --size 200 --overlap 50 \
    --vectors work/emb_arctic_m15_200_50.npy --onnx work/onnx_dist_c3 \
    --prefix "Represent this sentence for searching relevant passages: " --w-dense 3.0
python build/eval_suite.py <folder with main.py + index/>
python task/local_check.py cuba_submission.zip
```

`submission/` (main.py + index/) is the complete submission and is in git. `work/` (embeddings,
synthetic slips, checkpoints) is not.
