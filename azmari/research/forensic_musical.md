# Forensic musical analysis of train-input.wav (known splice 14.960–20.965 s)

Code, plots and tables are in `forensic_musical/`. Scripts `m01`–`m24` run in order, each taking `<wav> <outdir>`. Key files:
- `notes_train.csv`: every note with onset, duration in eighths, MIDI, cents, f0, vibrato and h1..h12 in dB.
- `harmonic_tables_dB.json`: median h1..h16 profile per pitch, for the original and the splice separately.
- Plots: `spec_*.png`, `cue_boundaries.png`, `reverb_tails.png`, `waveshape.png`, `lf_wave_splice.png`, `transitions.png`, `vibrato_per_note.png`, `env_longnotes.png`.

## 1. Headline findings

1. **The original take is a deterministic per-note renderer.** The same pitch and duration give an almost identical waveform: aligned repeats correlate at r = 0.987–0.9998, and the residual is −16 to −34 dB. The harmonic profile per pitch matches to about ±1 dB everywhere in the file.
2. **The splice is a cut from a separate, continuous render**, in a different register, key and timbre, with its own reverb, and it went through a strong **asymmetric nonlinearity**. That nonlinearity is the source of the 20–200 Hz content: intermodulation (IM) difference tones between each note and the reverb tail of the note before it.
3. **The reverb tail is cut at both seams, and orphan tails appear.** At every real transition the previous note's partials persist at −15 to −25 dB and decay at about −20 dB/s. At the start seam the original E4 tail drops to −51 dB at once, and an A4 tail from the splice source (a note that is not in the file) sits under the first inserted note. After the end seam an E4 tail appears that belongs to a removed original note.
4. **Rhythm grid.** One eighth note is 0.300 s (100 BPM in quarters). The grid phase is +0.048 s before the splice, while the splice's own grid starts at 14.96, and +0.195 s after the splice. The original's grid therefore shifts by 0.15 s (half an eighth) across the splice. Either the removed and inserted lengths differ by ±0.15 s, or the original changed phase inside the removed part. This file cannot tell which.

## 2. Note list (tempo grid: eighth = 0.300 s; durations in eighths)

`*` marks the splice. Full detail is in `notes_train.csv`.

```
69:2 67:2 64:2 62:2 64:2 67:2 64:4 62:4 60:2 62:2 64:2 65:2 64:2 62:2 60:9 62:2 65:3 64:4(cut at 14.96)
71:4* 72:3* 76:2* 74:3* 72:2* 71:2* 74:1* 76:1* 74:2*     (= exactly 20 eighths = 6.0 s, starts at 14.96)
65:4 67:6 64:2 62:2 60:10 62:2 60:4 62:4 65:1 64:2 67:4 65:4 62:4 60:4 62:2 60:6 62:3 65:2 67:4 65:2
62:2 60:2 62:1 60:6 62:3 60:2 64:4 62:2 64:2 60:6 62:3 64:1 65:2 67:2 65:2 62:3 60:1.5(file end)
```

**Original melody.**
- Pitch set {60, 62, 64, 65, 67, 69} (C4–A4). That is C-major hexatonic without B, and A4 occurs only as the first note.
- It is a first-order random walk:
  - Steps of ±1 scale degree make up 65%, and ±2 degrees 35%.
  - The largest interval is 4 semitones. The interval counts are −4:1, −3:6, −2:19, −1:3, +1:2, +2:16, +3:5, +4:1.
  - Transitions lean strongly toward C and D: 60→62 nine times, 62→60 ten times.
- Duration counts in eighths are 1:4, 2:28, 3:5, 4:12, 6:4, 9:1, 10:1. Long notes land on C or D.
- **No phrase repeats exactly.** No (pitch, duration) 4-gram repeats, and no pitch 8-gram repeats. Only 5–6-note pitch motifs recur, such as 67-64-62-60-62 and 62-60-62-60-62. So the replaced phrase cannot be predicted from repeats elsewhere, only from statistics. The orphan E4 tail after the end seam suggests the removed phrase ended … E4 → F4, with F4 at 20.895.

**Splice melody.**
- Pitch set {71, 72, 74, 76} (B4, C5, D5, E5). It lies entirely above the original's maximum and includes **pitch class B, which never occurs in the original**.
- It fits the same random-walk style transposed up a fifth (G-A-B-C-D-E). The orphan A4 tail and the 53 Hz IM tone at the splice start show that the source's previous note was A4, which is in that scale.
- Interval sizes and durations (1–4 eighths) look like the original's.
- Onsets fall at 14.96 + 0.3k, with a residual of −7 ± 16 ms.

**Seam intervals.** The melody jumps +7 (E4→B4) and −9 (D5→F4). The original never moves more than 4 semitones.

## 3. Tuning

These values use the h1-only frequency from a zero-padded FFT of each note's core.
- **Original:** C4 +8.1, D4 +8.2, E4 +5.2, F4 +4.4, G4 +3.7 cents against ET with A4 = 440 (the first-note A4 reads −2.5). The offsets are identical on every repeat (±1 c), so this is ET plus a fixed small offset per pitch, not just intonation.
- **Splice:** B4 +6, C5 +13.5, D5 +13 (spread +7 to +15), E5 +3 (spread −3 to +8). The tuning is less stable, and it is useless as a cue because the ranges overlap.

## 4. Timbre: harmonic profile in dB relative to h1 (median per pitch)

| | h2 | h3 | h4 | h5 | h6 | h7 | h8 | h9 | h10 | h11 | h12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| orig C4 | −7 | −18 | −11 | −22 | −16 | −24 | −29 | −35 | −40 | −36 | −49 |
| orig D4 | −3 | −16 | −11 | −19 | −15 | −20 | −23 | −32 | −39 | −35 | −44 |
| orig E4 | +1 | −6 | −4 | −9 | −17 | −28 | −39 | −28 | −31 | −39 | −33 |
| orig F4 | 0 | −7 | −5 | −8 | −19 | −30 | −40 | −28 | −32 | −41 | −35 |
| orig G4 | −4 | −9 | −11 | −17 | −36 | −35 | −32 | −43 | −41 | −51 | −56 |
| splice B4 | −8 | −13 | −33 | −27 | −35 | −39 | −48 | −55 | −56 | −58 | −69 |
| splice C5 | −16 | −1 | −33 | −27 | −49 | −35 | −53 | −52 | −57 | −53 | −60 |
| splice D5 | −17 | −4 | −33 | −27 | −51 | −38 | −55 | −53 | −57 | −53 | −61 |
| splice E5 | −7 | −24 | −31 | −30 | −45 | −42 | −50 | −50 | −57 | −58 | −60 |

**Original.** The profile is rich and dominated by even harmonics: odd/even energy is −9 dB and the tilt is −3.9 dB per harmonic. The pattern is fixed per pitch and looks like a body-resonance filter. E4 and F4 share a notch near 2.65 kHz. Harmonics are visible up to 10 kHz or more.

**Splice.** The profile is steep and sparse: h4 and above sit at −27 dB or lower, and the tilt is −5.4 dB per harmonic. C5 and D5 are odd-dominant (h3 at about −1 to −4, h2 at −16), while B4 and E5 show a pulse-like waveform with a flat negative half. The positive/negative peak ratio is 1.7–2.0 inside, against 1.0–1.3 in the original, and skewness is +0.4 to +1.06 against +0.27 to +0.5. Median odd/even is **+12 dB**, about 21 dB away from the original.

**Inharmonicity.** Neither part shows any measurable inharmonicity (|B| < 5e-5): the partials are exactly harmonic in both.

## 5. Vibrato and envelopes

**Original vibrato.** Notes of 0.9 s or longer carry a 4.0–4.9 Hz vibrato at ±8–10 cents peak, with AM of 3–5 dB at the same rate. Short notes show a single scoop or bump of about 10 cents. The phase is locked to the onset, so the contour is identical for repeats of the same pitch and duration (see `vibrato_per_note.png`).

**Original envelope.** Playing is legato:
- Attack (−10 → 0 dB) has a median of about 110 ms, and release about 70 ms.
- At a crossfade the broadband RMS dips by about −16 dB, with a −6 dB width of about 130 ms.
- **Long notes are re-articulated on every beat (0.6 s).** The RMS dips by 8 dB or more on the grid, at 25.68, 26.28, 26.88 and 27.46 s, which looks like bow changes (`env_longnotes.png`).

**Splice vibrato.** It is weak and irregular, 5–8 c with no steady 4–5 Hz rate, and AM is 2 dB or less.

**Splice envelope.** Playing is detached or tongued. Attack is about 45 ms and release about 48 ms. The dip is about −12 dB with a −6 dB width of about 56 ms, and the note often decays almost to silence before the next attack.

## 6. The 20–200 Hz content inside the splice: intermodulation, not a drone or a low note

Inside the splice, each note carries a tone at |f_cur − f_prev|, where f_prev is the previous note's reverb tail. The measured matches:

| Note | f_cur − f_prev (Hz) | Measured tone (Hz) |
|---|---|---|
| C5 after B4 | 31.7 | 31.2 |
| D5 after E5 | 70.2 | 71.3 |
| C5 after D5 | 64.6 | 63.4, plus 130.6 (2×) |
| B4 after C5 | 32.2 | 29.5–33 |
| D5 after B4 | 95.3 | 95.3–95.6 |
| E5 after D5 | 67.5 | 68.6 |
| first B4 | ≈53 | 50–55 (implies a 442 Hz A4 tail) |

Each note also carries 2f1−f2 (for example 558 Hz under C5) and f1+f2 (1023 Hz).

- The difference tone sits about 6–9 dB below the tail component itself, independent of tail level. That gives a quadratic coefficient a2 ≈ 20–40 (full-scale units) inside, against an upper bound below 3 outside (`m19_im.py`).
- In practice the 20–150 Hz band runs at −65 to −80 dBFS inside against −92 to −95 dBFS outside, which is **+20 to +30 dB**. It is not constant: it dips to about −88 dB during the long first B4 (15.6–16.0 s).
- The waveform shape (flat negative half) and the IM levels match a heavily driven asymmetric saturation applied to the peak-normalised source before scaling. A biased tanh with drive 3–4 and bias about 0.4 comes within about 3 dB (`m20_nlfit.py`). The exact curve is not identified.
- **DC is about 0.13 LSB inside against +1.4 to +2.8 LSB outside**, so the source was mean-removed after the saturation.

## 7. The "vertical broadband lines"

These are onset transients of the splice notes. Mostly they are **low-frequency thumps**: 20–200 Hz energy at a splice onset runs +13 dB over the following sustain, against +1.3 dB at original onsets, followed by ringing at the new IM difference frequency. They also have a weak broadband part, about 3 dB stronger than at original onsets and up to +7 dB on a few.

They are the hard, detached attacks after they pass through the nonlinearity. The original's soft legato crossfades produce no such lines. The lines show clearly in the spectrogram partly because the splice has little high-harmonic energy to mask them.

## 8. Reverb, noise, level

**Reverb.** Both parts are reverberant. In the original, the outgoing partial sits at −15 to −25 dB 0.15 s after the next onset and then decays at −18 to −25 dB/s, which implies RT60 ≈ 2.5–3 s with the wet signal at roughly −15 dB against the direct. Transitions inside the splice show similar slopes, about −16 to −17 dB/s. At the seams the outgoing partial falls to **−51 to −66 dB within 50 ms** (`reverb_tails.png`).

**Additive noise.**
- It is stationary and the same inside and out: the robust 2–10 kHz floor is −112.8 dB inside against −111.5 outside, and the 8–11 kHz band is unchanged.
- Total level is about −74 dBFS RMS, about 37 dB below the −37.5 dBFS signal. That is consistent with the residual between repeated notes.
- The PSD is about −108 to −112 dB/Hz and flat up to about 3 kHz, then falls about 8.5 dB per octave to about −138 dB/Hz at 10–11 kHz, which is close to quantisation level.
- Because it is the same across the seams, it was probably added after the splice.

**Level.** RMS is −37.5 dBFS in both parts (per-note h1 ranges from −35 to −44 dBFS), and peaks are about 1300–1400 LSB.

## 9. Recipe for a simulator (statistically similar file)

1. **Grid.** 22050 Hz, mono, 16-bit, 55.8 s, eighth note = 0.3 s, global grid offset U(0, 0.3).
2. **Original melody.** A random walk on the scale [60, 62, 64, 65, 67, 69]:
   - P(±1 degree) = 0.65, P(±2 degrees) = 0.35.
   - Weight the walk toward 60/62.
   - Durations in eighths with probabilities {1:.07, 2:.50, 3:.09, 4:.22, 6:.07, 9–10:.04}, using the long values mainly on 60/62.
3. **Original renderer.** Additive synthesis, harmonics 1..40 below Nyquist, from the fixed per-pitch tables in `harmonic_tables_dB.json` (anything with a −4 dB/harmonic tilt, strong even harmonics and a fixed body EQ will do). Then:
   - ET tuning with a fixed per-pitch offset of +3 to +8 c.
   - Onset-locked vibrato at 4–5 Hz, ±9 c, with coupled AM of 3–5 dB.
   - Legato crossfades: attack 110 ms, release 70 ms, overlap so RMS dips about −16 dB over about 130 ms.
   - Re-articulate long notes every 0.6 s with an 8 dB dip.
   - Make it deterministic per (pitch, duration).
   - Add reverb with RT60 2.5–3 s, wet about −15 dB, and add DC of about +2 LSB.
4. **Splice source.** A separate continuous render (with notes before and after the excerpt) of a walk on a different scale, transposed +7 (pitches 67–76), using the same duration grid. Then:
   - Odd-dominant or pulse-like steep timbre (tables above).
   - Detached envelopes: attack about 45 ms, release about 48 ms, dip about −12 dB.
   - Weak vibrato of 5 c or less.
   - Its own reverb, same RT60.
   - Normalise to peak 1, then apply asymmetric saturation, for example `y = tanh(3.5(u + 0.4)) − tanh(1.4)`. Calibrate it so that f1 − f2 lands about 7 dB below the previous-note tail.
   - Remove the mean and scale to the original's RMS.
5. **Splice.** Pick a start and a length of about 6.0 s (20 eighths), and take the excerpt from the source starting at one of its note onsets. Replace `orig[start : start + L ± 0.15 s]` so the grid shifts by half an eighth after the splice. Use a short crossfade at each seam: 20–30 ms at the start and about 60 ms at the end. Do not carry over the original's reverb tails.
6. **Post.** Add stationary Gaussian noise at −74 dBFS RMS, flat to 3 kHz and −8.5 dB per octave above, then quantise to int16.

## 10. Cues that separate the splice, with boundary sharpness

| Cue | Inside vs outside | Measured boundary (true 14.960 / 20.965) | Sharpness |
|---|---|---|---|
| Register (pyin MIDI) | 71–76 vs 60–69 | 14.976 / 20.883 | ≤ 20 ms (one frame). Note-quantised, so it hits the seam only because the splice starts and ends on notes |
| Pitch class B present | 2 of 9 notes vs never | first B at 14.96, last B ends 19.74 | note-level. Alone it puts the end about 1.2 s early |
| Melodic leap > 4 st | +7, −9 at the seams only | 14.96 / 20.90 | one transition, about ±30 ms |
| LF 20–150 Hz (IM products) | −65..−80 vs −92..−95 dBFS | jump at 14.96, drop at 20.90–20.97 | 20–70 ms at the seams; internal dips to −88 dB at 15.6–16.0 |
| Harmonic tilt / odd-even | −5.4 vs −3.9 dB/harm; +12 vs −9 dB | 14.976 / 20.902 | 20 ms at the seams, but varies note to note inside (E5 reads "bright" in band ratios) |
| Per-pitch timbre table mismatch | n/a (pitches differ here) | — | note-level. **Key cue if a hidden test keeps the register**: the original repeats the same profile for the same pitch |
| Waveform asymmetry (skew, +/− peak) | 0.4–1.06 vs 0.27–0.5 | 15.11 / 20.41 | 150–500 ms; weak for C5/D5 |
| Articulation (dip width, attack) | 56 / 45 ms vs 130 / 110 ms | note-level | ±0.3–1.2 s |
| Vibrato regularity | none vs 4–5 Hz ±9 c | only on notes ≥ 0.9 s | about ±1 s |
| Reverb-tail cut-off | out-partial −51..−66 dB vs −15..−25 dB at +0.15 s | exactly at the seams | about ±20–50 ms. **The most physics-based cue: it should survive a same-instrument splice** |
| Orphan tails | A4 under the first splice note; E4 after the end seam | at the seams | ±0.1 s |
| Grid phase | 0.048 / −0.05 / 0.195 s | note-level | ±0.3–0.6 s |
| DC offset | 0.13 vs 1.4–2.8 LSB | needs windows of 1 s or more | ±0.5 s |
| Noise floor / HF floor | same | — | none |

## 11. Implications for the detector and caveats

- On this file almost every family flags 14.96–20.96, so register alone already solves it. For hidden tests, the families that do not depend on register or instrument are worth combining:
  1. Reverb-tail continuity at transitions: a seam is where the previous note's partials vanish within 50 ms instead of decaying at about −20 dB/s.
  2. IM/nonlinearity energy (LF band and 2f1−f2) relative to the previous-note tail.
  3. Inconsistency with the per-pitch timbre table seen elsewhere (the original is deterministic, so a "real" note matches its siblings at r > 0.98).
  4. DC and sub-20 Hz level.
  5. Grid-phase change.
- Unverified: whether the 0.15 s grid shift comes from unequal cut and insert lengths, and the exact saturation curve. The original's reverb is estimated only from partial decay; there is no impulse response.
