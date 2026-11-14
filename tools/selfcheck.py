"""Cross-check main.solve against an independent time-expanded search.

The reference search keeps absolute time (no mod-period folding, no
heuristic) and expands every (cell, mask) reachable at each minute in order,
so its first arrival at G is the true optimum. Random valleys exercise
fords, swamps, heights, raised/open bridges and multi-bridge winches.

    python tools/selfcheck.py [n_cases] [seed]
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import main  # noqa: E402


def reference(v: main.Valley, t_max: int = 3000) -> int | None:
    rules = main.Rules(v)
    layers: dict[int, set[tuple[int, int]]] = defaultdict(set)
    layers[0].add((rules.start, rules.mask0))
    seen: set[tuple[int, int, int]] = set()
    for t in range(t_max + 1):
        layer = layers.pop(t, None)
        if not layer:
            continue
        for cell, mask in layer:
            if cell == rules.goal:
                return t
        for cell, mask in layer:
            if (cell, mask, t) in seen:
                continue
            seen.add((cell, mask, t))
            # wait
            t2 = t + v.wait_cost
            if not rules.ford[cell] or rules.tide_ok(t2):
                layers[t2].add((cell, mask))
            for _, j, c in rules.nbrs[cell]:
                if rules.bridge[j] and not (mask & rules.bridge[j]):
                    continue
                t2 = t + c
                if rules.ford[j] and not rules.tide_ok(t2):
                    continue
                layers[t2].add((j, mask ^ rules.toggle[j]))
    return None


def random_valley(rng: random.Random) -> main.Valley:
    R, C = rng.randint(5, 11), rng.randint(5, 13)
    n_bridges = rng.randint(0, 4)
    letters = [chr(ord("A") + i) for i in range(n_bridges)]
    cells = []
    for _ in range(R * C):
        x = rng.random()
        cells.append("." if x < 0.45 else "," if x < 0.6 else "#" if x < 0.7 else "=" if x < 0.78 else "~")
    # carve a river column of water/fords/bridges to force interesting crossings
    col = rng.randrange(1, C - 1)
    for r in range(R):
        cells[r * C + col] = rng.choice("==~~" + "".join(letters) * 2) if letters else rng.choice("=~~")
    for b in letters:
        cells[rng.randrange(R) * C + col] = b
    free = [i for i in range(R * C) if cells[i] in ".,"]
    rng.shuffle(free)
    s, g = free.pop(), free.pop()
    cells[s], cells[g] = "S", "G"
    winches = {}
    for k in range(rng.randint(0, 3) if letters else 0):
        if not free:
            break
        w = chr(ord("a") + k)
        cells[free.pop()] = w
        winches[w] = set(rng.sample(letters, rng.randint(1, len(letters))))
    v = main.Valley()
    v.grid = ["".join(cells[r * C:(r + 1) * C]) for r in range(R)]
    v.rows, v.cols = R, C
    v.heights = [[rng.randint(0, 5) if rng.random() < 0.5 else 0 for _ in range(C)] for _ in range(R)]
    v.open_bridges = set(rng.sample(letters, rng.randint(0, len(letters)))) if letters else set()
    v.winches = winches
    v.period = rng.choice([4, 6, 8, 16])
    lo = rng.randrange(v.period)
    v.window = set(range(lo, min(v.period, lo + rng.randint(1, max(1, v.period // 3)))))
    return v


def run(n: int, seed: int) -> int:
    rng = random.Random(seed)
    solved = unsolved = 0
    for case in range(n):
        v = random_valley(rng)
        ref = reference(v)
        got = main.solve(v)
        got0 = main.solve(v, use_heuristic=False)
        if ref is None:
            assert got is None and got0 is None, (case, got, got0, v.grid)
            unsolved += 1
            continue
        assert got is not None and got[0] == ref, (case, ref, got, v.grid)
        assert got0 is not None and got0[0] == ref, (case, ref, got0)
        ok, info = main.replay(v, got[1])
        assert ok and info == ref, (case, ok, info, ref)
        solved += 1
    print(f"ok: {solved} solvable valleys match the reference optimum, {unsolved} unsolvable agree")
    return 0


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    sys.exit(run(n, seed))
