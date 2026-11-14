# Review: statistical robustness of the quality gate (main_under_review.py)

Every number below comes from a script in this folder. Run them from `wf2/` with
`PYTHONPATH=<fez dir>`. Run order: `st_cache.py` (writes st_cache.pkl), `st_synrates.py` (st_syn.pkl),
`st_variants.py` (st_variants.pkl), `st_thin.py` (st_thin.pkl). The other scripts read those caches.
Sanity check: the embedded TABLES equal `build_tables(load_all())`, and the honest 5-fold result reproduces
at 0.8525 with 316 expensive (`st_cache.py`, `sim_copy.py main_under_review.py`).

## Verdict
No defect pushes expected quality below 0.80. The risk is real, though, and higher than the 0.6% / 3.3% / 8.8% in
context.txt suggests, because sim.py treats the per-family rates from train as exact. Quality is about equal to
"all-expensive minus one row" (0.8525 vs 0.855), so the risk comes mostly from the mix and the expensive guide's
own accuracy. Routing cannot fix that. None of the fixes I tried raises worst-case quality robustly. The best one
is +0.004 in the train-label world and -0.003 in the synthetic-label world.

## 1. sim.py understates P(quality < 0.80) because it leaves out rate uncertainty  [measured]
sim.py resamples a family's 13-45 train rows as if their hit rate were the true rate. A double bootstrap first
resamples each family's rows to form a "population", then draws the 500-row test from it. Same alphas as
tools/sim.py (400/100/40), 3000 reps. Command: `python3 st_mix.py 1`

| mix shift | sim.py method P(q<.80) | double bootstrap P(q<.80) | double-boot p1 |
|---|---|---|---|
| none (train mix) | 0.00% | 0.83% | 0.800 |
| alpha 400 (mild) | 0.23% | 1.37% | 0.798 |
| alpha 100 (moderate) | 2.70% | 4.73% | 0.772 |
| alpha 40 (strong) | 7.70% | 9.50% | 0.750 |

Second, independent check: tests drawn from the GPU-labelled synthetic rows (large pools, gen.py prompts)
give 0.10% / 1.15% / 4.20% / 10.35%, with mean 0.845 (`st_synworld2.py`). Both methods agree: about 1% at a
mild shift, 4-5% at a moderate shift, about 10% at a strong one.

## 2. Mix shift toward families where the expensive guide is weak  [measured]
walk3, walk4, stall2, fee_most and fee_least make up 31% of train, with a combined routed quality of 0.556. The
rest score 0.986 (`st_fam.py`). With no sampling noise, quality = 0.986 - 0.43 x (that share), so it falls below
0.80 once the share reaches about 43%. Scenarios (`st_stress.py 7 2000`, double bootstrap, N=500):
- those five families x1.3: mean 0.828, P(q<.80) 10.3%
- uniform over the 14 subfamilies: mean 0.830, P(q<.80) 10.4%
- price share x0.5: mean 0.839, P(q<.80) 3.5%

Part of that loss comes from the budget cap, not the guides. Under the uniform-14 mix, price falls from 11% to 7%
and the 395-row cap cuts about 43 positive-gain rows per test. That costs 0.0064 (0.8375 uncapped vs 0.8311
capped; `st_capcut.py`). The cap cuts walk4 detours (both guides wrong, no loss), crate1 with c<=12 (no loss),
about 9 price_ind rows, and some fee_least rows where cheap is 0/1 and expensive 1/1.

## 3. Generator vs train differences, beyond the three already known  [measured]
Commands: `st_gen.py` (ranges and value sets), `st_calib.py` (do synthetic-only tables predict the train labels,
cell by cell), `st_walk.py`, `st_pind.py`.
- **price_ind, cheap guide (decision-relevant):** synthetic/grid 0.78 (n=2020, every position 0.72-0.87). Train
  CPU 12/22 = 0.55, and GPU on the same 22 prompts 11/22. The gap is in the prompts, not the CUDA build. The
  cell-conditional z is -2.66. Names, positions, prices, wording and duplicate prices all match, so I could not
  find the cause. Effect: p_cheap for price_ind is overestimated by about 0.2. These rows have the lowest gain
  among rows with real gain, so the cap cuts them first.
- **walk3 with a direct edge, expensive guide (decision-relevant):** synthetic 197/256 = 0.77. Train CPU 22/23,
  and GPU on the same prompts 21/23. Cell-conditional z = +2.2. As a result, every walk3 `dir_max1` row (direct
  edge = longest edge) goes cheap, with p_c 0.72-0.79 against p_e 0.69-0.73. On train those 10 rows score cheap
  6/10 vs expensive 9/10, which accounts for the router's whole net loss against all-expensive (lost 4, won 1).
  `st_cheaprows.py` shows it.
- Ties (direct = a+b): synthetic 5% (walk3) / 3% (walk4), train 0/67 (p of about 0.05).
- fee_most crates: train mean 5.5 (skewed low), synthetic uniform 1-19 (mean 10.5). The net gap tops out at 42 in
  train vs 151 in synthetic, and the train fee_most answer is never in position 3 (0/13). The g2 bucket in
  synthetic is mostly easy wide gaps. Effect: small, because these rows go expensive anyway.
- take answer position: train mean 1.05 vs 1.5 for a uniform draw (z about -2.5). The cheap logit conditions on
  position, so the effect is nil.
- toll2 w2 = lim (synthetic 5%, train 0/27) and stall1 opening hour (train mean 7.95 vs 7.5): these don't change
  any decision. Both families always go expensive.
- Overall, synthetic-only tables predict 337.1 expensive hits on the 400 train prompts against 342 observed
  (z +0.99), and an honest-routing quality of 0.8475 against 0.8525 observed.

## 4. Thin cells  [measured, harmless]
79 train rows hit a cheap cell with n_eff < 20. All of them are toll1 `b|n` or stall1 `h|open` cells, and none
flip a decision: p_c is at most about 0.3 against p_e of about 1, so they all go expensive (`st_thin.py`).
The decisions that do change with cell granularity are the walk3 `dir_max1` rows from section 3. Those cells have
n_eff 50-120, so what drives them is the synthetic/train disagreement, not thin data. Honest 5-fold results:
cells as built 0.8525, everything pooled to parents 0.8575, family rates only 0.8475. That spread is ±2 rows,
so the fine cells don't earn measurable quality (`st_flip.py` lists the rows that flip).

## 5. GPU vs CPU label bias  [measured, not harmful]
On the 400 train prompts, the same routing scores 0.8600 with GPU labels vs 0.8525 with CPU labels. The GPU
expensive model does better on stall2 (+2), fee_least (+1) and toll2 (+1), so any estimate made in the synthetic
world runs about 0.0075 optimistic. In the families where decisions are made, the bias is safe or nil: crate1
cheap GPU 27/43 vs CPU 30/43 (pessimistic, so fewer rows go cheap), and walks, fee and price_ind are within ±1
(`st_fam.py`).

## 6. Leakage behind the 0.8525  [measured, none material]
- Count leakage: tables built with zero train rows score 0.8550 on train, against 0.8525 honest and 0.8550
  in-sample (`st_cache.py`, then `st_fam.py`). The train rows don't inflate anything.
- Design or hyperparameter leakage: the routing's net effect on train is -1 row against all-expensive, and
  alternative cell designs land within ±2 rows (section 4). So whatever selection went into the design cannot
  have inflated the estimate by more than about 0.005. The open uncertainty is the ±0.018 binomial SE of the
  train rates themselves, which section 1 covers.
- Exact prompt matches between grid and train exist (grid enumerates every toll1 prompt). Cells key on numbers,
  and the hidden test gets the same coverage, so this is not leakage.

## Fix tried, not recommended as a must-do
V3: ignore the synthetic labels for price_ind cheap and walk3 expensive, and use only train counts there
(`st_variants.py`, then `st_stress.py`, paired tests).
- Honest 5-fold: 0.8550 vs 0.8525.
- Stress scenarios: mean +0.0025 to +0.005. P(q<.80) drops 4.95% -> 3.25% at alpha 100, 9.85% -> 7.85% at
  alpha 40, and 10.25% -> 7.55% with the expensive-weak families at x1.3.
- If the synthetic labels are the truth, V3 costs 0.0034 (`st_synworld.py`, V0 in-sample there, so that cost is
  an overestimate).
- The evidence for V3 comes from the same train rows it is scored on. That is about ±2 rows of effect, and it
  doesn't clear the bar of a measurable worst-case gain. Ship as is, or apply V3 if you trust train over gen.py
  for these two cells. Neither choice moves P(fail) by more than about 2 points.
