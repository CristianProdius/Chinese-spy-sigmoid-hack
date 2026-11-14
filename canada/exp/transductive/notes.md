# Transductive strategy: notes

**Uses the unlabelled sealed fingerprints only.** No sealed labels and no sealed text. Nothing was
labelled by hand. Pseudo-labels always come from our own trained models. Dev (`data/gen/dev_*`) was
only used to score models, never to train or fit anything.

## Result

| model | what | dev acc (en / fr) | sealed TV gap | vault |
|---|---|---|---|---|
| `ens4.npz` (**best**) | mean of 4 SNOWFLAKE openers (below) | **0.875** (0.872 / 0.878) | 0.060 | SNOWFLAKE |
| `st2single_a0.3_C3_g0.0_b0.3_r3.npz` | base a=0.3 C=3 + 4 rounds language-balanced self-training | 0.872 (0.878 / 0.867) | 0.051 | SNOWFLAKE |
| `fs_a0.3_up_g0.5_C3.0.npz` | base + df-shift feature scaling, no self-training | 0.861 (0.861 / 0.861) | 0.070 | SNOWFLAKE |
| `runs/st2anch_comm_b0.3_r1.npz` | committee self-training, prior-anchored | 0.844 | 0.068 | SNOWFLAKE |
| `runs/st2comm_long_b0.3_r5.npz` | committee self-training, 6 rounds, not anchored (storm mix drifts 0.20 to 0.34) | 0.858 | 0.038 | **nothing** |

Vault tries used: 5 of 6, with 1 left. Words seen: **SNOWFLAKE** only. It is new, not the known decoy
SNOWBLIND, but it may still be a decoy. Every model at roughly 0.84-0.875 dev opened it. No model
opened a second door. The replayed vault rule says "would open" on dev for every model at or above
base level (shares +0.10 to +0.15).

## What was tried (logs: `st_log.txt`, `fs_log.txt`, `st2_log.txt`, `vault_log.txt`)

1. **Base LR** on the generated train and boundary sets, each with 2 copies padded by 1-3 same-language
   filler sentences, plus the recombined corpus at total weight alpha. Weights are balanced by class x
   language. Dev is about 0.84-0.87 for every alpha in {0, 0.1, 0.3, 1} and C in {0.3..10}, so the
   differences are noise (SE about 0.02). The corpus alone (recomb_C0.3) scores 0.389. More corpus
   lowers the sealed TV gap (alpha=0: 0.10, alpha=1: 0.06-0.07).
   The LR is a GPU L-BFGS with sklearn's objective (`common._train_lr_torch`). It matches the sklearn
   numbers and runs about 50x faster on the loaded box.
2. **EM prior re-estimation (Saerens)**: it fails. Sealed posteriors are under-confident (median margin
   0.74 on sealed vs 1.20 on dev), and EM collapses onto storm: drought and ground priors go to 0 and
   dev drops to 0.58. At T=2, dev is 0.24. EM-shifted pseudo-labels collapse in the same way
   (mix becomes 0.95-0.99 storm).
3. **Diagnosis of the sealed shift** (`dfshift.py`): real reports are number-heavy. The bucket "0 0"
   (dates, "1,200") fires in 59% of sealed reports vs 27% of generated ones, and the base puts +2.65
   wildfire on it. "km" and "0 km" fire 2.5x more often and carry +3.2 storm. "0 mm" carries +3.75 flood.
   This explains the storm sink.
4. **df-shift feature scaling** (`df_scale`, mode 'up'): shrink bucket j by (df_gen/df_sealed)^gamma
   where it fires more often in sealed reports. Training is done on scaled columns, so the shrink acts
   as extra L2 on those buckets. gamma 0.5-1 keeps dev (0.85-0.86) and cuts TV (a=0: 0.10 to 0.06-0.09).
   Mode 'sym' also shrinks buckets that are rare in sealed reports. It hurts dev (down to 0.74-0.84).
5. **Self-training** (`st.py`, `st2.py`): pseudo-label the surest sealed reports and retrain from
   scratch, q = 0.3, 0.5, 0.7, 0.85. 'bal' selection takes the same count per class from EN and FR, so
   the pseudo-label class mix is identical in both languages. Pseudo-label weight is 0.3 of the train
   weight. Dev holds or rises a little (0.85 to 0.87) and the TV gap drops to 0.04-0.06. **The risk is
   class drift.** Plain or committee ST lets flood or storm grow (storm 0.20 to 0.34 after 6 rounds),
   and that model lost SNOWFLAKE. The fix is the **prior anchor**: after each round, a bias shift keeps
   the sealed mean-softmax class mix at the base model's mix. Committee pseudo-labels (4 differently
   trained members must agree) did not beat the single-model ST on dev.
6. **Averaging** the four SNOWFLAKE openers (still linear) gives the best dev, 0.875.

## Takeaways
- A low TV gap alone is not a good target. The lowest-TV model (0.038) opened nothing because of the
  storm drift. Keep the class mix anchored.
- SNOWFLAKE opens robustly across base, df-scaled, self-trained and averaged models. If it is a decoy,
  the true door needs something these models share and get wrong systematically (for example rule
  edge cases or the primary-hazard rule). More transductive tuning does not reveal another door.

## Reproduce (from canada/)
```
tools/h100.sh python3 -W ignore exp/transductive/st.py grid            # base grid -> runs/base_*.npz
tools/h100.sh python3 -W ignore exp/transductive/st.py st 0.3 1.0      # EM + ST grid (log only)
tools/h100.sh python3 -W ignore exp/transductive/fs.py                 # df-shift scaling -> fs_*.npz
tools/h100.sh python3 -W ignore exp/transductive/st2.py single         # -> st2single_*_r{1,2,3}.npz
tools/h100.sh python3 -W ignore exp/transductive/st2.py anchor         # -> st2anch_*, st2comm_long_*
.venv/bin/python exp/transductive/ensemble.py                          # -> ens4.npz
tools/h100.sh .venv/bin/python tools/eval_model.py exp/transductive/ens4.npz [--vault]
```
`python3` on the H100 is the system Python with torch and CUDA, used for the GPU LR. Scripts write
models to `exp/transductive/`. Intermediates were then moved to `runs/` by hand. `ensemble.py` looks in
both places. `base.py` is the first sklearn version of the base grid, superseded by `st.py grid`.
