# Two Solitudes

**Flag: `SIGMOID_SNOWFLAKE`**

```
cd canada
uv venv -p 3.11 .venv && uv pip install -p .venv/bin/python numpy==2.2.6 scikit-learn==1.7.2
.venv/bin/python solve.py 6             # ~4 min on 6 cores: rebuilds model.npz from scratch, opens the vault
.venv/bin/python task/open_vault.py model.npz      # -> The vault releases: SIGMOID_SNOWFLAKE
```

`model.npz` (W 9x4096, b 9) is committed too, so the last line works on its own.

## The short version

The first model fails on real reports for three reasons:

- It learned the corpus's shortcuts: language, place names, months and generic impact lines.
- It never saw the vocabulary that real reports use.
- It opens a decoy door (`SNOWBLIND`).

We kept the given fingerprint and a linear model. We fixed the training data:

1. **Decorrelated the synthetic corpus.** We dropped rows with no hazard and reshuffled the headers and generic lines across rows of the same language.
2. **Wrote our own labelled reports.** These are 1,300 invented incident reports in English and French, written in styles from 1900 to 2020, plus boundary cases and hazard-free filler.
3. **Trained a balanced ensemble.** We fit 12 class x language balanced logistic regressions and averaged them into one W, b.

Judged by an independent held-out dev set, the result scores 87% (86% English, 87% French). The first model scores 46% on that set. Our model opens the `SNOWFLAKE` door.

## 1. What the materials do (read from the code)

- **Fingerprint** (`task/featurize.py`):
  - The text becomes lowercase word tokens, and digit runs become "0".
  - Unigrams and adjacent bigrams are hashed with crc32 % 4096. Each cell holds 1 + log(count), and each row is L2-normalised.
  - There's no secret, so any text we write can be fingerprinted exactly like the real reports.
- **Vault** (`task/open_vault.py`): a Reed-Solomon threshold lock.
  - It works over GF(65521), with n = 1,369 reports, polynomial degree < k = 643, and **5 doors**.
  - Each report contributes the table value of its predicted class, and only a door's own labelling lies on that door's polynomial.
  - The vault sorts reports by confidence (top-1 minus top-2 score). It opens a door when enough of the surest reports agree:
    - 73.5% of all 1,369
    - 76.1% of the surest 90%
    - 79.4% of the surest 80%
    - 83.6% of the surest 70%
    - 89.2% of the surest 60%
    - 97.0% of the surest 50%

    Shares below 50% can never open.
  - Five doors means five labellings. The first model opens `SNOWBLIND`, which the baseline says is not the flag. The other doors are decoys for other wrong approaches, and one door holds the true labels.

## 2. What is wrong with the first model (diagnosis)

| finding | evidence |
|---|---|
| Language shortcut, the "two solitudes" | Corpus hazard by language (en/fr): flood 331/719, storm 739/311, winter 242/808, wildfire 323/727, industrial 675/375, transport 725/325. |
| Hazard-free rows | About 17% of rows hold only generic impact lines, such as "Roads were closed" and "Insured losses reached $0 million". These lines are themselves skewed by class and language. |
| Junk features | The top weights go to province codes (pe, sk, bc, qc), town names (Sydney, Yellowknife, Val-d'Or), month names and function words. |
| Narrow vocabulary | The corpus has 1,926 word types. Real reports are longer (median ~60 tokens against 37) and richer, and unknown words hash into buckets that hold weights for other words. |
| Unsupervised symptom | On the real reports, the first model's predicted class mix differs strongly between English and French: the total-variation gap is 0.27. |

## 3. What we built

- **Recombined corpus** (`exp/inline/recombine.py`): hazard-free rows dropped. Place/date headers and generic impact lines are drawn at random from the same-language pool, so they no longer predict the label.
- **Generated data** (`data/gen/`, written by Claude agents from the briefs in `agents/`; every event is invented and nothing was looked up):
  - `train_a|b|c_*.jsonl`: 1,080 reports, 60 English and 60 French per class. They cover three eras (early-1900s newspaper, mid-century, modern government summary) and broad vocabulary, and about 20% mention a secondary hazard.
  - `boundary_*.jsonl`: 220 boundary cases with the stated rules applied:
    - ice storm counts as winter, storm surge as storm, heat wave as drought;
    - a town fire or mine blast counts as industrial;
    - avalanche and tsunami count as ground;
    - a blackout or a bridge or dam collapse counts as industrial.
  - `filler_*.jsonl`: 600 hazard-free sentences, used only to pad training reports so the model learns to ignore impact and relief prose.
  - `dev_hist_*`, `dev_modern_*`: 360 held-out reports written by two separate agents in two era styles. These agents never saw the training briefs. **Never trained on.** They're used only to compare models.
- **Model** (`solve.py`, built on `exp/data/common.py` and `exp/data/bag.py`): 12 logistic regressions over the given fingerprint.
  - Training data: generated train and boundary reports (each with 3 augmented copies: filler insertion and sentence dropout), plus the recombined corpus at 25-50% of the weight.
  - Sample weights are balanced over class x language cells, with C = 3.
  - The members differ in seeds and data mix, and their W and b are averaged. That is still one linear model.

## 4. Results

The dev set is 360 held-out invented reports. The sealed gap is the difference between the English and French predicted class mix on the real reports (lower means more language-invariant).

| model | dev acc (en / fr) | sealed gap | vault |
|---|---|---|---|
| first_model (given) | 0.464 (0.417 / 0.511) | 0.271 | SNOWBLIND (decoy) |
| recombined corpus only | 0.389 | 0.108 | nothing |
| generated data only | 0.858 | 0.121 | (not tried) |
| **final `model.npz`** (solve.py) | **0.867 (0.861 / 0.872)** | **0.078** | **SNOWFLAKE** |
| `model_strict.npz` (`STRICT=1`, see section 6) | 0.869 (0.856 / 0.883) | 0.071 | SNOWFLAKE |

Three modeling strategies were explored in parallel. Each folder holds notes, logs and reproduce commands:

| strategy | best | dev | gap | vault |
|---|---|---|---|---|
| data-centric LR (`exp/data/`) | bag_div | 0.867 | 0.078 | SNOWFLAKE |
| sparse / lexicon, robust to hash noise (`exp/sparse/`) | sparse_ens5 | 0.878 | 0.053 | SNOWFLAKE |
| transductive: self-training, df-shift (`exp/transductive/`) | ens4 | 0.875 | 0.060 | SNOWFLAKE |

The final model is the data-centric one, because its training never touches the sealed reports.

## 5. Why SNOWFLAKE is the flag and not another decoy

- Every model above about 0.85 dev opened `SNOWFLAKE`, across three different strategies, about 10 models in all. No model opened a second door.
- **Rule probe:** the same recipe trained with the naive conventions (ice storm counted as storm, avalanche as winter, tsunami as flood) changes 13% of the real predictions and opens nothing. So the SNOWFLAKE labelling follows the rules stated in the task.
- **Drift probe:** a self-trained model that let predictions drift toward storm opened nothing. Models that look worse to us lose the door.
- Corpus-only models open nothing, and the first model opens only `SNOWBLIND`.

## 6. Rules

- **No real incident records** from any outside source, for training or lookup. All extra text was written by our agents as invented events, with no web access. Real Canadian place names appear only as settings.
- **Strict check:** about 50 generated reports name real diseases or pandemics (COVID-19, SARS, H1N1). `STRICT=1 .venv/bin/python solve.py` drops all of them and still releases `SNOWFLAKE`, so the flag does not rest on them.
- **The sealed reports were never labelled**, by hand or otherwise. The final model's training does not use them at all. They appear only in diagnostics (the English/French class-mix gap) and in the vault.
  - The sparse and transductive explorations used them unlabelled: bucket frequencies, and self-training on our own model's predictions. Their notes say so.
  - We did not extract any labelling from the vault. We only read which word it releases.
- `RESEARCH.md` has the research log. `agents/` holds the exact briefs the writing and modeling agents worked from.

## File map

| path | what |
|---|---|
| `task/` | given materials, unchanged |
| `solve.py` | rebuilds the final model and opens the vault |
| `model.npz`, `model_strict.npz` | final models |
| `lib.py`, `tools/eval_model.py`, `tools/validate_gen.py` | shared helpers, evaluation (dev, vault rule replayed on dev, sealed gap), data validator |
| `tools/h100.sh` | runs a command on our GPU box (the dev server was overloaded); optional |
| `exp/inline/` | corpus recombination and early probes |
| `exp/data/`, `exp/sparse/`, `exp/transductive/` | the three strategies, with `notes.md` each |
| `data/gen/` | generated training, boundary, filler and held-out dev data |
| `data/corpus_recombined.jsonl` | the decorrelated corpus (seed 0) |
| `agents/` | briefs given to the writing and modeling agents |
