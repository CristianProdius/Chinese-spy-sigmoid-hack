"""Practice benchmark: play many seeded practice games in parallel.

python bench.py --agent agent.py --games-per-arena 4 --workers 16 \
    [--bundle ../task/island-duel/island-duel-participant] [--engine path]

Seeds are drawn deterministically from --seed-base so runs are comparable.
Prints win rate overall, by seat, by opponent profile and the number of
arenas (groups) with at least one win, mirroring the qualification rule
(>= 308/512 wins, wins in >= 24 of 32 groups).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing as mp
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BUNDLE = os.path.join(HERE, "..", "task", "island-duel", "island-duel-participant")

_env = None
_choose = None
_reset = None


def _load_agent(path):
    path = os.path.abspath(path)
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("bench_agent", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.choose_action, getattr(mod, "reset_agent", lambda: None)


def _init(bundle, engine, agent):
    global _env, _choose, _reset
    sys.path.insert(0, os.path.abspath(bundle))
    from client import ArenaClient

    _env = ArenaClient(engine)
    _choose, _reset = _load_agent(agent)


def _play(task):
    arena, seed = task
    t0 = time.time()
    _reset()
    resp = _env.reset(arena, seed)
    obs = resp["observation"]
    seat, profile = obs["seat"], obs["opponent_profile"]
    n = 0
    while not resp["done"]:
        a = _choose(resp["observation"])
        if a not in resp["observation"]["legal_actions"]:
            raise ValueError(f"illegal action {a} arena={arena} seed={seed}")
        resp = _env.step(a)
        n += 1
    scores = resp["scores"]
    return {
        "arena": arena, "seed": seed, "seat": seat, "profile": profile,
        "me": scores[seat], "opp": scores[1 - seat], "winner": resp["winner"],
        "win": resp["winner"] == seat, "draw": resp["winner"] is None,
        "secs": time.time() - t0, "steps": n,
    }


def run(agent, games_per_arena, workers, bundle, engine, seed_base, arenas=range(32)):
    tasks = [(a, (seed_base * 1_000_003 + a * 7919 + g * 104729) & 0xFFFFFFFF)
             for g in range(games_per_arena) for a in arenas]
    with mp.Pool(workers, initializer=_init, initargs=(bundle, engine, agent)) as pool:
        return list(pool.imap_unordered(_play, tasks))


def report(results):
    n = len(results)
    wins = sum(r["win"] for r in results)
    draws = sum(r["draw"] for r in results)
    print(f"games {n}  wins {wins} ({wins / n:.1%})  draws {draws}  "
          f"avg margin {sum(r['me'] - r['opp'] for r in results) / n:+.1f}  "
          f"avg score {sum(r['me'] for r in results) / n:.1f} vs {sum(r['opp'] for r in results) / n:.1f}  "
          f"avg secs/game {sum(r['secs'] for r in results) / n:.2f}")
    for key in ("seat", "profile"):
        g = defaultdict(list)
        for r in results:
            g[r[key]].append(r)
        print(f"  by {key}: " + "  ".join(
            f"{k}: {sum(x['win'] for x in v)}/{len(v)} ({sum(x['win'] for x in v) / len(v):.0%}, "
            f"margin {sum(x['me'] - x['opp'] for x in v) / len(v):+.0f})"
            for k, v in sorted(g.items())))
    by_arena = defaultdict(list)
    for r in results:
        by_arena[r["arena"]].append(r["win"])
    print(f"  arenas with a win: {sum(any(v) for v in by_arena.values())}/{len(by_arena)}  "
          "per-arena win rate: " + " ".join(f"{a}:{sum(v)}/{len(v)}" for a, v in sorted(by_arena.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--games-per-arena", type=int, default=4)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--bundle", default=DEFAULT_BUNDLE)
    ap.add_argument("--engine", default=None)
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--arenas", default=None, help="comma list, default all 32")
    ap.add_argument("--out", default=None, help="write per-game results JSON")
    args = ap.parse_args()
    arenas = range(32) if not args.arenas else [int(x) for x in args.arenas.split(",")]
    t0 = time.time()
    results = run(args.agent, args.games_per_arena, args.workers, args.bundle, args.engine,
                  args.seed_base, arenas)
    report(results)
    print(f"wall {time.time() - t0:.1f}s")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f)


if __name__ == "__main__":
    main()
