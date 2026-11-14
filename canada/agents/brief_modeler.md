# Brief: modeler

Read `agents/context.md` first. Your task names your STRATEGY (section below) and your folder
`exp/<name>/`. Write only inside that folder. Read-only: lib.py, tools/, task/, data/.

## Data
- Labelled: `task/corpus.csv` (synthetic, skewed, see context), `data/gen/train_*.jsonl` and
  `data/gen/boundary_*.jsonl` (agent-written, realistic). Filler: `data/gen/filler_*.jsonl` (label
  "none", hazard-free sentences: use them to append noise to training docs, never as a 10th class).
- Held-out: `data/gen/dev_*.jsonl`. Never train or fit anything on it. Use it only to compare models.
- Unlabelled real fingerprints: `lib.load_sealed()`.

## Evaluation (same for everyone)
`.venv/bin/python tools/eval_model.py exp/<name>/<model>.npz [...]` prints dev accuracy (overall,
en, fr, per class), the vault rule replayed on dev ("shares"; any positive = would open), and the
sealed English/French class-mix gap. Add `--vault` to try the real vault (~10 s). At most 6 vault
tries in total: only for your best candidates. SNOWBLIND is a known decoy. Report every word you see.

## Strategies
- **data**: data-centric logistic regression. Clean the corpus (drop hazard-free rows and generic
  impact or header sentences, or recombine sentences so headers, generic lines and language no longer
  predict the label; balance class x language), add the generated train + boundary sets, append
  random filler sentences to training docs so the model learns to ignore unknown words, tune C and the
  weight of corpus vs generated data.
- **sparse**: robustness to hashing noise. Real reports carry many words our data never shows; they
  land in buckets that hold weights for other words. Try: a hand-written bilingual hazard lexicon
  (unigrams and bigrams, from general language knowledge only) turned into bucket weights; LR restricted
  to the buckets of known hazard vocabulary (all other columns of W set to 0); L1 / elastic net;
  hybrids of lexicon and learned weights.
- **transductive**: unsupervised adaptation to the real fingerprints, starting from a solid base model
  (corpus cleaned + generated train data). Try: EM re-estimation of class priors on the sealed set
  (Saerens et al.) to fix b; self-training on the surest sealed predictions with language-balanced
  pseudo-labels, retraining a few rounds; checks that the English/French class-mix gap shrinks while
  dev accuracy holds. Note in your notes that this uses unlabelled sealed fingerprints only.

## Finish
Save your best 1-3 models as `exp/<name>/*.npz` and write `exp/<name>/notes.md` (what you tried, the
numbers, what worked, the exact commands to reproduce). Keep your final reply short (the schema).
