All the must-haves and the other critic items that could change the answer are fixed, with one partial (the confidence gate, below). Both suites pass: `test_analyze.py` is 36/36 (the 12 old fixtures plus 24 new), with all incorrect-run verdicts, the interleaved variants and the CLI checks passing; `eval_redteam.py` is 5/5, with the same lead or bigger on every case. Everything I wrote is inside `waterline/`.

**Must-haves**
- **Run labels and `--incorrect`:**
  - The analyzer now reads each dict as a whole, anywhere in the file: `flagged: true` on a response, `runs_summary` with `outcome: incorrect`, maps like `{"r2": "incorrect"}`, and `is_correct: false`.
  - `--incorrect RUN` (repeatable or comma-separated) overrides the verdict. An unknown run id exits with the list of real run ids.
- **Answer must be a `source_id`:** when any id sits under a `source_id`-like key (`source_id`, `sourceId`, `source.id`, `source-id`, `src`, `sources`), nothing else can rank #1. Ids that never appear under such a key are sorted last and say why.
- **`--answer FILE`:** writes the raw id plus `\n`, reads the file back and prints its bytes in hex.
- **BOM:** the file loads as `utf-8-sig`, and the report prints its sha256 so you can compare it with the laptop copy.
- **Naive item times:** checked as both UTC and Luanda time (UTC+1). The item is flagged expired if either reading has expired.
- **Dropped items:** `context_evicted`-style events, `included/used/selected: false` and `status: dropped/evicted/...` now mean the item didn't reach the model in that run. This applies to content, order and nearest-list matching too.
- **Request lists:** when a model request has both a candidates/retrieved/considered list and a context/included list, only the context/included list counts.
- **Retries:** `model_request_retry` counts as the request the model answered. A tool retry counts as a call, and only the call it names in `retry_of` gets the retried flag.
- **Timeouts, status, cache:**
  - `timeout_ms` or a deadline is checked against when the result arrived.
  - A result whose `status` is timeout, error, fallback or degraded is flagged. These words only count as single-word status codes, so a sentence like "Pump failure" isn't flagged.
  - `cached_at`/`stored_at` plus a TTL is checked against when the item was served.
- **`\btest\b`:** "latest" no longer counts as a test status.
- **Nested foreign run ids:** an item or result carrying another run's id (`origin_run`, `trace.run_id`, ...) is flagged as cross-run.
- **Tool arguments:** if the wrong run's call sent a different value than every correct run (e.g. `area: Kilamba Kiaxi`), or named a place the question didn't ask about, that call's results are flagged.
- **Past-deadline rule:** skips sentences that say supply is already back ("cut until 07h00, now restored").

**Other critic items I fixed, because they can also change the answer**
- **#8 (shared culprit):** if the wrong run saw nothing the correct runs didn't, the "also in correct runs" penalty is dropped and items are ranked by which supplies the wrong claims.
- **#9b (summaries):** if the final request quotes an earlier answer from the same run, items that reached the earlier request count as reaching the model (via "upstream").
- **#13 (places):** places now come from the user's question only. System prompts are ignored, and the model request is the fallback when there's no prompt event.
- **#16:** "overrides/disregard the earlier notice" no longer counts as injection. I deleted the +10 for ids cited in the wrong answer. A request's inline `result` field is now treated as input, not as the request's own output.

**One guard I added that wasn't in the critic's list.** Drop markers now override content matching, which opened a trap: an item logged as dropped whose text actually appears in the request. Such an item still counts as reaching the model, unless a kept item carries the same text, and it's flagged `dropped_but_sent`.

**Fixtures**
- There are 24 new fixtures (13–36), one per fix.
- Every one fails on the pre-change analyzer, which I saved as `analyze_pre_critic1.py`.
- I also undid each fix on its own in a temp copy, and each fixture fails when its fix is removed. So none of them passes because of a neighbouring fix.
- `test_analyze.py` now loads files through `analyze.load_file`. It passes the `--incorrect` override from `_incorrect_override` in `answers.json`, and checks the `--answer` bytes on the BOM, override and homoglyph fixtures.

**Skipped or partial**
- **Fixture 05 changed:** it mixed `id` and `source_id` keys, which the new source_id rule correctly rejects. I switched its one `source_id` key to `id`, since the real task says the answer is a `source_id`.
- **Confidence gate (partial):** there is now a CHECK line, which flags a lead under 10, no known-correct run, or an ineligible top id. I did not make "the alternative verdict agrees" a condition. The alternative is just the two sides swapped, so it disagrees on every majority vote; it's printed as an "if runs X were wrong instead, the answer would be Y" line.
- **Copying the file with scp/getclip:** that's procedure, not code. The printed sha256 is what lets you check it.
- **Tool arguments are still left out of item text:** the new argument diff and argument place check cover that case instead.
- **Length:** analyze.py is 1,093 lines (891 before), so about 9% over the ~1,000 target. I deleted five flags that never decided a result, plus the +10 citation bonus:
  - `slow_result`
  - `duplicate_result`
  - `after_request`
  - `after_final` (it added points to items that arrived after the answer)
  - the bare `cache_hit` flag (the TTL and staleness checks cover stale cache)

  Getting further down would mean cutting timing checks that the red-team winners use, or the upstream and subset fixes.

Only Python 3.12 is installed here, so I ran the tests on 3.12 and only checked that the three files parse under the 3.10 grammar.
