# Red team of the final detector (`wf2/final/main.py`)

Target: `SP/wf2/final/main.py` (md5 `528c0c1b…`). It was not edited; I only imported it read-only for diagnostics.

## Headline

| set | files | pass | notes |
|---|---|---|---|
| batch 1: the requested list | 52 | **50** | fails: `long_2` (12 s), `s1_b_slow` (qenet only) |
| batch 2: weak-cue chain × the same geometries | 22 | **19** | fails: `x_dchp_short`, `x_sat_edge`, `x_b_ctrl` |
| **all** (official `sim2/eval2.py`) | **74** | **69 (93.2 %)** | train still PASS (−0.02 / −0.02 s) |

The official harness (`results/eval2.txt`) and my diagnostic run (`results/diag_all.csv`) agree file for file.

The five failures fall into three causes:

1. **A qenet-only splice** (2 files). This is the known b_7 blind spot. No family fires at the truth.
2. **One weak chain cue outvoted by correlated content families** (2 files). The right family peaks on the
   truth, but 5-7 content families with small weights all peak on the same natural passage, and their sum wins.
3. **The length prior on a splice over 10 s** (1 file, plus thin margins on most long splices).

The edges, mid-note seams, lower register, other host qenet/register/tempo, louder and quieter noise, and 30 s and
90 s files caused no failure by themselves.

## How the files were made (nothing tuned)

- `rt_gen.py` imports `sim2/gen2.py` (renderer, reverb, saturation, noise, `base_params`) and `wf1/out/sim/gen.py`
  (the SIM1 take builder) unchanged, and adds overrides for length, placement, mid-note starts, the borrowed
  take's chain, and the host's tonic/scale/tempo, noise and file length.
- Seeds are `20261200 + 100·k`, disjoint from SIM1 and SIM2. Each file has one seed, and nothing was regenerated
  or swapped.
- Batch 2 was written down after batch 1's results came in. Batch 1 showed that every near-train chain passes on
  the DC/LF cue, so batch 2 crosses the weaker chains with the same geometries. **Batch 2's pass rate is an
  adversarial number, not an estimate of the hidden-test rate.**
- The new chains:
  - `host`: the borrowed take is the same renderer and register through the host's own room IR and square-law DC.
  - `sat_only`: the host chain plus asymmetric tanh, with the excerpt DC restored, so only the waveform shape
    changes.
  - `dchp`: the host chain plus a 20 Hz (or 40 Hz) HP and mean removal, or mean removal only.

## Results by group (`results/eval2.txt`)

| group | what | pass | median max-err | median margin |
|---|---|---|---|---|
| short | 2.0-2.1 s: near ×2, hard medium sat, washint T=0 | 4/4 | 0.36 s | +0.205 |
| long | 10.5-12 s: near ×2, hard medium, washint no-sat | **3/4** | 0.44 s | +0.045 |
| edge | starts at 3.0-4.5 s / ends 3.5-4 s before the end | 5/5 | 0.10 s | +0.120 |
| midnote | excerpt starts +0.5 / +1.3 eighth into a note, host seam mid-note | 3/3 | 0.05 s | +0.155 |
| satonly | host chain + saturation only (drive 0.5/0.8/1.0/1.3), DC kept | 4/4 | 0.15 s | +0.105 |
| dchp | host chain + HP 20 / mean-only / HP 20 in `same` reverb / HP 40 | 4/4 | 0.32 s | +0.129 |
| lowreg | T = −5, −7, −12 (washint chain); host voice T=−7 mild sat | 4/4 | 0.12 s | +0.126 |
| hostvar | host D3 ambassel, A4 anchihoye, eighth 0.20 s and 0.45 s | 5/5 | 0.06 s | +0.116 |
| noise | noise −64, −58, −88 dBFS; hard at −64; mild at −86; take at −46 dBFS | 6/6 | 0.14 s | +0.135 |
| dur | 30 s ×3 and 90 s ×3 (near, hard, weak) | 6/6 | 0.05 s | +0.115 |
| sim1x | SIM1 a 30 s / a 90 s+11 s / c 2 s / d 11 s / g at 3.5 s / h 90 s / b slow | **6/7** | 0.08 s | +0.095 |
| x_dchp | DC/HP only × 2 s, 11.5 s, edge, 90 s, mid-note, noise −64 | **5/6** | 0.36 s | +0.084 |
| x_sat | saturation only × 2 s, 11.5 s, edge, 30 s, 90 s, noise −64 | **5/6** | 0.43 s | +0.088 |
| x_mild | hard mild sat × 2 s, 11.5 s, 90 s | 3/3 | 0.03 s | +0.149 |
| x_long | near chain × 11.5 s, 11.0 s (repeat of the long_2 geometry) | 2/2 | 0.08 s | +0.086 |
| x_sim1 | SIM1 h × 2 s, 11 s, edge; b at the default beat; g × 11 s | **4/5** | 0.12 s | +0.103 |

Margin is log(best passing cell) − log(best failing cell) of the fused score; above 0 means pass. The median over
all passes is +0.118.

## Failures by cause

Scores are the fused totals (after the prior) at the true cell and at the winner. "Best pass" is the best cell
within ±1.5 s of both edges. The counterfactuals come from `rt_cf.py` and re-score the detector's own debug output
(`results/cf_1.txt`, `cf_2.txt`). They diagnose; they are not fixes.

### Cause 1: a qenet-only splice (`x_b_ctrl`, `s1_b_slow`). Known blind spot, now 2/2

The splice keeps the instrument, tuning, chain and noise statistics; only the scale changes.

| file | truth → pred | winner families (contribution) | truth / winner / best pass |
|---|---|---|---|
| `x_b_ctrl` (tizita_major {58,60,62,65,67} → tizita_minor {58,60,**61**,65,**66**}, beat 0.62) | 37.09-43.02 → 12.79-15.79 | pitchprint alone (z 7.9, w 0.80) | 1.7 / 6.5 / 3.4 |
| `s1_b_slow` (anchihoye → tizita_major, beat 0.8) | 24.38-30.38 → 9.30-24.29 | lowfreq, noisefloor, spectral, hfband, dcsub, all on one 15 s drift | 10.1 / 24.0 / 12.5 |

- Two new pitch classes do not move `chroma`: z −0.2 at the truth, weight 0.
- Only `pitchanom` (own best 37.7-39.6, inside the truth) and, in `s1_b_slow`, `timbre` partly see the splice.
- Every counterfactual fails, including no prior, top family only and no content families. The cause is the
  missing cue, not the fusion.
- The default-beat control fails too, so the slow tempo is not the cause.
- With SIM1's 7/8, qenet-only splices now stand at **7/10**.

### Cause 2: one weak chain cue, outvoted by correlated content families (`x_dchp_short`, `x_sat_edge`)

| file | truth → pred | winner families (contribution) | truth / winner / best pass | the right family |
|---|---|---|---|---|
| `x_dchp_short`: same renderer, HP 20 + mean removal only, **2.1 s** | 33.41-35.52 → 6.45-9.45 | chroma 6.2, lowfreq 4.1, spectral 3.8, noisefloor 2.5, hfband 2.3, pitch 1.9 | 13.0 / 25.8 / 14.3 | dcsub peaks on the truth (33.04-35.93, z 7.1) but w = 1.84 |
| `x_sat_edge`: saturation only (0.8 / 0.15, DC kept), 5.1 s, ends 3.3 s before the end | 49.01-54.14 → 28.69-31.94 | pitch 4.4, nonlin 3.2, spectral 2.7, pitchprint_f 2.5, noisefloor 1.4 | 13.3 / 17.2 / 15.3 | lowfreq peaks on the truth (48.98-53.58, z 6.3) but w = 1.62 |

**What goes wrong.** In both files the right family alone passes, and fusion without the 7 content families
passes. But 5-7 content families, each with a weight of 0.3-1.1, put their own best interval on the same natural
passage. Prominence fusion treats them as independent evidence, and together they outvote the single chain
family. In `x_dchp_short` the summed content weight is 3.0, against 0.2-1.6 in the six DC-only files that pass.

**Why the right family's weight is low:**
- **`x_dchp_short`: the splice is short.** Its 2.1 s gives dcsub a top z of 7.2 and a weight of 1.84. The five
  passing DC-only files of 3.9-11.4 s give dcsub weights of 3.4-5.4.
- **`x_sat_edge`: a prominence artefact.** dcsub's best interval (50.88-54.58, z 8.2) splits the splice. Its
  "disjoint second peak" (49.38-50.88, z 6.2) is the other part of the same splice. So dcsub's prominence is
  8.2/6.2 = 1.32 and its weight is 0.12. `dynamics` (7.0 vs 5.4) loses its weight the same way.

**The edge is not the cause.** The prior at the true cell is 1.0, and the no-prior counterfactual still fails.

### Cause 3: the length prior on a splice over 10 s (`long_2`), plus thin margins on long splices

| file | truth → pred | winner families (contribution) | truth / winner / best pass |
|---|---|---|---|
| `long_2`: near chain, **12.0 s** | 18.38-30.38 → 18.39-28.39 (end −1.99 s) | hfband 70.2, timbre 54.2, lowfreq 48.8, dynamics 36.9 | 336.6 / 350.8 / 347.7 |

- The prior takes 6 % off a 12 s interval and nothing off a 10 s one. Without the prior the truth scores 358 and
  wins (counterfactual `no_prior` gives 18.39-30.39, PASS).
- Several families also fade over the last ~2 s of the splice: the own bests of hfband, lowfreq and tuning_g end at
  27.7-28.4. That makes the 10 s cell close in the first place.
- **The same pattern makes every long splice fragile.** Of the 13 splices of 10 s or more, 1 fails and 6 of the 12
  passes have a margin under 0.05: long_3, long_4, s1_a90, x_dchp_long, x_sat_long and x_mild_long. Their median
  margin is +0.047, against +0.118 over all passes.
- The only other thin pass is `x_sat_noise` (+0.018).

## What held up

| condition | result |
|---|---|
| 2 s splices | pass with any cue but DC-only (short ×4, x_sat_short, x_mild_short, and x_h_short at 1.65 s) |
| 3-5 s from either end | the edge prior never bit (8 edge files pass; the 9th, `x_sat_edge`, fails for cause 2) |
| mid-note seams | 4/4, margins 0.11-0.16 |
| low-level saturation only, drive 0.5-1.3 | 9/10; the failure is `x_sat_edge` (cause 2) |
| DC/HP only | 9/9 at 3.9 s and longer; the one failure is the 2.1 s file |
| lower register | 4/4, including T = −12 |
| host in D3, A4, eighth 0.20 s or 0.45 s, ambassel/anchihoye/tizita | 5/5 |
| noise from −58 to −88 dBFS, take at −46 dBFS | 6/6 |
| 30 s and 90 s files | 13/13 |

**Runtime.** A 90 s file (`d90_2`) takes 6.2 s user CPU, with 648 MB max RSS (vs 469 MB at 70 s). Under the
load-300 box its wall time was 20.6 s. The slowest file in the 4-parallel official eval took 18 s.

## Caveats

- The `sat_only` and `dchp` chains are my guesses at how a careful forger would make a splice whose only trace is
  saturation or a DC/HP change. They are not taken from the real file.
- The `s1_*` and `x_h_*`/`x_b_*`/`x_g_*` files use my relaxed snapping: seams land within ±0.6 s of the requested
  length. That is why `x_h_short` ended up 1.65 s long.
- Each cell has one seed. Treat the per-group rates as existence proofs, not estimates.

## Where a fix would go (untested; the detector is unchanged)

1. **Cause 1** needs a pitch-class novelty cue. Chroma, as built, does not respond.
2. **Cause 2** has two weak points:
   - the content families are correlated but summed as if independent (cap their joint weight?);
   - the prominence check counts a neighbouring piece of the same splice as a competitor (require the second
     peak to lie away from the top, not merely be disjoint?).
3. **Cause 3** comes from the length prior above 10 s. The task's "a few seconds" makes splices this long less
   likely, but the prior is what flips `long_2`.

Any change should be re-checked on SIM1, SIM2 and this set together. Batch 1 here is held out; batch 2 is not
neutral.

## Files

- `rt_gen.py`: the generator. `--files a,b` regenerates a subset and merges the labels. It is deterministic;
  batch-1 md5s were rechecked after batch 2 was generated.
- `data/*.wav` (74 files, 180 MB) and `data/labels.csv` (file, group, start_s, end_s, label, dur_s, params JSON).
- `rt_diag.py` gives the per-file diagnosis: `results/diag_all.{csv,jsonl}`, plus `diag.jsonl` (batch 1) and
  `diag_sub.jsonl` (batch 2), with per-family w, prominence, z, contribution at truth and winner, and cue stats.
- `rt_cf.py` gives the counterfactual fusions: `results/cf_1.txt`, `cf_2.txt`.
- `results/eval2.{txt,csv}`: the official harness run, including train.
