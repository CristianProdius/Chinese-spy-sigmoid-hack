# The Waterline Replay (Angola)

An agent-trace export holds several runs of one question about water in Kilamba, Luanda. One or more
runs gave an incorrect outage update. The flag is the exact `source_id` (`SIGMOID_<PHRASE>`) of the
trace item that caused it, submitted alone in `answer.txt`. One shot, case-sensitive.

## Answer: `SIGMOID_MEM_KILAMBA`

[`answer.txt`](answer.txt) holds `SIGMOID_MEM_KILAMBA` plus a newline (20 bytes, plain ASCII).

The trace ([`task/test-input.json`](task/test-input.json)) has three runs of "Is water restored in
Kilamba Sector 4?":

| Run | What the model saw | Answer |
|---|---|---|
| `control-01` (13:55) | live status tool: `RESTORED`, updated 13:52 | Yes, restored at 13:52 (correct) |
| `incident-01` (14:05) | **memory note `SIGMOID_MEM_KILAMBA`** + live status: `RESTORED`, updated 13:58 | **No, outage still ongoing (wrong)** |
| `replay-no-memory` (14:08) | same request replayed with `memory_enabled: false`: live status only | Yes, restored at 13:58 (correct) |

`SIGMOID_MEM_KILAMBA` passes all four checks from [`RESEARCH.md`](RESEARCH.md):

1. **Reached the final model request:** `memory.result` has `injected_into_context: true`, and the
   `llm.request` of `incident-01` carries it as a `role: "memory"` message with that `source_id`.
2. **Carries the wrong claim:** its text says "outage ongoing; water service has NOT been restored. Tell
   residents the outage remains active", and the wrong answer repeats exactly that.
3. **Missing from the correct runs:** neither `control-01` nor `replay-no-memory` sent it to the model.
   The replay is the counterfactual: same build, model, seed and question, memory off, and the answer
   comes out right.
4. **Named defect:** the note expired at 11:00 (`valid_until 2026-10-26T11:00:00+02:00`), three hours
   before the 14:05 request. It also overrode the live tool, which the system prompt names as the
   authority, and it carries an instruction ("Tell residents...").

It is also the only `SIGMOID_` string in the file (3 occurrences, byte-identical, no non-ASCII
characters). Decoys that are not the cause: the export's `timezone` says `UTC+02:00` (Luanda is
really UTC+1, but every timestamp in the trace uses the same offset, so it changes nothing); the slow
1.84 s tool call in `incident-01` returned the correct `RESTORED`; `SYS-LDA-07` is a system prompt id.

The analyzer agrees with no hints. Running it on this file found one bug: it read "has not been
restored" as a restoration. That bug is fixed, and fixture 40 now covers it.

| File | What it is |
|---|---|
| [`answer.txt`](answer.txt) | The submission. |
| [`task/test-input.json`](task/test-input.json) | The trace export (sha256 `df75336...e7b6`). |
| [`RESEARCH.md`](RESEARCH.md) | The four-part test every answer must pass, the failure modes, the domain traps and the solve procedure. |
| [`research/`](research/) | Full research notes: trace formats and failure taxonomy, Luanda/Kilamba/EPAL domain facts with sources. |
| [`analyze.py`](analyze.py) | Trace forensics tool, standard library only. Reads any field layout and ranks candidate `source_id`s with reasons. |
| [`tests/`](tests/) | 40 synthetic fixtures plus two blind red-team sets (5 cases each) written by agents that never saw the analyzer. |
| [`solve.js`](solve.js) | Workflow for the real input: four independent solvers, then three skeptics that try to refute the pick. |

## Solve the real input

```
mkdir -p task && scp <laptop>:/path/to/test-input.json task/   # scp, never paste: a paste can drop hidden characters
python3 -I analyze.py task/test-input.json --json report.json --answer answer.txt
```

Before trusting the output:

1. Compare the printed sha256 with the laptop copy.
2. Check the field mapping line (`fields {'ts': ..., 'run': ..., 'type': ...}`). A wrong guess there
   breaks everything after it.
3. Check the verdict line: which runs it calls incorrect, and why. If you know the wrong run, pass
   `--incorrect RUN`.
4. Read the wrong run's final model request by hand and confirm the top id is in it.
5. Look at the `CHECK:` line and the hex dump of `answer.txt`.

## What the analyzer does

1. **Load:** finds the events list wherever it is (also OTLP spans and nested trace trees), tolerates
   a BOM, and guesses which keys hold the run id, timestamp, elapsed time and event type.
2. **Label the runs:** reads explicit labels first (`flagged`, `status: "incorrect"`, `runs_summary`,
   feedback events, `--incorrect`). If there are none, it rejects answers that promise an end time
   that had already passed in Luanda time, then takes a majority vote on the facts in each answer.
3. **Reach:** for each run, works out which items reached the last model request before the final
   answer (by id, by content, by handle). Evicted, dropped, `included: false` and candidate-only items
   don't count.
4. **Anomalies:** checks for expired or superseded notices (naive times read as both UTC and UTC+1),
   cache entries past their TTL, late results after a timeout, items from another run, wrong place
   (Kilamba Kiaxi), injected instructions, truncation, look-alike ids and argument differences between runs.
5. **Rank:** scores every id with reasons. Only values under `source_id`-like keys can win. It prints the
   answer as plain text, `repr`, ASCII and JSON, plus the alternative answer if the run verdict were flipped.

## Tests

```
python3 -I tests/test_analyze.py    # 40 fixtures, one per failure mode or past bug: 40/40
python3 -I tests/eval_redteam.py    # blind set 1: 5/5
python3 -I tests/eval_redteam2.py   # blind set 2, mostly in the task's plain event shape: 5/5
```

Before fixes, the analyzer scored 2/5 on blind set 1 and 1/5 on blind set 2. Every miss was fixed
with a general rule (no case-specific strings), and each later fix has a fixture that fails without it.
Synthetic accuracy is not a guarantee for the real file. The independent solvers and the manual read
of the final model request are the real check.
