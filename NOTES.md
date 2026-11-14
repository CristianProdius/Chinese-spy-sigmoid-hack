# The Great American Token Mystery: solver notes

`main.py` finds the tokenizer whose encoding of `calibration.text` reproduces `calibration.token_ids`,
then decodes `challenge.token_ids` with it.

## Run it

```bash
cd /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/NLP-united-states
uv sync                                   # once: tiktoken, transformers, tokenizers, sentencepiece, protobuf, huggingface_hub
uv run python prefetch.py                 # once: download tokenizer files for every candidate (18s here)

# the task contract: reads ./test-input.json, writes ./test-output.json
cd <dir with test-input.json> && HF_HUB_OFFLINE=1 uv run --project /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/NLP-united-states python /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/NLP-united-states/main.py

# or with explicit paths
uv run python main.py data/test-input.json /tmp/out.json
uv run python main.py data/test-input.json /tmp/out.json --all          # score every candidate, list collisions
uv run python main.py data/test-input.json /tmp/out.json --only gpt2,p50k_base
```

stdout gets the output JSON. stderr gets one line per candidate tried, the chosen engine and variant,
collisions, the raw decode with special tokens kept, and the final message. Add `--quiet` to silence it.

Files:

| File | What it is |
|---|---|
| `main.py` | The solver. Holds the candidate list (output id, kind, sources, vocab hint). |
| `prefetch.py` | Warms the HF and tiktoken caches (tokenizer files only), then loads every candidate offline. Writes `prefetch-report.json`. `--verify` skips downloads. |
| `verify.py` | Generates calibration/challenge pairs with 31 author-side encoders and runs `main.py` on each in its own dir under `/tmp/nlp-us-verify/`. `--collisions` scans every candidate for exact collisions. Writes `verify-report.json`. |

## Results on the real data (`data/`, committed in `8d2fc79` by another session)

| Input | Answer | Matches | Time |
|---|---|---|---|
| `data/train-input-2.json` | `p50k_base`, "TRAIN_SAMPLE: Verification successful ..." | `data/train-output-3.json` byte for byte | 1.3s |
| `data/test-input.json` | `cl100k_base`, "SIGMOID_TOKENIZATION\nCongratulations! ..." | the committed `test-output.json` byte for byte | 0.4s |

The train calibration is Python code with indentation. Its runs of spaces become p50k whitespace tokens
(max id 50258), which rules out `gpt2`/`r50k_base`. `p50k_edit` collides with `p50k_base` and loses the
tie-break.

## How it works

1. **Pre-filter.** Skip any candidate whose vocab size (a hint stored in `CANDIDATES`, measured by
   `prefetch.py`) is <= the largest id in the calibration or the challenge.
2. **Engines.** Each candidate is tried with up to four engines, loaded lazily, cheapest first:
   - tiktoken: `encode_ordinary` and `encode(allowed_special="all")`
   - transformers `AutoTokenizer`: `encode(add_special_tokens=True/False)`
   - raw `tokenizers.Tokenizer.from_file(tokenizer.json)`: `encode(add_special_tokens=True/False)`
   - raw `sentencepiece` on every `.model` file in the repo, using raw spm ids (no fairseq offset)

   Each engine also tries three text variants: the text as given, `text.strip()`, and `" " + text`.
   The raw `tokenizer.json` engine is skipped when the transformers engine scores below 0.5 fuzzy similarity (same ids, so it would only cost load time).
3. **Match levels** for the calibration ids:
   - 3: the engine's own `encode()` output equals the ids exactly
   - 2: equal once a single BOS/EOS/CLS/SEP is added by hand at either end
   - 1: equal between the special tokens, with other special tokens around them (language codes and so on)
   - 0: no match; a fuzzy score (multiset overlap plus longest common prefix) is kept for the fallback
4. **Challenge checks** for each matching candidate:
   - every challenge id is inside the vocab
   - the decoded challenge contains `sigmoid_<word>` (case-insensitive)
   - decode → re-encode gives the challenge ids back, ignoring special, `<unk>` and whitespace-only tokens. This check only counts against a tokenizer that round-trips the calibration. Lossy tokenizers such as T5, uncased BERT and Marian can't round-trip the challenge either.
5. **Ranking:** match >= 1, then ids in range, then flag, then level, then round-trip, then fuzzy, then list position. The search stops at the first candidate with level 3, ids in range and a round-trip. Nothing later can beat it except on list preference.
6. **Decoding.** Decode with special tokens skipped. Then pick the post-processing (`none`, `lstrip`,
   WordPiece de-spacing, or both) that best reproduces the *calibration text* from the calibration ids.
   For lossless tokenizers that is always `none`, and the output is untouched. For lossy ones
   (calibration round-trip < 1.0) the flag is also normalised to `SIGMOID_<WORD>` (e.g. bert-uncased's
   `sigmoid _ test`).
7. **Never crashes.** A missing or malformed input, an empty challenge, no network or a cold cache still
   write a `test-output.json` and exit 0. If nothing matches, the closest candidate is used.

## Candidates (97 entries, 96 tokenizer ids, all load offline)

The order in `CANDIDATES` is the preference order. Groups:

- **tiktoken:** cl100k_base, o200k_base, gpt2, r50k_base, p50k_base, p50k_edit, o200k_harmony
- **Classic HF:** gpt2, bert-base-uncased/cased, bert-base-multilingual-cased/uncased, roberta-base,
  xlm-roberta-base, t5-base, google/mt5-small, Llama-2, Llama-3, Mistral-7B-v0.1, Qwen2.5,
  gemma-2b, bloom-560m, gpt-neox-20b, falcon-7b, opt-125m, byt5-small, albert-base-v2,
  xlnet-base-cased, deberta-v3-base, mdeberta-v3-base, camembert-base
- **Spanish / bilingual / translation:** BETO cased and uncased (dccuchile), PlanTL roberta-base-bne
  and gpt2-base-bne, bertin-roberta-base-spanish, DeepESP/gpt2-spanish, opus-mt-en-es and -es-en,
  nllb-200-distilled-600M, m2m100_418M, mbart-large-50 and -cc25, xglm-564M, LaBSE, whisper-small,
  umt5-small, rembert, mGPT, salamandra-2b
- **Newer LLMs:** Llama-3.1, Mistral-7B-v0.3, Mistral-Nemo (Tekken), Qwen2, Qwen3, Qwen3.5, gemma-2,
  gemma-3, phi-2, Phi-3-mini, phi-4, deepseek-llm, deepseek-coder, DeepSeek-V3, Yi-6B, starcoder,
  starcoder2, codegen-350M-mono, stablelm-2-1_6b, SmolLM2, OLMo-2
- **Other encoders:** deberta-base, all-mpnet-base-v2, clip-vit-base-patch32, canine-s, pegasus-large,
  bigbird-roberta-base
- **Same vocab as an earlier entry** (kept so collisions get reported): distilgpt2, gpt-neo-125m,
  gpt-j-6b, distilbert-*, electra-base, all-MiniLM-L6-v2, distiluse-multilingual, distilroberta,
  bart-base, longformer, paraphrase-multilingual-MiniLM, multilingual-e5-base, bge-m3, t5-small,
  flan-t5-base, pythia-160m, huggyllama/llama-7b, TinyLlama

### Gated or broken, and what loads instead

The output id stays the canonical name either way.

| Wanted | Problem | Loaded from |
|---|---|---|
| `meta-llama/Llama-2-7b-hf` | gated (401, no HF token on this box) | `NousResearch/Llama-2-7b-hf` |
| `meta-llama/Meta-Llama-3-8B`, `Llama-3.1-8B` | gated | `NousResearch/Meta-Llama-3-8B`, `NousResearch/Meta-Llama-3.1-8B-Instruct` |
| `google/gemma-2b`, `gemma-2-2b`, `gemma-3-4b-it` | gated | `unsloth/gemma-2b`, `unsloth/gemma-2-2b`, `unsloth/gemma-3-4b-it` |
| `bigcode/starcoder` (and `starcoderbase-1b`) | gated | `bigcode/tiny_starcoder_py` (same tokenizer) |
| `PlanTL-GOB-ES/roberta-base-bne`, `gpt2-base-bne` | repos emptied (README only); `BSC-LT/*` copies don't exist | fine-tunes `JonatanGk/roberta-base-bne-finetuned-sqac`, `joancipria/gpt2-base-bne-FineTunedEmoEvent` |
| `mistralai/Mistral-7B-v0.1`, `-v0.3` | not gated for tokenizer files | official repo |

Left out on purpose: tokenizers that need `trust_remote_code` (Kimi-K2, ChatGLM/GLM-4, Baichuan,
InternLM), plus gated Command-R/Aya-23 and Llama-4.

## Verification (synthetic, 31 cases)

Calibration text: four lines of English/Spanish with accents, ñ, ¿¡, the 🇺🇸🌮 emoji, `$12.50`,
quotes and `24/7`. Challenge: two lines with `SIGMOID_TEST` and a 🎉 emoji. The p50k case adds an
indented code block. Every case is encoded the way an author would: tiktoken `enc.encode`, HF
`tok.encode`, `tokenizers` `Tokenizer.encode`, or raw `sp.encode`. Then `main.py` runs offline in its
own directory.

| # | Case (how the ids were made) | Expected | main.py answer | Tokenizer | Text | Time |
|---|---|---|---|---|---|---|
| 1 | tiktoken cl100k_base | `cl100k_base` | `cl100k_base` | exact | exact | 0.6s |
| 2 | tiktoken o200k_base | `o200k_base` | `o200k_base` | exact | exact | 1.0s |
| 3 | tiktoken p50k_base, challenge with space runs | `p50k_base` | `p50k_base` | exact | exact | 1.5s |
| 4 | transformers gpt2 | `gpt2` | `gpt2` | exact | exact | 1.9s |
| 5 | bert-base-uncased | `bert-base-uncased` | `bert-base-uncased` | exact | 0.933 (lossy) | 8.5s |
| 6 | bert-base-multilingual-cased | `bert-base-multilingual-cased` | same | exact | 0.988 (lossy) | 6.2s |
| 7 | xlm-roberta-base | `xlm-roberta-base` | same | exact | 0.994 (lossy) | 7.2s |
| 8 | xlm-roberta raw sentencepiece ids | `xlm-roberta-base` | same | exact | 0.994 (lossy) | 9.9s |
| 9 | t5-base | `t5-base` | same | exact | 0.972 (lossy) | 22.1s |
| 10 | mt5 raw sentencepiece | `google/mt5-small` | same | exact | 0.994 (lossy) | 11.5s |
| 11 | Llama-2 (HF, BOS) | `meta-llama/Llama-2-7b-hf` | same | exact | exact | 19.6s |
| 12 | Llama-2 raw sentencepiece | `meta-llama/Llama-2-7b-hf` | same | exact | exact | 19.6s |
| 13 | Llama-3 (HF, BOS) | `meta-llama/Meta-Llama-3-8B` | same | exact | exact | 14.0s |
| 14 | Mistral-7B-v0.1 | `mistralai/Mistral-7B-v0.1` | same | exact | exact | 19.5s |
| 15 | Qwen2.5 | `Qwen/Qwen2.5-0.5B` | same | exact | exact | 14.1s |
| 16 | gemma-2b | `google/gemma-2b` | same | exact | exact | 15.6s |
| 17 | bloom via `tokenizers` lib | `bigscience/bloom-560m` | same | exact | exact | 15.1s |
| 18 | gpt-neox-20b | `EleutherAI/gpt-neox-20b` | same | exact | exact | 25.0s |
| 19 | BETO cased | `dccuchile/bert-base-spanish-wwm-cased` | same | exact | 0.988 (lossy) | 29.0s |
| 20 | opus-mt-en-es | `Helsinki-NLP/opus-mt-en-es` | same | exact | 0.988 (lossy) | 24.7s |
| 21 | nllb-200 | `facebook/nllb-200-distilled-600M` | same | exact | 0.988 (lossy) | 6.4s |
| 22 | byt5 | `google/byt5-small` | same | exact | exact | 25.4s |
| 23 | deberta-v3 | `microsoft/deberta-v3-base` | same | exact | 0.994 (lossy) | 25.5s |
| 24 | Phi-3-mini | `microsoft/Phi-3-mini-4k-instruct` | `meta-llama/Llama-2-7b-hf` | collision, tie-break | exact | 19.3s |
| 25 | bart-base | `facebook/bart-base` | `roberta-base` | collision, tie-break | exact | 9.2s |
| 26 | o200k_harmony | `o200k_harmony` | `o200k_base` | collision, tie-break | exact | 1.1s |
| 27 | gpt2 + `<\|endoftext\|>` added by hand | `gpt2` | `gpt2` | exact | exact | 107.0s (full scan) |
| 28 | bert-base-cased, `add_special_tokens=False` | `bert-base-cased` | same | exact | 0.988 (lossy) | 8.3s |
| 29 | Llama-2 without BOS | `meta-llama/Llama-2-7b-hf` | same | exact | exact | 23.4s |
| 30 | Llama-3 without BOS | `meta-llama/Meta-Llama-3-8B` | `cl100k_base` | collision, tie-break | exact | 0.9s |
| 31 | scibert (deliberately not a candidate) | — | `bert-base-multilingual-cased` | miss (expected) | 0.146 | 110.2s, no crash |

So 30 of 31 tokenizers are recovered (25 exact, 5 collision tie-breaks), and every lossless tokenizer
returns the exact text. The "lossy" rows are lossy by design of the tokenizer, not the solver:
- WordPiece and most sentencepiece models fold `\n` into a space.
- BERT-style vocabs and Marian map emoji to `[UNK]`.
- Uncased BERT lowercases and strips accents.
- T5's vocab has no ñ, í, ¿ or ¡.

Even in those rows the flag comes back as `SIGMOID_TEST`.

Also checked:
- A missing or malformed input writes `{"tokenizer_id": "", "decoded_message": ""}` and exits 0.
- An empty challenge works.
- Online mode with a warm cache makes no network calls (5.7s).
- A cold cache online downloads only that repo's 4 tokenizer files and solves (4.1s).
- A cold cache offline falls back to tiktoken without crashing.

## Collisions and the tie-break rule

`verify.py --collisions` loads every candidate and lists all that reproduce the calibration ids exactly.
With this bilingual text:

| Group (identical ids) | main.py answers |
|---|---|
| cl100k_base, Llama-3 / 3.1 **without BOS**, phi-4, OLMo-2 | `cl100k_base` |
| o200k_base, o200k_harmony | `o200k_base` |
| gpt2, r50k_base, p50k_base, p50k_edit, phi-2, codegen-350M-mono, distilgpt2, gpt-neo-125m, gpt-j-6b (single-spaced text) | `gpt2` |
| p50k_base, p50k_edit (text with space runs) | `p50k_base` |
| bert-base-uncased, distilbert-base-uncased, electra-base-discriminator, all-MiniLM-L6-v2 | `bert-base-uncased` |
| bert-base-cased, distilbert-base-cased | `bert-base-cased` |
| bert-base-multilingual-cased, distilbert-base-multilingual-cased, distiluse-base-multilingual-cased-v2 | `bert-base-multilingual-cased` |
| roberta-base, distilroberta-base, bart-base, longformer-base-4096 | `roberta-base` |
| xlm-roberta-base, paraphrase-multilingual-MiniLM-L12-v2, multilingual-e5-base, bge-m3 (+ mbart-50/cc25 for raw spm ids) | `xlm-roberta-base` |
| t5-base, t5-small, flan-t5-base | `t5-base` |
| Llama-2, Phi-3-mini (no BOS), huggyllama/llama-7b, TinyLlama | `meta-llama/Llama-2-7b-hf` |
| Llama-3, Llama-3.1 (with BOS) | `meta-llama/Meta-Llama-3-8B` |
| Qwen2.5, Qwen2, Qwen3 | `Qwen/Qwen2.5-0.5B` |
| gemma-2b, gemma-2-2b | `google/gemma-2b` |
| gpt-neox-20b, pythia-160m | `EleutherAI/gpt-neox-20b` |

**Rule:** the challenge decides first: ids in range, flag present, round-trip. If that still ties, the
earliest entry in `CANDIDATES` wins. Inside each group the canonical name comes first:
- the tiktoken encoding name over HF re-packagings (`cl100k_base`, `o200k_base`, `p50k_base`)
- `gpt2` over `r50k_base` (identical ranks; `gpt2` is both a tiktoken and an HF id)
- the original model over distilled or fine-tuned copies (`bert-base-uncased`, `roberta-base`, `xlm-roberta-base`, `t5-base`)
- the family's first release (`meta-llama/Llama-2-7b-hf`, `meta-llama/Meta-Llama-3-8B`, `google/gemma-2b`, `EleutherAI/gpt-neox-20b`)

Members of a group decode the shared ids to the same text, so a tie can only cost the tokenizer-id half
of the score, never the message.

## Timing

Measured on this box at load average ~250 on 48 cores.
- tiktoken match: 0.4 to 2s.
- HF match: 6 to 30s depending on list position. Each HF load is 0.2 to 7s; the 250k-vocab ones are the slow end.
- No native exact match (full scan of all candidates): about 110s.
- Downloading every candidate's tokenizer files: 18s. Loading all 97 offline: about 150s.

## Offline behaviour

- HF files: `~/.cache/huggingface/hub`. tiktoken files: `~/.cache/tiktoken` (`TIKTOKEN_CACHE_DIR`
  defaults there; tiktoken's own default is `/tmp/data-gym-cache`).
- `main.py` always loads with `local_files_only=True`. It downloads a repo's tokenizer files (never
  weights) only when they aren't cached and `HF_HUB_OFFLINE` isn't set. After the first network error
  it stays offline for the rest of the run.
- `HF_HUB_OFFLINE=1` works with a warm cache. Online with a warm cache, it makes no network calls.

## Known limits

- Lossy tokenizers can't give back text they threw away: newlines, emoji, case, accents. The solver
  picks the decode cleanup that best reproduces the calibration text and normalises the flag, but the
  exact text is out of reach.
- Llama-3 encoded **without** BOS gives the same ids as cl100k_base for Latin-script text. The solver
  answers `cl100k_base` unless a challenge id falls outside cl100k's vocab.
- transformers is 5.23. Where v4 and v5 differ (Llama legacy spacing, etc.), the raw `tokenizers` and
  raw `sentencepiece` engines cover the v4-style ids.
- Marian runs without `sacremoses`. If the author had it installed, punctuation normalisation could
  change the opus-mt ids.
