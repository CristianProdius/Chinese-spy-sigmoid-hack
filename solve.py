"""Bihainim Angkol: learn angkol's policy from the logbook, then beat it.

1. Imitation: build angkol's state -> action table from dataset/logbook.csv and
   replay it in the simulator to check it reproduces his logged catch.
2. Improvement: the lagoon is a small finite-horizon MDP whose dynamics are
   fully given by lagoon.py (bite and tide chances, one independent draw each
   per step). Backward induction over steps_left gives the policy with the
   highest expected catch from every state, which is the best any
   state -> action table can do on unseen days.
3. Export main.py with lagoon.export_main and report the catch on the practice
   days and on fresh seeds.

Usage: python solve.py [--out main.py] [--eval-seeds 20000]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.join(HERE, "task", "task_papua_new_guinea")
sys.path.insert(0, TASK)

import lagoon  # noqa: E402

# Tie-break order when two actions have the same expected catch.
ORDER = ("FISH", "NORTH", "SOUTH", "EAST", "WEST", "WAIT")


def angkol_policy(path: str) -> tuple[dict, dict]:
    """Behaviour cloning: the action angkol took most often in each state."""
    seen: dict = defaultdict(Counter)
    logged: dict = defaultdict(int)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            s = (int(r["row"]), int(r["col"]), int(r["hold"]), int(r["steps_left"]))
            seen[s][r["action"]] += 1
            logged[int(r["day"])] += int(r["reward"])
    return {s: c.most_common(1)[0][0] for s, c in seen.items()}, dict(logged)


def solve() -> tuple[dict, dict]:
    """Backward induction. Returns (policy, value) keyed by state."""
    value = {s: 0.0 for s in lagoon.all_states()}
    policy = {}
    terminal = lambda nxt, t: 0.0 if t == 0 else value[(*nxt, t)]  # noqa: E731
    for t in range(1, lagoon.STEPS_PER_DAY + 1):  # value[t] depends on value[t-1]
        for (r, c, h, tt) in lagoon.all_states():
            if tt != t:
                continue
            p_bite = lagoon.BITE_CHANCE.get(lagoon.GRID[r][c], 0.0)
            p_tide = lagoon.TIDE_CHANCE
            best_a, best_q = None, -1.0
            for a in ORDER:
                q = 0.0
                for bite, pb in ((True, p_bite), (False, 1 - p_bite)):
                    if pb == 0:
                        continue
                    for tide, pt in ((True, p_tide), (False, 1 - p_tide)):
                        nr, nc, nh, landed = lagoon._advance(r, c, h, a, bite, tide)
                        q += pb * pt * (landed + terminal((nr, nc, nh), t - 1))
                if q > best_q + 1e-12:
                    best_a, best_q = a, q
            policy[(r, c, h, t)] = best_a
            value[(r, c, h, t)] = best_q
    return policy, value


def mean_catch(policy, seeds) -> float:
    seeds = list(seeds)
    return sum(lagoon.play_day(policy, s)[0] for s in seeds) / len(seeds)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "main.py"))
    ap.add_argument("--eval-seeds", type=int, default=20000)
    args = ap.parse_args()

    with open(os.path.join(TASK, "train-output.json")) as f:
        ref = json.load(f)
    days = ref["days"]

    # 1. Imitation
    bc, logged = angkol_policy(os.path.join(TASK, "dataset", "logbook.csv"))
    replay = {d: lagoon.play_day(bc, d)[0] for d in days}
    mismatches = sum(replay[d] != c for d, c in zip(days, ref["angkol_catch"]))
    print(f"angkol logbook: {len(bc)} states seen, logged mean {sum(logged.values()) / len(logged):.3f}")
    print(f"cloned angkol replayed on practice days: {sum(replay.values()) / len(days):.3f} "
          f"({mismatches} days differ from train-output.json)")

    # 2. Improvement
    policy, value = solve()
    start = (*lagoon.START, 0, lagoon.STEPS_PER_DAY)
    print(f"optimal expected catch from the beach: {value[start]:.3f} fish/day")

    # 3. Evaluate and export
    train_mean = mean_catch(policy, days)
    print(f"optimal policy on practice days: {train_mean:.3f} "
          f"= {train_mean / ref['angkol_mean']:.3f}x angkol (target {ref['target_ratio']}x)")
    fresh = range(10_000_000, 10_000_000 + args.eval_seeds)
    ours, theirs = mean_catch(policy, fresh), mean_catch(lambda s: bc.get(s, "WAIT"), fresh)
    print(f"{args.eval_seeds} unseen seeds: ours {ours:.3f}, cloned angkol {theirs:.3f}, ratio {ours / theirs:.3f}")

    catch, traj = lagoon.play_day(policy, days[0])
    print(f"sample day {days[0]}: " + " ".join(a[0] if a != "WAIT" else "." for _, a, _ in traj) + f" -> {catch} fish")

    lagoon.export_main(policy, args.out)
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
