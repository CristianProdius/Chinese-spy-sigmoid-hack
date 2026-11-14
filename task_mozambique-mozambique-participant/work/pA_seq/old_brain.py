# ---- brain: sequence planner with exact two-sided rollouts (uses names from core) ----
try:
    from core import *          # noqa: F401,F403  (stripped by build.py)
except ImportError:
    pass
import time as _time

BOAT_TOK = 8                    # pseudo contract: build the third boat
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


class Planner(Professor):
    """Our logistics decoder: the Professor's prepare() run on our own side."""

    def __init__(self, mp, seat):
        Professor.__init__(self, (1.8, 0.85, 0), seat)
        self.mp = mp

    def sim_of(self, side, stocks, claims, rnd):
        s = Sim.__new__(Sim)
        s.home = side.home
        s.score = side.score
        s.crafted = side.crafted
        s.boats = [b[:] for b in side.boats]
        s.wh = side.wh[:]
        s.ws = side.ws[:]
        s.jobs = side.jobs[:]
        s.stocks = stocks[:]
        s.claims = claims[:]
        s.round = 0                 # sequential clock; relative, so 160-round cap is not hit early
        s.ok = True
        s.acts = None
        s.memo = None
        return s

    def decode(self, side, stocks, claims, rnd, seq, B):
        """seq of tokens -> (per-boat queues, tokens kept)."""
        STATS['decodes'] += 1
        self.B = B
        s = self.sim_of(side, stocks, claims, rnd)
        # keep regeneration phase aligned with the real round
        s.round = rnd & 3
        kept = []
        for tok in seq:
            if tok == BOAT_TOK:
                if is_legal(self.mp, s, s.stocks, s.claims, s.round, BUILD_BOAT):
                    self.step(s, BUILD_BOAT)
                    kept.append(tok)
                continue
            if s.claims[tok] != -1:
                continue
            r = self.prepare(s, tok)
            if r is None:
                continue
            s = r
            kept.append(tok)
        queues = [[], [], []]
        for a in s.actions():
            if a[0] != 'wait':
                queues[a[1] if a[1] > 0 else 0].append(a)
        return queues, kept


class Plan(object):
    __slots__ = ('seq', 'B', 'var', 'queues', 'qi')

    def __init__(self, seq, B, var, queues):
        self.seq = list(seq)
        self.B = B
        self.var = var
        self.queues = queues
        self.qi = [0, 0, 0]

    def copy(self):
        p = Plan(self.seq, self.B, self.var, self.queues)
        p.qi = self.qi[:]
        return p

    def empty(self):
        q = self.queues
        qi = self.qi
        return qi[0] >= len(q[0]) and qi[1] >= len(q[1]) and qi[2] >= len(q[2])


def pick_order(mp, eng, seat, plan):
    """Dispatcher. Returns (order, boat queue index) or (WAIT, -1) or (None, -1) when the plan needs repair."""
    side = eng.sides[seat]
    claims = eng.claims
    rnd = eng.round
    stocks = eng.stocks
    queues = plan.queues
    qi = plan.qi
    chosen = -1
    chosen_o = None
    pending = False
    waiting_ok = False
    var = plan.var
    for i in range(3):
        b = (var + i) % 3
        q = queues[b]
        k = qi[b]
        if k >= len(q):
            continue
        o = q[k]
        pending = True
        op = o[0]
        if op == 'deliver':
            c = o[5]
            if claims[c] != -1 or mp.c_deadline[c] <= rnd:
                return None, -1
        if is_legal(mp, side, stocks, claims, rnd, o):
            if op == 'deliver':
                return o, b
            if chosen < 0:
                chosen = b
                chosen_o = o
        else:
            if op == 'build_boat':
                continue
            boat = side.boats[o[1]] if o[1] < len(side.boats) else None
            if boat is None:
                waiting_ok = True            # boat not built yet
            elif boat[2] != 0:
                waiting_ok = True            # sailing
            elif op == 'gather' and mp.roles[boat[0]] == o[3] and 3 - (boat[3] + boat[4] + boat[5]) >= o[4]:
                waiting_ok = True            # stock short: regenerates
            elif (op == 'load' and o[3] == 2) or op == 'craft':
                if side.jobs[boat[0]] != 0:
                    waiting_ok = True
    if chosen >= 0:
        return chosen_o, chosen
    if pending and not waiting_ok:
        busy = False
        for boat in side.boats:
            if boat[2] != 0:
                busy = True
        for j in side.jobs:
            if j:
                busy = True
        if not busy:
            return None, -1
    return WAIT, -1


def rollout(eng, prof, plan, seat, planner, info=None, max_repairs=3, tail=None):
    """Plays eng (a private clone) to the end. Returns margin (our score - theirs)."""
    STATS['rollouts'] += 1
    mp = eng.mp
    ps = 1 - seat
    repairs = 0
    stall = 0
    orders = [None, None]
    claims = eng.claims
    while eng.round < 80:
        rnd = eng.round
        o, b = pick_order(mp, eng, seat, plan)
        if o is None:
            # repair: drop dead contracts, decode again from here
            if repairs < max_repairs:
                repairs += 1
                seq = [c for c in plan.seq if c == BOAT_TOK or (claims[c] == -1 and mp.c_deadline[c] > rnd)]
                side = eng.sides[seat]
                queues, kept = planner.decode(side, eng.stocks, claims, rnd, seq, plan.B)
                plan.seq = kept
                plan.queues = queues
                plan.qi = [0, 0, 0]
                o, b = pick_order(mp, eng, seat, plan)
            if o is None:
                plan.queues = [[], [], []]
                plan.qi = [0, 0, 0]
                plan.seq = []
                o = WAIT
                b = -1
        if o is WAIT:
            stall += 1
        po = prof.choose_e(eng)
        orders[seat] = o
        orders[ps] = po
        ok = eng.step(orders)
        if b >= 0:
            if ok[seat]:
                plan.qi[b] += 1
                if info is not None and o[0] == 'deliver':
                    info['ours'].append((o[5], rnd))
        if info is not None and po[0] == 'deliver' and ok[ps]:
            info['theirs'].append((po[5], rnd))
        if -1 not in claims:
            break
    if info is not None:
        info['repairs'] = repairs
        info['end'] = eng.round
    return eng.sides[seat].score - eng.sides[ps].score


# ---------------------------------------------------------------------------------------------
# timetable plans (sched.py) and their exact rollout
# ---------------------------------------------------------------------------------------------
try:
    from sched import *         # noqa: F401,F403  (stripped by build.py)
except ImportError:
    pass


class TPlan(object):
    __slots__ = ('seq', 'B', 'tt', 'pend')

    def __init__(self, seq, B, tt):
        self.seq = seq          # tokens still wanted, in priority order
        self.B = B
        self.tt = tt            # slot -> order
        self.pend = None

    def copy(self):
        return TPlan(self.seq, self.B, self.tt)


def make_tplan(mp, side, stocks, claims, rnd, seq, B):
    S, kept = decode_seq(mp, side, stocks, claims, rnd, seq, B)
    return TPlan(kept, B, S.timetable()), S


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
                seq = [c for c in seq if (c == BOAT_TOK and len(side.boats) < 3) or
                       (c != BOAT_TOK and claims[c] == -1 and dl[c] > rnd)]
                S, seq = decode_seq(mp, side, stocks, claims, rnd, seq, plan.B)
                tt = S.timetable()
                o = tt.get(rnd)
                if o is not None and not is_legal(mp, side, stocks, claims, rnd, o):
                    o = None
            else:
                tt = {}
                o = None
        if o is None:
            o = WAIT
        po = prof.choose_e(eng)
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
