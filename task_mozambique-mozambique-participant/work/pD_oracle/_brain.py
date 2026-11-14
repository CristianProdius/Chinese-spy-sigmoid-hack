
# =============================================================================================
# Oracle agent: exact opponent tracking + Professor-style planner with foresight.
# =============================================================================================
import json
import sys
import time

PARAMS = dict(
    style=(1.8, 0.85, 0),      # our planner's (B, A, W)
    depth=4, width=8,
    lam=0.6,                   # extra value (fraction of points) for contracts the opponent would take
    use_fast=True,
    select='min', blend_w=1.0,
    replan_on_hyp_change=False,
    horizon=80, iters=3,
    replan_after_delivery=True,
    ext_depth=2, ext_width=4, ext_max=3,
    regen_wait=4,
    # candidate generators: (planner style (B, A, W), steal bonus, use predicted deadlines, top-k)
    cfgs=[((1.8, 0.85, 0), 0.6, True, 2), ((3.5, 0.0, 0), 0.6, True, 2),
          ((0.0, 0.85, 8), 0.6, True, 2), ((1.8, 1.15, 0), 0.6, True, 1),
          ((1.8, 0.85, 0), 0.0, False, 1),
          ((1.8, 0.85, 0), 0.6, True, 2, 'boat'), ((3.5, 0.0, 0), 0.6, True, 1, 'boat')],
    budget_soft=40.0,          # CPU s per game: above this, cheaper planning
    budget_hard=60.0,          # above this, no planning at all (follow plan / deliver / wait)
    first_extra=6.0,           # extra budget in the first game of a process (cold JIT)
)
_GAMES = [0]
try:
    import os as _os
    if _os.environ.get('PD_PARAMS'):
        for _k, _v in json.loads(_os.environ['PD_PARAMS']).items():
            if _k == 'cfgs':
                _v = [(tuple(x[0]),) + tuple(x[1:]) for x in _v]
            PARAMS[_k] = _v
except Exception:  # noqa: BLE001
    pass


def _load_fastcore():
    """The fast engine + Professor (work/fast/fastcore.py), embedded by build.sh as a string and
    executed into its own module namespace (its names clash with the reference core above)."""
    import types
    src = globals().get('_FASTCORE_SRC')
    if src is None:
        import os
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fast',
                                'fastcore.py')).read()
    m = types.ModuleType('fastcore_inline')
    exec(compile(src, 'fastcore_inline', 'exec'), m.__dict__)
    return m


try:
    F = _load_fastcore() if PARAMS.get('use_fast', True) else None
except Exception:  # noqa: BLE001
    F = None


def side_copy(s):
    n = Side.__new__(Side)
    n.home = s.home
    n.score = s.score
    n.crafted = s.crafted
    n.boats = [b[:] for b in s.boats]
    n.wh = s.wh[:]
    n.ws = s.ws[:]
    n.jobs = s.jobs[:]
    return n


def eng_copy(e):
    n = Engine.__new__(Engine)
    n.mp = e.mp
    n.round = e.round
    n.sides = [side_copy(e.sides[0]), side_copy(e.sides[1])]
    n.stocks = e.stocks[:]
    n.claims = e.claims[:]
    return n


_RC = {}          # opponent replan cache, cleared every game
STATS = {}
DEBUG = False
CHEAT = None


def _st(k, v=1):
    STATS[k] = STATS.get(k, 0) + v


class Opp(Professor):
    """The Professor, decision-for-decision identical, with a replan cache shared by all copies."""

    def clone(self):
        p = Opp.__new__(Opp)
        p.B = self.B
        p.A = self.A
        p.W = self.W
        p.seat = self.seat
        p.last_round = self.last_round
        p.est = self.est[:]
        p.plan = deque(self.plan)
        p.plan_contracts = self.plan_contracts[:]
        p.mp = self.mp
        p.replans = 0
        return p

    def choose(self, view):
        rnd = view.round
        if rnd == 0:
            self.last_round = -1
            self.est = [4] * 10
            self.plan.clear()
            self.plan_contracts = []
        self.mp = mp = view.mp
        self.seat = view.seat
        d = rnd // 4 if self.last_round < 0 else rnd // 4 - (self.last_round >> 2)
        est = self.est
        vis = view.visible
        vst = view.stocks
        for s in range(10):
            v = est[s] + d
            if v > 6:
                v = 6
            if vis[s]:
                v = vst[s]
            est[s] = v
        self.last_round = rnd
        claims = view.claims
        for c in self.plan_contracts:
            if claims[c] != -1 and claims[c] != self.seat:
                self.plan.clear()
        side = view.side
        if rnd >= 80:
            return WAIT
        for b, boat in enumerate(side.boats):
            if boat[2] != 0:
                continue
            pos = boat[0]
            for c in range(mp.ncontracts):
                if (claims[c] == -1 and mp.c_deadline[c] > rnd and mp.c_dest[c] == pos
                        and boat[3 + mp.c_good[c]] >= mp.c_qty[c]):
                    self.plan.clear()
                    self.plan_contracts = []
                    return o_deliver(b, c)
        if self.plan and is_legal(mp, side, vst, claims, rnd, self.plan[0]):
            return self.plan.popleft()
        self.plan.clear()
        self.plan_contracts = []
        key = (self.B, self.A, self.W, rnd, side.score, side.crafted,
               tuple([tuple(b) for b in side.boats]), tuple(side.wh), tuple(side.ws),
               tuple(side.jobs), tuple(est), tuple(claims))
        r = _RC.get(key, 0)
        if r == 0:
            _st('opp_replans')
            best = self.replan(view)
            r = (tuple(best[0].actions()), tuple(best[1])) if best is not None else None
            _RC[key] = r
        if r is not None and r[0]:
            self.plan_contracts = list(r[1])
            self.plan = deque(r[0])
            if is_legal(mp, side, vst, claims, rnd, self.plan[0]):
                return self.plan.popleft()
        self.plan.clear()
        return WAIT


class Planner(Professor):
    """Our planner: the Professor's beam search on our side, run on a map whose deadlines and
    points encode the opponent's predicted claims, with the opponent's predicted gathers applied
    to the natural stocks round by round."""

    def __init__(self, style, seat, depth=4, width=8):
        Professor.__init__(self, style, seat)
        self.depth = depth
        self.width = width
        self.og = {}

    def step(self, s, o, lenient=False):
        if not s.ok or s.round >= 160:
            s.ok = False
            return
        mp = self.mp
        ev = self.og.get(s.round)
        if ev is not None and (s.round & 1) != self.seat:
            st = s.stocks
            for site, q in ev:
                st[site] = st[site] - q if st[site] > q else 0
            ev = None
        if lenient and o[0] == 'deliver':
            boat = s.boats[o[1]]
            c = o[5]
            if (boat[2] != 0 or boat[0] != mp.c_dest[c] or boat[3 + mp.c_good[c]] < mp.c_qty[c]
                    or s.claims[c] != -1):
                s.ok = False
                return
        elif not is_legal(mp, s, s.stocks, s.claims, s.round, o):
            s.ok = False
            return
        if not apply_order(mp, s, s.stocks, s.claims, self.seat, o, None):
            s.ok = False
            return
        if ev is not None:
            st = s.stocks
            for site, q in ev:
                st[site] = st[site] - q if st[site] > q else 0
        advance_side(s)
        s.round += 1
        if (s.round & 3) == 0:
            roles = mp.roles
            st = s.stocks
            for site in range(10):
                if (roles[site] == 0 or roles[site] == 1) and st[site] < 6:
                    st[site] += 1
        s.acts = (s.acts, o)

    def acquire(self, sim, b, need, dest, unload_at_dest):
        """Professor.acquire, but a natural site qualifies if it will hold enough stock when the
        boat arrives (regeneration counted), and the boat waits there for regeneration."""
        s = sim.copy()
        boat0 = s.boats[b][:]
        keep = max(need[0], boat0[3]) + max(need[1], boat0[4]) + max(need[2], boat0[5])
        if keep > 3:
            self.travel(s, b, boat0[1] if boat0[2] != 0 else boat0[0])
            for g in range(3):
                if need[g] < boat0[3 + g]:
                    self.step(s, o_unload(b, g, boat0[3 + g] - need[g]))
        if not s.ok:
            return None
        cargo = s.boats[b]
        missing = [max(0, need[g] - cargo[3 + g]) for g in range(3)]
        order = [g for g in range(3) if missing[g] > 0]
        best = [None]
        mp = self.mp
        dist = mp.dist
        roles = mp.roles
        maxwait = PARAMS['regen_wait']

        def rec(sm, idx):
            if not sm.ok:
                return
            bst = best[0]
            if bst is not None and not (sm.round < bst.round):
                return
            if idx == len(order):
                t = sm.copy()
                self.travel(t, b, dest)
                if unload_at_dest:
                    for g in range(3):
                        if need[g] != 0:
                            self.step(t, o_unload(b, g, need[g]))
                if t.ok and (best[0] is None or t.round < best[0].round):
                    best[0] = t
                return
            g = order[idx]
            m = missing[g]
            boat = sm.boats[b]
            cur = boat[1] if boat[2] != 0 else boat[0]
            dc = dist[cur]
            arr0 = sm.round + boat[2]
            cands = []
            for site in range(10):
                if unload_at_dest and dest == site:
                    continue
                if sm.wh[site * 3 + g] >= m:
                    cands.append((site, True))
            for site in range(10):
                if unload_at_dest and dest == site:
                    continue
                if roles[site] == g:
                    st = sm.stocks[site]
                    if m > st:
                        arr = arr0 + dc[site]
                        st = min(6, st + ((arr + maxwait) >> 2) - (sm.round >> 2))
                    if m <= st:
                        cands.append((site, False))
            cands.sort(key=lambda c: dc[c[0]] + dist[c[0]][dest])
            for site, is_load in cands[:5]:
                t = sm.copy()
                self.travel(t, b, site)
                if not is_load:
                    w = 0
                    while t.ok and t.stocks[site] < m and w < maxwait:
                        self.step(t, WAIT)
                        w += 1
                self.step(t, o_load(b, g, m) if is_load else o_gather(b, g, m))
                rec(t, idx + 1)

        while True:
            rec(s, 0)
            if len(order) <= 1:
                break
            i = len(order) - 2
            while i >= 0 and order[i] >= order[i + 1]:
                i -= 1
            if i < 0:
                break
            j = len(order) - 1
            while order[j] <= order[i]:
                j -= 1
            order[i], order[j] = order[j], order[i]
            order[i + 1:] = reversed(order[i + 1:])
        return best[0]

    def interleave(self, actions, variant):
        """Professor.interleave, but waiting is allowed while a queue front is a gather whose site
        is still regenerating (the Professor only waits for sailing boats and running jobs)."""
        s = self.cur.copy()
        queues = [deque(), deque(), deque(), deque()]
        for a in actions:
            if a[0] != 'wait':
                queues[3 if a[0] == 'build_boat' else a[1]].append(a)
        mp = self.mp
        roles = mp.roles
        idle = 0
        while s.round < 80:
            if not (queues[0] or queues[1] or queues[2] or queues[3]):
                return s
            n = len(s.boats)
            chosen = -1
            for i in range(variant, variant + n):
                b = i % n
                q = queues[b]
                if q and is_legal(mp, s, s.stocks, s.claims, s.round, q[0]):
                    is_deliver = q[0][0] == 'deliver'
                    if chosen < 0 or is_deliver:
                        chosen = b
                    if is_deliver:
                        break
            if chosen < 0 and queues[3] and is_legal(mp, s, s.stocks, s.claims, s.round, queues[3][0]):
                chosen = 3
            if chosen < 0:
                busy = False
                for boat in s.boats:
                    if boat[2] > 0:
                        busy = True
                for j in s.jobs:
                    if j > 0:
                        busy = True
                if not busy:
                    for q in queues:
                        if q and q[0][0] == 'gather':
                            bt = s.boats[q[0][1]]
                            if roles[bt[0]] == q[0][3] and s.stocks[bt[0]] < 6:
                                busy = True
                    idle += 1
                    if idle > PARAMS['regen_wait']:
                        busy = False
                if not busy:
                    return None
                self.step(s, WAIT)
            else:
                idle = 0
                self.step(s, queues[chosen].popleft())
            if not s.ok:
                return None
        if queues[0] or queues[1] or queues[2] or queues[3]:
            return None
        return s

    def replan(self, view, allnodes=None, cur=None):
        mp = self.mp
        if cur is None:
            cur = self.make_sim(view)
        self.cur = cur
        cur_has_ws = any(cur.ws)
        best = None
        frontier = [(cur, [], 0.0)]
        for _depth in range(self.depth):
            nxt = []
            for node_sim, node_contracts, _ in frontier:
                for c in range(mp.ncontracts):
                    if node_sim.claims[c] != -1 or not (cur.round < mp.c_deadline[c]):
                        continue
                    opt = self.prepare(node_sim, c)
                    if opt is None:
                        continue
                    acts = opt.actions()
                    for variant in (0, 1):
                        res = self.interleave(acts, variant)
                        if res is None:
                            continue
                        bonus = self.W if (not cur_has_ws and any(res.ws)) else 0
                        score = ((stock_value(res) * 0.1 + float((res.score - cur.score) + bonus))
                                 / pow(float((res.round - cur.round) + 3), self.A))
                        node = (res, node_contracts + [c], score)
                        if best is None or best[2] < score:
                            best = node
                        nxt.append(node)
            if not nxt:
                break
            nxt.sort(key=lambda nd: (-nd[2], nd[0].round))
            if allnodes is not None:
                allnodes.extend(nxt)
            frontier = nxt[:self.width]
        return best


def eff_map(mp, deadlines, points):
    m = Map.__new__(Map)
    m.__dict__.update(mp.__dict__)
    m.c_deadline = deadlines
    m.c_points = points
    return m


class Pred:
    __slots__ = ('opp_claim', 'our_claim', 'og', 'us', 'them', 'opp_orders')


class Exec:
    """Robust plan executor. The plan (one order per round, waits included) is split into
    per-boat queues tagged with their planned round. Each round the executor plays the legal
    queue front with the earliest planned round (deliveries first). Undisturbed, this replays the
    plan exactly; when an order is delayed (failed sail, stock not there yet) the rest of that
    boat's queue waits instead of the whole plan being dropped."""
    __slots__ = ('qs', 'stuck')

    def __init__(self, plan, t0):
        qs = [deque(), deque(), deque(), deque()]
        for i, o in enumerate(plan):
            op = o[0]
            if op == 'wait':
                continue
            qs[3 if op == 'build_boat' else o[1]].append((t0 + i, o))
        self.qs = qs
        self.stuck = 0

    def empty(self):
        q = self.qs
        return not (q[0] or q[1] or q[2] or q[3])

    def clear(self):
        for q in self.qs:
            q.clear()

    def next(self, mp, side, stocks, claims, rnd):
        best = None
        bq = None
        for q in self.qs:
            while q and q[0][1][0] == 'deliver' and claims[q[0][1][5]] != -1:
                q.popleft()
            if q:
                t, o = q[0]
                if is_legal(mp, side, stocks, claims, rnd, o):
                    k = t if o[0] == 'deliver' else t + 1000
                    if best is None or k < best:
                        best = k
                        bq = q
        if bq is None:
            return None
        return bq.popleft()[1]

    def push_front(self, o, rnd):
        self.qs[3 if o[0] == 'build_boat' else o[1]].appendleft((rnd, o))

    def note_idle(self, side):
        """Called when nothing was playable. Returns True when the plan is dead (nothing can
        become legal by waiting: no boat sailing, no job running) for a few rounds."""
        for b in side.boats:
            if b[2] != 0:
                self.stuck = 0
                return False
        for j in side.jobs:
            if j != 0:
                self.stuck = 0
                return False
        self.stuck += 1
        return self.stuck >= PARAMS['regen_wait'] + 1


def first_delivery(mp, side, claims, r, urg=None):
    best = None
    for b, boat in enumerate(side.boats):
        if boat[2] != 0:
            continue
        pos = boat[0]
        for c in range(mp.ncontracts):
            if (claims[c] == -1 and mp.c_deadline[c] > r and mp.c_dest[c] == pos
                    and boat[3 + mp.c_good[c]] >= mp.c_qty[c]):
                k = urg[c] if urg is not None else c
                if best is None or k < best[0]:
                    best = (k, o_deliver(b, c))
    return best[1] if best is not None else None


def rollout(eng, prof, plan, seat, hz=80, mp=None):
    """Plays the game exactly from the current state up to round hz: the opponent (prof, a
    hypothesis) against our side executing `plan` with Exec; once the plan is over (or dead) our
    side only delivers what it can and otherwise waits. `mp` = reference Map for our side."""
    e = eng.clone() if hasattr(eng, 'clone') else eng_copy(eng)
    p = prof.clone()
    ps = 1 - seat
    if mp is None:
        mp = e.mp
    ex = Exec(plan, e.round)
    live = not ex.empty()
    nc = mp.ncontracts
    pr = Pred()
    pr.opp_claim = [-1] * nc
    pr.our_claim = [-1] * nc
    og = {}
    claims = e.claims
    sides = e.sides
    orders = [None, None]
    while e.round < hz:
        r = e.round
        po = p.choose(e.view(ps))
        side = sides[seat]
        mine = None
        if live:
            mine = ex.next(mp, side, e.stocks, claims, r)
            if mine is None:
                if ex.empty() or ex.note_idle(side):
                    live = False
            else:
                ex.stuck = 0
        if mine is None:
            mine = first_delivery(mp, side, claims, r) or WAIT
        if po[0] == 'gather':
            og.setdefault(r, []).append((sides[ps].boats[po[1]][0], po[4]))
        pre = [c for c in range(nc) if claims[c] == -1]
        orders[seat] = mine
        orders[ps] = po
        ok = e.step(orders)
        if live and not ok[seat] and (mine[0] == 'sail' or mine[0] == 'gather'):
            ex.push_front(mine, r)
        claims = e.claims
        for c in pre:
            if claims[c] == ps:
                pr.opp_claim[c] = r
            elif claims[c] == seat:
                pr.our_claim[c] = r
    pr.og = og
    pr.us = sides[seat].score
    pr.them = sides[ps].score
    pr.opp_orders = None
    return pr


class Hyp:
    __slots__ = ('style', 'eng', 'prof')

    def __init__(self, style, eng, prof):
        self.style = style
        self.eng = eng
        self.prof = prof


def obs_mismatch(obs, eng, seat):
    ps = 1 - seat
    if obs['opponent_score'] != eng.sides[ps].score:
        return True
    if obs['claims'] != eng.claims:
        return True
    side = eng.sides[seat]
    own = obs['own']
    if own['score'] != side.score:
        return True
    ob = own['boats']
    if len(ob) != len(side.boats):
        return True
    for b, sb in zip(ob, side.boats):
        if (b['position'] != sb[0] or b['destination'] != sb[1] or b['eta'] != sb[2]
                or b['cargo'] != sb[3:6]):
            return True
    st = obs['stocks']
    est = eng.stocks
    for s in range(10):
        v = st[s]
        if v is not None and v != est[s]:
            return True
    vis = obs['visible']
    exp = []
    for i, b in enumerate(eng.sides[ps].boats):
        if vis[b[0]] or (b[1] >= 0 and vis[b[1]]):
            exp.append((i, b[0], b[1], b[2]))
    got = sorted((b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats'])
    if got != exp:
        return True
    return False


class Game:
    def __init__(self, obs):
        self.mp = Map(obs['map'])
        self.seat = obs['seat']
        self.ps = 1 - self.seat
        styles = range(5) if CHEAT is None else [CHEAT]
        if F is not None:
            self.fmp = F.Map(obs['map'])
            self.hyps = [Hyp(s, F.Engine(self.fmp), F.Professor(s, self.ps)) for s in styles]
        else:
            self.hyps = [Hyp(s, Engine(self.mp), Opp(s, self.ps)) for s in styles]
        self.plan = deque()
        self.plan_c = []
        self.ex = None
        self.from_plan = False
        self.need = True            # replan at the next decision
        self.cpu = 0.0
        self.fb = None
        self.preds = {}             # style -> Pred, valid while we follow self.plan
        self.threat = [False] * self.mp.ncontracts
        self.extra = PARAMS['first_extra'] if _GAMES[0] == 0 else 0.0
        _GAMES[0] += 1
        self.next_replan = 0
        self.urg = list(self.mp.c_deadline)

    # ---- fallback: plain Professor clone on our observation -------------------------------
    def fallback(self, obs):
        if self.fb is None:
            self.fb = Professor(PARAMS['style'], self.seat)
        return self.fb.choose(view_from_observation(obs, self.mp))

    def act(self, obs):
        seat = self.seat
        ps = self.ps
        nh = len(self.hyps)
        self.hyps = [h for h in self.hyps if not obs_mismatch(obs, h.eng, seat)]
        if not self.hyps:
            return self.fallback(obs)
        if len(self.hyps) != nh and PARAMS['replan_on_hyp_change']:
            self.need = True
        legal = [order_from_json(a) for a in obs['legal_actions']]
        lset = set(legal)
        mine = self.decide(obs, legal, lset)
        if mine not in lset:
            mine = WAIT
        t0 = time.process_time()
        oks = []
        for h in self.hyps:
            po = h.prof.choose(h.eng.view(ps))
            orders = [None, None]
            orders[seat] = mine
            orders[ps] = po
            oks.append(h.eng.step(orders)[seat])
        # a failed sail/gather goes back to the front of its boat's queue (same on every live
        # hypothesis by construction: they agree on everything we can observe next round)
        if self.from_plan and not oks[0] and (mine[0] == 'sail' or mine[0] == 'gather'):
            self.ex.push_front(mine, obs['round'])
        _st('t_track', time.process_time() - t0)
        return mine

    def decide(self, obs, legal, lset):
        rnd = obs['round']
        self.from_plan = False
        side = self.hyps[0].eng.sides[self.seat]
        claims = self.hyps[0].eng.claims
        stocks = self.hyps[0].eng.stocks
        if not self.need and self.ex is not None:
            o = self.ex.next(self.mp, side, stocks, claims, rnd)
            if o is not None and o in lset:
                self.ex.stuck = 0
                self.from_plan = True
                if o[0] == 'deliver' and PARAMS['replan_after_delivery']:
                    self.need = True
                return o
            if o is None:
                if self.ex.empty() or self.ex.note_idle(side):
                    self.need = True
                else:
                    return WAIT
        if self.cpu > PARAMS['budget_hard'] + self.extra:
            return first_delivery(self.mp, side, claims, rnd, self.urg) or WAIT
        if self.need and rnd >= self.next_replan:
            self.replan(rnd)
            if self.ex.empty():
                self.next_replan = rnd + 3
            o = self.ex.next(self.mp, side, stocks, claims, rnd)
            if o is not None and o in lset:
                self.from_plan = True
                if o[0] == 'deliver' and PARAMS['replan_after_delivery']:
                    self.need = True
                return o
        d = first_delivery(self.mp, side, claims, rnd, self.urg)
        if d is not None:
            self.need = True
            self.preds = {}
            return d
        return WAIT

    def extend(self, pl, res, acts):
        """Chains further planner segments after a candidate so every candidate covers the
        rest of the game (a short plan would otherwise be judged with us idle afterwards)."""
        depth, width = pl.depth, pl.width
        pl.depth, pl.width = PARAMS['ext_depth'], PARAMS['ext_width']
        for _ in range(PARAMS['ext_max']):
            if res.round >= 78:
                break
            cur = res.copy()
            cur.acts = None
            cur.memo = None
            best = pl.replan(None, None, cur)
            if best is None:
                break
            more = best[0].actions()
            if not more:
                break
            acts.extend(more)
            res = best[0]
        pl.depth, pl.width = depth, width
        return tuple(acts)

    def predict(self, plan, rnd, hz=80):
        t0 = time.process_time()
        out = {}
        for h in self.hyps:
            out[h.style] = rollout(h.eng, h.prof, plan, self.seat, hz, self.mp)
        _st('t_roll', time.process_time() - t0)
        _st('rollouts', len(out))
        return out

    def replan(self, rnd):
        _st('replans')
        seat = self.seat
        mp = self.mp
        hyps = self.hyps
        nc = mp.ncontracts
        cheap = self.cpu > PARAMS['budget_soft'] + self.extra
        old = ()
        if self.ex is not None and not self.ex.empty():
            items = sorted(it for q in self.ex.qs for it in q)
            seq = []
            for t, o in items:
                while rnd + len(seq) < t:
                    seq.append(WAIT)
                seq.append(o)
            old = tuple(seq)
        base = self.preds
        if any(h.style not in base for h in hyps):
            base = self.predict(old, rnd)
        dl = list(mp.c_deadline)
        threat = self.threat
        for pr in base.values():
            for c in range(nc):
                r = pr.opp_claim[c]
                if r >= rnd:
                    e = r + 1 if (r & 1) == seat else r
                    if e < dl[c]:
                        dl[c] = e
                    threat[c] = True
        h0 = hyps[0]
        view = h0.eng.view(seat)
        stocks = h0.eng.stocks
        cands = []
        seen = {}
        best = [None]

        tag = [None]

        def consider(acts, cs, sc):
            """Evaluates a candidate by exact rollouts (one per live hypothesis)."""
            if acts in seen:
                return seen[acts]
            if acts == old and len(base) == len(hyps):
                preds = base
            else:
                preds = self.predict(acts, rnd)
            margins = [preds[h.style].us - preds[h.style].them for h in hyps]
            i = len(cands)
            mode = PARAMS['select']
            if mode == 'mean':
                key = (sum(margins), min(margins), -i)
            elif mode == 'blend':
                key = (min(margins) + PARAMS['blend_w'] * sum(margins) / len(margins), -i)
            else:
                key = (min(margins), sum(margins), -i)
            cands.append((acts, cs, sc))
            seen[acts] = preds
            if DEBUG:
                dr = [(rnd + j, o[5]) for j, o in enumerate(acts) if o[0] == 'deliver']
                print('    cand %d head=%s delivers=%s margins=%s' % (i, cs, dr, margins))
            if best[0] is None or key > best[0][0]:
                best[0] = (key, acts, cs, preds, tag[0])
            return preds

        if old and old[0] in set(legal_actions(mp, view.side, stocks, view.claims, rnd)):
            tag[0] = 'old'
            consider(old, list(self.plan_c), 1e9)
        t0 = time.process_time()
        cfgs = PARAMS['cfgs'][:1] if cheap else PARAMS['cfgs']
        side0 = view.side
        can_boat = (len(side0.boats) <= 2 and side0.wh[side0.home * 3] >= 4
                    and side0.wh[side0.home * 3 + 1] >= 2)
        for ci, cfg in enumerate(cfgs):
            style, lam, use_eff, k = cfg[:4]
            pre = cfg[4] if len(cfg) > 4 else ''
            if pre == 'boat' and not can_boat:
                continue
            dls = dl[:] if use_eff else list(mp.c_deadline)
            thr = threat[:]
            for it in range(PARAMS['iters'] if use_eff else 1):
                pts = [mp.c_points[c] * (1.0 + lam) if (thr[c] and dls[c] > rnd) else mp.c_points[c]
                       for c in range(nc)]
                pl = Planner(style, seat, depth=PARAMS['depth'], width=PARAMS['width'])
                pl.mp = eff_map(mp, dls, pts)
                pl.og = base[h0.style].og
                pl.est = stocks[:]
                view.mp = pl.mp
                nodes = []
                if pre == 'boat':
                    c0 = pl.make_sim(view)
                    pl.step(c0, BUILD_BOAT)
                    c0.acts = None
                    pl.replan(view, nodes, c0)
                else:
                    pl.replan(view, nodes)
                nodes.sort(key=lambda nd: (-nd[2], nd[0].round))
                got = 0
                heads = set()
                first = None
                for nd in nodes:
                    head = tuple(nd[1])
                    if head in heads:
                        continue
                    heads.add(head)
                    tag[0] = 'c%d.i%d.k%d' % (ci, it, got)
                    acts = self.extend(pl, nd[0], ([BUILD_BOAT] if pre == 'boat' else []) + nd[0].actions())
                    if not acts:
                        continue
                    preds = consider(acts, nd[1], nd[2])
                    if first is None:
                        first = (acts, preds)
                    got += 1
                    if got >= k:
                        break
                if first is None:
                    break
                # fixed point: contracts of the top candidate that the opponent still takes first
                # get its claim round as deadline, then the planner runs again
                acts, preds = first
                mine = set(o[5] for o in acts if o[0] == 'deliver')
                lost = False
                for pr in preds.values():
                    for c in mine:
                        r = pr.opp_claim[c]
                        if pr.our_claim[c] < 0 and r >= rnd:
                            e = r + 1 if (r & 1) == seat else r
                            if e < dls[c]:
                                dls[c] = e
                                lost = True
                            thr[c] = True
                    for c in range(nc):
                        if pr.opp_claim[c] >= rnd:
                            thr[c] = True
                if not lost:
                    break
                _st('iter_lost')
        _st('t_plan', time.process_time() - t0)
        best = best[0]
        _st('cands', len(cands))
        if best is not None and len(cands) > 1:
            _st('win_' + str(best[4]))
        if best is None:
            self.plan, self.plan_c, self.preds = deque(), [], {}
        else:
            self.plan = deque(best[1])
            self.plan_c = list(best[2])
            self.preds = best[3]
        self.ex = Exec(self.plan, rnd)
        self.need = False
        self.urg = dl[:]
        if DEBUG:
            pr0 = self.preds.get(h0.style) if self.preds else None
            dr = [rnd + i for i, o in enumerate(self.plan) if o[0] == 'deliver']
            print('  REPLAN r%d hyps=%s ncand=%d best=%s plan_c=%s deliver_rounds=%s eff=%s %s' % (
                rnd, [h.style for h in hyps], len(cands), best[0] if best else None, self.plan_c, dr, dl,
                ('pred opp=%s our=%s' % (pr0.opp_claim, pr0.our_claim)) if pr0 else ''))


def agent(observation, memory):
    t0 = time.process_time()
    legal = observation['legal_actions']
    try:
        g = memory.get('g')
        if g is None or observation['round'] == 0:
            if observation['round'] == 0:
                _RC.clear()
            g = memory['g'] = Game(observation)
        o = g.act(observation)
        a = order_to_json(o)
        g.cpu += time.process_time() - t0
        if a in legal:
            return a
    except Exception:  # noqa: BLE001
        import traceback
        traceback.print_exc(file=sys.stderr)
        memory['g'] = None
        memory['dead'] = True
    for a in legal:
        if a.get('op') == 'deliver':
            return a
    return legal[0]


def serve():
    protocol = sys.stdout
    sys.stdout = sys.stderr
    memory = {}
    for line in sys.stdin:
        observation = json.loads(line)['observation']
        if observation['round'] == 0:
            memory = {}
        protocol.write(json.dumps(agent(observation, memory)) + '\n')
        protocol.flush()


if __name__ == '__main__':
    serve()
