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


def rem_len(geo, s, b, queue, idx):
    """Rough remaining duration of a boat's queue (travel time + 1 per non-travel step)."""
    p = s.pos[b]
    tot = s.arr[b] - s.t
    if tot < 0:
        tot = 0
    dist = geo.dist
    for i in range(idx, len(queue)):
        st = queue[i]
        if st[0] == GO:
            tot += dist[p][st[1]]
            p = st[1]
        else:
            tot += 1
    return tot


def choose(s, geo, queues, idxs):
    """Skip no-op steps (advancing idxs) and pick (boat, action, step_kind) for this round, or None."""
    best = None
    bestkey = -1
    for b in range(s.nb):
        if s.arr[b] > s.t:
            continue
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
        key = rem_len(geo, s, b, q, i) * 4 + (3 - b if b < 3 else 0)
        if key > bestkey:
            bestkey = key
            best = (b, act, q[i][0])
    return best


def simulate(s0, geo, queues, idxs0, until=NROUNDS):
    """Run queues from state s0 (start of round s0.t, not yet played).
    Returns (deliveries {c: round}, final state, finish round per boat)."""
    s = s0.copy()
    idxs = idxs0[:]
    deliv = {}
    nb = s.nb
    fin = [s.t] * nb
    while s.t < until:
        ch = choose(s, geo, queues, idxs)
        if ch is not None:
            b, act, kind = ch
            if act[0] == 'deliver':
                deliv[act[1]] = s.t
            apply_action(s, geo, b, act)
            if kind in ONESHOT:
                idxs[b] += 1
            fin[b] = s.t + 1
        else:
            done = True
            for b in range(nb):
                if idxs[b] < len(queues[b]):
                    done = False
                    break
            if done:
                break
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

    def value(self, deliv):
        geo = self.geo
        v = 0.0
        for c, t in deliv.items():
            v += geo.contracts[c]['points'] * self.win(c, t) - 0.01 * t
        return v

    def end_pos(self, s, q, b):
        p = s.pos[b]
        for st in q:
            if st[0] == GO:
                p = st[1]
        return p

    def candidates(self, s, qs):
        geo = self.geo
        home = self.home
        nb = s.nb
        n = geo.n
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
        out = []
        mfg_open = []
        for c in open_c:
            con = geo.contracts[c]
            g = con['good']
            d = con['destination']
            if g != M:
                srcs = [home] + (geo.tsites if g == T else geo.fsites)
                for x in range(n):
                    if x != home and s.wh[x][g] >= 2:
                        srcs.append(x)
                for b in range(nb):
                    out.append((('raw', c, -1, b), [(0, b, [(GO, d), (DELIV, c)])]))
                    for src in srcs:
                        out.append((('raw', c, src, b), [(0, b, [(GO, src), (TAKE, g, 2), (GO, d), (DELIV, c)])]))
            else:
                mfg_open.append(c)
                for b in range(nb):
                    out.append((('mdel', c, -1, b), [(0, b, [(GO, d), (DELIV, c)])]))
                    for m in ws_sites:
                        out.append((('mdel', c, m, b), [(0, b, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]))
        if not mfg_open:
            return out
        # workshop kit from home + first delivery
        if nb >= 2 and s.wh[home][T] >= 4 and s.wh[home][F] >= 2:
            for m in free_ms:
                for b0 in range(nb):
                    for b1 in range(nb):
                        if b1 == b0:
                            continue
                        k0 = [(GO, home), (TAKE, T, 3), (GO, m), (DROP, T, 3), (PROC, m)]
                        k1 = [(GO, home), (TAKE, T, 1), (TAKE, F, 2), (GO, m), (DROP, T, 1), (DROP, F, 2), (PROC, m)]
                        for c in mfg_open:
                            d = geo.contracts[c]['destination']
                            for bd in (b0, b1):
                                out.append((('kit', c, m, bd), [(0, b0, k0), (0, b1, k1), (1, bd, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]))
        # feed 2T+1F to a workshop site + delivery
        dist = geo.dist
        for m in ws_sites:
            for b in range(nb):
                p = endp[b]
                pairs = []
                if s.wh[home][T] >= 2 and s.wh[home][F] >= 1:
                    pairs.append((dist[p][home] + dist[home][m], home, home))
                for ts in geo.tsites:
                    for fs in geo.fsites:
                        c1 = dist[p][ts] + dist[ts][fs] + dist[fs][m]
                        c2 = dist[p][fs] + dist[fs][ts] + dist[ts][m]
                        pairs.append((min(c1, c2), ts, fs))
                pairs.sort()
                for _, ts, fs in pairs[:3]:
                    if ts == fs:
                        st = [(GO, ts), (TAKE, T, 2), (TAKE, F, 1)]
                    elif dist[p][ts] + dist[ts][fs] + dist[fs][m] <= dist[p][fs] + dist[fs][ts] + dist[ts][m]:
                        st = [(GO, ts), (TAKE, T, 2), (GO, fs), (TAKE, F, 1)]
                    else:
                        st = [(GO, fs), (TAKE, F, 1), (GO, ts), (TAKE, T, 2)]
                    st = st + [(GO, m), (DROP, T, 2), (DROP, F, 1), (PROC, m)]
                    for c in mfg_open:
                        d = geo.contracts[c]['destination']
                        for bd in range(nb):
                            out.append((('feed', c, m, b, ts, fs, bd), [(0, b, st), (1, bd, [(GO, m), (PICK,), (GO, d), (DELIV, c)])]))
        return out

    def greedy(self, s, qs, tags, next_tag, budget=1200, max_iter=6):
        """Append projects greedily. qs/tags are modified copies; returns (qs, tags, next_tag)."""
        geo = self.geo
        nb = s.nb
        z = [0] * nb
        deliv, sf, fin = simulate(s, geo, qs, z)
        self.sims += 1
        base = self.value(deliv)
        basefin = max(fin)
        used = 0
        for _ in range(max_iter):
            best = None
            bestkey = None
            for name, parts in self.candidates(s, qs):
                nq = [q[:] for q in qs]
                for _, b, steps in parts:
                    nq[b].extend(steps)
                d2, s2, f2 = simulate(s, geo, nq, z)
                used += 1
                gain = self.value(d2) - base
                if gain <= 0.05:
                    continue
                key = gain - 0.03 * (max(f2) - basefin)
                if bestkey is None or key > bestkey:
                    bestkey = key
                    best = (parts, d2, f2)
                if used >= budget:
                    break
            if best is None:
                break
            parts, deliv, fin = best
            for grp, b, steps in parts:
                qs[b].extend(steps)
                tags[b].extend([next_tag + grp] * len(steps))
            next_tag += 2
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
PARAMS = dict(safe=2, late_p=0.15, tie_p=0.5, replan_every=5, push=4)


def make_win(mem):
    tp = mem['tprof']
    safe = PARAMS['safe']
    late_p = PARAMS['late_p']
    tie_p = PARAMS['tie_p']

    def win(c, t):
        x = tp[c]
        if x is None:
            return 1.0
        if t < x - safe:
            return 1.0
        if t <= x:
            return tie_p
        return late_p
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
    try:
        mem['tprof'] = professor_model(mp, ehome)
    except Exception:
        mem['tprof'] = [None] * len(mp['contracts'])
    mem['tprof0'] = list(mem['tprof'])


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
    # Professor estimate: if its expected time passed and the contract is still open, push it later
    tp = mem['tprof']
    for c in range(len(tp)):
        if tp[c] is not None and s.claims[c] == -1 and tp[c] < t:
            tp[c] = t + PARAMS['push']
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
        planner = Planner(geo, geo.home, make_win(mem))
        budget = 1200
        if mem.get('cpu', 0.0) > 6.0:
            budget = 150
        elif mem.get('cpu', 0.0) > 3.0:
            budget = 500
        qs, tags, mem['next_tag'] = planner.greedy(s, qs, tags, mem['next_tag'], budget=budget)
        mem['last_plan'] = t
    idxs = [0] * nb
    ch = choose(s, geo, qs, idxs)
    for b in range(nb):
        if idxs[b]:
            qs[b] = qs[b][idxs[b]:]
            tags[b] = tags[b][idxs[b]:]
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
    if qs[b]:
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
