# Round 2 integration: final detector

Deliverable: `SP/wf2/final/main.py` (671 lines, md5 `528c0c1b…`). It is one self-contained file that uses only
numpy, scipy and the stdlib. It is deterministic and writes only `detection.csv`.

What it contains:
- **Features**: the 8 baseline families, plus `nonlin`, `dcsub` and `hfband` from fam-chain, plus `tuning_g`,
  `pitchprint` and `pitchprint_f` from fam-pitch. The new code is copied verbatim from those agents, minus the
  dropped families.
- **Search**: the baseline's pooled mean-shift scan and robust-z calibration. On top of it, fusion's
  prominence-weighted fusion (`PROM_THR = 1.2`) and its weak edge/length prior.
- **Dropped**: fam-chain's `reverb`, fam-pitch's per-pitch `tuning`, and fusion's two-sided scan.

## Headline

| | SIM1 /72 | SIM2 /48 | train | CPU (user, train / 70 s file) |
|---|---|---|---|---|
| baseline | 45 | 36 | PASS −0.02 / −0.02 s | 1.9 / 2.1 s |
| **final** | **71** | **48** | **PASS −0.02 / −0.02 s** (14.943–20.940) | **3.8 / 4.7 s** |

Both rows come from the official `eval.py` (SIM1 + train) and `eval2.py --data sim2/data` (SIM2).
Logs: `results/final_sim1.{txt,csv}` and `results/final_sim2.{txt,csv}`. The only failure is b_7: a scale-only
change with no timbre or tuning trace, which no family sees.

At these rates, P(3 of 3 hidden files pass) is 95.9% on SIM1 and 100% on SIM2. Neither benchmark is
the hidden generator.

## 1. Baseline, each component, and the integration steps

These tables come from the lab, which reproduces every official run file for file (section 5).

| detector | a | b | c | d | e | f | g | h | i | SIM1 /72 | near | weak | hard | SIM2 /48 | train err (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline (wf1) | 8 | 2 | 7 | 5 | 8 | 4 | 4 | 0 | 7 | **45** | 16 | 11 | 9 | **36** | -0.02 / -0.02 |
| + chain families (fam-chain main.py) | 8 | 5 | 7 | 7 | 8 | 8 | 6 | 1 | 8 | **58** | 16 | 15 | 13 | **44** | -0.02 / -0.02 |
| + pitch families (fam-pitch main.py) | 8 | 6 | 8 | 5 | 8 | 5 | 5 | 8 | 8 | **61** | **13** | 15 | 11 | **39** | +0.03 / -0.02 |
| + fusion (fusion main.py) | 8 | 4 | 7 | 7 | 8 | 8 | 3 | 7 | 8 | **60** | 16 | 15 | 11 | **42** | -0.02 / -0.02 |
| chain + pitch, Σ relu(z)² | 8 | 7 | 8 | 7 | 8 | 8 | 6 | 7 | 8 | **67** | 15 | 16 | 15 | **46** | -0.02 / -0.02 |
| chain + fusion | 8 | 6 | 8 | 8 | 8 | 8 | 5 | 5 | 8 | **64** | 16 | 15 | 15 | **46** | -0.07 / -0.02 |
| pitch + fusion | 8 | 7 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | **70** | 16 | 16 | 14 | **46** | -0.02 / -0.02 |
| all three as built (two-sided scan, priors) | 8 | 7 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | **70** | 16 | 15 | 16 | **47** | -0.07 / -0.02 |
| all, pooled scan (no two-sided) | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 |
| **FINAL** (− reverb, − tuning, pooled) | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 |

**Overfitting watch.** The pitch families under the old Σ relu(z)² fusion win SIM1 (+16) but lose 3 of 16 SIM2
`near` files, which are the train-like ones. With prominence fusion the pitch families no longer cost anything
(near 16/16). The pitch families therefore ship only together with prominence fusion, never with the old fusion.

## 2. Ablation around the final

Each row adds or removes one component. The train margin is log(best score among intervals that pass) − log(best
score among intervals that fail); higher is safer. "Thin" counts files whose margin is below 0.05, failures
included.

| config | a | b | c | d | e | f | g | h | i | SIM1 /72 | near | weak | hard | SIM2 /48 | train err (s) | train margin | thin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **FINAL** | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.131 | 6 |
| + reverb | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.119 | 6 |
| + tuning | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.130 | 6 |
| + two-sided scan | 8 | 7 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | **70** | 16 | 15 | 16 | **47** | -0.07 / -0.02 | +0.128 | 8 |
| − priors | 8 | 7 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | **70** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.131 | 8 |
| − nonlin | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.116 | 7 |
| − dcsub | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 16 | 13 | **45** | -0.07 / -0.02 | +0.128 | 8 |
| − hfband | 8 | 7 | 8 | 8 | 8 | 7 | 8 | 8 | 8 | **70** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.131 | 7 |
| − tuning_g | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 4 | 8 | **67** | 16 | 16 | 16 | **48** | -0.07 / -0.02 | +0.128 | 11 |
| − pitchprint | 8 | 7 | 8 | 8 | 8 | 8 | 5 | 8 | 8 | **68** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.131 | 7 |
| − pitchprint_f | 8 | 6 | 8 | 8 | 8 | 8 | 6 | 8 | 8 | **68** | 16 | 16 | 16 | **48** | -0.02 / -0.02 | +0.131 | 9 |
| − all chain (nonlin, dcsub, hfband) | 8 | 7 | 8 | 7 | 8 | 7 | 8 | 8 | 8 | **69** | 16 | 16 | 13 | **45** | -0.02 / -0.02 | +0.114 | 13 |
| − all pitch (tuning_g, pitchprint, pitchprint_f) | 8 | 6 | 8 | 8 | 8 | 8 | 4 | 4 | 8 | **62** | 16 | 15 | 15 | **46** | -0.07 / -0.02 | +0.129 | 15 |
| SIM1-only strict elimination (see 3) | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | **71** | 16 | 15 | 13 | **44** | -0.02 / -0.02 | +0.110 | 13 |

`PROM_THR` plateau (final config): SIM1 71, SIM2 48 and train PASS hold for every threshold in
{1.0, 1.1, 1.2, 1.3, 1.5, 2.0} (`lab/thr.py`). The threshold is not tuned.

## 3. Selection protocol and decisions

**Lab.** The lab caches the 16 families once per file (`lab/lab.py feats`). It then scores all 1024 combinations
of the 8 new families × two-sided on/off × priors on/off (`lab/lab2.py`), using exactly the scan, calibration and
fusion code of the merged detector (`lab/merged.py`).

**Strict SIM1 run.** First I ran a strict SIM1-only backward elimination (`lab/ana2.py`): drop any component
whose removal keeps the SIM1 pass count. It ends at hfband + tuning + pitchprint + pitchprint_f + priors (pooled):
71/72 on SIM1, but only 44/48 on SIM2 and train margin 0.110.

It drops dcsub, nonlin and reverb because SIM1 cannot see them. SIM1 has no square-law stage and no DC model.
Those families target exactly the chain cues the forensic reports found on the real train file. So a SIM1 tie is
no evidence about them either way.

**Final rule.** Remove a component when it ties everywhere (SIM1 passes, SIM2 passes, train still passing).
Keep it when removal loses on any of the three.

**Caveat.** For the chain families SIM2 became a tie-breaker, so the final's 48/48 is not a clean held-out
number. The clean SIM1-only pipeline scores 44/48.

| component | decision | evidence |
|---|---|---|
| prominence fusion (fusion) | **keep** | the largest single gain: chain + pitch go from 67 → 71 on SIM1 and 46 → 48 on SIM2; flat over thresholds 1.0-2.0 |
| two-sided scan (fusion) | **drop** | in the full stack it costs 1 file on SIM1 (g_8) and 1 on SIM2 (weak_01) and moves the train start error from −0.02 to −0.07 s. It only helped with the 8 baseline families. A win in fusion's own setting that loses once merged. |
| edge/length prior (fusion) | **keep** | +1 on SIM1 (g_8), tie on SIM2 and train; 6 lines |
| tuning_g (fam-pitch) | **keep** | −4 h files on SIM1 without it |
| tuning (fam-pitch) | **drop** | duplicate of tuning_g once prominence fusion is in; ties everywhere. The simpler one is kept: no per-pitch table. |
| pitchprint, pitchprint_f (fam-pitch) | **keep** | −3 and −4 on SIM1 (g, b) without each |
| hfband (fam-chain) | **keep** | −1 on SIM1 (f_3) without it |
| dcsub (fam-chain) | **keep** | −3 SIM2 hard files without it (hard_01/05/13, the no-saturation splices) and train start error −0.07. It is the train DC cue (+2 LSB outside, ~0 inside). |
| nonlin (fam-chain) | **keep** (judgement) | Ties on pass counts. It is the top-weighted family on train (weight 8.6, above lowfreq 7.5), and train margin drops 0.131 → 0.116 without it. It is the square-law signature of the real file; ~25 lines, cheap. |
| reverb (fam-chain) | **drop** | Ties everywhere, lowers train margin 0.131 → 0.119, and is the most expensive family (fine STFT). Dry-insert files in g pass without it via pitchprint. |

## 4. CPU time

`/usr/bin/time`, isolated temp dir, BLAS threads 1, on a shared box at load ~210-270. User time is the
stable figure. Sys time swings between 0.6 and 9 s from run to run with box load (page faults), so treat it as
noise. Every config stays far below the 60 s limit.

| detector | train 55.8 s: user / sys / wall | h_4 69.9 s (longest): user / sys / wall | max RSS |
|---|---|---|---|
| baseline | 1.91 / 4.12 / 6.3 s | 2.07 / 9.18 / 12.4 s | 412 MB |
| fam-chain | 4.46 / 7.36 / 12.8 s | 4.83 / 8.11 / 13.9 s | 466 MB |
| fam-pitch | 2.31 / 4.94 / 7.9 s | 2.58 / 4.12 / 7.2 s | 452 MB |
| fusion | 3.19 / 0.67 / 4.0 s | 3.85 / 1.11 / 5.1 s | 418 MB |
| **final** | **3.80 / 0.59 / 4.6 s** | **4.66 / 0.89 / 5.7 s** | 469 MB |

In the official evals (4 files at once) the slowest file took 13.8 s of wall time.

## 5. Verification

- **The lab matches every agent's own official run, file for file**: 0 mismatches.
  - fam-chain `runs/eval_final.csv`: 73 files.
  - fam-pitch `eval_full.csv`: 73 files.
  - fusion `results/final_eval.csv`: 73 files.
  - sim2 `baseline_results.csv`: 49 files.
- **The lab's matrix-form enumeration** (`lab2.py`) matches the merged detector's own `fuse()` (`res_v1.json`) on
  7 reference configs × 121 files: 0 mismatches.
- **The final `main.py` under the official evals** gives exactly the lab's predictions for the chosen config on all
  121 files (72 SIM1 + 48 SIM2 + train): 0 mismatches.
- **Final run checks**: train in an isolated dir gives 14.943,20.940; only `detection.csv` is written; it
  imports only numpy, scipy and the stdlib.

## 6. Residual risk

- **Thin passes**: margin below 0.05 on d_7 (0.032), g_6 (0.030), g_7 (0.009; start error −1.43 s, right at the
  tolerance), weak_01 (0.019) and hard_13 (0.007). On a fresh seed, expect ±1-2 files of noise in those
  scenarios.
- **Train-like files are not marginal**: SIM1 a and SIM2 near pass 24/24 with median max-edge error under 0.1 s.
  The real train file passes with errors of 0.02 s; its margin is 0.131, i.e. the best wrong interval scores 88%
  of the right one.
- **b_7 still fails**: a different scale only, same voice and tuning. No current family carries that cue.
- **SIM2 is not fully held out**: it served as the tie-breaker for keeping dcsub and nonlin (section 3).

## Files

- `main.py`: the deliverable.
- `results/final_sim1.{txt,csv}`, `results/final_sim2.{txt,csv}`: the official eval logs.
- `lab/assemble.py`: builds `lab/merged.py`, which is all components behind switches.
- `lab/build_final.py`: strips the unselected components into `main.py`.
- `lab/lab.py`: the feature cache (`lab/cache/`, 101 MB) and the named configs (`res_v1.json`).
- `lab/lab2.py`: the exhaustive 1024-config table with margins (`exh_v1.pkl`).
- `lab/ana2.py`, `lab/ana3.py`, `lab/ana4.py`: the elimination runs.
- `lab/thr.py`: the threshold plateau.
- `lab/tables.py`: produces `lab/tables.md`.
