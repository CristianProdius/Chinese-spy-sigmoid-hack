# The Waterline Replay (Angola)

An agent-trace export holds several runs of one question about water in Kilamba, Luanda. One or more
runs gave an incorrect outage update. The flag is the exact `source_id` (`SIGMOID_<PHRASE>`) of the
trace item that caused it, submitted alone in `answer.txt`. One shot, case-sensitive.

**Status:** research and tooling are done. The real `test-input.json` is not in the repo yet, so
`answer.txt` does not exist yet.

| File | What it is |
|---|---|
| [`RESEARCH.md`](RESEARCH.md) | The four-part test every answer must pass, the failure modes, the domain traps and the solve procedure. |
| [`research/`](research/) | Full research notes: trace formats and failure taxonomy, Luanda/Kilamba/EPAL domain facts with sources. |
| [`analyze.py`](analyze.py) | Trace forensics tool, standard library only. Reads any field layout and ranks candidate `source_id`s with reasons. |
| [`tests/`](tests/) | 39 synthetic fixtures plus two blind red-team sets (5 cases each) written by agents that never saw the analyzer. |
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
python3 -I tests/test_analyze.py    # 39 fixtures, one per failure mode or past bug: 39/39
python3 -I tests/eval_redteam.py    # blind set 1: 5/5
python3 -I tests/eval_redteam2.py   # blind set 2, mostly in the task's plain event shape: 5/5
```

Before fixes, the analyzer scored 2/5 on blind set 1 and 1/5 on blind set 2. Every miss was fixed
with a general rule (no case-specific strings), and each later fix has a fixture that fails without it.
Synthetic accuracy is not a guarantee for the real file. The independent solvers and the manual read
of the final model request are the real check.
