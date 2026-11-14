# work/fast: a faster, order-for-order identical engine + Professor

`fastcore.py` is a drop-in replacement for `work/binary/professor.py` for use inside the agent's
lookahead. It produces the same orders, plans, plan contracts, stock estimates and engine states
as the validated reference (see "Verification"), only faster. Stdlib only, PyPy 3.10 / CPython 3.8+,
one self-contained 67 KB file, so it can be pasted into `main.py`.

## Files

| file | what |
|---|---|
| `fastcore.py` | the fast core: engine, Professor, replan cache, Tracker |
| `difftest.py` | lockstep differential test against `professor.py` (games + Tracker) |
| `bench.py` | benchmarks: replans, whole games, tracking, lookahead rollouts |
| `quickcheck.py`, `benchreplan.py` | replay a recorded replan corpus: check exactness / time it |
| `mkcorpus.py`, `mkcorpus_tracker.py` | record replan corpora (normal games / 5-style tracking) |
| `ab.py` | A/B two fastcore versions on a corpus in one process (for further tuning) |
| `corpus_a.pkl`, `corpus_b.pkl`, `corpus_tr.pkl` | recorded replans (881 / 1381 / 416) with the reference outputs |
| `results/` | logs of the final runs |

## API

Everything `professor.py` exports, same names, same order tuples:
`Map`, `Engine` (`.view(seat)`, `.legal(seat)`, `.step([o0, o1])`), `Side`, `View`,
`legal_actions`, `is_legal`, `apply_order`, `advance_side`, `Professor(style, seat)` with
`.choose(view)`, `.clone()` and the attributes `plan`, `plan_contracts`, `est`, `last_round`,
`replans`, `view_from_observation`, `order_to_json`, `order_from_json`, `generate_map`,
`style_permutation`, `STYLES`, `WAIT`, `BUILD_BOAT`, `o_sail` ... `o_deliver`, `stock_value`.

Additions:

- `Engine.clone()`: cheap deep copy (use it instead of `copy.deepcopy`).
- `Professor(style, seat, cache=None, use_cache=True)`. By default a Professor uses the shared
  cache of its map and style (`Map.replan_cache(style)`), so all clones of one style on one map
  share replans. `clone()` shares the cache. `use_cache=False` turns memoisation off.
- `Professor.replan(view)` returns `(plan orders, contracts, score)` or `None` (the reference
  returns `(sim, contracts, score)`; `choose` uses only the orders and contracts).
  `replan_uncached(view)` bypasses the cache.
- `ReplanCache(maxsize=20000)`: `.hits`, `.misses`, `len()`, `.clear()`. Key = the replan input
  (round, own side, stock estimates, claims) packed as int16 bytes; value = (plan codes,
  contracts, score). When full, the oldest half is dropped (hits move to the young end).
  Measured ~0.7 KB per entry, so a full cache is ~14 MB. Keep `Map` objects (they own the
  caches) only for maps you still need, or pass a smaller `cache_size`.
- `Tracker(obs, styles=(0,1,2,3,4), mp=None, strict=False, cache_size=None)`: five style
  hypotheses. Each round: `alive = tr.observe(obs)` prunes and computes each survivor's Professor
  order, then `tr.commit(our_order)` (tuple or JSON dict) steps every hypothesis.
  `tr.hyps` are `Hypothesis` objects: `.style`, `.eng` (full two-sided `Engine`: their boats,
  cargo, warehouses, all stocks), `.prof` (full `Professor`: plan, plan_contracts, est),
  `.order()` (their order this round), `.clone()` (independent copy, shares the cache),
  `.step(our_order)` (play one round). `tr.dropped` maps style -> round it was dropped.
  Pass `styles=` to start from fewer styles (e.g. styles already met on this map in earlier
  games of the process) and `mp=` to reuse one `Map` (and its caches) across games of a map.
  Pruning compares every field `compare_observation` compares except `legal_actions`, which is a
  function of the compared fields (`strict=True` compares it too).
- `encode_order(o)` / `decode_order(code)`: the planner's int order codes.

Lookahead sketch:

```python
alive = tr.observe(obs)
for h in alive:                       # plan against every surviving style
    for plan in candidate_plans:
        x = h.clone()
        for o in plan:
            x.step(o)                 # their reply is computed exactly (replans are cached)
        score = x.eng.sides[seat].score - x.eng.sides[1 - seat].score
...
tr.commit(chosen_order)
```

## What changed (and why behaviour is identical)

Profile of the reference: 85% of a replan was `Sim.step`, called ~9,000 times per replan,
mostly by `travel` inside `acquire`.

1. **Flat Sim.** The planner's Sim is one int list (round, ok, score, crafted, home, boats count,
   estimates, claims, warehouses, workshops, jobs, boats); a copy is one slice. Orders inside the
   planner are ints (`op | boat << 4 | arg << 6`), converted to the same tuples at the boundary.
2. **O(1) travel.** `travel` = wait for the boat to dock, then sail the next-hop path. Nothing
   else happens in those rounds except time passing, so the other boats, jobs and stock
   regeneration are advanced in one step (`_ff`), with the exact 160-round Sim limit (a step
   that would start at round >= 160 fails, as in `Sim::step`). A failed Sim is never read again,
   so failing early is safe.
3. **No waits in sequential sims.** `interleave` drops waits from its input, so `prepare`'s
   sequential sims only record non-wait orders.
4. **Legality checks only where they can fail.** Travel sails, loads/gathers/unloads inside
   `acquire` and the delivery in `prepare` are legal by construction (shown in the code
   comments); `interleave` checks each front once (the reference checks twice).
5. **Interleave waits in bulk** up to the next event that can change a front's legality
   (a boat docks, a job finishes, a stock regenerates, round 80).
6. **Exact pruning before copying.** `acquire` computes a branch's finishing round before
   copying and skips branches that cannot beat the best. Callers pass the bar they will apply:
   `prepare` passes the best round of the boats tried so far, `supply` passes its best cost
   (cost = round - surplus * B, and the surplus at the workshop is known before the search).
   A result the caller would reject is never built. Same for `manufactured`: a candidate's cost
   is known before it travels (stock_value cannot change while a boat sails).
7. **Interleave resumes from the parent's run.** A child node's queues are its parent's queues
   with orders appended, so its run is identical until the first moment a boat queue of the
   parent ran dry; the run state there is stored once and reused.
8. **Identical siblings are expanded once.** The two interleave variants of a `prepare` give the
   same state 43% of the time; their children are then identical (interleave only sees per-boat
   order), so they share one expansion memo.
9. **Whole-replan cache** (`ReplanCache`), keyed by everything replan reads.

Candidate order, tie-breaks (stable sorts, strict `<`), float expressions and evaluation order
are kept as in the reference.

Tried and dropped: running both interleave variants in lockstep (10% slower under PyPy), lower
PyPy JIT thresholds (slower).

## Verification

RESULTS_PLACEHOLDER

## Speed

SPEED_PLACEHOLDER

## Rerun

```
PYPY=/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3
nice -n 10 $PYPY difftest.py --games 2000 --tracker-games 400 --jobs 8 --seed 20261114
nice -n 10 $PYPY bench.py --games 16
nice -n 10 $PYPY quickcheck.py corpus_tr.pkl          # exactness on a recorded corpus, seconds
nice -n 10 $PYPY benchreplan.py corpus_b.pkl          # replan speed, ref vs fast
```
