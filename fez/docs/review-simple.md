# Review lens: does the table router's complexity earn its keep?

**Verdict: it does. Keep `main_under_review.py`.** The simplest router I could build (`simple_router.py`) loses 1.3 to 1.8 quality points on both test beds. It does worse in 80 to 97% of paired simulated tests. Its chance of failing the 0.80 gate is 1.5 to 8 times higher, depending on bed and shift (0% vs 1.5% on Bed A with no shift).

## The simple router (`wf2/simple_router.py`, 110 lines, no solver)
- It assigns each request to one of 17 groups. The base group is the template family, found by keyword. Three hand rules split off cases where the cheap guide does about as well:
  - `walk_detour`: the shortest walk is a two-hop path, found with a two-hop check.
  - `toll1_10`: the toll is 10 dirham a cart.
  - `crate1_small`: crate1 with at most 15 crates.
- The submitted version embeds (p_cheap, p_expensive) per group, counted on the 400 train rows.
- Allocation matches the table router: rank by gain p_e - p_c and send the top floor(19N/24) with positive gain to expensive.
- Its groups match the solver-derived groups on all 12,465 labelled rows (0 mismatches).
- End to end on train input, in-sample: quality 0.8500, cost 7984. The table router scores 0.8550 with the same cost. Command: `python3 -I ../evalroute.py simple_router.py`.

## Honest comparison: `python3 eval_simple.py` (output in `eval_dedup.txt`)
- **Bed A:** the 400 train rows with CPU labels, 5-fold using sim.py's split.
  - Table router: tables from `build.build_tables` on the other folds plus all synthetic and grid rows.
  - Simple router: rates from the other train folds.
- **Bed B:** the 3,256 synthetic rows labelled by the GPU build, 5-fold.
  - Table router: tables built on everything except the held-out fold.
  - Simple router: rates from the 400 train rows.
- **Dedup:** I dropped every fitting row whose prompt text equals a held-out prompt. Duplicates exist: 463 synthetic=grid, 19 synthetic=train, 74 grid=train. The table router still scores 0.8525 on Bed A, so the dedup changes nothing there.
- **Simulation:** 3,000 paired 500-row tests per setting, Dirichlet mix around the train family mix with alpha 200, 50 and 20, cap 395. Both routers are scored on the same draws.

| Bed / mix | Table: mean / p5 / P(q<0.80) | Simple: mean / p5 / P(q<0.80) | Simple worse in |
|---|---|---|---|
| A, full 400 | 0.8525 | 0.8350 | |
| A, no shift | 0.853 / 0.826 / 0.0% | 0.835 / 0.808 / 1.5% | 97% |
| A, alpha 200 | 0.852 / 0.816 / 0.8% | 0.835 / 0.796 / 6.4% | 94% |
| A, alpha 50 | 0.851 / 0.794 / 6.1% | 0.835 / 0.772 / 14.8% | 87% |
| A, alpha 20 | 0.850 / 0.766 / 13.6% | 0.834 / 0.742 / 24.1% | 80% |
| B, own mix 3256 | 0.8031 | 0.7779 | |
| B, no shift | 0.842 / 0.816 / 0.5% | 0.829 / 0.802 / 3.2% | 95% |
| B, alpha 200 | 0.842 / 0.804 / 3.0% | 0.829 / 0.790 / 9.9% | 94% |
| B, alpha 50 | 0.842 / 0.784 / 11.3% | 0.827 / 0.768 / 21.2% | 91% |
| B, alpha 20 | 0.842 / 0.756 / 19.0% | 0.826 / 0.738 / 28.7% | 90% |

The two other simple variants are worse:
- Family rates only, no rules: Bed A 0.8325.
- The rules forced to cheap (the earlier draft): Bed A 0.8350, Bed B 0.7712.

## Where the table router's edge comes from (`python3 breakdown.py`, rows correct vs the simple router)
- **Bed A (CPU, +7 of 400):**
  - fee_least +6: the souk-pick logit predicts which of the 15 the cheap guide gets right, so 4 stay cheap.
  - crate1 +2, walk4 +1, toll1 +1.
  - walk3 -2, fee_most -1.
- **Bed B (GPU, +82 of 3256):**
  - crate1 +45. This is likely inflated: its (crates, per-crate) cells are learned from the GPU grid, the same labeller as this bed. On CPU-labelled train it is only +2.
  - walk3 +19, fee_least +10, walk4 +4, fee_most +3, toll1 +1.
- **The gain that holds on both beds is the cheap-guide souk-pick model.** The cheap guide almost never names the first-listed souk: 7-10% of synthetic rows, 3 of 67 train rows.

## Caveats (they cut in both directions)
- **Bed A slightly favors the simple router.** Its three rule thresholds were picked by eye from all of train in wf1. Bed B is fully honest for them, and they hold on the synthetic set: toll at 10 gives cheap 0.82 vs at most 0.32 for other charges. The crate1 split is weaker there, 0.77 vs 0.54.
- **Bed B favors the table router,** because its tables include GPU-labelled rows from the other folds.
- **Bed A tails are rough.** The bootstrap draws from only 13-45 train rows per family.
- **The earlier tail numbers can't be reproduced from `fez/sim.py` as it stands.** The context reports 0.6% / 3.3% / 8.8%, but the Dirichlet loop is disabled (`for alpha_scale in ():`, line 36) and so is the up-weighting loop (`for f in []:`). The alpha values behind those numbers aren't recorded. I used 200/50/20, which gives 0.8% / 6.1% / 13.6% for the table router on Bed A.
- **Under strong shift (alpha 20), both routers miss 0.80 in 14-29% of simulated tests.** The cap already sends 316-395 requests to expensive, so the remaining risk comes from the mix, not from the routing.

## Recommendation
- Upload `main_under_review.py`.
- The simple router is easier to read, but it gives up about 1.7 points and multiplies the failure rate several times.
- If you want a middle ground later, the one piece worth keeping is the souk-pick model for fee/take. The cell tables for stall, toll2 and price_ind add nothing measurable on either bed (diff 0).
