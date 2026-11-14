# exp/data: data-centric logistic regression

## Pipeline (`common.py`)
- Generated train + boundary reports (`data/gen/train_*`, `boundary_*`, 1,300 docs), each kept once as is
  plus 3 augmented copies: sentence dropout (p=0.25) and 0-3 random same-language filler sentences
  (`data/gen/filler_*`, label "none") inserted at random positions.
- Corpus: `exp/inline/recombine.build(seed)` (hazard-free rows dropped, headers and generic lines
  reshuffled within language), 2 seeds per model, also given 0-3 filler sentences.
- Weights: each source is balanced over class x language cells. Total corpus weight = alpha x gen weight.
- Multinomial LR (sklearn lbfgs, sparse X), C=3.
- Optional knobs: pseudo-word noise, boundary repeats, multi-hazard mixes (a primary report plus 1-2
  sentences from a report of another class, label kept), seed bagging (average W and b of K members).

## Results (dev = 360 held-out agent reports; `tools/eval_model.py`)
| model | dev | en | fr | sealed TV gap | vault |
|---|---|---|---|---|---|
| first_model (given) | 0.464 | 0.417 | 0.511 | 0.271 | SNOWBLIND (decoy) |
| recomb_C0.3 (inline) | 0.389 | 0.389 | 0.389 | 0.108 | none |
| gen only, no filler, C=3 | 0.858 | 0.850 | 0.867 | 0.121 | - |
| gen + filler + drop, C=10 | 0.858-0.878 | | | 0.117-0.124 | - |
| **d_a25** (alpha 0.25, filler, drop, C=3) | 0.875 | 0.856 | 0.894 | 0.072 | **SNOWFLAKE** |
| **bag_a25** (8 seeds of d_a25 config) | 0.864 | 0.856 | 0.872 | 0.093 | not tried |
| **bag_div** (12 members, 4 config variants) | 0.867 | 0.861 | 0.872 | 0.078 | **SNOWFLAKE** |

bag_div's vault rule replayed on dev: +0.13 to +0.17 at shares 1.0-0.7, +0.02 at 0.5 (would open).
Vault tries used: 2 (d_a25, bag_div). Both released only SNOWFLAKE. We cannot tell from here whether
it is the flag or another decoy.

## What we learned
- The generated data is what matters: about 0.86 dev, against 0.39-0.46 for corpus-only models.
- Filler sentences add about +1.5 pt. Pseudo-word noise and 8 copies add nothing.
- Adding the corpus (alpha 0.25-0.5) leaves overall dev flat. It helps the modern-style dev half
  (0.844 -> 0.878), cuts the sealed EN/FR gap (0.12 -> 0.05-0.08), and raises sealed margins.
- Changing the seed alone moves dev accuracy from 0.836 to 0.886 (n=360, SE ~1.8 pt). So almost no grid
  difference is real. The same config with different seeds agrees on only ~87-91% of sealed reports,
  so we average seeds and variants (bagging) to steady predictions and the margin ranking.
- Boundary repeats and multi-hazard mixes made no dev difference that stood out from that noise.
- Dev errors that persist: extreme cold read as drought (shared temperature words), subsidence or
  landslide read as industrial or flood, dam or bridge failures read as flood or transport, road
  accidents read as ground. I did not write extra data aimed at these errors, because that would leak
  dev.
- Diagnostic (`probe_vocab.py`, `probe_gap.py`) uses unlabelled sealed fingerprints only, and only for
  bucket document frequencies. Real reports collide common words onto rare hazard buckets, e.g. the
  "influenza" bucket fires in 15% of EN sealed docs and shares a hash with "individuals" and
  "populated"; "tsunami" shares one with "buildings". The sealed set was never labelled or trained on.

## Reproduce (from canada/)
    tools/h100.sh .venv/bin/python exp/data/train.py d_a25          # -> exp/data/d_a25.npz
    tools/h100.sh .venv/bin/python exp/data/bag.py bag_a25 8 4 alpha=0.25 C=3.0
    tools/h100.sh .venv/bin/python exp/data/bag.py bag_div 12 6 variants=div
    tools/h100.sh .venv/bin/python exp/data/grid.py stage1|stage2 [jobs]   # results_stage*.jsonl
    tools/h100.sh .venv/bin/python tools/eval_model.py exp/data/bag_div.npz [--vault]
