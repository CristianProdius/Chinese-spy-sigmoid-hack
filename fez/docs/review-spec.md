# Review: spec compliance and crash safety of main_under_review.py

Verdict: **no defects for a test file shaped like train-input.csv.** Every spec line holds on Python 3.10.21, 3.11.16 and 3.12.3.
The only crash paths I could trigger need malformed input that the task statement rules out (listed under hardening below).

Scripts and scratch dirs: `wf2/rs/` (check_parse.py, cross.py, edge.py, weird.py, weird2.py, trap/, huge/).
Shorthand: `W=.../fez/wf2/rs`, `D=.../fez`, `P10/P11/P12` = the uv 3.10, uv 3.11 and /usr/bin/python3.12 interpreters.

## Spec, line by line

| Spec line | Result | Evidence |
|---|---|---|
| Reads `test-input.csv` by bare filename from the cwd | OK | `INPUT = "test-input.csv"`, opened relative to the cwd; FileNotFoundError when it is missing (trap/missing) |
| Writes `routing_log.csv` there, header `request_id,model` | OK | edge.py checks header == `["request_id","model"]` in every case; UTF-8, LF, no BOM, no CR |
| One row per input row, in input order | OK | check_parse.py asserts output ids == input ids in order (400/400); edge.py does the same for every case, including 10 duplicated ids (410 rows out) |
| Only `cheap` / `expensive` | OK | edge.py: no other values in any case |
| Cost <= 20*N (10,000 at N=500) | OK, proven | `max_expensive = 19N//24`, so cost = N + 24E <= 20N. Sweep over route() for N = 0..1200, 4999, 5000 and 10007 with junk prompts mixed in: max(cost - 20N) = 0. N=500 gives E=395, cost 9980 |
| Standard library only, offline | OK | imports are only `csv, math, re, sys`; nothing touches socket, urllib, http, subprocess or os |
| Python 3.10 / 3.11 / 3.12 | OK | train run: identical md5 `ef9f2afe…` on all three; all 19 edge.py cases pass on all three |
| Fast | OK | 400 rows 0.08-0.14 s, about 15 MB. 200,000 rows: 12.9 s and 130 MB on a box at load 337 (linear) |
| Never crashes on prompt content | OK | `score()` wraps parse+estimate in `except Exception` and falls back to keyword family, then UNKNOWN; neither fallback can raise on a str |

## Parser accuracy
- Train: parse() reproduces `reference_answer` on **400/400** prompts; estimate() returns probabilities in [0,1] for all 400 with no fallback (`python3 -I $W/check_parse.py $W/base/main.py $D/train-input.csv $D/train-answers.csv $W/base/routing_log.csv`).
- Synthetic: **12,779/12,779** synth1, synth2 and grid prompts parse to the same answer as solver.py and none hits the fallback (`python3 -I $W/cross.py $W/base/main.py $D/solver.py $D/synth1.csv $D/synth2.csv $D/grid.csv`).

## Input-format edge cases (all pass on 3.10, 3.11 and 3.12; `python3 -I $W/edge.py $W/base/main.py $P10 $P11 $P12`)
BOM, CRLF, BOM+CRLF, quoted multi-line prompts (routing identical to the plain run), extra columns, swapped column order,
duplicate ids, blank lines, no trailing newline, non-ASCII (accents, Arabic, emoji), 0, 1, 2 and 500 rows, empty prompts,
garbage prompts.

## Unseen wording and out-of-range numbers (`weird.py`, `weird2.py`): no crash
3 or 5 souks, 1 souk, unknown souk names, fee with 3 or 5 souks and a crate-count mismatch, walks with 1, 2 or 5 edges,
unreachable or missing destination, duplicate edges, 1 cart, 0 carts, 0 dirham, a 20-digit cart count, 0 hours, a 30-hour
shift, `99:99`, `7 am`, 0 crates, 1 apprentice, a 6-item board, an item missing from the board, off-topic and empty prompts,
2,000-souk, 3,000-item and 500-edge prompts (worst case 0.05 s). Each either parses or falls back to a family-level or
UNKNOWN estimate.
Note: `Which souk took the most money?` (wording not in train) fails the `\bmost\?` regex and parses as take_least. That
only shifts the gain estimate. The real template always ends `most?` / `least?`.

## Hardening only: reproduced, but outside the spec's input contract
The task statement says test-input.csv has the same columns as train. Train is pure ASCII with LF line endings, no BOM and
the header `request_id,prompt`, and the organiser's run_guides.py reads it as utf-8-sig. Each case below needs input that
breaks that contract. Each fails as a crash or an empty log (= FAIL). Repros are in `$W/trap/<case>/`; run `$P -I main.py` there.
1. Any byte that is not valid UTF-8 (latin-1 `\xe7`, UTF-16) raises UnicodeDecodeError on all versions. Fix: `errors="replace"` on open.
2. A NUL byte in a field raises `_csv.Error: line contains NUL` on **3.10 only**; 3.11 and 3.12 pass.
3. A field over 131,072 chars raises `_csv.Error: field larger than field limit`. Fix: `csv.field_size_limit(10**9)`.
4. A header with different case (`Request_ID,Prompt`), no header, or a tab or `;` delimiter writes a header-only log with
   0 rows (rc 0). A header of `request_id, prompt` (with a space) keeps the ids but blanks every prompt, so routing falls back to input order.
5. A row with an empty request_id is dropped from the log. Whitespace around an id is stripped in the output.
None of these is likely on the real file. Items 1 and 3 are one-line fixes if you want belt and braces.
