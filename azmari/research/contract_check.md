# Contract check of SP/wf2/final/main.py (md5 528c0c1b…)

Verdict: on the train format (22.05 kHz mono 16-bit, about 56 s) it meets the contract and passes train:
14.943,20.940 against the truth 14.960,20.965. It is deterministic. It writes no extra files and runs in
about 4-5 s of CPU with 400 MB peak. Four bugs turned up on odd inputs: one crash with no output (bug 1),
one wrong answer on padded audio (bug 2) and two edge cases. All four are fixed in `main_fixed.py`,
whose lines 1-649 (the detector) are byte-identical to main.py.

## How it was run
- System `python3` (3.12.3) has no numpy, so the runs use PY (Python 3.14, numpy 2.5.4, scipy 1.18.1). They were
  repeated on two older stacks: `venv39` (Python 3.9, numpy 1.21.6, scipy 1.7.3) and `venv312` (Python 3.12,
  numpy 1.26.4, scipy 1.11.4).
- Each file ran in a fresh dir that held only `main.py` and `test-1-input.wav`, as
  `python main.py test-1-input.wav`, with the thread env vars unset and `/usr/bin/time -v`.
- Inputs: 38 WAVs made from the train file by `tools/gen_inputs.py` (truth in `inputs/truth.csv`).
  Harness: `tools/run_contract.py`. Logs: `run/all.txt` (main.py), `run/old39.txt` (main.py on the old
  stack), `run/fixed.txt` and `run/fixed39.txt` (main_fixed.py).

## Results for main.py
- CSV: the bytes are `start_s,end_s\r\n14.943,20.940\r\n`. The CRLF endings come from the csv module and match
  `train-output.csv` byte for byte, so they are fine. Each run writes one row with start < end, and the end
  stays inside the file's duration.
- Determinism: the md5 is the same over 3 runs. The output is the same with 1, 2 (default) or 8 BLAS threads,
  and the same on numpy 1.21/scipy 1.7.3 and on numpy 1.26/scipy 1.11.
- These inputs all give a valid row that hits the truth within 1.5 s:
  - stereo, and stereo with different L/R levels
  - 8, 16, 44.1, 48 and 96 kHz
  - u8, 24-bit, 32-bit int, float32 and float64
  - WAVEX 24-bit stereo at 48 kHz
  - a LIST chunk before or after the data
  - bext, junk, fact and id3 chunks
  - a RIFF size of 0xFFFFFFFF, and a truncated data chunk
  - DC offset +3000 LSB, x40 clipping, -40 dB level, and one NaN sample
  - silence padding on both ends (an edge moved 0.2 s but still hit)
  - 180 s at 22.05 kHz, and 180 s at 48 kHz stereo 24-bit
- The no-splice file, the all-zero file and the 0.2-5 s files each write a valid row.
- Runtime and memory. The box sat at load average 260-470 during the sweeps, which inflates the CPU times.
  An idle profile of the 180 s file took 16 s.

  | input | CPU | peak RSS |
  |---|---|---|
  | train format | 4.1-5.3 s | 400 MB |
  | 44.1 kHz | 8 s | 670 MB |
  | 48 kHz | 10-15 s | 1.1 GB |
  | 96 kHz | 19 s | 2.0 GB |
  | 180 s at 22.05 kHz | 47 s | 1.15 GB |
  | 180 s at 48 kHz, stereo, 24-bit | 116 s | **3.2 GB** |

## Bugs (each repro: `python main.py test-1-input.wav` in a fresh dir; the inputs are in `inputs/`)
1. **A WAV whose RIFF size is 0 crashes the run with no output.** Repro: `inputs/riff_size_zero.wav`, which is
   the train file with the RIFF size field set to 0, as streaming writers leave it. scipy raises
   `UnboundLocalError: ... 'fs'`. `load_wav` sits outside the try block in `main()`, so the run exits 1 and
   writes no detection.csv. This is the same on scipy 1.7.3.
2. **Trailing digital silence gets picked as the splice.** Repro: `inputs/silpad_end20.wav`, which is train
   plus 20 s of zeros at the end. main.py outputs `57.824,72.817` against the truth 14.96-20.965, a miss. Any long
   stretch of zero samples at either end beats the real splice.
3. **An empty or one-sample WAV writes `0.000,0.000`**, so start == end. Repro: `inputs/empty.wav` and
   `inputs/one_sample.wav`. This is cosmetic, because no valid answer exists for such a file.
4. **A kill leaves no file.** If the process is killed (OOM killer, a grader timeout) there is no
   detection.csv. Repro: `timeout -s KILL 2.5 python main.py test-1-input.wav` on train gives no file. The run
   only writes at the very end.

## Fixes in main_fixed.py (md5 76a1a9c3…, only `main()` and new helpers after line 649)
- `_read_riff_tolerant`: when scipy fails, a fallback reader parses the RIFF chunks itself. It reads data to
  EOF when the data size is 0, 0xFFFFFFFF or past EOF, and handles PCM 8/16/24/32, float 32/64, WAVEX and RIFX.
  If both readers fail, it still writes a row (the middle of a duration guessed from file size). Its samples
  match scipy's on all 37 files scipy can read (parity check in the transcript).
- A provisional middle row is written right after loading, then overwritten by the real answer. This fixes
  bug 4: the kill repro now leaves `24.922,30.922`.
- `_edge_silence` drops leading and trailing runs of at least 1 s with peaks ≤ 2.5 LSB (in 50 ms blocks)
  before `detect()`, then adds the offset back. It is skipped if under 5 s would remain.
- The fallback always gives start < end (`0.000,0.001` for files under 2 ms).

Verification of the fixes:
- Every input not listed below gives byte-identical output to main.py. That includes train
  (14.943,20.940) and every hi-res, long and odd-chunk case.
- These changed:
  - riff_size_zero: crash → `14.943,20.940` (HIT)
  - silpad_end20: `57.824,72.817` (miss) → `14.943,20.940` (HIT)
  - silpad10 and ditherpad10: edges moved from 24.739/30.986 to 24.939/30.936. Both still HIT, now closer.
  - empty and one_sample: `0.000,0.001`
- The edge trim fires on none of the 72 SIM1 files or on train, and the loader path is unchanged. So the SIM1
  and SIM2 scores are unchanged by construction.
- The same results hold on numpy 1.21/scipy 1.7.3.
- Harness note: `run/fixed.txt` shows a FAIL "outside [0,0.000]" for riff_size_zero. That is my harness:
  soundfile also reads that file as 0 s. The real duration is 55.845 s, and the row is valid.

## Not fixed (risks, not contract bugs)
- **10 s files miss.** short10 gives `1.349,8.896` against the truth 2.96-8.965, a start error of 1.61 s. The
  far-reference musical families need notes more than 10 s apart, so they have nothing to work with on a 10 s
  file. The row is still valid.
- **Memory grows with sample rate.** nfft is 16384 at 48 kHz and 32768 at 96 kHz, and the frame matrix plus
  its int64 index array is T×nfft. A 3-minute 48 kHz file peaks at 3.2 GB. This only matters if a hidden
  file is long and hi-res and the grader has under about 4 GB.
- **Harmless stderr warnings**: WavFileWarning on unknown chunks, and "Mean of empty slice" on short files.
- A middle-of-file silent gap (not at the edges) would still attract the detector. That was not tested.
