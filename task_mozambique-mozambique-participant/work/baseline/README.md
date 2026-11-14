# baseline/: evaluation harness + first heuristic agent

## eval.py

    python3 eval.py AGENT.py [--maps 48] [--seed 20261114] [--jobs 6] [--nice 10]
                             [--games 0,1,2,3,4] [--groups 0,1] [--cases ../../train-input.json]
                             [--out results/x.json] [--quiet]

* Same protocol as `arena.py`: the agent runs as a subprocess (PyPy 3.10 by default, under `nice`),
  one JSON observation per line in, one action per line out. Module globals survive across games
  in one process, like the real evaluator.
* Maps: map m gets group `m % 8` (so 48 maps = 6 per group) and a seed from `random.Random(--seed)`,
  the same scheme as `arena.py`. A fixed `--seed` gives identical maps every run. Every map is played
  for each game index (style) and counts by its worst game.
* `--jobs` workers each own one engine and one agent process and pull games from a shared queue.
* Reports: match score (sum of per-map worst half-points / 2·maps), map W/D/L, win/draw/loss and
  mean/min score margin per game index, per seat, per topology, per seat×game; per-game CPU time
  of the agent process (utime+stime from /proc, the honest number on this loaded box) and wall time.
* Any illegal action, crash, bad JSON or a 30 s stall scores the game as a loss, restarts the agent
  and is listed under ERRORS.
* JSON output (`results/*.json`): `summary`, `maps` (worst + per-game scores), `games` (per game:
  scores, half_points, margin, cpu, wall, `claim_round[8]` and `claim_by` "U/P/." per contract).

`tools/runall.sh A.py B.py ...` runs 48-map evals one after another and prints the headlines.
Other tools: `tools/trace.py AGENT GROUP SEED GAME` (in-process round-by-round trace),
`tools/plan0.py AGENT GROUP SEED GAME [C]` (round-0 plan, and the effect of forcing raw contract C),
`tools/probe.py` (scripted actions), `tools/prof_timeline.py` (Professor claim rounds when we wait),
`tools/survival.py` / `tools/contest_surv.py` (claim time minus the Professor's lower bound),
`tools/solo.py` (planner quality with no opponent).

## agent_v1.py

See the module docstring. Plan-and-simulate: per-boat step queues, an own-side simulator with the
one-action-per-round dispatcher, greedy project insertion valued by a survival model of the
Professor's claim times, re-planned every few rounds.

CPU guard: the search stops at 1.2 s of process CPU on round 0 and 0.25 s on later re-plans
(`PARAMS['tmax0']`, `PARAMS['tmax']`), with smaller budgets once a game has used 3 s or 6 s.

### Score (48 maps × 5 games, `--seed 20261114`, `results/48_agent_v1_final.*`)

    MATCH SCORE 0.2292   map half-points 22/96   map W/D/L 10/2/36
    all games     110/240 W110 D45 L85   45.8%   (mean score 31.9 vs Professor 33.0)
    game 0..4     50.0% / 45.8% / 45.8% / 39.6% / 47.9% wins
    seat 0 44.2%  seat 1 47.5%   topology 0..3: 40.0 / 46.7 / 50.0 / 46.7%
    cpu/game max 2.76 s (first game of a process), 1.90 s otherwise, mean 0.86 s; no errors

Far from the ~92% per-game win rate a pass needs (each map counts its worst of 5 games). Treat
this as a baseline and a planner/simulator to reuse, not a contender. The path to a pass is the
exact Professor clone in `../binary/professor.py` (style tracking + exact claim prediction).

### Iterations (48 maps, same seeds; ±3% per-game noise at 240 games)

| version | change | games won | match |
|---|---|---|---|
| v1c | composite projects (kit+delivery, feed+delivery), survival-model win weights | 43.8% | 0.104 |
| v1d | + PICK priority, one-step lookahead, kit follow-up feed, second workshop | 40.4% | 0.135 |
| v1f | + pilot search at round 0 (complete top-6 first moves greedily), double M delivery | 41.2% | 0.188 |
| **v1g** | + insertion at every project boundary, adjacent block swaps | **45.4%** | **0.229** |
| v1g_margin | weight contracts the Professor would take by (1 + P(it takes them)) | 45.0% | 0.177 |
| v1g_more | re-plan every 2 rounds + pilots later (CPU mean 1.8 s) | 48.3% | 0.146 |
| v1g_nolook | no one-step lookahead | 43.3% | 0.146 |
| v1h | v1g + deduped pilots + an extra pilot per early raw contract | 41.7% | 0.146 |
| final | v1g + CPU guard | 45.8% | 0.229 |

### What the losses look like (results/48_v1g.json)

* The Professor claims raw contracts early (median claim round 8-14, even the deadline-72 one);
  we take ours late. In our 85 losses we claimed only 6/14/17/22 of the four raw contracts.
* All 20 five-point losses had a raw contract nobody claimed (mostly c0, deadline 24): one extra
  raw delivery turns each into a draw. Example: group 1 seed 3992200452 (c0 is 3 rounds from our
  home; the round-0 plan skips it for the workshop kit).
* Forcing such a raw delivery into the plan raises the simulated plan value (25.9 -> 27.4 there),
  but v1h, which searches for those plans, did not win more against the real Professor: the
  survival-model win weights are too crude to rank plans that close.
