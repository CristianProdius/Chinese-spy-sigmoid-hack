# The Azmari's Borrowed Melody (Ethiopia)

Find the few seconds of a recording that were replaced by a phrase from another take.

| File | What it is |
|---|---|
| [`main.py`](main.py) | The submission. `python main.py test-1-input.wav` reads the WAV from the working dir and writes `detection.csv` (`start_s,end_s`). numpy + scipy + stdlib only, about 4 s CPU and 400 MB. |
| [`research/`](research/) | Literature review, forensic analysis of the training file, integration, red-team and contract-check reports. |
| [`tools/`](tools/) | Two synthetic splice generators (`sim1_gen.py`, `sim2_gen.py`) and `eval.py`, which runs `main.py` the way the grader does and scores it at the 1.5 s tolerance. |

Training file: detects `14.943,20.940`, truth `14.960,20.965` (errors 0.02 s).

## What gives the splice away

In the training file the borrowed phrase is a separate render pushed through a different chain:

- asymmetric saturation: intermodulation tones at 20-200 Hz, 20-30 dB above the rest of the file;
- a ~20 Hz high-pass: the DC offset (about +2 LSB elsewhere) drops to zero;
- no room: the reverb tail of the previous note is cut within 50 ms;
- another register and timbre: B4-E5 against C4-A4, and pitch class B appears nowhere else.

The background noise is identical inside and out (added after the splice), and the seams are RMS-matched
20-60 ms crossfades, so listening for a seam finds nothing.

## How the detector works

1. Frame the audio at a 50 ms hop and compute 14 feature families: spectral shape, low-frequency band and DC,
   noise floor, pitch anomaly, pitch height, chroma, dynamics, MFCC timbre, nonlinearity (LF intermodulation,
   waveform asymmetry), DC/sub-20 Hz, high-band noise floor, tuning in cents against same-pitch notes elsewhere,
   and the per-pitch harmonic fingerprint (the host renders each pitch identically; borrowed notes do not match).
2. For every interval of 1.5-15 s, score each family with an epidemic mean-shift statistic (inside vs outside)
   and calibrate it to a robust z over all intervals.
3. Weight each family by its prominence (its peak over its best disjoint peak), so a family with one clear
   anomaly counts and families tracking normal phrase structure drop to zero. Sum and take the argmax. There
   is no position or length prior. When the weights sum below 2.5 (short files, or a splice that is a large
   share of the file, where the stretch on the far side of the splice scores like the splice itself), fall
   back to the sum of squared z over the 8 base families.
4. Never crash: a tolerant RIFF reader, trimming of digital silence padding, and a provisional answer written
   before detection starts.

## Verification

Run end to end with `tools/eval.py`, the way the grader runs it (bare filename, fresh dir):

| Set | Files | This detector | Baseline (checkpoint a637b24) |
|---|---|---|---|
| Training file | 1 | 1 | 1 |
| SIM1: one tell per scenario (register, scale, timbre, noise, hum, band-limit, reverb, other take, mixes) | 72 | 70 | 45 |
| SIM2: the reverse-engineered generator, near-train / one cue weakened / same register, chain-only | 48 | 48 | 36 |
| Red team: fresh seeds, 2 s and 12 s splices, splices near the ends, lower register, other qenet, 30 s and 90 s files | 74 | 70 | 47 |
| Real audio: train resampled (11-48 kHz), cut short, gain, noise, DC, reversed, stereo | 18 | 17 | 18 |
| Real audio: the real splice 0.5-4 s from either end of a 50 s file | 12 | 12 | 12 |
| Real audio: the real splice re-inserted with its tells stripped (no LF, shifted into the host register, reverb added) | 21 | 21 | 21 |
| Real audio: decoys in the host (loud passage, crowd noise, claps, pause, register change) | 20 | 15 | 16 |

Misses:
- scale change with nothing else changed (no family fires);
- single weak cues on short splices, outvoted by normal musical variation;
- a 23 s file cut so the splice ends 2 s before the end;
- decoys: loud crowd noise in the host fools both detectors. A single strong one-family decoy (claps, a
  register change) can also win here, because prominence fusion lets one clear family decide.

The real splice stays easy to find with every tell stripped, because its timbre and articulation differ
from the host's.

The first submission (probably the baseline, the only version on GitHub at the time) failed test-1 and
test-3. So the hidden tests differ from train in ways none of these sets fully capture.

```
python tools/sim2_gen.py                                # writes tools/data/ (git-ignored)
python tools/eval.py main.py --data tools/data
python tools/realaudio/mkdecoy.py                       # writes tools/data/decoy
python tools/eval.py main.py --data tools/data/decoy --no-train --keep-names
```
