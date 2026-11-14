The analyzer now gets all 5 new blind cases right (it got 1 of 5 before), and the two older sets are still at 100%. All 5 stated answers are correct. I read every case myself, and there was no generator code in the redteam2 folder.

## Accuracy

| Set | Before | After |
|---|---|---|
| `test_analyze.py` (36 synthetic fixtures) | 36/36 | 36/36, all checks pass |
| `eval_redteam.py` (red team 1) | 5/5 | 5/5 |
| `eval_redteam2.py` (new) | **1/5** | **5/5**, each answer leads #2 by 31–81 points |

## Are the stated answers right?

- **case1** `SIGMOID_ETA_KILAMBA_PARALISADA`: right. In kil-r3 the retry had a smaller context budget and dropped the newer notice that replaces this one, so the model saw only the old "paralisada, sem data de reposição" notice. The tanker item the answer cites is a decoy.
- **case2** `SIGMOID_CORTE_PROGRAMADO_KILAMBA_R3`: right. Its end time is 16:00 Angola time (15:00Z) with no time zone written, and w-03 ran at 15:21Z, so the cut was already over. The support-line item is a decoy.
- **case3** `SIGMOID_ESTADO_KILAMBA_V41`: right. run_k3 got a cache hit about 3h50m old against a 900 s TTL.
- **case4** `SIGMOID_INTERRUPCAO_ETA_KILAMBA_0930`: right. It came from a call that timed out in trace C but whose result still reached the final model call. I checked the bytes: the real id uses the digit 0, and the `_O930` with a letter O in trace A is the look-alike.
- **case5** `SIGMOID_MEMORIA_SESSAO_0412`: right. It is a memory record written by another trace (`tr-kiaxi-5521`), 678 s old (TTL 1800 s), and only tr-5c's answer step saw it.

Two small slips in the explanations, neither of which changes an answer:
- **case4** says the late result arrived at "+6.15 s, still inside the 6 s window". 6.15 s isn't inside 6 s; it only fits if the window starts when the tool call starts, about 0.9 s after the run starts.
- **case5** says "Golfe/Nova Vida '22h00…'". The memory text says that, but the wrong answer itself never names Golfe or Nova Vida; it just says Kilamba.

## Why it missed, and what changed

All changes are general rules, with no case ids or strings in the code.

- **Case 4 (OTLP spans) and case 5 (nested trace tree) weren't parsed.** The analyzer read span names and step ids as run ids. A new `normalize()` step turns OTLP exports into one event per span (run = trace id) and flattens nested traces into one run per trace. Every other input passes through unchanged; only these two files get reshaped.
- **"Supersedes / refers to" links weren't tracked.** Now an old item that reached the model without its newer replacement is flagged as superseded, as long as the newer item existed for that run. Where both reached the model, the old item's problems count as answered.
- **Being invalid only in the wrong run now scores higher.** If an item reached both wrong and correct runs, but was expired or superseded only in the wrong one, it now gets a bonus instead of a penalty. This fixed cases 1 and 2.
- **Old issue dates no longer make everything look stale.** An item is only flagged stale if it states a supply condition and has no validity window of its own. A year-old contact line or FAQ is no longer marked stale.
- **A reference isn't delivery.** An id that only shows up inside another item's `supersedes` or `previous_version` field no longer counts as having reached the model. Before this, case 4 passed but its explanation was wrong.
- **Items written by another trace are flagged.** A field like `origin_trace` that names a different trace or session now counts as a cross-run problem.
- **More Portuguese and English wording:**
  - "restored": reposto, retomou, terminou
  - "outage": parada, halted, stopped
  - end times that have already passed: "prevista para as 16h00", "previsão de reposição: 12h00", and ranges like "das 08h00 às 16h00"

## Files (all in `waterline/`)

- `analyze.py`: the changes above (1093 → 1263 lines).
- `eval_redteam2.py`: the new eval. It exits non-zero unless all 5 cases pass.
- `analyze_pre_rt2.py`: the old version, kept as a baseline. `python3 eval_redteam2.py analyze_pre_rt2` reproduces the 1/5.
