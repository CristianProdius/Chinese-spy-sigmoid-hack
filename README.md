# Chinese-spy-sigmoid-hack

## The Braided River Run (New Zealand) - 293 minutes

Fastest route from `S` to `G` through the 47x61 braided-river valley:
**293 minutes, 246 actions**. The target was 296 or less and the ranger's
best is 297. 293 is the true optimum: an exhaustive search over the
official simulator's own rules gives the same number.

| File | What it is |
|---|---|
| [`main.py`](main.py) | The submission. Reads `test-input.txt`, writes `solution.txt`, exits 0. Standard library only, runs in about 0.3s. |
| [`solution.txt`](solution.txt) | The 293-minute route. |
| [`RESEARCH.md`](RESEARCH.md) | Approach, why it is exact, and verification. |
| [`tools/selfcheck.py`](tools/selfcheck.py) | Checks the solver against an independent absolute-time search on random valleys. |
| [`task/`](task/) | The challenge files: maps, simulator, practice answer. |

### How it works

Exact A* search over `(cell, bridge mask, minute mod 16)`. The tide repeats
every 16 minutes, so reaching the same cell with the same bridges at the same
tide phase earlier always beats reaching it later, which makes the search
exact. Winches flip bits in the bridge mask. The heuristic is the
cost-to-goal with every bridge down and every ford open, so A* never
overestimates.

### Run and check

```
cd task
python ../main.py --map test-input.txt --out ../solution.txt
python environment.py --map test-input.txt --replay-file ../solution.txt
# valid run: 293 minutes (246 actions)
```

The practice valley gives 114 minutes, matching `task/train-output.txt`.
