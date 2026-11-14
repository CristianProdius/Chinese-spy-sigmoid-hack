# Shared context: "Two Solitudes" (ML puzzle)

Root: /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/NLP-Noth-america-tasks/canada
(all paths below are relative to it). Python: `.venv/bin/python` (numpy 2.2.6, scikit-learn 1.7.2).
Prefix heavy commands with `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4` (shared machine).
The dev server is overloaded (load ~650). Run anything heavier than a few seconds (training, eval,
vault) on the H100 box with `tools/h100.sh <command>`, e.g. `tools/h100.sh .venv/bin/python
exp/data/train.py`: it syncs the folder up, runs there, and syncs exp/ and data/ back.

## The task
Build a linear model W (9x4096), b (9) that sorts REAL Canadian incident reports (English and French,
written by people over 1900-2020) into nine hazards. A report goes to argmax(W @ fingerprint + b).
- `task/featurize.py`: text -> 4096-d fingerprint: lowercased word tokens (digit runs -> "0"),
  unigrams AND adjacent bigrams hashed with crc32 % 4096, value 1+log(count), row L2-normalised.
- `task/corpus.csv`: 9,462 SYNTHETIC templated reports (id,text,label), our only given labels.
- `task/sealed_reports.npz`: fingerprints of the 1,369 real reports (no text, no labels). `lib.load_sealed()`.
- `task/open_vault.py`: Reed-Solomon vault with 5 doors. A door opens when enough of the model's
  most confident predictions are right: >= 73.5% of all 1,369, or 83.6% of the surest 70%, 89% of the
  surest 60%, 97% of the surest 50% (confidence = top1 - top2 score margin). No score is shown.
  `lib.vault(W, b)` returns the list of words opened (~10 s). The first model opens the decoy door
  SNOWBLIND, which is NOT the flag. Other decoys may exist.

## Classes (order matters) and labelling rules
flood, storm, winter, wildfire, drought, ground, industrial, transport, epidemic
- flood: river, lake, coastal or flash flooding from rain, snowmelt, ice jams, high water.
- storm: thunderstorm, hail, tornado, hurricane, tropical storm, windstorm, storm surge.
- winter: snowstorm, blizzard, ICE STORM, freezing rain, extreme cold / cold wave.
- wildfire: forest, bush or grass fire in the wild.
- drought: drought, dry spell, crop failure from dryness, HEAT WAVE, dust from drought.
- ground: landslide, rockslide, mudslide, snow AVALANCHE, earthquake, TSUNAMI, subsidence.
- industrial: urban or building fire, explosion, hazardous spill or leak, mine disaster,
  infrastructure failure (power grid, bridge/building/dam collapse).
- transport: rail, air, marine (ship, ferry, boat) and road accidents.
- epidemic: outbreaks of human disease, epidemics, pandemics.
A report about several hazards takes the label of its PRIMARY hazard: the main event the report is
about (usually named first and given the most space; the others are causes, side effects or context).

## Hard rules (a flag obtained otherwise fails review)
- No real incident records from any outside source: no web search/fetch, no disaster databases, and
  do not recall or paraphrase real recorded events (named historic disasters, real date+place+figures).
  Invent every incident. Real Canadian place names are fine as settings for invented events.
- Never label the sealed reports by hand or by any means other than a model we train.
- Write only the files your brief assigns to you. Do not commit or push.

## What we know so far (orchestrator diagnostics)
- Corpus is language-skewed: flood 331 en/719 fr, storm 739/311, winter 242/808, wildfire 323/727,
  industrial 675/375, transport 725/325 (others ~balanced). The first model learns language as a cue.
- Corpus vocabulary is tiny (1,926 word types) and templated. ~17% of rows contain no hazard sentence,
  only generic impact lines ("Roads were closed", "Insured losses reached $0 million") that are
  themselves skewed by class and language. Many rows add distractor sentences about other hazards.
- The first model's top weights are junk: province codes (pe, sk, bc, qc), town names, month names,
  function words. Real reports: ~720 English, ~650 French; median ~60 tokens (range ~15-160), longer
  and far richer than the corpus.
- Unsupervised check `lib.sealed_report(W, b)`: predicted class mix on sealed English vs French
  reports; TV gap = 0.27 for the first model, ~0.35 for a stripped corpus model. A language-invariant
  model should have a small gap (assuming both languages cover similar events).
- `data/corpus_recombined.jsonl` (built by `exp/inline/recombine.py`): the corpus with hazard-free
  rows dropped, generic lines and headers reshuffled across rows of the same language. LR on it with
  class x language balanced weights (C=0.3) cuts the sealed TV gap to 0.11 and opens no vault door.
- `lib.py` has: load_corpus, corpus_xy, featurize, tokens, bucket, train_lr, load_sealed, fp_lang,
  sealed_report, vault, save_model, sentences, text_lang. `tools/validate_gen.py` checks JSONL.

## Generated data layout (JSONL lines {"text","label","lang"})
- `data/gen/train_*.jsonl`: training reports written by agents (labels = 9 classes).
- `data/gen/boundary_*.jsonl`: tricky boundary-case training reports. `data/gen/filler_*.jsonl`:
  hazard-free sentences, label "none" (noise augmentation only).
- `data/gen/dev_*.jsonl`: HELD-OUT proxy dev set. Never train on it, never tune on it per item.
