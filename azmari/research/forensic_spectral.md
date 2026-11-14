# Non-musical forensic cues in train-input.wav (ground truth 14.960-20.965 s)

Code, tables (`t*.md`) and plots (`p*.png`) live in `wf1/out/forensic_spectral/` (scripts `s01`-`s14`, shared helpers in `common.py`).
Run the scripts with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`. Without it, BLAS spun up to 13 cores on this box.

How to read the numbers:
- **robust z** = (median inside − median outside) / (1.4826·MAD outside), with 0.25 s guards at the seams.
- **AUC** = P(random inside frame > random outside frame). 0.5 means no separation, 1.0 or 0.0 means perfect.
- **Global interval** = best single 2-15 s interval from a rank-based two-change-point search over the whole file. Error is start/end in s.
- **Local CP** = a single mean-shift change point within ±3 s of each true seam. Error in s.
- **Register test** (`s11_register_test.py`) splices 6 s into 40-46 s and scores only 23-56 s:
  - **A**: outside material resampled up a fifth (outside chain, inside-like register). This is the false-positive control.
  - **B**: inside material resampled down a fifth, with the original >7.3 kHz band refilled (inside chain, outside register). This is the survival test.
  - **C**: B plus a synthetic 1.8 s exponential reverb.

## Main finding

The inserted take went through a **different signal chain and room**. Three independent physical signatures show it, and none of them depends on pitch:

1. **Strong even-order (square-law) nonlinearity, then a DC-block / ~20 Hz high-pass.** Inside, the 22-175 Hz band of x is coherently predicted by the same band of x_hp² (x high-passed at 215 Hz):
   - Transfer |H| ≈ 15-35, flat from 25-250 Hz, phase ≈ 0, coherence 0.44.
   - Outside: |H| ≈ 0.3-0.4, coherence 0.02.
   - The inside |H| collapses below ~20 Hz, so the inserted material was DC-blocked. Inside DC is 0.14 LSB. Outside DC is +1.7/+2.3 LSB and scales with power (DC ≈ 0.64-0.73·meansq − 2 LSB, corr +0.5..0.57), i.e. a mild x² term without a DC block.
   - The LF lines inside (31, 64-72, 93, 128 Hz) are difference tones and envelope products, not hum and not musical fundamentals.
2. **The inside is dry; the outside is reverberant.** After a note change outside, the old note's partials decay at a median −33 dB/s (IQR −37..−21) and are only −16 dB down 0.2-0.3 s later. Inside, they drop 30-55 dB within 50 ms. The note before the splice has its tail **cut** at 14.96-15.00.
3. **Impulsive LPC residual inside** (peak/MAD ≈ 6-8 vs ≈ 4 outside). This is partly the dryness: synthetic reverb (test C) halves it. It is also the sharpest boundary marker of all.

The background noise in 200 Hz-11 kHz is identical inside and outside: the inter-harmonic floor and the 10-11 kHz floor match within 0.7 dB. So noise was matched or added after splicing, and there is no hum, no band-limit, no codec grid and no LSB trace.

## Cue table (best setting per cue)

| cue | robust z | AUC | global interval (err s/e) | local CP err s/e | survives same register? |
|---|---|---|---|---|---|
| LF energy 22-175 Hz (steep FIR), 0.5 s | **+15.8** | 1.00 | 14.72-21.12 (−0.24/+0.15) | −0.24/+0.05 | **Yes** (B: z +12.5, hit). A: z −1.9, opposite sign, but a two-sided search still picked A's interval, so use it one-sided ("excess LF") |
| same, 0.25 s | +13.0 | 1.00 | 14.79-20.99 (−0.17/+0.03) | −0.12/−0.02 | same |
| Inter-harmonic floor 30-200 Hz (f0-guided), 0.25 s | +8.5 (+12.4 at 0.5 s) | 1.00 | 14.84-21.01 (−0.12/+0.05) | −0.08/−0.04 | Yes (same mechanism as LF energy). Needs f0 |
| HPSS residual 30-200 Hz, 0.5 s | +5.9 | 0.99 | 14.74-21.01 (−0.22/+0.05) | −0.17/−0.04 | Yes (same mechanism) |
| **LF corr(x, x_hp²)** (nonlinearity coupling), 0.5 s | +9.9 | 1.00 | 14.47-21.07 (−0.49/+0.10) | −0.24/−0.10 | **Yes** (B: +7.9 hit; A: −0.4, no false positive). Weakens under reverb (C: +3.1, miss). Level-independent |
| same, 0.25 s | +8.0 | 1.00 | 14.39-20.94 (−0.57/−0.02) | −0.12/−0.07 | |
| **LPC residual peak/MAD** (order 24, 46 ms blocks) | +3.6 per block (+7 after a 0.5 s median) | 0.97 | 14.90-20.98 (**−0.06/+0.01**) | **+0.01/+0.01** | **Yes** (B: +7.2 hit; A: +0.25, no false positive; C: +3.0, still a hit). Higher f0 should *lower* this metric, yet inside is higher |
| Release/reverb tail at note changes (old-partial decay slope) | slope −27.8, floor −4.1, t(−20 dB) −4.0 | n/a (30 outside vs 5 inside transitions) | event-based only | first inside transition 15.00 (+0.04), last 20.90 (−0.07) | **Yes by construction** (room property). Coarse in time: needs a note change near each seam (one every ~1-1.5 s) |
| DC-vs-power residual (DC − fitted b·meansq − c) | −2.2 (test B) | | B: 40.46-46.15 (hit) | | Yes, but weak per frame |
| 0-20 Hz band level (DC + sub-20 Hz), p50 0.5 s | −4.3 | 0.03 | 13.00-22.10 (−1.96/+1.13) | −1.86/+1.13 | Yes (DC block is a chain property). Poor boundary precision (±2 s). Raw DC mean per 0.5 s: z −1.0, AUC 0.17 |
| Skewness, 0.5 s | +2.0 | 0.73 | 14.97-20.52 (+0.01/−0.45) | +0.01/−0.50 | Probably partly yes (x² term adds skew). Not tested |
| diff/std (brightness), 0.5 s | +1.8 | 0.88 | 12.92-24.41 (−2.04/+3.45) | +1.21/+0.10 | **No**: musical/register |
| 10.5-11 kHz level, 1 s | +8.1 | 1.00 | 12.90-24.09 (−2.06/+3.13) | +1.14/+0.20 | **No**: inside partials reach Nyquist. The *floor* there (p10) is unchanged: −129.6 vs −130.3 dB |

## Null results (measured, no usable difference)

- **50/60 Hz hum / ENF:** there is no narrow line at 50/60/100/120/150/180 Hz anywhere. The outside has only a broad −107 dB bump at 43-56 Hz. The "+9 to +11 z at 50 and 60 Hz" from narrow band-passes is the broadband nonlinearity, not hum.
- **HF roll-off, band-limit, resampling:** identical in pre, in and post: −10 dB point at 10.0-10.1 kHz, slope −3.5 dB/kHz from 3-10 kHz, floor −139 dB/Hz at 10.8-11 kHz. No anti-alias edge and no imaging.
- **Inter-harmonic noise floor from 200 Hz to 10 kHz:** |z| ≤ 0.7, AUC 0.45-0.68. Residual spectral slope from 1-8 kHz: z −0.8, AUC 0.24-0.31 (weak).
- **LSB / quantization / dither:**
  - Odd-sample fraction is 0.498-0.499 everywhere, mod-4 counts are uniform, and there are no missing codes or histogram comb.
  - Code 0 is about 2x over-represented equally in pre, in and post. That points to a truncation-toward-zero quantizer applied once to the whole file after the splice.
  - Kurtosis is about 3 everywhere.
- **Sample-level discontinuity:** there is no click. LPC-residual peak/MAD in the seam blocks is 4.4-8.5, against a global p99 of 8.1.
- **Phase coherence:** harmonic relative-phase stability gives z −0.7..−0.9 (AUC ≈ 0.3). Period-to-period self-similarity (HNR) gives z +0.3..+0.7. Neither is useful.
- **Codec/processing block grid:** none. Folded |Δ²x|² profiles for P = 256/441/480/512/576/1024/1152/2048 all sit at null level (z ≤ 1.5 among every period from 200-2100), equally in pre, in and post.

## Crossfade shape (`p17_crossfade.png`, `p09_seam_*_zoom.png`)

- **Start:** the gains of the outgoing (E4, 331 Hz) and incoming (B4, 494 Hz) partials cross at **14.959 s**. The fade is about 20-30 ms. The outgoing note was already decaying, so the power sum shows no extra dip; there is only a 1-2 ms envelope notch at 14.960. The LF/nonlinearity signature switches on in the same 10 ms.
- **End:** the inside D5 (594 Hz) is cut at 20.875-20.89 and the outside F4 (351 Hz) rises from 20.87 to 20.93. The crossover is at **20.885, 80 ms before the label**. The non-musical cues put the end at 20.90-20.99 (LF corr 20.895, inter-harmonic floor 20.925, LF energy 20.95-20.99, LPC 20.975). So the label is probably the end of a ~0.1 s fade. This doesn't matter at a 1.5 s tolerance.

## Background stationarity, for "background changed" test files (`s14`)

Robust std of the outside floor in 0.5 s frames, p10:

- 40-100 Hz: 0.79 dB
- 10-11 kHz: 0.77 dB
- 8-10 kHz: 2.3 dB
- 0-20 Hz: 3-6 dB

A splice whose room tone differs by 2.5 dB or more in 40-100 Hz (below the lowest fundamental) or 10-11 kHz (above most partials) would show z ≥ 3 at roughly ±0.1-0.2 s. In this file, 10-11 kHz is unchanged and 40-100 Hz is swamped by the nonlinearity (+17 dB).

## Recommendations for main.py (numpy + scipy only)

1. **Non-musical cue families worth combining.** All are cheap, and register-robust per test B:
   - (a) LF energy below the lowest fundamental, with the band set adaptively to roughly 22 Hz up to 0.7·min(f0).
   - (b) LF corr(x, x_hp²).
   - (c) LPC residual peak/MAD, using `scipy.linalg.solve_toeplitz`.
   - (d) Old-partial decay at note changes.
   - (e) DC-vs-power residual.
   - (f) Stationary-band floors (p10, 40-100 Hz and 10-11 kHz).
   Score each frame series with the rank-based best-interval search, then fuse.
2. **Use steep FIR filters (`firwin` with ~4001 taps plus `fftconvolve`) for LF bands.** Butterworth `filtfilt` let the C4 fundamental at 262 Hz leak into 20-200 Hz and erased the cue: z +0.2 instead of +16.
3. **Make the LF-energy cue one-sided** ("more LF than the rest"). In test A, transposed outside material *lowered* LF energy, and a two-sided search locked onto it.
4. **Boundary precision is not the bottleneck.** Every strong cue lands within ±0.25 s, and LPC peakiness within ±0.06 s. The risk is a hidden test where the inserted chain has no nonlinearity and no dryness difference. Then only (d), (f) or musical cues remain.
