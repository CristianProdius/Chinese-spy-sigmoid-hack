"""Cross-entropy tuning of our searcher's evaluation against the champion clone
(C simulator, fog on, real generator maps; practice data only).

python tune.py maps.jsonl <gens> <pop> <maps_per_gen> <out.jsonl> [init.json]
"""
import json
import math
import multiprocessing as mp
import random
import sys
import time

import sim_fog
from simlib import Game

# name, transform, init, sigma, lo, hi
SPEC = [
    ("E", "log", 100, 0.3, 10, 600), ("Eopp", "log", 100, 0.3, 5, 600), ("F", "log", 16, 0.2, 1, 60),
    ("h2c", "lin", 0.35, 0.15, 0, 2), ("ha", "lin", 3, 0.5, 0.5, 8), ("hb", "lin", 4, 0.7, 0, 10),
    ("d1", "log", 10, 0.3, 2, 60), ("d2", "log", 24, 0.3, 4, 120), ("capw", "lin", 0, 5, -40, 40),
    ("Fopp", "lin", 1, 0.15, 0, 2), ("pw", "lin", 5, 0.8, 1, 9), ("pc", "lin", 3, 0.4, 1, 4),
]


def to_params(z):
    v = []
    for (name, tr, init, sig, lo, hi), zi in zip(SPEC, z):
        x = math.exp(zi) if tr == "log" else zi
        v.append(min(hi, max(lo, x)))
    return v


def to_z(v):
    return [math.log(x) if s[1] == "log" else x for s, x in zip(SPEC, v)]


def run_game(job):
    vals, m = job
    sim_fog.AGENT = "ext"
    sim_fog.P = {"prm": vals[:10], "pw": vals[10], "pc": vals[11]}
    r = sim_fog.play(m)
    return r[3]


def main():
    maps = [json.loads(l) for l in open(sys.argv[1])]
    gens, pop, per, out = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    init = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else [s[2] for s in SPEC]
    mean = to_z(init)
    sig = [s[3] for s in SPEC]
    rng = random.Random(7)
    pool = mp.Pool(24)
    log = open(out, "a")
    for gen in range(gens):
        t = time.time()
        sub = rng.sample(maps, per)
        cands = [mean] + [[mu + s * rng.gauss(0, 1) for mu, s in zip(mean, sig)] for _ in range(pop)]
        params = [to_params(z) for z in cands]
        jobs = [(p, m) for p in params for m in sub]
        res = pool.map(run_game, jobs, chunksize=4)
        fits = []
        for k in range(len(cands)):
            ms = res[k * per:(k + 1) * per]
            wins = sum(x > 0 for x in ms)
            fits.append((wins + sum(ms) / per / 1000, wins, sum(ms) / per))
        order = sorted(range(len(cands)), key=lambda k: -fits[k][0])
        elite = [cands[k] for k in order[:max(2, pop // 4)]]
        new_mean = [sum(e[i] for e in elite) / len(elite) for i in range(len(SPEC))]
        new_sig = [math.sqrt(sum((e[i] - new_mean[i]) ** 2 for e in elite) / len(elite)) for i in range(len(SPEC))]
        mean = [0.3 * a + 0.7 * b for a, b in zip(mean, new_mean)]
        sig = [max(0.25 * s0[3], min(s0[3], 0.5 * a + 0.5 * b)) for a, b, s0 in zip(sig, new_sig, SPEC)]
        rec = {"gen": gen, "parent_wr": fits[0][1] / per, "parent_margin": round(fits[0][2], 1),
               "best_wr": fits[order[0]][1] / per, "best": [round(x, 3) for x in params[order[0]]],
               "mean": [round(x, 3) for x in to_params(mean)], "secs": round(time.time() - t)}
        print(json.dumps(rec), flush=True)
        log.write(json.dumps(rec) + "\n")
        log.flush()


if __name__ == "__main__":
    main()
