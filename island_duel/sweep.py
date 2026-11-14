"""Grid/random sweep over ID_PARAMS for an agent, same seeds for every config.

python sweep.py --agent search_agent.py --grid '{"depth":[3,4],"k_energy":[1,1.4]}' \
    --games-per-arena 8 --workers 24
"""

import argparse
import itertools
import json
import os
import time

import bench


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", required=True)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--base", default="{}")
    ap.add_argument("--games-per-arena", type=int, default=8)
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--bundle", default="../bundle")
    ap.add_argument("--engine", default="../samoa-wrapped")
    ap.add_argument("--seed-base", type=int, default=1)
    ap.add_argument("--log", default="sweep.jsonl")
    args = ap.parse_args()
    grid = json.loads(args.grid)
    base = json.loads(args.base)
    keys = list(grid)
    rows = []
    for combo in itertools.product(*(grid[k] for k in keys)):
        params = {**base, **dict(zip(keys, combo))}
        os.environ["ID_PARAMS"] = json.dumps(params)
        t0 = time.time()
        res = bench.run(args.agent, args.games_per_arena, args.workers, args.bundle,
                        args.engine, args.seed_base)
        n = len(res)
        row = {
            "params": params,
            "win": sum(r["win"] for r in res) / n,
            "win_s0": sum(r["win"] for r in res if r["seat"] == 0) / max(1, sum(r["seat"] == 0 for r in res)),
            "win_s1": sum(r["win"] for r in res if r["seat"] == 1) / max(1, sum(r["seat"] == 1 for r in res)),
            "margin": sum(r["me"] - r["opp"] for r in res) / n,
            "secs": time.time() - t0,
        }
        for p in range(3):
            sub = [r for r in res if r["profile"] == p]
            row[f"win_p{p}"] = sum(r["win"] for r in sub) / max(1, len(sub))
        rows.append(row)
        with open(args.log, "a") as f:
            f.write(json.dumps(row) + "\n")
        print(f"{row['win']:.3f} s0 {row['win_s0']:.2f} s1 {row['win_s1']:.2f} "
              f"p {row['win_p0']:.2f}/{row['win_p1']:.2f}/{row['win_p2']:.2f} "
              f"m {row['margin']:+6.1f} {row['secs']:5.1f}s {json.dumps(dict(zip(keys, combo)))}", flush=True)
    rows.sort(key=lambda r: -r["win"])
    print("TOP")
    for r in rows[:8]:
        print(f"{r['win']:.3f} m {r['margin']:+6.1f} {json.dumps(r['params'])}")


if __name__ == "__main__":
    main()
