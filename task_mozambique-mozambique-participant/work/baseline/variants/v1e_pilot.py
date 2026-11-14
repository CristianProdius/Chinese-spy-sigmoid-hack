"""Heuristic plan-and-simulate agent for "The Professor of Maputo Bay" (main.py format, stdlib only).

Idea: keep a per-boat queue of steps (go / take / drop / process / pick / deliver). A deterministic
own-side simulator runs the queues with the real one-action-per-round constraint (a dispatcher picks
which boat acts each round), so a plan can be scored by the rounds its deliveries land. Plans are
built by greedy insertion of projects (raw delivery, workshop kit, feed+craft, manufactured
delivery), valued by contract points if we arrive before the deadline and before our estimate of
the Professor's arrival. Each round we re-sync the simulator to the observation, drop steps that
became pointless, re-plan when needed, and play the dispatcher's action for this round.
"""
import json
import sys
import time

INF = 10 ** 9
T, F, M = 0, 1, 2
GO, TAKE, DROP, PROC, PICK, DELIV = 0, 1, 2, 3, 4, 5
NROUNDS = 80


# --------------------------------------------------------------------------- map / geometry
class Geo:
    def __init__(self, mp, home, ehome):
        R = mp['routes']
        n = len(R)
        self.n = n
        self.R = R
        self.roles = mp['roles']
        self.home = home
        self.ehome = ehome
        self.contracts = mp['contracts']
        # shortest paths with weight = 10*time + 3*hops (prefer fewer hops on ties)
        W = [[INF] * n for _ in range(n)]
        nxt = [[-1] * n for _ in range(n)]
        for i in range(n):
            W[i][i] = 0
            nxt[i][i] = i
            for j in range(n):
                if R[i][j] > 0:
                    W[i][j] = 10 * R[i][j] + 3
                    nxt[i][j] = j
        for k in range(n):
            Wk = W[k]
            for i in range(n):
                Wi = W[i]
                wik = Wi[k]
                if wik >= INF:
                    continue
                nik = nxt[i][k]
                for j in range(n):
                    v = wik + Wk[j]
                    if v < Wi[j]:
                        Wi[j] = v
                        nxt[i][j] = nik
        self.nxt = nxt
        self.dist = [[0] * n for _ in range(n)]
        self.hops = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if W[i][j] >= INF:
                    self.dist[i][j] = INF
                    self.hops[i][j] = INF
                    continue
                a, d, h = i, 0, 0
                while a != j:
                    b = nxt[a][j]
                    d += R[a][b]
                    h += 1
                    a = b
                self.dist[i][j] = d
                self.hops[i][j] = h
        self.tsites = [s for s in range(n) if self.roles[s] == 0]
        self.fsites = [s for s in range(n) if self.roles[s] == 1]
        self.msites = [s for s in range(n) if self.roles[s] == 2]
        self.natural = [s for s in range(n) if self.roles[s] in (0, 1)]
        self.mfg_contracts = [c for c, con in enumerate(self.contracts) if con['good'] == 2]


# --------------------------------------------------------------------------- simulator
class St:
    __slots__ = ('t', 'pos', 'arr', 'cargo', 'wh', 'ws', 'jobdone', 'stock', 'claims', 'nb')

    def copy(self):
        s = St.__new__(St)
        s.t = self.t
        s.pos = self.pos[:]
        s.arr = self.arr[:]
        s.cargo = [c[:] for c in self.cargo]
        s.wh = [w[:] for w in self.wh]
        s.ws = self.ws[:]
        s.jobdone = self.jobdone[:]
        s.stock = self.stock[:]
        s.claims = self.claims[:]
        s.nb = self.nb
        return s


def advance_round(s, geo):
    """Called at the start of round s.t (after s.t was incremented): job outputs and regen."""
    t = s.t
    jd = s.jobdone
    for site in range(geo.n):
        if jd[site] and jd[site] <= t:
            s.wh[site][M] += 1
            jd[site] = 0
    if t % 4 == 0:
        st = s.stock
        for site in geo.natural:
            if st[site] < 6:
                st[site] += 1


def step_action(s, geo, b, step):
    """Return (status, action) for boat b's step in state s.
    status: 0 = done/skip (no action needed), 1 = action available, 2 = blocked (wait)."""
    k = step[0]
    p = s.pos[b]
    if k == GO:
        tgt = step[1]
        if p == tgt:
            return 0, None
        return 1, ('sail', geo.nxt[p][tgt])
    cg = s.cargo[b]
    if k == TAKE:
        g, q = step[1], step[2]
        have = cg[g]
        if have >= q:
            return 0, None
        need = q - have
        free = 3 - cg[0] - cg[1] - cg[2]
        if free <= 0:
            return 0, None
        if need > free:
            need = free
        w = s.wh[p][g]
        if w > 0:
            return 1, ('load', g, need if w >= need else w)
        if geo.roles[p] == g:
            st = s.stock[p]
            if st >= need:
                return 1, ('gather', g, need)
            if st > 0 and s.t >= NROUNDS - 4:
                return 1, ('gather', g, st)
            return 2, None
        return 0, None    # nothing here: give up on this take
    if k == DROP:
        g, q = step[1], step[2]
        have = cg[g]
        if have <= 0:
            return 0, None
        return 1, ('unload', g, q if have >= q else have)
    if k == PROC:
        if p != step[1]:
            return 0, None
        w = s.wh[p]
        if w[0] >= 2 and w[1] >= 1:
            if not s.ws[p]:
                return 1, ('build',)
            if s.jobdone[p] == 0:
                return 1, ('craft',)
            return 2, None
        return 0, None
    if k == PICK:
        if cg[M] >= 1:
            return 0, None
        if cg[0] + cg[1] + cg[2] >= 3:
            return 0, None
        if s.wh[p][M] >= 1:
            return 1, ('load', M, 1)
        if s.jobdone[p]:
            return 2, None
        return 2, None
    if k == DELIV:
        c = step[1]
        if s.claims[c] != -1:
            return 0, None
        con = geo.contracts[c]
        if p != con['destination'] or s.t >= con['deadline']:
            return 0, None
        if cg[con['good']] >= con['quantity']:
            return 1, ('deliver', c)
        return 0, None
    return 0, None


def apply_action(s, geo, b, act):
    k = act[0]
    p = s.pos[b]
    if k == 'sail':
        d = act[1]
        s.arr[b] = s.t + geo.R[p][d]
        s.pos[b] = d
    elif k == 'load':
        g, q = act[1], act[2]
        s.wh[p][g] -= q
        s.cargo[b][g] += q
    elif k == 'gather':
        g, q = act[1], act[2]
        s.stock[p] -= q
        s.cargo[b][g] += q
    elif k == 'unload':
        g, q = act[1], act[2]
        s.wh[p][g] += q
        s.cargo[b][g] -= q
    elif k == 'build':
        w = s.wh[p]
        w[0] -= 2
        w[1] -= 1
        s.ws[p] = True
    elif k == 'craft':
        w = s.wh[p]
        w[0] -= 2
        w[1] -= 1
        s.jobdone[p] = s.t + 3
    elif k == 'deliver':
        c = act[1]
        con = geo.contracts[c]
        s.cargo[b][con['good']] -= con['quantity']
        s.claims[c] = 0   # ours (sim uses 0 = us)


ONESHOT = (DROP, PICK, DELIV)


def precompute(geo, q):
    """Per-index data for O(1) remaining-length estimates: (first GO index, non-GO count before it,
    static tail cost after it)."""
    n = len(q)
    dist = geo.dist
    tail = [0] * (n + 1)
    # previous GO target for each index (static part)
    prevt = [-1] * n
    last = -1
    for j in range(n):
        prevt[j] = last
        if q[j][0] == GO:
            last = q[j][1]
    for j in range(n - 1, -1, -1):
        st = q[j]
        if st[0] == GO:
            pt = prevt[j]
            tail[j] = tail[j + 1] + (dist[pt][st[1]] if pt >= 0 else 0)
        else:
            tail[j] = tail[j + 1] + 1
    firstgo = [-1] * (n + 1)
    nongo = [0] * (n + 1)
    fg = -1
    cnt = 0
    for j in range(n - 1, -1, -1):
        if q[j][0] == GO:
            fg = j
            cnt = 0
        else:
            cnt += 1
        firstgo[j] = fg
        nongo[j] = cnt
    return firstgo, nongo, tail


def rem_len(geo, s, b, q, i, pre):
    firstgo, nongo, tail = pre
    w = s.arr[b] - s.t
    if w < 0:
        w = 0
    fg = firstgo[i]
    if fg < 0:
        return w + (len(q) - i)
    return w + nongo[i] + geo.dist[s.pos[b]][q[fg][1]] + tail[fg + 1]


def mfg_demand(s, geo):
    t = s.t + 3
    for c in geo.mfg_contracts:
        if s.claims[c] == -1 and geo.contracts[c]['deadline'] > t:
            return True
    return False


def choose(s, geo, queues, idxs, pres):
    """Skip no-op steps (advancing idxs) and pick (boat, action, step_kind) for this round, or None.
    Priorities: deliveries first, then opportunistic crafting at a built workshop, then the boat
    with the longest remaining queue."""
    best = None
    bestkey = -1
    demand = None
    for b in range(s.nb):
        if s.arr[b] > s.t:
            continue
        p = s.pos[b]
        if s.ws[p] and s.jobdone[p] == 0:
            w = s.wh[p]
            if w[0] >= 2 and w[1] >= 1:
                if demand is None:
                    demand = mfg_demand(s, geo)
                if demand:
                    key = 100000 + 3 - b
                    if key > bestkey:
                        bestkey = key
                        best = (b, ('craft',), -1)
        q = queues[b]
        i = idxs[b]
        n = len(q)
        stt = 0
        act = None
        while i < n:
            stt, act = step_action(s, geo, b, q[i])
            if stt == 0:
                i += 1
                continue
            break
        idxs[b] = i
        if i >= n or stt != 1:
            continue
        kind = q[i][0]
        if kind == DELIV:
            key = 200000 + 3 - b
        elif kind == PICK and PARAMS['pick_prio']:
            key = 50000 + 3 - b
        else:
            key = rem_len(geo, s, b, q, i, pres[b]) * 4 + 3 - b
        if key > bestkey:
            bestkey = key
            best = (b, act, kind)
    return best


def simulate(s0, geo, queues, idxs0, until=NROUNDS, first=None):
    """Run queues from state s0 (start of round s0.t, not yet played).
    `first` forces this round's (boat, action, kind). Returns (deliveries {c: round}, final state,
    finish round per boat)."""
    s = s0.copy()
    idxs = idxs0[:]
    deliv = {}
    nb = s.nb
    fin = [s.t] * nb
    pres = [precompute(geo, q) for q in queues]
    while s.t < until:
        if first is not None:
            ch = first
            first = None
        else:
            ch = choose(s, geo, queues, idxs, pres)
        if ch is not None:
            b, act, kind = ch
            if act[0] == 'deliver':
                deliv[act[1]] = s.t
            apply_action(s, geo, b, act)
            if kind in ONESHOT:
                idxs[b] += 1
            fin[b] = s.t + 1
        else:
            # nothing can act this round: jump to the next event (arrival, job output, regen)
            te = INF
            take_blocked = False
            for b in range(nb):
                a = s.arr[b]
                if a > s.t:
                    if a < te:
                        te = a
                elif idxs[b] < len(queues[b]) and queues[b][idxs[b]][0] == TAKE:
                    take_blocked = True
            for x in s.jobdone:
                if x and x < te:
                    te = x
            if take_blocked:
                r = (s.t // 4 + 1) * 4
                if r < te:
                    te = r
            if te >= INF:
                break
            if te > until:
                te = until
            while s.t < te - 1:
                s.t += 1
                advance_round(s, geo)
        s.t += 1
        advance_round(s, geo)
    for b in range(nb):
        if s.arr[b] > fin[b]:
            fin[b] = s.arr[b]
    return deliv, s, fin


# --------------------------------------------------------------------------- planning
class Planner:
    """Greedy project insertion. win(c, t) -> probability we keep contract c delivered at round t."""

    def __init__(self, geo, home, win):
        self.geo = geo
        self.home = home
        self.win = win
        self.sims = 0
        self.ntgt = 2
        self.nbulk = 2

    def value(self, deliv):
        geo = self.geo
        v = 0.0
        for c, t in deliv.items():
            v += geo.contracts[c]['points'] * self.win(c, t) - 0.01 * t
        return v

    def best_pair(self, p, m):
        """Nearest (timber site, fibre site) pair for a trip p -> ts/fs -> m."""
        geo = self.geo
        dist = geo.dist
        best = None
        for ts in geo.tsites:
            for fs in geo.fsites:
                c = min(dist[p][ts] + dist[ts][fs] + dist[fs][m], dist[p][fs] + dist[fs][ts] + dist[ts][m])
                c += geo.hops[p][ts] + geo.hops[ts][fs] + geo.hops[fs][m]
                if best is None or c < best[0]:
                    best = (c, ts, fs)
        return None if best is None else (best[1], best[2])

    def feed_steps(self, pair, p, m):
        ts, fs = pair
        dist = self.geo.dist
        if ts == fs:
            st = [(GO, ts), (TAKE, T, 2), (TAKE, F, 1)]
        elif dist[p][ts] + dist[ts][fs] + dist[fs][m] <= dist[p][fs] + dist[fs][ts] + dist[ts][m]:
            st = [(GO, ts), (TAKE, T, 2), (GO, fs), (TAKE, F, 1)]
        else:
            st = [(GO, fs), (TAKE, F, 1), (GO, ts), (TAKE, T, 2)]
        return st + [(GO, m), (DROP, T, 2), (DROP, F, 1), (PROC, m)]

    def end_pos(self, s, q, b):
        p = s.pos[b]
        for st in q:
            if st[0] == GO:
                p = st[1]
        return p

    def candidates(self, s, qs):
        """Candidate projects: list of (name, front_ok, [(group, boat, steps), ...]).
        Parts in the same group share a tag (kept or dropped together)."""
        geo = self.geo
        home = self.home
        nb = s.nb
        n = geo.n
        dist = geo.dist
        targeted = set()
        planned_ws = set()
        for b in range(nb):
            for st in qs[b]:
                if st[0] == DELIV:
                    targeted.add(st[1])
                elif st[0] == PROC:
                    planned_ws.add(st[1])
        open_c = [c for c in range(len(geo.contracts)) if s.claims[c] == -1 and c not in targeted
                  and geo.contracts[c]['deadline'] > s.t + 1]
        ws_sites = [m for m in geo.msites if s.ws[m] or m in planned_ws]
        free_ms = [m for m in geo.msites if m not in ws_sites]
        endp = [self.end_pos(s, qs[b], b) for b in range(nb)]
        hw = s.wh[home]
        out = []
        mfg_open = []
        for c in open_c:
            con = geo.contracts[c]
            g = con['good']
            d = con['destination']
            if g != M:
                srcs = (geo.tsites if g == T else geo.fsites)[:]
                for x in range(n):
                    if s.wh[x][g] >= 2:
                        srcs.append(x)
                for b in range(nb):
                    out.append((('raw', c, -1, b), True, [(0, b, [(GO, d), (DELIV, c)])]))
                    for src in srcs:
                        out.append((('raw', c, src, b), True, [(0, b, [(GO, src), (TAKE, g, 2), (GO, d), (DELIV, c)])]))
            else:
                mfg_open.append(c)
                for b in range(nb):
                    out.append((('mdel', c, -1, b), True, [(0, b, [(GO, d), (DELIV, c)])]))
                    for m in ws_sites:
                        out.append((('mdel', c, m, b), True, [(0, b, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]))
        if not mfg_open:
            return out
        tgt = sorted(mfg_open, key=lambda c: geo.contracts[c]['deadline'])[:self.ntgt]

        def nearest(sites, frm, k):
            return sorted(sites, key=lambda x: dist[frm][x])[:k]

        # workshop kit (A brings 3 T, B brings 1 T + 2 F) + first delivery + a follow-up feed/delivery
        if nb >= 2 and (not ws_sites or (PARAMS['second_ws'] and len(ws_sites) < 2)):
            for m in free_ms:
                fpair = self.best_pair(m, m)
                for b0 in range(nb):
                    for b1 in range(nb):
                        if b1 == b0:
                            continue
                        partA = []
                        if hw[T] >= 3:
                            partA.append(([(GO, home), (TAKE, T, 3)], 3))
                        for x in nearest(geo.tsites, endp[b0], 2):
                            partA.append(([(GO, x), (TAKE, T, 3)], 0))
                        for stA, usedT in partA:
                            partB = []
                            if hw[T] - usedT >= 1 and hw[F] >= 2:
                                partB.append([(GO, home), (TAKE, T, 1), (TAKE, F, 2)])
                            else:
                                fs = nearest(geo.fsites, endp[b1], 1)[0]
                                if hw[T] - usedT >= 1:
                                    partB.append([(GO, home), (TAKE, T, 1), (GO, fs), (TAKE, F, 2)])
                                else:
                                    ts = nearest(geo.tsites, fs, 1)[0]
                                    partB.append([(GO, fs), (TAKE, F, 2), (GO, ts), (TAKE, T, 1)])
                            for stB in partB:
                                kA = stA + [(GO, m), (DROP, T, 3), (PROC, m)]
                                kB = stB + [(GO, m), (DROP, T, 1), (DROP, F, 2), (PROC, m)]
                                for c in tgt:
                                    d = geo.contracts[c]['destination']
                                    c2 = [x for x in tgt if x != c]
                                    for bd in (b0, b1):
                                        parts = [(0, b0, kA), (0, b1, kB), (1, bd, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]
                                        if PARAMS['kit_follow'] and c2 and fpair is not None:
                                            bf = b1 if bd == b0 else b0
                                            d2 = geo.contracts[c2[0]]['destination']
                                            parts.append((2, bf, self.feed_steps(fpair, m, m) + [(GO, m), (PICK,), (GO, d2), (DELIV, c2[0])]))
                                        out.append((('kit', c, m, bd), False, parts))
        # feeds to an existing/planned workshop + a delivery
        for m in ws_sites:
            for b in range(nb):
                p = endp[b]
                feeds = []
                pairs = []
                if hw[T] >= 2 and hw[F] >= 1:
                    pairs.append((dist[p][home] + dist[home][m], home, home))
                for ts in geo.tsites:
                    for fs in geo.fsites:
                        c1 = dist[p][ts] + dist[ts][fs] + dist[fs][m]
                        c2 = dist[p][fs] + dist[fs][ts] + dist[ts][m]
                        pairs.append((min(c1, c2), ts, fs))
                pairs.sort()
                for _, ts, fs in pairs[:2]:
                    if ts == fs:
                        st = [(GO, ts), (TAKE, T, 2), (TAKE, F, 1)]
                    elif dist[p][ts] + dist[ts][fs] + dist[fs][m] <= dist[p][fs] + dist[fs][ts] + dist[ts][m]:
                        st = [(GO, ts), (TAKE, T, 2), (GO, fs), (TAKE, F, 1)]
                    else:
                        st = [(GO, fs), (TAKE, F, 1), (GO, ts), (TAKE, T, 2)]
                    feeds.append(st + [(GO, m), (DROP, T, 2), (DROP, F, 1), (PROC, m)])
                # bulk trips: 3 of one good
                for g, sites in ((T, geo.tsites), (F, geo.fsites)):
                    srcs = sorted(sites, key=lambda x: dist[p][x] + dist[x][m])[:self.nbulk]
                    if hw[g] >= 3:
                        srcs = [home] + srcs[:self.nbulk - 1]
                    for x in srcs:
                        feeds.append([(GO, x), (TAKE, g, 3), (GO, m), (DROP, g, 3), (PROC, m)])
                for st in feeds:
                    for c in tgt:
                        d = geo.contracts[c]['destination']
                        for bd in range(nb):
                            out.append((('feed', c, m, b, bd), False, [(0, b, st), (1, bd, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]))
        return out

    def scan(self, s, qs, lock, base, basefin, budget):
        """Evaluate every candidate insertion; returns ([(key, parts, front, deliv, fin)], sims used)."""
        geo = self.geo
        z = [0] * s.nb
        res = []
        used = 0
        for name, front_ok, parts in self.candidates(s, qs):
            for front in (False, True):
                if front and (not front_ok or all(lock[b] == len(qs[b]) for _, b, _ in parts)):
                    continue
                nq = [q[:] for q in qs]
                if front:
                    for _, b, steps in reversed(parts):
                        nq[b][lock[b]:lock[b]] = steps
                else:
                    for _, b, steps in parts:
                        nq[b].extend(steps)
                d2, s2, f2 = simulate(s, geo, nq, z)
                used += 1
                gain = self.value(d2) - base
                if gain <= 0.05:
                    continue
                res.append((gain - 0.03 * (max(f2) - basefin), parts, front, d2, f2))
            if used >= budget:
                break
        return res, used

    @staticmethod
    def apply(qs, tags, parts, front, lock, next_tag):
        if front:
            for grp, b, steps in reversed(parts):
                qs[b][lock[b]:lock[b]] = steps
                tags[b][lock[b]:lock[b]] = [next_tag + grp] * len(steps)
        else:
            for grp, b, steps in parts:
                qs[b].extend(steps)
                tags[b].extend([next_tag + grp] * len(steps))
        return next_tag + 4

    def greedy(self, s, qs, tags, next_tag, budget=1200, max_iter=6, pilot_k=0, lock=None):
        """Insert projects greedily, each either at the end of a boat's queue or right after its
        locked prefix (the started projects present on entry). With pilot_k > 0 the first insertion
        is chosen among the top pilot_k candidates by completing each greedily.
        Returns (qs, tags, next_tag)."""
        geo = self.geo
        nb = s.nb
        z = [0] * nb
        if lock is None:
            lock = [len(q) for q in qs]
        deliv, sf, fin = simulate(s, geo, qs, z)
        self.sims += 1
        base = self.value(deliv)
        basefin = max(fin)
        used = 0
        if pilot_k > 0 and max_iter > 0:
            res, u = self.scan(s, qs, lock, base, basefin, budget)
            used += u
            res.sort(key=lambda r: -r[0])
            best = None
            per = max(200, (budget - used) // max(1, min(pilot_k, len(res))))
            for key, parts, front, d2, f2 in res[:pilot_k]:
                q2 = [q[:] for q in qs]
                t2 = [x[:] for x in tags]
                nt = self.apply(q2, t2, parts, front, lock, next_tag)
                q2, t2, nt = self.greedy(s, q2, t2, nt, budget=per, max_iter=max_iter - 1, lock=lock)
                d3, s3, f3 = simulate(s, geo, q2, z)
                v = self.value(d3) - 0.001 * max(f3)
                if best is None or v > best[0]:
                    best = (v, q2, t2, nt)
            self.sims += used
            if best is None:
                return qs, tags, next_tag
            return best[1], best[2], best[3]
        for _ in range(max_iter):
            res, u = self.scan(s, qs, lock, base, basefin, budget - used)
            used += u
            if not res:
                break
            key, parts, front, deliv, fin = max(res, key=lambda r: r[0])
            next_tag = self.apply(qs, tags, parts, front, lock, next_tag)
            base = self.value(deliv)
            basefin = max(fin)
            if used >= budget:
                break
        self.sims += used
        return qs, tags, next_tag


# --------------------------------------------------------------------------- observation sync
def sync_state(obs, geo, mem):
    own = obs['own']
    s = St.__new__(St)
    t = obs['round']
    s.t = t
    boats = own['boats']
    s.nb = len(boats)
    s.pos = []
    s.arr = []
    s.cargo = []
    for bt in boats:
        dst = bt.get('destination')
        if dst is not None and dst >= 0:
            s.pos.append(dst)
            s.arr.append(t + bt['eta'])
        else:
            s.pos.append(bt['position'])
            s.arr.append(t)
        s.cargo.append(list(bt['cargo']))
    s.wh = [list(w) for w in own['warehouses']]
    s.ws = list(own['workshops'])
    s.jobdone = [(t + j) if j else 0 for j in own['jobs']]
    est = mem['stock_est']
    seen = mem['stock_seen']
    stocks = obs['stocks']
    vis = obs['visible']
    for site in geo.natural:
        v = stocks[site]
        if v is not None and vis[site]:
            est[site] = v
            seen[site] = t
        elif t > 0 and t % 4 == 0 and est[site] < 6:
            est[site] += 1
    s.stock = est[:]
    seat = obs['seat']
    s.claims = [(-1 if c == -1 else (0 if c == seat else 1)) for c in obs['claims']]
    return s


def fresh_state(geo, home, t=0):
    s = St.__new__(St)
    s.t = t
    s.nb = 2
    s.pos = [home, home]
    s.arr = [t, t]
    s.cargo = [[0, 0, 0], [0, 0, 0]]
    s.wh = [[0, 0, 0] for _ in range(geo.n)]
    s.wh[home] = [5, 3, 0]
    s.ws = [False] * geo.n
    s.jobdone = [0] * geo.n
    s.stock = [4 if geo.roles[x] in (0, 1) else 0 for x in range(geo.n)]
    s.claims = [-1] * len(geo.contracts)
    return s


def single_lb(mp, home):
    """Earliest delivery round of each contract for a side at `home` doing only that contract."""
    geo = Geo(mp, home, home)
    s = fresh_state(geo, home)
    out = []
    for c, con in enumerate(geo.contracts):
        g, d = con['good'], con['destination']
        best = INF
        if g != M:
            for src in [home] + (geo.tsites if g == T else geo.fsites):
                q = [[(GO, src), (TAKE, g, 2), (GO, d), (DELIV, c)], []]
                dl, _, _ = simulate(s, geo, q, [0, 0])
                if c in dl:
                    best = min(best, dl[c])
        else:
            for m in geo.msites:
                for b0 in (0, 1):
                    q = [None, None]
                    q[b0] = [(TAKE, T, 3), (GO, m), (DROP, T, 3), (PROC, m)]
                    q[1 - b0] = [(TAKE, T, 1), (TAKE, F, 2), (GO, m), (DROP, T, 1), (DROP, F, 2), (PROC, m)]
                    for bd in (0, 1):
                        qq = [q[0][:], q[1][:]]
                        qq[bd] += [(GO, m), (PICK,), (GO, d), (DELIV, c)]
                        dl, _, _ = simulate(s, geo, qq, [0, 0])
                        if c in dl:
                            best = min(best, dl[c])
        out.append(best if best < INF else None)
    return out


def professor_model(mp, ehome):
    """Plan the Professor's game with our own planner (no opponent): contract -> planned round."""
    geo = Geo(mp, ehome, ehome)
    s = fresh_state(geo, ehome)
    pl = Planner(geo, ehome, lambda c, t: 1.0)
    qs, tags, _ = pl.greedy(s, [[], []], [[], []], 0, budget=3000, max_iter=10)
    deliv, _, _ = simulate(s, geo, qs, [0, 0])
    return [deliv.get(c) for c in range(len(geo.contracts))]


# --------------------------------------------------------------------------- agent
PARAMS = dict(replan_every=5, surv_pow=1.0, margin_w=0.0, pilot_k=6, pilot_k_later=0, budget0=8000, lookahead=True, pick_prio=True, kit_follow=True, second_ws=True)

# P(Professor has not claimed contract c by its single-contract lower bound + x), measured with a
# passive opponent over 80 practice games (knots x: value). Contract order is fixed by the engine:
# raw T dl24, raw F dl40, raw T dl56, raw F dl72, manufactured dl40, 56, 72, 80.
SURV_KNOTS = [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 80]
SURV = [
    [0.81, 0.74, 0.70, 0.69, 0.68, 0.65, 0.62, 0.60, 0.57, 0.57, 0.57, 0.57, 0.57, 0.57],
    [0.93, 0.81, 0.74, 0.72, 0.69, 0.69, 0.69, 0.65, 0.57, 0.42, 0.36, 0.20, 0.20, 0.20],
    [0.90, 0.81, 0.72, 0.71, 0.70, 0.70, 0.70, 0.68, 0.64, 0.57, 0.53, 0.42, 0.20, 0.20],
    [0.97, 0.96, 0.85, 0.80, 0.75, 0.66, 0.60, 0.57, 0.56, 0.55, 0.47, 0.31, 0.14, 0.14],
    [1.00, 0.99, 0.96, 0.94, 0.93, 0.89, 0.80, 0.62, 0.50, 0.45, 0.45, 0.45, 0.45, 0.45],
    [1.00, 0.95, 0.86, 0.82, 0.76, 0.75, 0.68, 0.68, 0.53, 0.38, 0.30, 0.07, 0.07, 0.07],
    [1.00, 0.97, 0.96, 0.90, 0.88, 0.85, 0.82, 0.74, 0.69, 0.59, 0.51, 0.23, 0.06, 0.06],
    [1.00, 1.00, 0.99, 0.97, 0.93, 0.90, 0.89, 0.89, 0.80, 0.70, 0.66, 0.42, 0.12, 0.12],
]


def surv_table(row):
    out = []
    for x in range(81):
        k = 0
        while k + 1 < len(SURV_KNOTS) and SURV_KNOTS[k + 1] <= x:
            k += 1
        if k + 1 >= len(SURV_KNOTS):
            out.append(row[-1])
        else:
            x0, x1 = SURV_KNOTS[k], SURV_KNOTS[k + 1]
            out.append(row[k] + (row[k + 1] - row[k]) * (x - x0) / float(x1 - x0))
    return out


SURV_T = [surv_table(r) for r in SURV]


def make_win(mem, now):
    """win(c, t): our weight for delivering contract c at round t = P(Professor has not claimed it
    by t | not claimed by now), times (1 + margin_w * P(Professor would claim it eventually))."""
    lbp = mem['lbprof']
    tabs = mem['survtab']
    pw = PARAMS['surv_pow']
    mw = PARAMS['margin_w']
    cond = []
    mult = []
    for c in range(len(lbp)):
        x = now - lbp[c]
        tab = tabs[c]
        base = 1.0 if x < 0 else tab[min(x, 80)]
        base = max(base, 0.05)
        cond.append(base)
        mult.append(1.0 + mw * max(0.0, (base - tab[80]) / base))

    def win(c, t):
        x = t - lbp[c]
        if x < 0:
            return mult[c]
        v = tabs[c][x if x <= 80 else 80] / cond[c]
        if v > 1.0:
            v = 1.0
        if pw != 1.0:
            v = v ** pw
        return v * mult[c]
    return win


def to_action(b, act):
    k = act[0]
    if k == 'sail':
        return {'op': 'sail', 'boat': b, 'destination': act[1]}
    if k == 'load':
        return {'op': 'load', 'boat': b, 'good': act[1], 'quantity': act[2]}
    if k == 'gather':
        return {'op': 'gather', 'boat': b, 'good': act[1], 'quantity': act[2]}
    if k == 'unload':
        return {'op': 'unload', 'boat': b, 'good': act[1], 'quantity': act[2]}
    if k == 'build':
        return {'op': 'build_workshop', 'boat': b}
    if k == 'craft':
        return {'op': 'craft', 'boat': b}
    if k == 'deliver':
        return {'op': 'deliver', 'boat': b, 'contract': act[1]}
    return {'op': 'wait'}


def init_memory(obs, mem):
    mp = obs['map']
    seat = obs['seat']
    home = obs['own']['home']
    ehome = mp['homes'][1 - seat]
    geo = Geo(mp, home, ehome)
    mem['geo'] = geo
    mem['stock_est'] = [4 if geo.roles[x] in (0, 1) else 0 for x in range(geo.n)]
    mem['stock_seen'] = [0] * geo.n
    mem['qs'] = None
    mem['tags'] = None
    mem['next_tag'] = 0
    mem['started'] = set()
    mem['last_plan'] = -100
    mem['blocked'] = None
    lb = single_lb(mp, ehome)
    mem['lbprof'] = [x if x is not None else 200 for x in lb]
    std = [(0, 24), (1, 40), (0, 56), (1, 72), (2, 40), (2, 56), (2, 72), (2, 80)]
    tabs = []
    for c, con in enumerate(mp['contracts']):
        key = (con['good'], con['deadline'])
        tabs.append(SURV_T[std.index(key)] if key in std else SURV_T[4 if con['good'] == 2 else 1])
    mem['survtab'] = tabs


def drop_tags(qs, tags, dead):
    for b in range(len(qs)):
        keep = [i for i in range(len(qs[b])) if tags[b][i] not in dead]
        qs[b] = [qs[b][i] for i in keep]
        tags[b] = [tags[b][i] for i in keep]


def decide(obs, mem):
    if 'geo' not in mem:
        init_memory(obs, mem)
    geo = mem['geo']
    s = sync_state(obs, geo, mem)
    t = s.t
    nb = s.nb
    qs = mem['qs']
    tags = mem['tags']
    if qs is None:
        qs = [[] for _ in range(nb)]
        tags = [[] for _ in range(nb)]
    while len(qs) < nb:
        qs.append([])
        tags.append([])
    started = mem['started']
    # drop projects whose contract is gone
    dead = set()
    for b in range(nb):
        for i, st in enumerate(qs[b]):
            if st[0] == DELIV:
                c = st[1]
                if s.claims[c] != -1 or geo.contracts[c]['deadline'] <= t:
                    dead.add(tags[b][i])
    # boats stuck on a blocked step for long: drop their head project
    blocked = mem['blocked'] or [0] * nb
    while len(blocked) < nb:
        blocked.append(0)
    for b in range(nb):
        if blocked[b] >= 8 and qs[b]:
            dead.add(tags[b][0])
            blocked[b] = 0
    replan = bool(dead) or t - mem['last_plan'] >= PARAMS['replan_every']
    if dead:
        drop_tags(qs, tags, dead)
    for b in range(nb):
        if not qs[b]:
            replan = True
    if replan:
        # keep started projects, re-plan everything else
        notstarted = set()
        for b in range(nb):
            for tg in tags[b]:
                if tg not in started:
                    notstarted.add(tg)
        drop_tags(qs, tags, notstarted)
        planner = Planner(geo, geo.home, make_win(mem, t))
        budget = 1200
        pk = PARAMS['pilot_k'] if t == 0 else PARAMS['pilot_k_later']
        if t == 0:
            budget = PARAMS['budget0']
        if mem.get('cpu', 0.0) > 6.0:
            budget = 150
            pk = 0
        elif mem.get('cpu', 0.0) > 3.0:
            budget = 500
            pk = 0
        qs, tags, mem['next_tag'] = planner.greedy(s, qs, tags, mem['next_tag'], budget=budget, pilot_k=pk)
        mem['last_plan'] = t
    idxs = [0] * nb
    ch = choose(s, geo, qs, idxs, [precompute(geo, q) for q in qs])
    for b in range(nb):
        if idxs[b]:
            qs[b] = qs[b][idxs[b]:]
            tags[b] = tags[b][idxs[b]:]
    # one-step lookahead over which boat acts this round
    if ch is not None and PARAMS['lookahead']:
        opts = []
        demand = mfg_demand(s, geo)
        for b in range(nb):
            if s.arr[b] > t:
                continue
            p = s.pos[b]
            if demand and s.ws[p] and s.jobdone[p] == 0 and s.wh[p][0] >= 2 and s.wh[p][1] >= 1:
                opts.append((b, ('craft',), -1))
            if qs[b]:
                stt, act = step_action(s, geo, b, qs[b][0])
                if stt == 1:
                    opts.append((b, act, qs[b][0][0]))
        if len(opts) >= 2:
            win = make_win(mem, t)
            pl = Planner(geo, geo.home, win)
            z = [0] * nb
            bestv = None
            for o in opts:
                d, sf, fin = simulate(s, geo, qs, z, first=o)
                v = pl.value(d) - 0.001 * max(fin)
                if o == ch:
                    v += 1e-6
                if bestv is None or v > bestv:
                    bestv = v
                    best = o
            ch = best
    # blocked bookkeeping: an idle boat whose head step cannot act
    for b in range(nb):
        if qs[b] and s.arr[b] <= t and (ch is None or ch[0] != b):
            stt, _ = step_action(s, geo, b, qs[b][0])
            blocked[b] = blocked[b] + 1 if stt == 2 else 0
        else:
            blocked[b] = 0
    mem['blocked'] = blocked
    mem['qs'] = qs
    mem['tags'] = tags
    if ch is None:
        return {'op': 'wait'}
    b, act, kind = ch
    if qs[b] and kind != -1:
        started.add(tags[b][0])
        if kind in ONESHOT:
            qs[b] = qs[b][1:]
            tags[b] = tags[b][1:]
    return to_action(b, act)


def agent(observation, memory):
    legal = observation['legal_actions']
    t0 = time.process_time()
    try:
        a = decide(observation, memory)
        if a in legal:
            memory['cpu'] = memory.get('cpu', 0.0) + time.process_time() - t0
            return a
        memory['illegal'] = memory.get('illegal', 0) + 1
    except Exception as e:  # never crash
        print('agent error: %r' % (e,), file=sys.stderr)
        memory['qs'] = None
    memory['cpu'] = memory.get('cpu', 0.0) + time.process_time() - t0
    for x in legal:
        if x.get('op') == 'wait':
            return x
    return legal[0]


def serve():
    protocol = sys.stdout
    sys.stdout = sys.stderr          # print() for debugging goes to stderr, not the protocol
    memory = {}
    for line in sys.stdin:
        observation = json.loads(line)['observation']
        if observation['round'] == 0:
            memory = {}
        protocol.write(json.dumps(agent(observation, memory)) + '\n')
        protocol.flush()


if __name__ == '__main__':
    serve()
