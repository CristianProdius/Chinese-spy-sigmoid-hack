"""Practice only: play agents against the champion clone in the C simulator
(full information for us -> upper bounds for planning).

python sim_play.py maps.jsonl <agent> [json params] [workers]
agents: negamax, om
"""
import json
import multiprocessing as mp
import sys
import time

from simlib import Game

MAPS = [json.loads(l) for l in open(sys.argv[1])]
AGENT = sys.argv[2]
P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
W = int(sys.argv[4]) if len(sys.argv) > 4 else 8


def act(g):
    if AGENT == "negamax":
        return g.negamax(P.get("E", 160), P.get("F", 9), P.get("budget", 2048), P.get("depth", 4))
    if AGENT == "om":
        return g.om(P.get("depth", 1), P.get("E", 160), P.get("F", 9), P.get("capw", 0.0))[0]
    if AGENT == "omnm":
        return g.om_nm(P.get("E", 160), P.get("F", 9), P.get("budget", 2048), P.get("depth", 4))[0]
    if AGENT == "roll":
        b, mv, vals = g.om_nm(P.get("E", 160), P.get("F", 9), 1000000, 2)
        cands = [a for _, a in sorted(zip(vals, mv), reverse=True)[:P.get("k", 4)]]
        nm = g.negamax(P.get("E", 160), P.get("F", 9))
        if nm not in cands:
            cands.append(nm)
        if len(cands) == 1:
            return cands[0]
        H = P.get("H", 0)
        if H:
            res = [(g.rollout_h(a, H, P.get("E", 160), P.get("F", 9), P.get("rb", 2048), 4), -i, a) for i, a in enumerate(cands)]
        else:
            res = [(g.rollout(a, P.get("E", 160), P.get("F", 9), P.get("rb", 2048), 4), -i, a) for i, a in enumerate(cands)]
        return max(res)[2]
    raise SystemExit("unknown agent")


def play(m):
    seat = m["seat"]
    g = Game(m, 1 - seat, m["profile"])
    while g.get("remaining") > 0:
        g.apply(act(g) if g.get("cur") == seat else g.champ())
    s = g.get("score", 2)
    return m["arena"], seat, m["profile"], s[seat] - s[1 - seat]


if __name__ == "__main__":
    t = time.time()
    with mp.Pool(W) as pool:
        res = pool.map(play, MAPS, chunksize=1)
    n = len(res)
    wins = sum(r[3] > 0 for r in res)
    draws = sum(r[3] == 0 for r in res)
    print(f"{AGENT} {P}: {wins}/{n} wins ({wins / n:.3f}) draws {draws} margin {sum(r[3] for r in res) / n:+.1f} "
          f"time {time.time() - t:.0f}s")
    for s in (0, 1):
        sub = [r for r in res if r[1] == s]
        print(f"  seat {s}: {sum(r[3] > 0 for r in sub)}/{len(sub)}")
    for p in (0, 1, 2):
        sub = [r for r in res if r[2] == p]
        print(f"  profile {p}: {sum(r[3] > 0 for r in sub)}/{len(sub)} margin {sum(r[3] for r in sub) / max(1, len(sub)):+.1f}")
