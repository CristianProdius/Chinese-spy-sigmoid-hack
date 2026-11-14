# The Braided River Run - approach

## What kind of problem this is

Deterministic, fully observed, known map, integer action costs, one start and
one goal. That is a shortest-path planning problem, not a learning problem. RL
(Q-learning, PPO) would need reward shaping and still gives no optimality
guarantee, and the target (296 or better against a ranger's 297) suggests the
optimum sits just under the record. Exact search returns the optimum directly.

## What makes it "hard"

1. **Time-dependent edges (tide).** An action may end on a ford only when
   `minute % 16` is in `0..4`. Plain Dijkstra on cells is wrong: arriving at a
   ford's bank one minute late can cost a full tide cycle, and it can also pay
   to arrive later on purpose (e.g. take a swamp detour instead of waiting).
2. **Bridge state.** Winches flip sets of bridges, so where you can go depends
   on which winches you've stepped on (an odd or even number of times). Same
   pattern as "keys and doors" bitmask BFS.
3. **Waiting is not free everywhere.** You can't wait on a ford into high
   tide, so the classic FIFO argument for time-dependent Dijkstra breaks on
   ford cells. The folding below handles it exactly.

## The model

State = `(cell, bridge_mask, minute mod 16)`.

- The tide is the only time-dependent rule and it repeats every 16 minutes.
  If you reach the same state at minutes `t1 < t2` with `t1 ≡ t2 (mod 16)`,
  every continuation from `t2` can be replayed from `t1` exactly `t2 - t1`
  minutes earlier. So the earliest arrival per state dominates, and
  Dijkstra/A* over this product graph is exact.
- Edges: `U/D/L/R` cost `1` (or `3` onto swamp) `+ climb levels`; `W` costs 1.
  A move into a raised bridge, rock, deep water or off-map is pruned; a move
  or wait that ends on a ford outside the low-tide window is pruned; stepping
  onto a winch XORs its bridges into the mask. G is terminal.
- Size: at most `47*61 * 2^winches * 16` states, and only reachable masks
  appear (the span of the winch vectors).

## Speed

A* with heuristic = reverse Dijkstra from G on a relaxed graph (all bridges
down, fords always open). That relaxation only removes constraints, so it is
admissible, and it is consistent because each edge keeps its real cost.
On synthetic 47x61 valleys with 5 channels, 10 bridges and 8 winches: A* runs
in about 0.05s and full Dijkstra in about 1s, far inside the 2-minute limit.
`main.py` still embeds the offline-found route as a fallback.

## Verification

- `tools/selfcheck.py` checks A* and Dijkstra against an independent
  time-expanded search over absolute time (no mod-16 folding, no heuristic)
  on 3000 random valleys with fords, swamps, heights, open/raised bridges and
  multi-bridge winches. All optima match and every route replays to the
  same minute.
- Once the official files are in: the practice valley must give 114, and
  every route goes through `python environment.py --map ... --replay-file ...`.

## Results on the official files

| Valley | Solver | Official replay | Exhaustive check over `environment._step` |
|---|---|---|---|
| practice (`train-input.txt`) | 114 min, 93 actions, 0.1s | valid, 114 | optimum 114 |
| test (`test-input.txt`) | 293 min, 246 actions, 0.2s | valid, 293 | optimum 293 |

293 is the true minimum for the test valley, 4 minutes under the ranger's 297.
`main.py` loads the map with `environment.load_map`, scores its route and the
embedded fallback with `environment.simulate`, writes the better one to
`solution.txt` and always exits 0. Tested on Python 3.10, 3.11 and 3.12, and
with the search forced to fail (fallback ships the same 293 route).
