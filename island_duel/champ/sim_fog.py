"""Practice only: fogged agents vs the champion clone in the C simulator.

python sim_fog.py maps.jsonl <agent> [json params] [workers]
agents: fognm (champion algorithm from our seat), plan (sampled worlds + rollouts)
"""
import json
import multiprocessing as mp
import random
import sys
import time

from fog import NB, Tracker, sample_world
from simlib import DEFAULT_PRM, Game, root_features, set_opponent_model, set_qdepth, search_decide, search_decide_ext, search_decide_fit

if __name__ == "__main__":
    MAPS = [json.loads(l) for l in open(sys.argv[1])]
    AGENT = sys.argv[2]
    P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    W = int(sys.argv[4]) if len(sys.argv) > 4 else 8
else:
    MAPS, AGENT, P, W = [], "", {}, 1


def observe(g, seat):
    owner, blocked = g.get("owner", 225), g.get("blocked", 225)
    w, c = g.get("w", 225), g.get("c", 225)
    vis = [False] * 225
    for i in range(225):
        if owner[i] == seat:
            vis[i] = True
            for j in NB[i]:
                vis[j] = True
    return {
        "seat": seat, "current_player": g.get("cur"), "actions_remaining": g.get("remaining"),
        "opponent_profile": g.get("cprof"), "energy": g.get("energy", 2), "scores": g.get("score", 2),
        "visible": vis,
        "owners": [(-2 if blocked[i] else owner[i]) if vis[i] else -3 for i in range(225)],
        "weights": [w[i] if vis[i] else None for i in range(225)],
        "costs": [c[i] if vis[i] else None for i in range(225)],
        "legal_actions": [None if a < 0 else a for a in g.legal()],
    }


class FogNM:
    def __init__(self, seat):
        self.seat = seat
        own, w, c = [-3] * 225, [5] * 225, [3] * 225
        own[0], own[224] = 0, 1
        w[0] = w[224] = c[0] = c[224] = 0
        self.mem = (own, w, c)

    def act(self, g, obs):
        t = {"blocked": g.get("blocked", 225), "w": g.get("w", 225), "c": g.get("c", 225),
             "owner": g.get("owner", 225), "energy": g.get("energy", 2), "score": g.get("score", 2),
             "remaining": g.get("remaining")}
        mode = P.get("info", "")
        if mode:
            # update our real fogged memory first (visible tiles), then overlay extra info
            mem = (list(self.mem[0]), list(self.mem[1]), list(self.mem[2]))
            vis = obs["visible"]
            for i in range(225):
                if vis[i]:
                    self.mem[0][i] = obs["owners"][i]
                    self.mem[1][i], self.mem[2][i] = obs["weights"][i], obs["costs"][i]
                elif self.mem[0][i] == self.seat:
                    self.mem[0][i] = 1 - self.seat
            mem = (list(self.mem[0]), list(self.mem[1]), list(self.mem[2]))
            if mode in ("terrain", "all"):
                for i in range(225):
                    if not vis[i]:
                        mem[1][i], mem[2][i] = t["w"][i], t["c"][i]
                        if t["blocked"][i]:
                            mem[0][i] = -2
                        elif mem[0][i] == -3:
                            mem[0][i] = -1
            if mode in ("owner", "all"):
                for i in range(225):
                    if not vis[i] and not t["blocked"][i] and t["owner"][i] in (0, 1):
                        mem[0][i] = t["owner"][i]
                        mem[1][i], mem[2][i] = t["w"][i], t["c"][i]
            return search_decide(t, self.seat, P.get("E", 160), P.get("F", 9), P.get("budget", 2048), 4, mem)
        return search_decide(t, self.seat, P.get("E", 160), P.get("F", 9), P.get("budget", 2048), 4, self.mem)


class Ext:
    """Our searcher with a tunable eval (P: prm list, budget, depth, pw, pc)."""

    def __init__(self, seat):
        self.seat = seat
        pw, pc = int(round(P.get("pw", 5))), int(round(P.get("pc", 3)))
        own, w, c = [-3] * 225, [pw] * 225, [pc] * 225
        own[0], own[224] = 0, 1
        w[0] = w[224] = c[0] = c[224] = 0
        self.mem = (own, w, c)
        self.prm = P.get("prm", DEFAULT_PRM)

    def act(self, g, obs):
        t = {"blocked": g.get("blocked", 225), "w": g.get("w", 225), "c": g.get("c", 225),
             "owner": g.get("owner", 225), "energy": g.get("energy", 2), "score": g.get("score", 2),
             "remaining": g.get("remaining")}
        return search_decide_ext(t, self.seat, self.prm, P.get("budget", 2048), P.get("depth", 4), self.mem)


class Fit:
    """Our searcher with the fitted linear eval (P: theta file, ha, hb, budget, depth, pw, pc)."""

    def __init__(self, seat):
        self.seat = seat
        pw, pc = int(round(P.get("pw", 6))), int(round(P.get("pc", 3)))
        own, w, c = [-3] * 225, [pw] * 225, [pc] * 225
        own[0], own[224] = 0, 1
        w[0] = w[224] = c[0] = c[224] = 0
        self.mem = (own, w, c)
        cfg = json.load(open(P["theta"]))
        self.ha, self.hb = cfg.get("ha", 3), cfg.get("hb", 4)
        self.cfg = cfg
        self.theta = cfg.get("theta")

    def act(self, g, obs):
        t = {"blocked": g.get("blocked", 225), "w": g.get("w", 225), "c": g.get("c", 225),
             "owner": g.get("owner", 225), "energy": g.get("energy", 2), "score": g.get("score", 2),
             "remaining": g.get("remaining")}
        set_opponent_model(P.get("omk", 0), obs["opponent_profile"])
        set_qdepth(P.get("qd", 0))
        if "split" in self.cfg:
            self.theta = self.cfg["split"][f"{obs['opponent_profile']},{self.seat}"]
        return search_decide_fit(t, self.seat, self.theta, self.ha, self.hb, P.get("budget", 2048),
                                 P.get("depth", 4), self.mem)


class Plan:
    def __init__(self, seat, seed):
        self.tr = Tracker(seat)
        self.rng = random.Random(seed)
        self.base = FogNM(seat)

    def act(self, g, obs):
        tr = self.tr
        tr.update(obs)
        legal = obs["legal_actions"]
        late = P.get("late", 999)
        if obs["actions_remaining"] > late:
            a = self.base.act(g, obs)
            a = None if a < 0 else a
        elif len(legal) == 1:
            a = legal[0]
        else:
            E, F = P.get("E", 160), P.get("F", 9)
            if P.get("abl"):
                worlds = []
                for _ in range(P.get("m", 4)):
                    wd = sample_world(tr, obs, self.rng)
                    tw = {k: g.get(k, 225) for k in ("blocked", "w", "c", "owner", "mo", "mw", "mc")}
                    if P["abl"] == "terrain_true":  # true terrain, sampled champion placement
                        cs = [i for i in range(225) if wd["owner"][i] == 1 - obs["seat"]]
                        for k in ("blocked", "w", "c"):
                            wd[k] = tw[k]
                        for i in cs:  # sampled champion tiles must not be blocked
                            if wd["blocked"][i]:
                                wd["owner"][i] = -1
                        terr = [i for i in range(225) if wd["owner"][i] == 1 - obs["seat"]]
                        mo, mw, mc = [-3] * 225, [5] * 225, [3] * 225
                        mo[0], mo[224] = 0, 1
                        mw[0] = mw[224] = mc[0] = mc[224] = 0
                        vis = set(terr)
                        for i in terr:
                            vis.update(NB[i])
                        for i in vis:
                            mo[i] = -2 if wd["blocked"][i] else wd["owner"][i]
                            mw[i], mc[i] = wd["w"][i], wd["c"][i]
                        wd["mo"], wd["mw"], wd["mc"] = mo, mw, mc
                    elif P["abl"] == "owners_true":  # true owners+memory, sampled unseen terrain elsewhere
                        own = tw["owner"]
                        for i in range(225):
                            if own[i] != -1 or i in tr.seen:
                                for k in ("blocked", "w", "c"):
                                    wd[k][i] = tw[k][i]
                        wd["owner"], wd["mo"], wd["mw"], wd["mc"] = tw["owner"], tw["mo"], tw["mw"], tw["mc"]
                    elif P["abl"] == "mem_true":  # everything true except the champion memory (rebuilt)
                        mo = wd["mo"]
                        wd = dict(tw)
                        terr = [i for i in range(225) if wd["owner"][i] == 1 - obs["seat"]]
                        mo, mw, mc = [-3] * 225, [5] * 225, [3] * 225
                        mo[0], mo[224] = 0, 1
                        mw[0] = mw[224] = mc[0] = mc[224] = 0
                        vis = set(terr)
                        for i in terr:
                            vis.update(NB[i])
                        for i in vis:
                            mo[i] = -2 if wd["blocked"][i] else wd["owner"][i]
                            mw[i], mc[i] = wd["w"][i], wd["c"][i]
                        wd["mo"], wd["mw"], wd["mc"] = mo, mw, mc
                    worlds.append(Game.from_world(wd, obs))
            elif P.get("oracle", 0):
                wd = {k: g.get(k, 225) for k in ("blocked", "w", "c", "owner", "mo", "mw", "mc")}
                worlds = [Game.from_world(wd, obs)]
            else:
                worlds = [Game.from_world(sample_world(tr, obs, self.rng, P.get("mean", 0)), obs) for _ in range(P.get("m", 4))]
            b, mv, vals = worlds[0].om_nm(E, F, 1000000, 2)
            cands = [x for _, x in sorted(zip(vals, mv), reverse=True)[:P.get("k", 3)]]
            for wd in worlds:
                x = wd.negamax(E, F)
                if x not in cands:
                    cands.append(x)
            score = {}
            for x in cands:
                if P.get("H", 0):
                    ms = [wd.rollout_h(x, P["H"], E, F, P.get("rb", 512), 4) for wd in worlds]
                else:
                    ms = [wd.rollout(x, E, F, P.get("rb", 512), 4) for wd in worlds]
                if P.get("H", 0) or P.get("marg", 0):
                    score[x] = sum(ms) / len(ms)
                else:
                    score[x] = sum((m > 0) - (m < 0) for m in ms) / len(ms) + sum(ms) / len(ms) / 200
            a = max(cands, key=lambda x: score[x])
            a = None if a < 0 else a
        if obs["actions_remaining"] <= late:
            self.base.act(g, obs)  # keep the base agent's memory current
        tr.remember(obs, a)
        return -1 if a is None else a


def play(m):
    seat = m["seat"]
    g = Game(m, 1 - seat, m["profile"])
    ag = {"fognm": FogNM, "ext": Ext, "fit": Fit}[AGENT](seat) if AGENT != "plan" else Plan(seat, m["seed"])
    rec = [] if P.get("record") else None
    while g.get("remaining") > 0:
        if g.get("cur") == seat:
            a = ag.act(g, observe(g, seat))
            if rec is not None:
                t = {"blocked": g.get("blocked", 225), "w": g.get("w", 225), "c": g.get("c", 225),
                     "owner": g.get("owner", 225), "energy": g.get("energy", 2), "score": g.get("score", 2),
                     "remaining": g.get("remaining")}
                b, fr, fc = root_features(t, seat, P.get("fha", 3), P.get("fhb", 4), ag.mem, a)
                rec.append((b, fr))
                rec.append((b if g.get("remaining") - 1 > 0 else b, fc, g.get("remaining") - 1))
            g.apply(a)
        else:
            g.apply(g.champ())
    s = g.get("score", 2)
    if rec is not None:
        return m["arena"], seat, m["profile"], s[seat] - s[1 - seat], rec
    return m["arena"], seat, m["profile"], s[seat] - s[1 - seat]


if __name__ == "__main__":
    t = time.time()
    with mp.Pool(W) as pool:
        res = pool.map(play, MAPS, chunksize=1)
    n = len(res)
    wins = sum(r[3] > 0 for r in res)
    print(f"{AGENT} {P}: {wins}/{n} wins ({wins / n:.3f}) draws {sum(r[3] == 0 for r in res)} "
          f"margin {sum(r[3] for r in res) / n:+.1f} time {time.time() - t:.0f}s", flush=True)
    for s in (0, 1):
        sub = [r for r in res if r[1] == s]
        print(f"  seat {s}: {sum(r[3] > 0 for r in sub)}/{len(sub)}")
    for p in (0, 1, 2):
        sub = [r for r in res if r[2] == p]
        print(f"  profile {p}: {sum(r[3] > 0 for r in sub)}/{len(sub)} margin {sum(r[3] for r in sub) / max(1, len(sub)):+.1f}")
