# Here, at your service! (Algeria) - register LoRA for SmolLM2-360M

`adapter.gguf` (66.3 MiB, f16, rank 64 on q/k/v/o/gate/up/down) passes the task's own
`evaluation_script.py` on the public data, run unmodified on CPU with the Q8_0 base:

| Gate | Value | Min |
|---|---|---|
| style conformance | 0.949 | 0.15 |
| entity class accuracy | 0.975 (40 entities) | 0.70 |
| content kept | 0.831 (59 fact prompts) | 0.55 |
| base log-prob | -1.685 | -2.6 |
| calls | 8/8 | 0.75 |

The public prompts and calls were never trained on. On a held-out set of 400 teacher-keyed fact
prompts, 80 open prompts and 200 calls (`data/val`, also never trained on), the GPU screen gives
entity class 0.89, calls 0.935 and content 0.485 against the untouched base model's own 0.532.

`adapter.gguf` is the submission (`sha256 51b2a86e708d4bd7a38959dc15b360b735ef1ed1f5df3c3ae691884266bf14a8`).

## How it works

1. **Prompts.** Qwen2.5-32B-Instruct (local vLLM on the H100) writes ~12.8k questions in the shape of the
   79 public prompts, across 48 topic cells (facts, Algeria/Maghreb, open why/how/describe questions).
   Near-copies of the public prompts and calls are dropped.
2. **Self-distillation.** The base model itself answers every prompt (greedy, on Q8_0-rounded weights).
   Fact answers are cut to their first short sentences and kept only when the teacher judges them
   correct; open answers are shortened by the teacher with minimal edits. The content is the base
   model's own, so the LoRA only has to learn the surface, which keeps knowledge and log-prob high.
3. **Deterministic register.** `src/register.py` rewrites plain English into the register: `Sem,`, table
   words with their suffix (incl. plurals), numerals from digit names, a class suffix on every name,
   and the seal of the last class-marked word. Name classes come from the teacher, labelled once per
   distinct name phrase. Every training target must score 1.0 on the task's `style_checker.py`.
4. **Calls.** ~4.3k one-noun calls generated per class, kept only when a second, independent teacher
   label agrees with the class. Target: `Sem, Mediterranean-um ta.`
5. **Coverage fixes.** Extra prompts for the 98 rarest table words, numeric facts the base model already
   answers right, and 3.9k exact arithmetic / unit / year items to teach digit-name spelling.
6. **Training.** PEFT LoRA r64/alpha64, lr 4e-4 cosine, 5 epochs, batch 32, loss on the reply and
   `<|im_end|>`, base weights fake-quantised to Q8_0 exactly as ggml does (`src/common.py`).

## Converter catch

The shipped `tools/lora_to_gguf.py` copies `lora_b` as is, but llama.cpp stores `attn_q`/`attn_k` rows
permuted for its rope layout. A q/k LoRA converted that way is applied to the wrong rows, silently.
`src/export.py` permutes q/k `lora_B` the same way before calling the shipped converter; `src/parity.py`
shows llama.cpp+adapter then tracks HF+adapter as closely as the two bases track each other.

## Files

| Path | What |
|---|---|
| `src/register.py` | plain English -> register, checked by the task's checker |
| `src/gen.py`, `src/names.py` | teacher prompts, answer fixes, name labels, call generation and checks |
| `src/basegen.py`, `src/numbers_gen.py` | base-model answers; exact numeric items |
| `src/build_sft.py` | dedup, decontaminate, convert, split -> `data/sft_train.jsonl`, `data/val/` |
| `src/train.py`, `src/export.py` | LoRA SFT; PEFT -> `adapter.gguf` via the shipped converter |
| `src/fasteval.py` | GPU screen with the grader's own scoring functions |
| `src/official.py` | runs `evaluation_script.py` unchanged, only capping llama.cpp threads (busy box) |
| `task_algeria/` | the challenge files |

Check: `cd task_algeria && python evaluation_script.py --model ../adapter.gguf --data public` (exit 0).

## Known weakness

Numbers recalled from memory are sometimes mis-spelled in digit names (guitar strings, hours in a
day): the model must translate each remembered digit into a name, and digit names share first tokens
(`s` for sik/sab, `n` for nol/nun). Copied and computed numbers come out right. Content still clears
its gate with a wide margin.
