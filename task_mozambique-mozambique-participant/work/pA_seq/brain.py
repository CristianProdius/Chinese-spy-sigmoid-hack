# ---- brain: sequence planner with exact two-sided rollouts (uses names from core) ----
try:
    from core import *          # noqa: F401,F403  (stripped by build.py)
except ImportError:
    pass
import time as _time

REPLAN_CACHE = {}
STATS = {'miss': 0, 'hit': 0, 'miss_t': 0.0, 'rollouts': 0, 'decodes': 0}


def clone_side(s):
    n = Side.__new__(Side)
    n.home = s.home
    n.score = s.score
    n.crafted = s.crafted
    n.boats = [b[:] for b in s.boats]
    n.wh = s.wh[:]
    n.ws = s.ws[:]
    n.jobs = s.jobs[:]
    return n


def clone_engine(e):
    n = Engine.__new__(Engine)
    n.mp = e.mp
    n.round = e.round
    n.sides = [clone_side(e.sides[0]), clone_side(e.sides[1])]
    n.stocks = e.stocks[:]
    n.claims = e.claims[:]
    return n


class CProf(Professor):
    """Professor with a replan cache (replans are pure functions of the key)."""

    def __init__(self, sid, seat):
        Professor.__init__(self, sid, seat)
        self.sid = sid

    def clone(self):
        p = CProf.__new__(CProf)
        p.B = self.B
        p.A = self.A
        p.W = self.W
        p.sid = self.sid
        p.seat = self.seat
        p.last_round = self.last_round
        p.est = self.est[:]
        p.plan = deque(self.plan)
        p.plan_contracts = self.plan_contracts
        p.mp = self.mp
        p.replans = 0
        return p

    def choose_e(self, eng):
        """Same as Professor.choose(eng.view(seat)) without building the View."""
        seat = self.seat
        rnd = eng.round
        mp = eng.mp
        side = eng.sides[seat]
        if rnd == 0:
            self.last_round = -1
            self.est = [4] * 10
            self.plan = deque()
            self.plan_contracts = ()
        self.mp = mp
        d = rnd // 4 if self.last_round < 0 else rnd // 4 - (self.last_round >> 2)
        est = self.est
        if d:
            for s in range(10):
                v = est[s] + d
                est[s] = 6 if v > 6 else v
        stocks = eng.stocks
        h = side.home
        est[h] = stocks[h]
        ws = side.ws
        for s in range(10):
            if ws[s]:
                est[s] = stocks[s]
        boats = side.boats
        for boat in boats:
            if boat[2] == 0:
                est[boat[0]] = stocks[boat[0]]
        self.last_round = rnd
        claims = eng.claims
        if self.plan:
            for c in self.plan_contracts:
                if claims[c] != -1 and claims[c] != seat:
                    self.plan = deque()
                    break
        if rnd >= 80:
            return WAIT
        c_dest = mp.c_dest
        c_dead = mp.c_deadline
        c_good = mp.c_good
        c_qty = mp.c_qty
        for b in range(len(boats)):
            boat = boats[b]
            if boat[2] != 0:
                continue
            pos = boat[0]
            for c in range(8):
                if (claims[c] == -1 and c_dest[c] == pos and c_dead[c] > rnd
                        and boat[3 + c_good[c]] >= c_qty[c]):
                    self.plan = deque()
                    self.plan_contracts = ()
                    return o_deliver(b, c)
        plan = self.plan
        if plan:
            o = plan[0]
            # the Professor's visible stocks: real where it is docked, which is all a gather needs
            if is_legal(mp, side, stocks, claims, rnd, o):
                return plan.popleft()
        key = (self.sid, rnd, tuple(est), tuple(claims), tuple(side.wh),
               tuple([x for bt in boats for x in bt]), tuple(side.jobs), tuple(ws))
        hit = REPLAN_CACHE.get(key)
        if hit is None:
            t0 = _time.perf_counter()
            v = View()
            v.mp = mp
            v.side = side
            v.round = rnd
            v.seat = seat
            v.claims = claims
            best = self.replan(v)
            if best is not None:
                hit = (tuple(best[0].actions()), tuple(best[1]))
            else:
                hit = ((), ())
            REPLAN_CACHE[key] = hit
            STATS['miss'] += 1
            STATS['miss_t'] += _time.perf_counter() - t0
        else:
            STATS['hit'] += 1
        acts = hit[0]
        if acts:
            self.plan_contracts = hit[1]
            if is_legal(mp, side, stocks, claims, rnd, acts[0]):
                self.plan = deque(acts)
                return self.plan.popleft()
        self.plan = deque()
        self.plan_contracts = ()     # note: engine keeps plan_contracts here; harmless (plan empty)
        return WAIT


if hasattr(Professor, 'replan_uncached'):
    # fastcore: the Professor has its own shared replan cache
    def new_prof(sid, seat):
        return Professor(sid, seat)

    def prof_choose(prof, eng):
        return prof.choose(eng.view(prof.seat))
else:
    def new_prof(sid, seat):
        return CProf(sid, seat)

    def prof_choose(prof, eng):
        return prof.choose_e(eng)


# ---------------------------------------------------------------------------------------------
# timetable plans (sched.py) and their exact rollout
# ---------------------------------------------------------------------------------------------
try:
    from tsched import *         # noqa: F401,F403  (stripped by build.py)
except ImportError:
    pass


class TPlan(object):
    __slots__ = ('seq', 'B', 'ahead', 'tt', 'deliv')

    def __init__(self, seq, B, ahead, tt, deliv=None):
        self.seq = seq          # tokens still wanted, in priority order
        self.B = B
        self.ahead = ahead
        self.tt = tt            # slot -> order
        self.deliv = deliv      # contract -> planned delivery slot


def make_tplan(mp, side, stocks, claims, rnd, seq, B, ahead=1):
    S, kept = decode_seq(mp, side, stocks, claims, rnd, seq, B, ahead)
    return TPlan(kept, B, ahead, S.timetable(), S.deliv), S


def live_tokens(mp, side, claims, rnd, seq):
    dl = mp.c_deadline
    return [c for c in seq if (c == BOAT_TOK and len(side.boats) < 3) or
            (c != BOAT_TOK and claims[c] == -1 and dl[c] > rnd)]


def rollout2(eng, prof, plan, seat, info=None, max_repairs=6):
    """Exact two-sided playout of a timetable plan (eng/prof/plan are private copies). Returns margin."""
    STATS['rollouts'] += 1
    mp = eng.mp
    ps = 1 - seat
    side = eng.sides[seat]
    claims = eng.claims
    stocks = eng.stocks
    orders = [None, None]
    tt = plan.tt
    seq = plan.seq
    repairs = 0
    dirty = False
    dl = mp.c_deadline
    while eng.round < 80:
        rnd = eng.round
        o = tt.get(rnd)
        if dirty or (o is not None and not is_legal(mp, side, stocks, claims, rnd, o)):
            dirty = False
            if repairs < max_repairs:
                repairs += 1
                seq = live_tokens(mp, side, claims, rnd, seq)
                S, seq = decode_seq(mp, side, stocks, claims, rnd, seq, plan.B, plan.ahead)
                tt = S.timetable()
                o = tt.get(rnd)
                if o is not None and not is_legal(mp, side, stocks, claims, rnd, o):
                    o = None
            else:
                tt = {}
                o = None
        if o is None:
            o = WAIT
        po = prof_choose(prof, eng)
        orders[seat] = o
        orders[ps] = po
        ok = eng.step(orders)
        if o is not WAIT:
            if not ok[seat]:
                dirty = True
            elif info is not None and o[0] == 'deliver':
                info['ours'].append((o[5], rnd))
        if po[0] == 'deliver' and ok[ps]:
            if info is not None:
                info['theirs'].append((po[5], rnd))
            if po[5] in seq:
                dirty = True
        if -1 not in claims:
            break
    if info is not None:
        info['repairs'] = repairs
    return side.score - eng.sides[ps].score


# ---------------------------------------------------------------------------------------------
# the agent
# ---------------------------------------------------------------------------------------------
import heapq as _heapq

import os as _os

TOTAL_BUDGET = 3.6          # seconds of CPU inside agent() per game that the search may use
HARD_BUDGET = 6.5           # CPU beyond this: stop tracking, play the timetable blindly
WALL_HARD = float(_os.environ.get('MAPUTO_WALL', '8.5'))   # same, wall clock (0 = off, for loaded dev boxes)
_clock = _time.process_time
FIRST_EXTRA = 3.0           # the first game of a process pays for JIT warm-up
_FIRST = [True]
PARAMS = ((3.5, 1), (0.0, 1))
ALL_PARAMS = ((3.5, 1), (0.0, 1), (3.5, 0), (1.8, 1))
BEAM_W = 4
BEAM_D = 6
TOPK = 5
ROLL_EMA = [0.06]           # CPU seconds per exact rollout, learned across games


def util(m):
    if m > 0:
        return 1000 + (m if m < 40 else 40)
    if m == 0:
        return 500
    return m if m > -40 else -40


class Hyp(object):
    __slots__ = ('sid', 'eng', 'prof', 'ok')


def proxy_margin(mp, seat, claims0, deliv, events):
    """Fungible-goods model of the Professor's reaction: its deliveries (events, sorted (t, c)) keep their
    times; one whose contract is gone moves to the nearest open contract for the same good."""
    cl = claims0[:]
    tcl = [0] * 8
    pts = mp.c_points
    good = mp.c_good
    dest = mp.c_dest
    dl = mp.c_deadline
    dist = mp.dist
    ours = []
    for c, t in deliv.items():
        if t >= 0:
            ours.append((t, c))
    ours.sort()
    heap = [(t, c, dest[c], 0) for (t, c) in events]
    _heapq.heapify(heap)
    us = 0
    th = 0
    i = 0
    n = len(ours)
    while i < n or heap:
        mine = False
        if i < n:
            if not heap:
                mine = True
            else:
                t1 = ours[i][0]
                t2 = heap[0][0]
                if t1 < t2 or (t1 == t2 and (t1 & 1) == seat):
                    mine = True
        if mine:
            t, c = ours[i]
            i += 1
            if cl[c] == -1 and t < dl[c]:
                cl[c] = seat
                tcl[c] = t
                us += pts[c]
            continue
        t, c, loc, hops = _heapq.heappop(heap)
        if cl[c] == -1 and t < dl[c]:
            cl[c] = 1 - seat
            tcl[c] = t
            th += pts[c]
            continue
        if hops >= 3:
            continue
        g = good[c]
        t0 = tcl[c] + 1
        if t0 < t:
            t0 = t
        best = -1
        bt = 999
        for c2 in range(8):
            if cl[c2] == -1 and good[c2] == g:
                t2 = t0 + dist[loc][dest[c2]] + 1
                if t2 < dl[c2] and t2 < bt:
                    bt = t2
                    best = c2
        if best >= 0:
            _heapq.heappush(heap, (bt, best, dest[best], hops + 1))
    return us - th


class Brain(object):
    def __init__(self, obs):
        self.mp = Map(obs['map'])
        self.seat = obs['seat']
        self.ps = 1 - self.seat
        self.hyps = []
        for sid in range(5):
            h = Hyp()
            h.sid = sid
            h.eng = Engine(self.mp)
            h.prof = new_prof(sid, self.ps)
            h.ok = True
            self.hyps.append(h)
        self.plan = None
        self.vals = {}          # sid -> exact margin of the incumbent plan
        self.events = {}        # sid -> sorted [(t, c)]: the Professor's deliveries in the incumbent scenario
        self.used = 0.0
        self.wall = 0.0
        self.budget = TOTAL_BUDGET + (FIRST_EXTRA if _FIRST[0] else 0.0)
        _FIRST[0] = False
        self.pool = []
        self.tested = set()
        self.beam_stale = True
        self.last_beam = -99
        self.blind = False
        self.nroll = 0
        self.nbeam = 0
        self.tm = {'track': 0.0, 'plans': 0.0, 'beam': 0.0, 'roll': 0.0}
        self.dirty_n = 0
        self.nb_done = False
        self.event = True

    # ---- tracking ---------------------------------------------------------------------------

    def consistent(self, obs, eng):
        seat = self.seat
        ps = self.ps
        if obs['opponent_score'] != eng.sides[ps].score:
            return False
        if obs['claims'] != eng.claims:
            return False
        own = obs['own']
        side = eng.sides[seat]
        ob = own['boats']
        if len(ob) != len(side.boats):
            return False
        for i in range(len(ob)):
            b = ob[i]
            sb = side.boats[i]
            if b['position'] != sb[0] or b['destination'] != sb[1] or b['eta'] != sb[2]:
                return False
            c = b['cargo']
            if c[0] != sb[3] or c[1] != sb[4] or c[2] != sb[5]:
                return False
        wh = own['warehouses']
        swh = side.wh
        for s in range(10):
            w = wh[s]
            if w[0] != swh[3 * s] or w[1] != swh[3 * s + 1] or w[2] != swh[3 * s + 2]:
                return False
        if own['score'] != side.score or own['jobs'] != side.jobs:
            return False
        stocks = obs['stocks']
        vis = obs['visible']
        es = eng.stocks
        for s in range(10):
            if vis[s] and stocks[s] is not None and stocks[s] != es[s]:
                return False
        exp = []
        eb = eng.sides[ps].boats
        for i in range(len(eb)):
            b = eb[i]
            if vis[b[0]] or (b[1] >= 0 and vis[b[1]]):
                exp.append((i, b[0], b[1], b[2]))
        got = [(b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats']]
        return exp == got

    # ---- exact evaluation -------------------------------------------------------------------

    def roll(self, plan, h, want_events):
        t0 = _clock()
        try:
            return self.roll_(plan, h, want_events)
        finally:
            dt = _clock() - t0
            self.tm['roll'] += dt
            ROLL_EMA[0] = 0.85 * ROLL_EMA[0] + 0.15 * dt

    def roll_(self, plan, h, want_events):
        eng = clone_engine(h.eng)
        prof = h.prof.clone()
        info = {'ours': [], 'theirs': []} if want_events else None
        m = rollout2(eng, prof, TPlan(plan.seq, plan.B, plan.ahead, plan.tt), self.seat, info)
        self.nroll += 1
        if want_events:
            ev = [(t, c) for (c, t) in info['theirs']]
            ev.sort()
            return m, ev
        return m, None

    def value(self, vals):
        lo = 99999
        tot = 0
        for h in self.hyps:
            u = util(vals[h.sid])
            tot += u
            if u < lo:
                lo = u
        return (lo, tot)

    def min_stocks(self):
        st = self.hyps[0].eng.stocks[:]
        for h in self.hyps[1:]:
            es = h.eng.stocks
            for s in range(10):
                if es[s] < st[s]:
                    st[s] = es[s]
        return st

    def decode(self, seq, B, ahead, rnd):
        h0 = self.hyps[0]
        side = h0.eng.sides[self.seat]
        claims = h0.eng.claims
        seq = live_tokens(self.mp, side, claims, rnd, seq)
        S, kept = decode_seq(self.mp, side, self.min_stocks(), claims, rnd, seq, B, ahead)
        return TPlan(kept, B, ahead, S.timetable(), S.deliv)

    # ---- proxy beam over token sequences ----------------------------------------------------

    def beam(self, rnd, tend):
        t0 = _clock()
        try:
            return self.beam_(rnd, tend)
        finally:
            self.tm['beam'] += _clock() - t0

    def beam_(self, rnd, tend):
        self.nbeam += 1
        mp = self.mp
        seat = self.seat
        h0 = self.hyps[0]
        side = h0.eng.sides[seat]
        claims = h0.eng.claims
        stocks = self.min_stocks()
        evs = [self.events.get(h.sid, ()) for h in self.hyps]
        base = side.score - h0.eng.sides[self.ps].score
        live = [c for c in range(8) if claims[c] == -1 and mp.c_deadline[c] > rnd + 1]
        out = {}
        perf = _clock
        for B, ahead in PARAMS:
            root = sched_root(mp, side, stocks, claims, rnd)
            frontier = [(root, ())]
            if len(side.boats) < 3 and B > 0:
                rb = root.add_boat()
                if rb is not None:
                    frontier.append((rb, (BOAT_TOK,)))
            for depth in range(BEAM_D):
                nxt = []
                for S, seq in frontier:
                    nm = 0
                    for c in live:
                        if c >= 4 and c not in S.deliv:
                            nm += 1
                    for c in live:
                        if c in S.deliv:
                            continue
                        more = 1 if (nm - (1 if c >= 4 else 0)) > 0 else 0
                        T = S.add(c, B, more, ahead)
                        if T is None:
                            continue
                        lo = 99999
                        tot = 0
                        for ev in evs:
                            u = util(base + proxy_margin(mp, seat, claims, T.deliv, ev))
                            tot += u
                            if u < lo:
                                lo = u
                        nxt.append((lo, tot, -T.nord, seq + (c,), T))
                    if perf() > tend:
                        break
                if not nxt:
                    break
                nxt.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
                for x in nxt:
                    out[(x[3], B, ahead)] = (x[0], x[1], x[2])
                frontier = [(x[4], x[3]) for x in nxt[:BEAM_W]]
                if perf() > tend:
                    break
        cands = sorted(out.items(), key=lambda kv: kv[1], reverse=True)
        return [k for k, _ in cands]

    # ---- one decision -----------------------------------------------------------------------

    def read_plans(self, rnd):
        """Cheap timelines: the deliveries each hypothesis' Professor has in its current plan."""
        evs = {}
        for h in self.hyps:
            p = h.prof.clone()
            o = prof_choose(p, h.eng)
            ev = []
            if o[0] == 'deliver':
                ev.append((rnd, o[5]))
            t = rnd + 1
            for o in p.plan:
                if o[0] == 'deliver':
                    ev.append((t, o[5]))
                t += 1
            evs[h.sid] = ev
        return evs

    def proxy_value(self, deliv, rnd):
        h0 = self.hyps[0]
        claims = h0.eng.claims
        base = h0.eng.sides[self.seat].score - h0.eng.sides[self.ps].score
        lo = 99999
        tot = 0
        for h in self.hyps:
            u = util(base + proxy_margin(self.mp, self.seat, claims, deliv, self.events.get(h.sid, ())))
            tot += u
            if u < lo:
                lo = u
        return (lo, tot)

    def neighbours(self, plan, rnd, tend):
        """Local moves around the incumbent, best proxy first."""
        mp = self.mp
        h0 = self.hyps[0]
        side = h0.eng.sides[self.seat]
        claims = h0.eng.claims
        seq = live_tokens(mp, side, claims, rnd, plan.seq)
        k = len(seq)
        keys = []
        for B, ahead in ALL_PARAMS:
            if B != plan.B or ahead != plan.ahead:
                keys.append((tuple(seq), B, ahead))
        for i in range(k - 1):
            s2 = seq[:]
            s2[i], s2[i + 1] = s2[i + 1], s2[i]
            keys.append((tuple(s2), plan.B, plan.ahead))
        for i in range(k):
            keys.append((tuple(seq[:i] + seq[i + 1:]), plan.B, plan.ahead))
        for i in range(1, k):
            keys.append((tuple([seq[i]] + seq[:i] + seq[i + 1:]), plan.B, plan.ahead))
        missing = [c for c in range(8) if claims[c] == -1 and mp.c_deadline[c] > rnd + 1 and c not in seq]
        if len(side.boats) < 3 and BOAT_TOK not in seq:
            missing.append(BOAT_TOK)
        for c in missing:
            for i in range(k + 1):
                keys.append((tuple(seq[:i] + [c] + seq[i:]), plan.B, plan.ahead))
        out = []
        seen = set()
        stocks = self.min_stocks()
        for key in keys:
            if key in seen or key in self.tested:
                continue
            seen.add(key)
            S, kept = decode_seq(mp, side, stocks, claims, rnd, list(key[0]), key[1], key[2])
            out.append((self.proxy_value(S.deliv, rnd), key))
            if _clock() > tend:
                break
        out.sort(reverse=True)
        return [key for _, key in out]

    def think(self, obs, tstart):
        perf = _clock
        rnd = obs['round']
        mp = self.mp
        seat = self.seat
        nh = len(self.hyps)
        left = self.budget - self.used
        h0 = self.hyps[0]
        side = h0.eng.sides[seat]
        claims = h0.eng.claims
        # repair the incumbent when the game left its timetable
        plan = self.plan
        if plan is not None:
            dirty = False
            for h in self.hyps:
                if not h.ok:
                    dirty = True
            for c in plan.seq:
                if c != BOAT_TOK and claims[c] != -1 and claims[c] != seat:
                    dirty = True
            o = plan.tt.get(rnd)
            if o is not None and not is_legal(mp, side, h0.eng.stocks, claims, rnd, o):
                dirty = True
            if dirty:
                self.plan = plan = self.decode(plan.seq, plan.B, plan.ahead, rnd)
                self.beam_stale = True
                self.nb_done = False
                self.dirty_n += 1
                self.event = True
        if plan is None:
            self.plan = plan = TPlan([], 3.5, 1, {}, {})
        if left <= 0.05:
            return
        open_c = False
        dl = mp.c_deadline
        for c in range(8):
            if claims[c] == -1 and dl[c] > rnd + 1:
                open_c = True
        if not open_c:
            return
        if rnd - self.last_beam >= 4 or not live_tokens(mp, side, claims, rnd, plan.seq):
            self.beam_stale = True
        event = rnd == 0 or self.event or self.beam_stale
        self.event = False
        if rnd == 0:
            tslice = min(1.2, left * 0.3)
        elif event:
            tslice = min(0.9, left * 0.22)
        else:
            tslice = min(0.08, left * 0.05)
        tend = tstart + tslice
        est = ROLL_EMA[0] * (2.0 if rnd < 8 else 1.0)
        if self.vals:
            exact = nh * est <= max(tslice, left * 0.12)      # keep an exact incumbent exact
        else:
            exact = event and ((nh == 1 and left > 0.3) or nh * est * 3.0 <= tslice
                               or (self.nroll == 0 and rnd >= 2 and nh * est <= left * 0.25))
        if not exact:
            # phase A: no rollouts; rank by the proxy against the plans the Professor holds right now
            self.vals = {}
            t0 = perf()
            evs = self.read_plans(rnd)
            self.tm['plans'] += perf() - t0
            if evs != self.events:
                self.events = evs
                self.beam_stale = True
            if self.beam_stale and left > 0.2:
                cands = self.beam(rnd, perf() + min(0.6, left * 0.3))
                self.beam_stale = False
                self.last_beam = rnd
                if cands:
                    seq, B, ahead = cands[0]
                    cand = self.decode(list(seq), B, ahead, rnd)
                    if self.proxy_value(cand.deliv, rnd) > self.proxy_value(plan.deliv, rnd):
                        self.plan = cand
            return
        # phase B: exact value of the incumbent against every live hypothesis (also gives timelines)
        for h in self.hyps:
            if h.sid not in self.vals:
                m, ev = self.roll(plan, h, True)
                self.vals[h.sid] = m
                self.events[h.sid] = ev
                self.beam_stale = True
        cur = self.value(self.vals)
        while perf() < tend:
            if not self.pool:
                if self.beam_stale:
                    self.pool = self.beam(rnd, tend + 0.2)[:TOPK]
                    self.beam_stale = False
                    self.last_beam = rnd
                    self.tested = set()
                    self.nb_done = False
                    if self.pool:
                        continue
                if not self.nb_done:
                    self.nb_done = True
                    self.pool = self.neighbours(plan, rnd, tend)[:TOPK + 3]
                    if self.pool:
                        continue
                break
            key = self.pool.pop(0)
            if key in self.tested:
                continue
            self.tested.add(key)
            seq, B, ahead = key
            cand = self.decode(list(seq), B, ahead, rnd)
            if cand.tt == plan.tt:
                continue
            vals = {}
            evs = {}
            ok = True
            order = sorted(self.hyps, key=lambda h: self.vals[h.sid])
            for h in order:
                m, ev = self.roll(cand, h, True)
                vals[h.sid] = m
                evs[h.sid] = ev
                if util(m) < cur[0]:
                    ok = False
                    break
            if ok and self.value(vals) > cur:
                self.plan = plan = cand
                self.vals = vals
                self.events = evs
                cur = self.value(vals)
                self.beam_stale = True
                self.nb_done = False

    def act(self, obs):
        perf = _clock
        t0 = perf()
        w0 = _time.perf_counter()
        rnd = obs['round']
        mp = self.mp
        seat = self.seat
        ps = self.ps
        legal = obs['legal_actions']
        if not self.blind:
            if rnd > 0:
                alive = [h for h in self.hyps if self.consistent(obs, h.eng)]
                if len(alive) != len(self.hyps):
                    self.hyps = alive
                    self.beam_stale = True
                    self.event = True
            if not self.hyps or self.used > HARD_BUDGET + self.budget - TOTAL_BUDGET or (WALL_HARD > 0 and self.wall > WALL_HARD):
                self.blind = True
        if self.blind:
            return self.blind_act(obs)
        try:
            self.think(obs, t0)
        except Exception:
            if DEBUG:
                raise
        h0 = self.hyps[0]
        o = None
        if self.plan is not None:
            o = self.plan.tt.get(rnd)
        act = None
        if o is not None:
            act = order_to_json(o)
            if act not in legal:
                act = None
        if act is None:
            o = WAIT
            act = legal[0]
        orders = [None, None]
        t1 = perf()
        for h in self.hyps:
            po = prof_choose(h.prof, h.eng)
            orders[seat] = o
            orders[ps] = po
            ok = h.eng.step(orders)
            h.ok = ok[seat] or o is WAIT
        self.tm['track'] += perf() - t1
        self.used += perf() - t0
        self.wall += _time.perf_counter() - w0
        return act

    def blind_act(self, obs):
        """No model left (all hypotheses dead or out of time): follow the timetable while it stays legal."""
        legal = obs['legal_actions']
        for a in legal:
            if a['op'] == 'deliver':
                return a
        if self.plan is not None:
            o = self.plan.tt.get(obs['round'])
            if o is not None:
                a = order_to_json(o)
                if a in legal:
                    return a
        return legal[0]


DEBUG = False
LAST_TM = None
_LAST_MAP = [None]


def agent(observation, memory):
    """Return one entry of observation['legal_actions']. `memory` resets each game."""
    legal = observation['legal_actions']
    try:
        if observation['round'] == 0 or 'brain' not in memory:
            if _LAST_MAP[0] != observation['map']:
                REPLAN_CACHE.clear()
                _LAST_MAP[0] = observation['map']
            elif len(REPLAN_CACHE) > 200000:
                REPLAN_CACHE.clear()
            memory['brain'] = Brain(observation) if observation['round'] == 0 else None
        brain = memory['brain']
        if brain is None:
            for a in legal:
                if a['op'] == 'deliver':
                    return a
            return legal[0]
        act = brain.act(observation)
        if observation['round'] == 79:
            global LAST_TM
            LAST_TM = dict((k, round(v, 2)) for k, v in brain.tm.items())
            LAST_TM['nroll'] = brain.nroll
            LAST_TM['nbeam'] = brain.nbeam
            LAST_TM['hyps'] = len(brain.hyps)
            LAST_TM['blind'] = brain.blind
            LAST_TM['dirty'] = brain.dirty_n
            LAST_TM['used'] = round(brain.used, 2)
        if act in legal:
            return act
    except Exception:
        if DEBUG:
            raise
    return legal[0]
