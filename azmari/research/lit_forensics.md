# Literature + forensics report: localizing ONE replaced phrase in ONE recording (no reference)

Task context: "Azmari's Borrowed Melody". Mono, 22,050 Hz, 16-bit, roughly 56 s, synthetic music. One 2-10 s interval was replaced. The seams are crossfaded with no click, no pop and no level jump. A test passes only if both edges are within ±1.5 s. The final script may use numpy and scipy only.

Author: lit-forensics research agent. Scripts behind the measured numbers: `wf1/out/lit_forensics_aux/quick_checks.py` and `quick_checks2.py`. Each runs single-threaded in under 10 s.

---

## 0. TL;DR

1. **Model the problem as one anomalous interval: an epidemic change point, also called a square-wave change.** Don't chase seams. The literature agrees that careful splices hide boundary artifacts. A crossfade of 1024 samples or more, plus a high-pass filter or added noise, defeats the training-free seam detector of Negroni et al. 2024. Learned PartialSpoof localizers also over-rely on boundary artifacts and fail out of domain: CFPRF goes from 7.6 % EER in-domain to 43 % on LlamaPartialSpoof. The robust signal is **segment-level inconsistency**: the inside differs from *both* outer parts, and the two outer parts agree with each other. Exhaustive search over (start, end) pairs with cumulative sums is cheap: about 60k candidates at a 0.1 s grid.
2. **Use several cue families. Calibrate each family's scan map against its own null, then combine.** Use block-permutation or circular-shift nulls so that a single strong family wins and noisy families don't create false peaks. Detailed recipe in section 3.
3. **Ranking for this task**, by how likely each family localizes a 2-10 s insert within ±1.5 s in a synthetic 22 kHz music file. Details in section 4.

| # | Cue family | Training file evidence (measured) | P(useful on hidden tests) | Time resolution |
|---|---|---|---|---|
| 1 | **Fine-band log-spectrum / channel-EQ consistency** (LTAS per window, including sub-100 Hz and >8 kHz bins) | **25-110 Hz band is +25-28 dB inside. It steps up exactly at 14.96 s and down exactly at 20.965 s, at 0.1 s resolution.** Window z-score +10.8. | High | 0.1-0.5 s |
| 2 | **Musical-content consistency** (pitch-class set, register, tuning offset in cents, timbre/harmonic profile, phrase repetition) | New pitch class B. Register up a 3rd-6th. 200-400 Hz band is −31 dB inside (z = −20.6). | High on train. Medium on hidden tests, where the generator may keep the register. | 0.25-1 s |
| 3 | **Noise floor per band** (minimum statistics, kurtosis-based estimator) | 3-11 kHz floor identical inside and outside, within 1 dB. Noise was likely added after the splice. | Medium. It decides the case when the generator varies the floor per take. | 0.5-2 s |
| 4 | **Seam cues** (crossfade power dip, phase/ENF step, low-bin leakage) | Brief reports a 20-60 ms envelope dip at both seams | Low as a detector, useful for refinement | 10-50 ms |
| 5 | **Reverb / room (RT60, decay-rate distribution)** | Inside decay looks slightly slower (RT≈0.68 s vs 0.57 s), but only 5 decays inside, so not significant | Low-medium | 2-5 s (needs several note offsets) |
| 6 | **Mains hum / ENF** | No hum in the file. 50/60/100/120 Hz peaks are under 4.5 dB, at around −110 dBFS. | Low unless the generator adds hum | 0.2-1 s for phase steps |
| 7 | **DC offset / quantization histogram** | DC about +2 LSB outside vs +0.14 LSB inside. Parity unchanged. | Low-medium (cheap; add as a weak family) | 1-2 s |
| 8 | **Codec / double compression / resampling** | High band is noise-dominated and identical. No visible brick-wall or codec holes. | Low (music is dark above 3 kHz, so the traces are under the noise) | 1-3 s |
| 9 | **Pretrained SSL embeddings** (wav2vec2, BEATs, CLAP, MERT) | Not run. These catch content/timbre changes that families 1-2 already capture, and mostly miss low-level traces at −100 dB. | Adds little; can't ship | 20 ms frames |

4. **Pretrained GPU model verdict:** Not worth more than a quick offline sanity check (section 5).

---

## 1. What the training file actually shows (my measurements)

Inside = [14.96, 20.965). Outside = the rest of the file minus a 0.5 s guard band around each seam.

**Long-term average spectrum** (Welch, 8192-point, dB re full scale²/Hz):

| band (Hz) | inside | outside | diff |
|---|---|---|---|
| 0-30 | −89.8 | −98.1 | +8.3 |
| 30-60 | −88.7 | −110.7 | **+22.0** |
| 60-100 | −87.4 | −115.4 | **+28.0** |
| 100-200 | −98.1 | −110.3 | +12.2 |
| 200-400 | −94.7 | −63.2 | **−31.5** (melody register) |
| 400-800 | −65.8 | −69.0 | +3.2 |
| 800-3200 | about −73 to −78 | about −75 to −83 | +1 to +5 |
| 3200-11025 | about −102 to −136 | same | within ±2.2 |

**Low band at 0.1 s steps across the seams** (25-110 Hz, dB):

- Seam at 14.96: `... -96 -98 | -70 -71 -75 ...`. The step happens in the frame that contains the seam.
- Seam at 20.965: `... -75 -76 | -98 -94 -95 ...`.

A midpoint threshold on the 0.5 s-smoothed curve crosses at 14.87 s and 20.92 s, both within 0.1 s of the truth. It also has one internal dip at 15.7-15.9 s, so you need an interval scan rather than a plain threshold.

**Minimum-statistics floor** (5th percentile of 46 ms frame power per band):

| band | inside | outside |
|---|---|---|
| 20-100 Hz | −95 dB | −102 dB |
| 100-400 Hz | −101 dB | −63 dB |
| 4-11 kHz | within 1-3 dB | same |

**High band (9-11 kHz high-pass residual):** std 1.5e-5 inside vs 1.3e-5 outside. Lag-1 to lag-3 autocorrelation is identical, which points to one global noise process.

**Mains hum:** No narrowband peak more than 4.5 dB above its neighbours at 50, 60, 100, 120, 150 or 180 Hz, inside or outside. ENF isn't usable on this file.

**What this means:**

- On train, the insert is given away by (a) **sub-100 Hz content** and (b) **pitch register / pitch classes**.
- Cue (a) is a classical channel or environment cue. It looks like a high-pass filter on the original take but not on the borrowed one, or rumble or a low drum in the borrowed take. It is sharp in time and doesn't depend on the notes played.
- Cue (b) is content.
- The high-band noise floor was equalized, probably by adding noise after splicing. Noise-only detectors would have failed on train.
- Expect hidden tests to switch which family carries the signal. The detector must not hard-code "sub-bass up" or "pitch up". It should look for any band or feature that is consistently different inside, in either direction, relative to both sides.

---

## 2. Framing: single-interval (epidemic) change detection

**Classical model.** The epidemic change-point model has observations distributed F₀ before τ₁ and after τ₂, and F₁ in between. Its likelihood-ratio test is the square-wave alternative of Yao 1993. A semiparametric version is in R `sac`. Joint estimation of (τ₁, τ₂) is studied in Jin, Han and Wu 2025. Multiple-epidemic search: aPELT.

- [Yao 1993](https://www.bohrium.com/paper-details/tests-for-change-points-with-epidemic-alternatives/812030156678889472-861)
- [sac package](https://packages.oit.ncsu.edu/cran/web/packages/sac/sac.pdf)
- [Jin, Han, Wu 2025](https://www.bohrium.com/paper-details/simultaneous-estimation-of-change-points-in-epidemic-change-models/1142944945863131137-24306)
- [aPELT](https://arxiv.org/pdf/1907.06810)

For multivariate features, the generic view is a cost function plus a search method plus a constraint ([Truong, Oudre, Vayatis 2020, the `ruptures` review](https://arxiv.org/abs/1801.00718)). Here the constraint is "exactly one interval, 2-10 s long", so **exhaustive search is optimal and cheap**.

**Music segmentation analogue.** Foote novelty correlates a checkerboard kernel along a self-similarity matrix and detects single boundaries. It responds to every section change in the music, so on its own it produces many false peaks. Use it for boundary refinement, not detection.

- [Foote 2000 / FXPAL](https://core.ac.uk/download/28906793.pdf)
- [Müller tutorial](https://www.audiolabs-erlangen.de/content/resources/MIR/00_2019_TutorialFMP_ISMIR/2019_MuellerZalkow_ISMIR-Tutorial_AudioStruct.pdf)

**Partial-fake localization in speech.** Zhang et al. (PartialSpoof) and the 2025 survey by He et al. split methods into four groups: frame-level authenticity, boundary perception, frame-level inconsistency, and multimodal fusion. Two later papers are critical of boundary-based methods:

- Luong et al. 2025 reframe localization as **sequential anomaly detection** and show that boundary-trained models collapse out of domain.
- The SAL paper (2026) shows models over-rely on transitions.

Our approach should sit on the **"frame-level inconsistency"** branch.

- [PartialSpoof (Zhang et al., TASLP 2023)](https://arxiv.org/abs/2204.05177)
- [He et al. survey 2025](https://arxiv.org/abs/2506.14396)
- [Luong et al. 2025](https://arxiv.org/abs/2507.03468)
- [SAL 2026](https://arxiv.org/abs/2601.21925)

---

## 3. Recommended scoring recipe (numpy/scipy only)

### Step 1. Frames

Use a hop of h = 0.1 s and windows of 0.2-1.0 s, depending on the feature. That gives T ≈ 560 frames for 56 s.

### Step 2. Feature families

Each family is a per-frame matrix.

**F1, fine-band log energy.** Use a log-spaced filterbank from 20 Hz to Nyquist with about 1/3-octave bands, roughly 30 bands. Take the log of the mean power per band from an STFT with a 2048-point window and a 220-sample hop, averaged to h. Include the extreme bands (<60 Hz and >8 kHz) explicitly, because that is where channel differences and splice leakage live (Negroni 2024).

**F1b, channel shape independent of level.** Subtract the per-frame mean over bands from F1, or take low-quefrency cepstral coefficients 1-12 of the per-frame log spectrum. This captures EQ, tilt and microphone curve while removing loudness.

**F2, noise floor per band.** Within a sliding 1-2 s window, take the 5th-10th percentile of frame power per band. This is minimum statistics, after Martin 2001.

**F3, content.**

- A 12-bin chroma vector. Log-frequency spectrum folded mod 12, or a pitch track from autocorrelation/YIN pooled into pitch-class bins.
- A tuning offset in cents: the median fractional MIDI value, as a circular mean.
- Register: the median f0.
- Harmonic-profile features: spectral centroid relative to f0, and odd/even harmonic ratio.

**F4, weak traces.**

- Local DC: mean of x over 1 s.
- Hum: mains bands ±1 Hz, both level and phase step.
- Kurtosis-based noise σ in band-pass channels.
- Fraction of empty bins in the int16 histogram, and comb periodicity of that histogram.

### Step 3. Robust standardization

Standardize each column by its median and MAD over the whole file.

### Step 4. Scan statistic per family

1. Build prefix sums of each feature and of its square.
2. For every candidate (a, b) with b − a in [1.5, 12] s, compute the inside mean μI and the left and right outside means μL and μR.
3. Use the **two-sided epidemic contrast**, per feature j:

   `c_j = sign-consistent min(|μI − μL|, |μI − μR|) / s_j`

   Set c_j to 0 if (μI − μL) and (μI − μR) have opposite signs. Here s_j is the pooled within-segment std. This term suppresses single step changes, for example "the second half is louder", and natural sections that only differ from one side.
4. Family map: `S_f(a,b) = sqrt(n_eff) · mean_j c_j²`, or the top-k mean if the family is wide. n_eff is a length-dependent factor, for example `sqrt(nI·nO/n)`, to balance short and long candidates.

### Step 5. Calibrate each family

Recompute S_f on B = 20-50 surrogate sequences. Make each surrogate by circularly shifting each feature column by a random offset, or by permuting 2-3 s blocks. This keeps autocorrelation and breaks the interval structure. Record the null distribution of max S_f and set `Z_f(a,b) = (S_f(a,b) − mean_null_max) / std_null_max`.

### Step 6. Combine

`C(a,b) = Σ_f max(Z_f(a,b), 0)` or `max_f Z_f(a,b)`. The sum rewards agreement between families. The max lets one family win alone. A safe compromise is `max_f Z_f + 0.5·Σ_other max(Z_f, 0)`.

Optionally add a mild length prior centred at 3-8 s. Exclude a ≤ 0.3 s and b ≥ T − 0.3 s.

### Step 7. Refine the boundaries

Within ±1.0 s of each coarse edge:

1. Rerun a single change-point CUSUM at 10-20 ms hop on the top 3-5 contributing features.
2. Nudge toward the nearest crossfade power dip in the smoothed RMS within ±0.3 s.

The brief reports 20-60 ms dips. An equal-gain crossfade of two uncorrelated signals dips about 3 dB at its midpoint, and a linear-gain crossfade dips up to about 6 dB.

### Cost and why this design

**Cost:** about 6×10⁴ candidates × about 60 features × (1 + B) scans. That is well under a second per family with numpy vectorization over the length dimension.

**Why this design:**

- It finds the "ONE contiguous interval most inconsistent with the rest", as required.
- It works when only one family carries the signal.
- It is direction-agnostic: up or down, any band.
- Calibration stops wide, noisy families (chroma, F1) from swamping a narrow, decisive one (DC, hum).

---

## 4. Technique catalogue

Each entry covers: what it detects, how to compute it with numpy/scipy, time resolution, failure modes, and my estimate for this task.

### 4.1 Channel / microphone / EQ response and long-term spectrum (rank 1)

**What it detects.** A different recording chain or room for the borrowed material: different microphone frequency response, high-pass or low-pass filtering, EQ, or presence or absence of rumble. Literature:

- **Zhao et al. 2014** model the environment as the magnitude of the room impulse response plus ambient noise. Per frame they estimate a log-spectral difference against a GMM clean-speech prior. They compare frames by normalized cross-correlation, use an extreme-value threshold, and refine with neighbouring frames (3-5 frames, 70-90 % suspect ratio). Localization is 100 % with frames of 1 s or longer on synthetic data and degrades below 0.5 s. The method is robust to MP3 at 32 kbps and above.
- **Cuccovillo et al.** and **Leonzio, Cuccovillo et al., TIFS 2023** do microphone-classification splice detection, with multiple splice points localized.
- **Capoferri et al.** use blind channel estimation footprints.
- **Negroni et al. 2024** need no training. They average dB over the quiet extreme bins: the lowest 16 bins below 60 Hz with a 4096-point Hann window, or the 5 bins above 7.96 kHz. The dynamic range max−min over time exposes splices, with AUC 98 % on PartialSpoof and 95 % on HAD. It fails with a high-pass at 100 Hz (AUC 56 %), with an OLA crossfade of 1024 samples or more plus low-passed noise, or with spectrally rich source data.

**Compute (numpy/scipy).**

1. `scipy.signal.stft`, nperseg 2048-4096.
2. Average power per log-spaced band.
3. Take 10·log10.
4. Smooth over 0.3-1 s.
5. Optional level removal: subtract the per-frame mean over bands, or use the DCT of the log spectrum and keep coefficients 1-12. This is cepstral-mean-style channel modelling.

**Time resolution.** 0.1-0.5 s for strong band differences. On train: within 0.1 s at both seams in the 25-110 Hz band.

**Failure modes.**

- **Content leakage.** Different notes move energy between bands, as with the 200-400 Hz band on train, and that is musical, not channel. It still localizes here, but a natural section change can mimic it.
- **Global post-processing.** Noise, EQ or a high-pass filter applied after splicing erases the cue. The high band on train shows this happened for noise.
- **Equal chains.** The generator may use the same chain for both takes.

**Estimate.** Highest prior. Content-independent where it applies, and it already wins on train.

### 4.2 Musical-content consistency (rank 2; not classical forensics, but the task story centres on it)

**What it detects.** A phrase "not played in that take": a new pitch-class set, a different register, a different tuning reference (the original is about +9 cents sharp; a borrowed take may sit at 0 cents or elsewhere), vibrato rate, timbre, or harmonic profile.

The closest forensic analogue is copy-move detection by pitch-sequence similarity (Yan, Yang, Huang, ICASSP 2015). Spectrogram-tensor and keypoint copy-move methods also exist: arXiv 2302.07584, and Ustubioglu et al., IEEE Access 2024. If the generator copied a phrase from elsewhere in the same file, a near-exact duplicate (normalized cross-correlation close to 1) shows up and ties to seam evidence.

**Compute.**

- **Chroma:** fold an STFT log-frequency magnitude into 12 bins with A4 = 440·2^(c/1200) and c estimated globally.
- **f0:** YIN or normalized autocorrelation per 46 ms frame; numpy-only YIN is about 30 lines.
- **Cents deviation:** `100·((12·log2(f0/440)+69) mod 1)`, as a circular mean.
- **Repetition score:** max cosine similarity of a 1-2 s chroma/MFCC block to any block at least 3 s away. The inserted phrase is unlikely to recur. Music-specific detail is left to the lit-music-cpd agent.

**Time resolution.** 0.25-1 s.

**Failure modes.**

- The generator keeps the same mode and register. A "borrowed melody" could come from the same performer and scale.
- A legitimately unique original phrase looks anomalous.
- Octave errors in f0.

**Estimate.** Strong but riskier. Use it as one family and never alone.

### 4.3 Noise floor / local noise level (rank 3)

**What it detects.** A different background noise level or colour between takes. Literature:

- **Pan, Zhang, Lyu, ICASSP 2012.** Band-pass-filtered natural audio has a near-constant kurtosis. With additive Gaussian noise of variance σ², the observed per-channel excess kurtosis obeys `sqrt(κ̃_k) = sqrt(κ)·(1 − σ²/σ̃_k²)`, where σ̃_k² is the observed channel variance. This is **linear in 1/σ̃_k²**. Regress sqrt(κ̃_k) on 1/σ̃_k² across about 8-16 band-pass channels: the intercept is sqrt(κ) and σ² = −slope/intercept. Run it per window and look for jumps.
- **Lyu, Pan, Zhang, IJCV 2014** is the image version of the same estimator.
- **Martin 2001** minimum statistics: track the minimum of smoothed per-bin power over about 0.8-1.5 s windows, with a bias correction. Works without voice activity detection.

**Compute.** Use `scipy.signal.sosfiltfilt` band-pass channels plus moments, or STFT percentiles. Both are trivial.

**Time resolution.**

- Percentile floor: 0.5-2 s.
- Kurtosis estimator: needs about 1 s or more for stable kurtosis.

**Failure modes.**

- Global noise added after splicing equalizes the floor. That is the case on train for 3-11 kHz.
- Music rarely has true silences, so the floor estimate is biased by sustained notes. The bowed masenqo is near-continuous.
- The kurtosis-constancy assumption is weaker for tonal music than for speech.

**Estimate.** Medium. Keep it as a family because the generator may vary the floor or the noise colour per test.

### 4.4 Seam cues: crossfade dip, phase discontinuity, leakage (rank 4, for refinement)

**What it detects.** The joint itself.

- **Negroni et al. 2024:** spectral leakage into quiet bins at a hard splice. Crossfading hides it.
- **Phase:** a discontinuity in the phase of a sustained partial. Track a partial with a short-time DFT. Instantaneous frequency is phase difference over hop. A splice produces a phase or IF outlier when the note continues across the seam.
- **Crossfade dip:** a 1-6 dB envelope dip over 20-60 ms.
- **Learned boundary detectors:** Cai et al. 2022, wav2vec2 boundary frames, 3.1 % EER on ADD. Learned and speech-only.

**Time resolution.** 10-50 ms, excellent.

**Failure modes.** The task explicitly says there is no audible seam. Natural note onsets, bow changes and breaths produce many similar dips and phase resets. On its own this has a very high false-alarm rate.

**Estimate.** Low as a detector, high value for snapping a coarse edge (from 4.1-4.3) within ±0.3 s.

### 4.5 Reverberation / room acoustics (rank 5)

**What it detects.** A different room or RT60.

- **Capoferri et al., WIFS 2020** track blind RT across windows and flag sudden changes.
- Ratnam et al. 2003 give an ML decay estimator that works on speech or music.
- Löllmann et al. 2018 give a closed-form ML estimator.
- Kendrick et al. 2007 report a multi-decay ML model accurate on orchestral music.

**Caution.** Moussa et al. 2022 found the RT baseline weak: top-1 splice accuracy 5-7 %, error ≤ 1.5 s for only about 30 % of samples.

**Compute.**

1. Band energy at a 10 ms hop.
2. Find free-decay runs: monotone decreasing for 80 ms or more and at least 10 dB down.
3. Fit the slope in dB/s.
4. Per window, take the slowest-decile slope as an RT60 proxy, or fit a Laplace/Rayleigh decay-rate distribution.

A cheaper proxy: the ratio of energy 50-200 ms after each detected offset to the pre-offset level.

**Time resolution.** It needs several decays, so 2-5 s. On train only 5 decays fall inside the insert: RT proxy 0.68 s vs 0.57 s, not significant.

**Failure modes.**

- Legato bowed and flute lines have few free decays.
- Synthetic generators often apply one global reverb after splicing, which erases the cue.
- Short inserts give too few samples.

**Estimate.** Low-medium. Cheap enough to include as a weak family. Never trust it alone.

### 4.6 Mains hum / ENF (rank 6)

**What it detects.**

- Presence, absence, level or frequency change of mains hum (50 vs 60 Hz and harmonics).
- Phase discontinuities of the hum at edits (Rodríguez, Apolinário, Biscainho, TIFS 2010).
- A version using higher harmonics (EUSIPCO 2013).
- A blind 1D-CNN on ENF phase and waveform (Sci. Rep. 2024).

**Compute.**

1. Look for narrow peaks at 50, 60, 100, 120, 150 and 180 Hz in a long Welch PSD (8192 points or more).
2. If a peak is at least 6 dB above its neighbours, band-pass ±1 Hz with `sosfiltfilt`.
3. Take the analytic signal (`scipy.signal.hilbert`), unwrap the phase, and remove the linear trend at nominal frequency.
4. Look for a phase step or residual-slope change. Alternatively, use the DFT1 phase estimate per 1 s block.
5. Use hum amplitude per block as a level cue.

**Time resolution.** Phase steps resolve to about 0.1-0.5 s. Level changes to about 1 s.

**Failure modes.**

- No hum. That is the case on train: all mains-bin peaks are within 4.5 dB of their neighbours, at around −110 dBFS.
- Music partials at around 100-180 Hz masquerade as hum. Note that 65-74 Hz peaks inside the train insert are not mains.
- A global hum added after splicing has a continuous phase.

**Estimate.** Low. Include the presence test because it costs about 10 ms. If a hidden test has hum, this may be the decisive family.

### 4.7 DC offset and quantization (rank 7)

**What it detects.** A different A/D converter or processing chain.

- The SWGDE audio-authentication best practices list DC offset, bit depth and butt-splice checks.
- Grigoras & Smith 2014 analyse the quantization level with five methods: QL histogram, QL length, greatest common divisor, FFT and cepstrum. Processing such as gain changes on already-quantized audio leaves histogram combing.
- **Caveat** (JAES 2013, via AES e-lib 16834): DC offset varies widely between and within small recorders, so it's weak as a comparison parameter.

**Compute.**

- Per-1 s mean of x. Outside, the signal has almost no energy below 100 Hz, so the mean is estimated very precisely. That makes the 2 LSB vs 0.14 LSB difference on train meaningful.
- Per-window int16 histogram: fraction of unused codes, and the FFT of the histogram to find comb periodicity.
- LSB-plane statistics.

**Time resolution.** 1-2 s.

**Failure modes.**

- A final global dither or noise addition, or a global re-quantization, erases these traces.
- Low-frequency musical content inflates the variance of the mean. That is true inside the train insert.

**Estimate.** Low-medium, but nearly free. Add it as a calibrated family.

### 4.8 Codec / double compression / resampling (rank 8)

**Codec.**

- Bianchi et al. 2014 compute MDCT-coefficient histograms for single vs double MP3. They work in short windows, which allows localization.
- Yang, Qu, Huang 2009/2012 use the frame-offset method: an insertion breaks the 576/1152-sample granule grid. They report about 99 % detection when the forgery was made after decoding to PCM and without re-encoding.

**Resampling.** Popescu-Farid-style periodic correlation, second-difference zero spacing, and peaks in the second derivative of the spectrum (Hou et al. 2014), plus band-partitioned spectral smoothness. A 2024 Applied Sciences paper (pyramid attention) is the learned state of the art. Gaussian noise and median filtering defeat the classical detectors.

**Compute.**

- **Codec grid:** for each candidate offset 0-575, compute a 576-hop MDCT using scipy.fft DCT-IV with a sine window. Count near-zero coefficients above about 5 kHz. A sharp maximum at one offset inside a window, which shifts across windows, marks the grid.
- **Bandwidth:** highest frequency at which the windowed LTAS exceeds the global noise floor by 6 dB. A brick-wall at 8 kHz inside suggests the insert was upsampled from 16 kHz.

**Time resolution.** 1-3 s.

**Failure modes.**

- Noise added after decoding destroys zero-coefficient patterns.
- On this dark, noise-dominated music (everything above 3.2 kHz is at about −100 dB or lower and identical inside and outside), resampling or low-pass traces sit under the floor.
- Content above 8 kHz is needed to see a 16 kHz upsampling cut.

**Estimate.** Low. Include only the cheap bandwidth/rolloff feature inside F1. Skip the MDCT grid search unless a hidden-test-like file shows codec holes.

### 4.9 Self-supervised embeddings and learned localizers

**Speech partial-spoof systems** are all trained on speech TTS or VC inserts. They use wav2vec2 or WavLM front ends with frame heads.

- Zhang et al. PartialSpoof with multi-resolution labels down to 20 ms (data on Zenodo 5766198).
- Cai et al. 2022 boundary detection.
- TDL 2023, embedding-similarity temporal localization.
- CFPRF 2024, coarse-to-fine proposals.
- Split-and-conquer 2026 (arXiv 2604.02913).
- NE-PADD (APSIPA 2025).

Out-of-domain they collapse: CFPRF 7.6 % → 43 % EER on LlamaPartialSpoof (Luong 2025). They over-rely on boundary artifacts (SAL 2026).

**Training-free embedding dynamics.** TRACE (arXiv 2604.01083) scores first-order frame-to-frame changes in frozen speech foundation-model embeddings: 8.1 % EER on PartialSpoof and 24 % on LlamaPartialSpoof with no training. That is the same idea as Foote novelty on embeddings.

**Music deepfake detectors.**

- MERT and Music2vec front ends on SONICS (about 48k real and 49k fake songs) and FakeMusicCaps (10 s clips from 5 text-to-music models).
- Segment Transformer (arXiv 2509.08283), CLAM/MoM (NeurIPS 2025).
- Near-ceiling in-distribution, with large OOD drops: SpecTTTra falls to 50-68 % F1 on unseen generators.
- These are utterance or clip classifiers, not localizers.

**What embeddings would give here.** A per-frame embedding (wav2vec2/WavLM at 50 Hz, BEATs at 16 kHz fbank, CLAP at 48 kHz, MERT at 24 kHz) can feed the same epidemic scan.

- **Pro:** rich timbre and content sensitivity.
- **Con:** they are trained to be invariant to the low-level traces that matter forensically: absolute level, sub-100 Hz rumble behind normalization, a −110 dB noise floor, DC and hum. Most also resample to 16 kHz, which discards 8-11 kHz. They mostly duplicate family 4.2.

### 4.10 LLM / agentic audio forensics (2025-2026)

- **PELM** (arXiv 2601.21463): a prior-enhanced audio LLM that frames speech-edit detection and localization as audio question answering. Localization EER 9.28 % on AiEdit. It reports that audio LLMs have "forgery bias" and "semantic-priority bias", and that fine acoustic traces are overlooked.
- **ThinkOmni** (arXiv 2607.26553): Qwen2.5-Omni plus XLS-R, evidence-driven chain-of-thought reports. Its README claims 74.7 % localization mAP cross-dataset. Training code and checkpoints were "coming soon" at the time of search.
- **SDD-APALLM** (arXiv 2601.23066): explicit acoustic evidence perception for audio-LLM speech deepfake detection.
- **ForenAgent** (image forensics): an agent calling SRM, FFT and JPEG-ghost tools. Its authors argue that tool-using agents are the next paradigm for multimedia forensics.

**Takeaway.** The 2026 trend is "LLM orchestrates handcrafted forensic tools and explains the evidence". That is what our pipeline does offline: agents explore the cues, and main.py ships a deterministic numpy scan. No audio LLM localizes music splices to ±1.5 s out of the box.

---

## 5. Would a pretrained model on a GPU add anything?

**Mostly no, for the shipped script. A small yes as an offline oracle.**

1. **It can't ship.** main.py is numpy/scipy only. Distilling an embedding into a numpy feature is not feasible with one labelled example. A random-feature or linear approximation would just be our spectral features again.
2. **Wrong invariances.** SSL encoders normalize level and resample to 16 kHz (24 kHz for MERT, 48 kHz for CLAP). They are known to prefer semantic or content cues (PELM's "semantic-priority bias"). The cue that wins on train, a +25 dB difference at 25-110 Hz at around −90 dB absolute, is near-invisible to them. Content changes such as pitch, register and timbre are already captured cheaply by chroma, f0 and band energies.
3. **Out-of-domain collapse** is the documented norm for learned partial-spoof localizers (43 % EER OOD). Synthetic Ethiopian masenqo/washint music is far out of domain for every public checkpoint.
4. **Where it could help (optional, at most an hour, CPU is fine):** run BEATs or MERT frame embeddings through the same epidemic scan on train and on simulator-generated variants. Use it as an independent check that the numpy families aren't missing a gross timbral cue. If embeddings localize a simulated case that our families miss, inspect which band or feature explains it and add that feature to numpy. Don't spend GPU time beyond that.

---

## 6. Concrete suggestions for main.py and for the simulator agent

1. **Families to include, all numpy/scipy:**
   - F1: about 30 log bands from 20 Hz to Nyquist, plus the level-removed shape and cepstrum 1-12.
   - F2: percentile noise floor per band.
   - F3: chroma (12), median f0 or register, cents offset, harmonic centroid ratio.
   - F4: DC, hum presence/level/phase (only if a hum peak exists), int16 histogram stats, high-band residual std and kurtosis.
   - F5: RT proxy (weak).
2. **Scan:** an epidemic two-sided contrast with prefix sums over a 0.1 s grid. Length 1.5-12 s. Margins of 0.3 s at the file ends.
3. **Per-family null calibration:** block or circular-shift surrogates, B ≥ 20. Use the deterministic seed `np.random.default_rng(0)` so output is reproducible.
4. **Combination:** `max_f Z_f + 0.5·Σ_{others} max(Z_f, 0)`. Report the argmax.
5. **Refinement:** single change-point CUSUM within ±1 s on the top features, then snap to an RMS dip within ±0.3 s if one exists.
6. **Guards:**
   - If the best interval is longer than about 12 s, or its two-sided contrast is one-sided (inside matches one outer side), fall back to the second-best candidate.
   - Always write a row. A fallback guess must still be a plausible 6 s window, never empty.
7. **Simulator test matrix.** Every family should be tested alone against the "nothing else differs" condition, including the null case where the insert matches in register and mode:
   - (a) sub-bass or high-pass mismatch only
   - (b) noise floor ±6 dB or different colour only
   - (c) RT60 0.3 vs 0.8 s only
   - (d) hum 50 vs 60 Hz, or a hum phase jump only
   - (e) tuning offset ±10-20 cents only
   - (f) different mode or pitch set only
   - (g) DC offset only
   - (h) MP3 round-trip of the insert only
   - (i) a band-limit at 8 kHz on the insert only

---

## 7. References (URLs)

**Classical splice forensics**

- Pan, Zhang, Lyu, "Detecting splicing in digital audios using local noise level estimation", ICASSP 2012: https://researchconnect.buffalo.edu/en/publications/detecting-splicing-in-digital-audios-using-local-noise-level-esti/ (PDF: https://cse.buffalo.edu/~siweilyu/papers/icassp12.pdf)
- Lyu, Pan, Zhang, "Exposing Region Splicing Forgeries with Blind Local Noise Estimation", IJCV 2014 (kurtosis noise estimator): https://cse.buffalo.edu/~siweilyu/papers/ijcv14.pdf
- Meng, Li, Tian, "Detecting Audio Splicing Forgery Algorithm Based On Local Noise Level Estimation": https://bohrium.dp.tech/paper/arxiv/5c5ec9a9e1cd8e525f69d5bc
- Zhao, Chen, Wang, Malik, "Audio Splicing Detection and Localization Using Environmental Signature", 2014: https://arxiv.org/abs/1411.7084 (HTML: https://ar5iv.labs.arxiv.org/html/1411.7084)
- Capoferri et al., "Speech Audio Splicing Detection and Localization Exploiting Reverberation Cues", WIFS 2020: https://re.public.polimi.it/handle/11311/1169879
- Leonzio, Cuccovillo et al., audio device splicing (TIFS): https://re.public.polimi.it/bitstream/11311/1246218/1/TIFS_Audio_Device_Splicing-11.pdf
- Moussa et al., "Towards Unconstrained Audio Splicing Detection and Localization with Neural Networks", 2022: https://arxiv.org/abs/2207.14682
- Negroni, Salvi, Bestagini, Tubaro, "Analyzing the Impact of Splicing Artifacts in Partially Fake Speech Signals", ASVspoof5 workshop 2024: https://arxiv.org/abs/2408.13784
- SWGDE Best Practices for Digital Audio Authentication v1.3 (2018): https://www.swgde.org/wp-content/uploads/2023/11/2018-09-20-SWGDE-Best-Practices-for-Digital-Aud.pdf
- Grigoras & Smith, "Quantization Level Analysis for Forensic Media Authentication", AES 54th conf. 2014: https://www.aes.org/e-lib/browse.cfm?elib=17320
- DC offset variability in small recorders, JAES 2013: https://www.aes.org/e-lib/browse.cfm?elib=16834

**ENF**

- Rodríguez, Apolinário, Biscainho, "Audio Authenticity: Detecting ENF Discontinuity With High Precision Phase Analysis", TIFS 2010: https://dblp.org/rec/journals/tifs/RodriguezAB10
- ENF higher harmonics discontinuity, EUSIPCO 2013: https://www.eurasip.org/Proceedings/Eusipco/Eusipco2013/papers/1569728299.pdf
- 1D-CNN audio tampering detection using ENF, Sci. Rep. 2024: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11099188/
- ENF spatio-temporal features for tampering detection, 2022: https://arxiv.org/abs/2208.11920

**Codec and resampling**

- Bianchi et al., double MP3 compression detection and localization, EURASIP JIS 2014: https://link.springer.com/10.1186/1687-417X-2014-10
- Bianchi et al., IH&MMSec 2013: https://iris.polito.it/bitstream/11583/2508475/2/bianchi_IHMMSEC13_OA.pdf
- Audio forgery and frame-offset overview (Archives of Acoustics): https://journals.pan.pl//Content/101430/PDF/07_paper.pdf
- Hou et al., resampling detection via spectral second-derivative peaks, 2014: https://www.journal.shu.edu.cn/CN/abstract/abstract5816.shtml
- Band-partitioning spectral smoothness for interpolation and stitching: https://www.jas.shu.edu.cn/EN/Y2010/V28/I2/142
- Speech resampling detection with pyramid feature attention, Appl. Sci. 2024: https://doaj.org/article/4e19559d44b3466697002c97dbfd609c
- Anti-forensics of speech resampling: https://www.bohrium.com/paper-details/antiforensics-of-speech-resampling-using-dual-path-strategy/812512522987896833-2861

**Reverb and noise estimation**

- Ratnam et al., blind RT estimation (ML), JASA 2003: https://www.ee.columbia.edu/~dpwe/papers/Ratnam03-reverb.pdf
- Löllmann, Brendel, Kellermann, closed-form ML RT estimator, EUSIPCO 2018: https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570437986.pdf
- Kendrick et al., blind estimation of room acoustic parameters from speech and music: https://salford-repository.worktribe.com/output/1452157/blind-estimation-of-room-acoustic-parameters-from-speech-and-music-signals
- Martin, "Noise PSD Estimation Based on Optimal Smoothing and Minimum Statistics", IEEE TSAP 2001: https://dblp.org/rec/journals/taslp/Martin01

**Copy-move**

- Local feature tensors on spectrograms: https://arxiv.org/abs/2302.07584
- Cochleagram plus SSIM, IEEE Access 2024: https://doaj.org/article/332fdec1fe36477cb36956afc35a5105
- Pitch-similarity copy-move (Yan, Yang, Huang, ICASSP 2015): https://ieeexplore.ieee.org/document/7178277

**Change points and segmentation**

- Truong, Oudre, Vayatis, selective review of offline change-point detection (`ruptures`), Signal Processing 2020: https://arxiv.org/abs/1801.00718
- Yao, epidemic alternatives: https://www.bohrium.com/paper-details/tests-for-change-points-with-epidemic-alternatives/812030156678889472-861
- Multiple epidemic change points (aPELT): https://arxiv.org/abs/1907.06810
- `sac` R package: https://packages.oit.ncsu.edu/cran/web/packages/sac/sac.pdf
- Foote / Cooper novelty and self-similarity: https://core.ac.uk/download/28906793.pdf
- Müller & Zalkow ISMIR tutorial (structure analysis): https://www.audiolabs-erlangen.de/content/resources/MIR/00_2019_TutorialFMP_ISMIR/2019_MuellerZalkow_ISMIR-Tutorial_AudioStruct.pdf

**Partial-fake localization, 2022-2026**

- PartialSpoof, TASLP 2023: https://arxiv.org/abs/2204.05177 (data: Zenodo 5766198)
- Cai et al., "Waveform Boundary Detection for Partially Spoofed Audio", 2022: https://arxiv.org/abs/2211.00226
- TDL, embedding-based temporal deepfake location, 2023: https://arxiv.org/abs/2309.03036
- CFPRF, coarse-to-fine proposal refinement, 2024: https://arxiv.org/abs/2407.16554
- Boundary-aware attention localization, 2024: https://arxiv.org/abs/2407.21611
- LlamaPartialSpoof, 2024/25: https://arxiv.org/abs/2409.14743
- Half-Truth (HAD), Interspeech 2021, Yi et al. (cited via the above)
- Luong et al., "Robust Localization of Partially Fake Speech: Metrics, Models, and OOD Evaluation", 2025: https://arxiv.org/abs/2507.03468
- He et al., "Manipulated Regions Localization for Partially Deepfake Audio: A Survey", 2025: https://arxiv.org/abs/2506.14396
- Unsupervised domain adaptation for locating manipulated regions: https://arxiv.org/abs/2407.08239
- SAL, "Localizing Speech Deepfakes Beyond Transitions via Segment-Aware Learning", 2026: https://arxiv.org/abs/2601.21925
- TRACE, training-free embedding dynamics, 2026: https://arxiv.org/abs/2604.01083
- Split-and-conquer boundary-then-segment, 2026: https://arxiv.org/html/2604.02913v1
- NE-PADD, APSIPA 2025: https://webdev.apsipa.org/proceedings/2025/papers/APSIPA2025_P126.pdf

**Music deepfake detection**

- Segment Transformer, 2025: https://arxiv.org/abs/2509.08283
- Melody or Machine, 2025: https://arxiv.org/abs/2512.00621
- CLAM, NeurIPS 2025: https://neurips.cc/virtual/2025/123780
- SONICS: https://liner.com/review/sonics-synthetic-or-not-identifying-counterfeit-songs
- ArtifactNet / OOD music detection: https://arxiv.org/abs/2604.16254

**Audio LLMs and agents**

- PELM, 2026: https://arxiv.org/abs/2601.21463
- ThinkOmni, 2026: https://arxiv.org/abs/2607.26553 (code: https://github.com/Beyond0814/ThinkOmni)
- SDD-APALLM: https://arxiv.org/abs/2601.23066
- DFALLM: https://arxiv.org/abs/2512.08403
- ForenAgent (image-forensics agent) topic page: https://www.emergentmind.com/topics/forenagent

**Caveat on sources**

- Several numbers come from abstracts or search snippets: TRACE, SAL, ThinkOmni README, ArtifactNet.
- The full texts of Pan 2012, Capoferri 2020 and Grigoras 2014 returned HTTP 403 or sit behind a paywall. Their method descriptions come from abstracts and citing papers.
- The kurtosis-estimator regression form in 4.3 is my derivation from the published model `κ̃ = κ·(1 − σ²/σ̃²)²`. Check it against Lyu et al. 2014 before relying on constants.
