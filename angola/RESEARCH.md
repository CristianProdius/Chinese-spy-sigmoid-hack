# The Waterline Replay - research

Task: an agent-trace export (`test-input.json`, ordered `events`) holds several runs of the same
"water in Kilamba" request. At least one run gave an incorrect outage update. Submit the exact
`source_id` (`SIGMOID_<PHRASE>`) of the trace item that caused it. One shot, case-sensitive.

Full notes from the research agents: [`research/failure-taxonomy.md`](research/failure-taxonomy.md)
(trace formats, failure modes, forensic procedure) and [`research/luanda-domain.md`](research/luanda-domain.md)
(Kilamba geography, EPAL water notices, time and date traps, with sources).

## The test every answer must pass

The culprit is the one item that:

1. **reached the final model request** of the wrong run (proven by the request itself, not by "it was
   retrieved"),
2. **carries the wrong claim** the answer repeats (status, times, cause, place),
3. **is missing or different** in the correct runs' final requests, and
4. **has a defect we can name** from its fields (stale, expired, other run, wrong place, injected, ...).

A decoy fails at least one of the four. The flag comes from a `source_id` field, never from a call id,
span id, prompt text or the answer's own citation.

## Failure modes to check (short form)

| # | Mode | What it looks like in the trace |
|---|---|---|
| F1 | Stale cache hit | `cache: hit`, tiny elapsed, `cached_at` older than its TTL or than a newer notice |
| F2 | Late result from a timed-out call | `timeout_ms` exceeded, retry issued, the slow original result still lands in the request |
| F3 | Result from another run | item's `run_id` or call id belongs to a different run |
| F4 | Wrong place | item is about Kilamba Kiaxi (a different municipality), Camama, Talatona, ... |
| F5 | Expired or superseded notice | `valid_until`/`expires_at` before request time (watch UTC vs WAT), `superseded_by` |
| F6 | Out-of-order events | array order and timestamps disagree; an item "from the future" |
| F7 | Truncation / eviction | `dropped`, `evicted`, `included: false`; the correct notice was cut only in the wrong run |
| F8 | Prompt injection | tool text telling the model what to say |
| F9 | Near-duplicate ids | case, Cyrillic look-alikes, zero-width chars, trailing space, `_V2` |
| F10 | Item no tool returned | in the request with no matching tool result in that run (memory, cache prefill, leak) |

## Domain facts that matter

- **Kilamba is not Kilamba Kiaxi.** Cidade do Kilamba is the planned new city in the south (Belas
  municipality before 2024, its own "Município do Kilamba" under Lei 14/24). Kilamba Kiaxi is a
  separate, older municipality. A Kilamba Kiaxi notice answering a Kilamba question is a textbook wrong-entity item.
- **Time zone:** Angola is WAT, UTC+1 all year, no DST. A `valid_until` of `18:00` with no offset is
  probably local time, which is `17:00Z`. Comparing it as UTC keeps an expired notice "valid" for an
  extra hour.
- **Dates:** Angola writes `dd/mm/yyyy`. `03/11` is 3 November, not 11 March.
- **EPAL notices:** use words like corte, interrupção, restrições no abastecimento, paralisação,
  reposição, restabelecimento. Time windows look like `das 08h00 às 18h00`. Often no end time at all.
- The storyline flavor (Fortaleza de São Miguel, semba, kizomba, funge, moamba) is decoration, not a
  clue. It may show up inside decoy id phrases.

## Procedure once the input arrives

1. Copy the file over intact (scp or `getclip`, never a paste: a paste can drop zero-width chars).
   Compare sha256 with the laptop copy.
2. `python3 -I analyze.py task/test-input.json --json report.json`. Check the printed field mapping
   (run id, timestamp, type) first. If it picked the wrong fields, everything after is wrong.
3. Read the wrong run's final model request by hand and list its `source_id`s.
4. Diff against the correct runs, find the item carrying the wrong claim, and name its defect.
5. Rule out every other `SIGMOID_` id with a reason.
6. Run independent solvers (three that don't see the analyzer, one that does) and three skeptics
   that try to refute the pick (`solve.js` workflow).
7. Write `answer.txt` from the id bytes inside the final request (`analyze.py --answer`), check
   `^SIGMOID_[A-Z0-9_]+$` and the hex dump, then push.
