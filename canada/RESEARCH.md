# Two Solitudes: research notes

## The problem in one line

A linear model (W 9x4096, b 9) trained on a synthetic EN/FR corpus has to classify 1,369 real,
human-written Canadian incident reports (EN and FR, over a century) that we only see as 4096-d
fingerprints. The vault gives pass/fail, no score.

## How the pieces work (confirmed by reading the code)

- **Fingerprint** (`task/featurize.py`): lowercase word tokens, digit runs -> "0", unigrams and
  adjacent bigrams hashed with crc32 % 4096, value 1 + log(count), row L2-normalised. No secret salt,
  so we can fingerprint any text we write ourselves.
- **Vault** (`task/open_vault.py`, `task/vault.npz`): a Reed-Solomon threshold lock over GF(65521),
  n = 1,369 points, polynomial degree < k = 643, five doors. Each report contributes the table value
  of its predicted class; only the true class lies on a door's polynomial. Reports are sorted by
  confidence (top1 - top2 margin) and the vault tries the surest share m of them:

  | share | m    | correct needed | accuracy needed |
  |-------|------|----------------|-----------------|
  | 1.0   | 1369 | 1006           | 73.5%           |
  | 0.9   | 1232 | 938            | 76.1%           |
  | 0.8   | 1095 | 869            | 79.4%           |
  | 0.7   | 958  | 801            | 83.6%           |
  | 0.6   | 821  | 732            | 89.2%           |
  | 0.5   | 684  | 664            | 97.0%           |

  Shares 0.42 and 0.34 can never open (m < k + 2). So the bar is roughly 73.5% overall, or a
  well-calibrated model that is very accurate on its confident reports.
- **Decoys**: five doors means five different labelings. The first model opens `SNOWBLIND`, which the
  baseline says is not the flag. Other doors are probably other shortcut labelings, with one door for
  the true labels.

## What breaks the first model (confirmed)

1. **Language shortcut ("Two Solitudes").** Corpus hazard by language (en / fr): flood 331/719,
   storm 739/311, winter 242/808, wildfire 323/727, industrial 675/375, transport 725/325. The rest are
   balanced. On the real reports (about 720 EN and 650 FR) the first model's predicted class mix
   differs a lot by language (total-variation gap 0.27).
2. **Hazard-free rows.** About 17% of corpus rows have no hazard sentence at all, only generic impact
   lines, and those generic lines are themselves skewed by class and language. Many rows also add
   distractor sentences about other hazards.
3. **Junk features.** The first model's top weights are province codes (pe, sk, bc, qc), town names
   (Sydney, Yellowknife, Val-d'Or), month names and function words ("un", "a", "à").
4. **Narrow vocabulary.** The corpus has 1,926 word types. Real reports are longer (median ~60 tokens
   vs 37, range ~15-160) and use far more words, which land in hash buckets that hold weights for
   other words (collision noise).

## Steps so far

| model | what | sealed EN/FR gap | vault |
|---|---|---|---|
| first_model | given | 0.27 | SNOWBLIND (decoy) |
| quick_strip | drop headers + generic lines, balanced | 0.35 | nothing |
| recomb C=0.3 | recombined corpus (`exp/inline/recombine.py`), class x language balanced | 0.11 | nothing |
| data / bag_div | + agent-written EN/FR reports, filler, 12-model average (dev 0.867) | 0.078 | SNOWFLAKE |
| sparse / ens5 | + lexicon pseudo-docs, hash-noise copies (dev 0.878) | 0.053 | SNOWFLAKE |
| transductive / ens4 | + df-shift scaling, anchored self-training (dev 0.875) | 0.060 | SNOWFLAKE |
| naive-conventions probe | ice storm->storm, avalanche->winter, tsunami->flood (dev 0.800) | 0.039 | nothing |
| final model.npz | `solve.py`, rebuilt from scratch, no sealed data in training | 0.078 | **SNOWFLAKE** |

Outcome and full write-up: `README.md`. Flag: `SIGMOID_SNOWFLAKE`.

## Rules we hold to

- No real incident records from any outside source, for training or lookup. All extra text is
  written by our agents as invented events (real place names allowed as settings), no web access.
- The sealed reports are never labelled by hand or by anything other than a trained model.
  Unlabelled use of their fingerprints (class-prior estimation, self-training) is flagged in notes.

## Plan

1. Agents write realistic EN/FR training reports for all nine classes, boundary cases and
   hazard-free filler, plus an independent held-out proxy dev set (two writers, two eras) that no
   model trains on.
2. Three modeling strategies in parallel: data-centric LR, sparse/lexicon (robust to hash noise),
   transductive adaptation on the sealed fingerprints.
3. Pick by proxy dev accuracy and the vault rule replayed on dev, then try the vault.
4. Compute runs on the H100 box (`tools/h100.sh`) because the dev server is overloaded.
