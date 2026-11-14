The analyzer now gets all 5 red-team cases right (it got 2 before), and all 12 fixtures still pass. All five stated red-team answers are correct.

| Set | Before | After |
|---|---|---|
| Fixtures (`test_analyze.py`) | 12/12, all checks pass | 12/12, all checks pass; leads equal or wider |
| Red-team top-1 | 2/5 | 5/5, every lead 17 points or more |

Before, the two red-team passes were cases 1 and 4, and case 4 was luck: it couldn't separate the runs, so the right id came first in a four-way tie. Case 2 picked the system-prompt id, case 3 blamed the wrong run, and case 5 crashed. After the changes the analyzer also names the correct incorrect run(s) in all five cases. Case 1 and the four cases where runs are interleaved still give the same top answer. I checked case 4's interleaving by hand because the test helper skips nested run keys.

**Is each red-team answer right?** I read every case myself, and none is wrong:
- **Case 1, `SIGMOID_TIN_ROOF_RAIN`:** run-02 timed out and retried, then the slow original call returned a stale replica result 6 s late and overwrote the fresh retry.
- **Case 2, `SIGMOID_HARBOR_LIGHT`:** run C received run B's historical record in place of its own live status.
- **Case 3, `SIGMOID_LONG_AFTERNOON`:** run 3 started at 18:31 Luanda time and served a cached notice that expired at 18:00 Luanda time; the cache compared that local time against UTC. Runs 1 and 2 gave the same answer earlier, while it was still true. That is why majority vote blamed run 4.
- **Case 4, `SIGMOID_LONG_NIGHT_LEDGER`:** in R-2 and R-4 the log was cut down to fit a smaller fallback model, losing the "repair complete" and "restored" lines. The truncation event has no id of its own, so this is the right id.
- **Case 5, `SIGMOID_GOLDEN_SPILLWAY`:** runs b and e used an old place index that labels a Kilamba Kiaxi zone as "Kilamba". The answer is the plain-ASCII id; the look-alike with a Cyrillic А is a dropped draft.

**What changed in `analyze.py`** (all general rules, no case strings or ids):
1. **Reading the export:**
   - It reads tool results stored as JSON text inside a field.
   - It now recognizes field names it missed: `t`, `t_ms`, `utc`, `ev`, and nested ones like `run.id`. It prefers `kind` over `name` for the event type.
   - The final answer is the last response that has text, not a bare "delivered" marker.
   - When no run has a final answer it reports that instead of crashing.
2. **Fixing false matches:**
   - A tool response quoted inside the model's input no longer counts as the model's output.
   - Duplicate-result checks stay within one run (call ids repeat across runs).
   - Items listed under `dropped` can't count as reaching the model.
   - Parent-span links and values stamped on every event of a run aren't treated as citations.
   - A look-alike id only matches if the exact spelling wasn't sent.
   - A `supersedes` field no longer flags the newer item as replaced.
3. **Item content:** an id inside a `meta`/`ref` sub-object takes its parent's text. A container id (like a knowledge-base name) doesn't inherit its child documents' text, and tool-call arguments don't count as content.
4. **New signals:**
   - Naive times are read in the item's own `tz` field when it has one.
   - A new flag marks items that were cut short before the model saw them.
   - "Water on vs water off" now counts when comparing answers. "No active interruptions" reads as no outage, and Portuguese outage words are recognized.
5. **New verdict rule:** if a run's answer says an outage lasts "until HH:MM" and that time had already passed (Luanda time, UTC+1) when the run started, that run is wrong, ahead of majority vote. Naive timestamps get 65 minutes of slack in case they're already local time.
6. **Ranking:**
   - An item shared with correct runs is only cleared if its content and validity both match (expired, truncated, cross-run and so on).
   - Wrong claims are measured only against correct runs that actually disagree.
   - The item that states the passed end time gets extra credit.
   - Validity problems now weigh more than timing jitter or cache hits.

The file grew from 754 to about 890 lines. I added `eval_redteam.py`, which scores the red-team cases (`python3 eval_redteam.py analyze_before` scores the old version), and kept the original as `analyze_before.py` for comparison. Both are in `waterline/`. While working I briefly put a few scratch files in `/tmp/claude-1003/`, outside `waterline/`; I've deleted them.
