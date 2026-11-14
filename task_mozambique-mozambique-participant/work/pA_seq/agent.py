"""Your submission. Upload only this file; keep it self-contained (standard library only).

The evaluator runs `python main.py`, sends one JSON line {"observation": ...} per
decision on stdin and reads one JSON action per line from stdout. Leave the loop
at the bottom as it is and put your strategy in agent().
"""
import json
import sys


# ==========================================================================================
# core.py
# ==========================================================================================
"""Python re-implementation of the mozambique-engine rules and of its built-in opponent
("the Professor", C++ class ReferencePlayer), reverse-engineered from the binary.

Stdlib only, runs on CPython 3 and PyPy 3.10. See PROFESSOR.md for the pseudocode and
test_professor.py for the check against the real engine.

Orders are tuples (op, boat, destination, good, quantity, contract) with the same default
field values the engine uses internally (so equality matches the engine's Order equality).
"""
from collections import deque

INF = 100000

WAIT = ('wait', -1, -1, -1, 0, -1)
BUILD_BOAT = ('build_boat', -1, -1, -1, 0, -1)


def o_sail(b, d): return ('sail', b, d, -1, 0, -1)
def o_gather(b, g, q): return ('gather', b, -1, g, q, -1)
def o_load(b, g, q): return ('load', b, -1, g, q, -1)
def o_unload(b, g, q): return ('unload', b, -1, g, q, -1)
def o_build_workshop(b): return ('build_workshop', b, -1, -1, 0, -1)
def o_craft(b): return ('craft', b, -1, -1, 0, -1)
def o_deliver(b, c): return ('deliver', b, -1, -1, 0, c)


def order_to_json(o):
    op = o[0]
    if op in ('wait', 'build_boat'):
        return {'op': op}
    if op == 'sail':
        return {'op': op, 'boat': o[1], 'destination': o[2]}
    if op in ('gather', 'load', 'unload'):
        return {'op': op, 'boat': o[1], 'good': o[3], 'quantity': o[4]}
    if op in ('build_workshop', 'craft'):
        return {'op': op, 'boat': o[1]}
    if op == 'deliver':
        return {'op': op, 'boat': o[1], 'contract': o[5]}
    raise ValueError(o)


def order_from_json(a):
    op = a['op']
    if op == 'wait':
        return WAIT
    if op == 'build_boat':
        return BUILD_BOAT
    if op == 'sail':
        return o_sail(a['boat'], a['destination'])
    if op in ('gather', 'load', 'unload'):
        return (op, a['boat'], -1, a['good'], a['quantity'], -1)
    if op in ('build_workshop', 'craft'):
        return (op, a['boat'], -1, -1, 0, -1)
    if op == 'deliver':
        return o_deliver(a['boat'], a['contract'])
    raise ValueError(a)


# Style table at .rodata 0xe2820, indexed by style id 0-4:
# (surplus weight B, time exponent A, first-workshop bonus W)
STYLES = [
    (3.5, 0.85, 8),
    (1.8, 1.15, 0),
    (1.8, 0.85, 0),
    (3.5, 0.0, 0),
    (0.0, 0.85, 8),
]

M64 = (1 << 64) - 1


def splitmix_next(state):
    """Returns (new_state, value). The engine's only RNG."""
    state = (state + 0x9e3779b97f4a7c15) & M64
    z = state
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
    return state, z ^ (z >> 31)


def style_permutation(seed):
    """perm[game] = style id used by the Professor in that game of the map (Game ctor, 0x1fed0)."""
    perm = [0, 1, 2, 3, 4]
    state = seed ^ 0x5354594c45534554          # "STYLESET"
    for i in range(5, 1, -1):
        state, v = splitmix_next(state)
        j = v % i
        perm[i - 1], perm[j] = perm[j], perm[i - 1]
    return perm


class Map:
    """Static map data plus the engine's all-pairs distances and next hops (Floyd-Warshall)."""

    def __init__(self, m):
        self.topology = m.get('topology', 0)
        self.roles = list(m['roles'])
        self.homes = list(m['homes'])
        self.routes = [list(r) for r in m['routes']]
        cs = m['contracts']
        self.c_good = [c['good'] for c in cs]
        self.c_qty = [c['quantity'] for c in cs]
        self.c_dest = [c['destination'] for c in cs]
        self.c_points = [c['points'] for c in cs]
        self.c_deadline = [c['deadline'] for c in cs]
        self.ncontracts = len(cs)
        n = 10
        dist = [[(self.routes[i][j] if self.routes[i][j] != 0 and i != j else (0 if i == j else INF))
                 for j in range(n)] for i in range(n)]
        nxt = [[(j if self.routes[i][j] != 0 else -1) for j in range(n)] for i in range(n)]
        for k in range(n):
            dk = dist[k]
            for i in range(n):
                di = dist[i]
                dik = di[k]
                ni = nxt[i]
                for j in range(n):
                    v = dk[j] + dik
                    if v < di[j]:
                        di[j] = v
                        ni[j] = ni[k]
        self.dist = dist
        self.nxt = nxt
        self.neigh = [[j for j in range(n) if self.routes[i][j] != 0] for i in range(n)]


# ---------------------------------------------------------------------------------------------
# Shared side mechanics. A "side" object has: home, score, crafted, boats, wh, ws, jobs.
# boats: list of [position, destination, eta, cargo0, cargo1, cargo2]
# wh: flat list of 30 ints (site * 3 + good); ws: list of 10 bools; jobs: list of 10 ints.
# ---------------------------------------------------------------------------------------------

def is_legal(mp, side, stocks, claims, rnd, o):
    """Exactly `o in legal_actions(...)` (engine function 0x21660)."""
    op = o[0]
    if op == 'wait':
        return True
    if op == 'build_boat':
        h3 = side.home * 3
        return len(side.boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2
    b = o[1]
    if b < 0 or b >= len(side.boats):
        return False
    boat = side.boats[b]
    if boat[2] != 0:
        return False
    pos = boat[0]
    if op == 'sail':
        d = o[2]
        return 0 <= d < 10 and mp.routes[pos][d] != 0
    free = 3 - (boat[3] + boat[4] + boat[5])
    if op == 'gather':
        role = mp.roles[pos]
        if role != 0 and role != 1:
            return False
        return o[3] == role and 1 <= o[4] <= min(stocks[pos], free)
    if op == 'load':
        g = o[3]
        return 0 <= g < 3 and 1 <= o[4] <= min(side.wh[pos * 3 + g], free)
    if op == 'unload':
        g = o[3]
        return 0 <= g < 3 and 1 <= o[4] <= boat[3 + g]
    if op == 'build_workshop':
        return (mp.roles[pos] == 2 and not side.ws[pos]
                and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1)
    if op == 'craft':
        return (mp.roles[pos] == 2 and side.ws[pos] and side.jobs[pos] == 0
                and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1)
    if op == 'deliver':
        c = o[5]
        return (0 <= c < mp.ncontracts and claims[c] == -1 and mp.c_deadline[c] > rnd
                and mp.c_dest[c] == pos and boat[3 + mp.c_good[c]] >= mp.c_qty[c])
    return False


def legal_actions(mp, side, stocks, claims, rnd):
    """Legal orders in the engine's order (0x21660)."""
    out = [WAIT]
    for b, boat in enumerate(side.boats):
        if boat[2] != 0:
            continue
        pos = boat[0]
        free = 3 - (boat[3] + boat[4] + boat[5])
        for j in range(10):
            if mp.routes[pos][j] != 0:
                out.append(o_sail(b, j))
        role = mp.roles[pos]
        if role == 0 or role == 1:
            for q in range(1, min(stocks[pos], free) + 1):
                out.append(o_gather(b, role, q))
        for g in range(3):
            for q in range(1, min(side.wh[pos * 3 + g], free) + 1):
                out.append(o_load(b, g, q))
            for q in range(1, boat[3 + g] + 1):
                out.append(o_unload(b, g, q))
        if role == 2 and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1:
            if not side.ws[pos]:
                out.append(o_build_workshop(b))
            elif side.jobs[pos] == 0:
                out.append(o_craft(b))
        for c in range(mp.ncontracts):
            if (claims[c] == -1 and mp.c_deadline[c] > rnd and mp.c_dest[c] == pos
                    and boat[3 + mp.c_good[c]] >= mp.c_qty[c]):
                out.append(o_deliver(b, c))
    h3 = side.home * 3
    if len(side.boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2:
        out.append(BUILD_BOAT)
    return out


def apply_order(mp, side, stocks, claims, seat, o, used_routes):
    """Engine function 0x22090. Returns False when the order fails (boat does nothing).
    `used_routes` is the per-round set of departed routes (both directions) or None in the planner."""
    op = o[0]
    if op == 'wait':
        return True
    if op == 'build_boat':
        h3 = side.home * 3
        side.wh[h3] -= 4
        side.wh[h3 + 1] -= 2
        side.boats.append([side.home, -1, 0, 0, 0, 0])
        return True
    boat = side.boats[o[1]]
    pos = boat[0]
    if op == 'sail':
        d = o[2]
        if used_routes is not None:
            if (pos, d) in used_routes:
                return False
            used_routes.add((pos, d))
            used_routes.add((d, pos))
        boat[1] = d
        boat[2] = mp.routes[pos][d]
        return True
    if op == 'gather':
        q = o[4]
        if stocks[pos] < q:
            return False
        stocks[pos] -= q
        boat[3 + o[3]] += q
        return True
    if op == 'load':
        side.wh[pos * 3 + o[3]] -= o[4]
        boat[3 + o[3]] += o[4]
        return True
    if op == 'unload':
        side.wh[pos * 3 + o[3]] += o[4]
        boat[3 + o[3]] -= o[4]
        return True
    if op == 'build_workshop':
        side.wh[pos * 3] -= 2
        side.wh[pos * 3 + 1] -= 1
        side.ws[pos] = True
        return True
    if op == 'craft':
        side.wh[pos * 3] -= 2
        side.wh[pos * 3 + 1] -= 1
        side.jobs[pos] = 3
        return True
    if op == 'deliver':
        c = o[5]
        if claims[c] != -1:
            return False
        g = mp.c_good[c]
        boat[3 + g] -= mp.c_qty[c]
        side.score += mp.c_points[c]
        if g == 2:
            side.crafted += 1
        claims[c] = seat
        return True
    raise ValueError('unknown order %r' % (o,))


def advance_side(side):
    for boat in side.boats:
        if boat[2] != 0:
            boat[2] -= 1
            if boat[2] == 0:
                boat[0] = boat[1]
                boat[1] = -1
    jobs = side.jobs
    for s in range(10):
        if jobs[s] != 0:
            jobs[s] -= 1
            if jobs[s] == 0:
                side.wh[s * 3 + 2] += 1


class Side:
    __slots__ = ('home', 'score', 'crafted', 'boats', 'wh', 'ws', 'jobs')

    def __init__(self, home):
        self.home = home
        self.score = 0
        self.crafted = 0
        self.boats = [[home, -1, 0, 0, 0, 0], [home, -1, 0, 0, 0, 0]]
        self.wh = [0] * 30
        self.wh[home * 3] = 5
        self.wh[home * 3 + 1] = 3
        self.ws = [False] * 10
        self.jobs = [0] * 10


class View:
    """What a seat is given each round (engine struct built by 0x311e0)."""
    __slots__ = ('mp', 'side', 'round', 'seat', 'opponent_score', 'stocks', 'visible', 'claims',
                 'enemy_boats')


class Engine:
    """Full two-sided game state (engine struct at game+8)."""

    def __init__(self, mp):
        self.mp = mp
        self.round = 0
        self.sides = [Side(mp.homes[0]), Side(mp.homes[1])]
        self.stocks = [4 if r in (0, 1) else 0 for r in mp.roles]
        self.claims = [-1] * mp.ncontracts

    def view(self, seat):
        v = View()
        side = self.sides[seat]
        v.mp = self.mp
        v.side = side
        v.round = self.round
        v.seat = seat
        v.opponent_score = self.sides[1 - seat].score
        vis = [False] * 10
        vis[side.home] = True
        for s in range(10):
            if side.ws[s]:
                vis[s] = True
        for boat in side.boats:
            if boat[2] == 0:
                vis[boat[0]] = True
        v.visible = vis
        v.stocks = [self.stocks[s] if vis[s] else 4 for s in range(10)]   # 4 = hidden placeholder
        v.claims = self.claims
        v.enemy_boats = [(i, boat[0], boat[1], boat[2])
                         for i, boat in enumerate(self.sides[1 - seat].boats)
                         if vis[boat[0]] or (boat[1] >= 0 and vis[boat[1]])]
        return v

    def legal(self, seat):
        if self.round >= 80:
            return []
        return legal_actions(self.mp, self.sides[seat], self.view(seat).stocks, self.claims, self.round)

    def step(self, orders):
        """orders[seat]. Seat round%2 resolves first. Returns [ok0, ok1]."""
        first = self.round % 2
        used = set()
        ok = [True, True]
        for seat in (first, 1 - first):
            ok[seat] = apply_order(self.mp, self.sides[seat], self.stocks, self.claims, seat,
                                   orders[seat], used)
        advance_side(self.sides[0])
        advance_side(self.sides[1])
        self.round += 1
        if self.round % 4 == 0:
            for s in range(10):
                if self.mp.roles[s] in (0, 1) and self.stocks[s] < 6:
                    self.stocks[s] += 1
        return ok


def view_from_observation(obs, mp=None):
    """Build a View from the JSON observation the agent receives."""
    v = View()
    v.mp = mp or Map(obs['map'])
    own = obs['own']
    side = Side(own['home'])
    side.score = own['score']
    side.crafted = own['crafted_deliveries']
    side.boats = [[b['position'], b['destination'], b['eta']] + list(b['cargo']) for b in own['boats']]
    side.wh = [x for row in own['warehouses'] for x in row]
    side.ws = [bool(x) for x in own['workshops']]
    side.jobs = list(own['jobs'])
    v.side = side
    v.round = obs['round']
    v.seat = obs['seat']
    v.opponent_score = obs['opponent_score']
    v.visible = [bool(x) for x in obs['visible']]
    v.stocks = [(s if s is not None else 4) for s in obs['stocks']]
    v.claims = list(obs['claims'])
    v.enemy_boats = [(b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats']]
    return v


# ---------------------------------------------------------------------------------------------
# The Professor
# ---------------------------------------------------------------------------------------------

class Sim:
    """ReferencePlayer::Sim: the Professor's one-sided forward model (0x140 bytes in the binary)."""
    __slots__ = ('home', 'score', 'crafted', 'boats', 'wh', 'ws', 'jobs', 'stocks', 'claims',
                 'round', 'ok', 'acts', 'memo')

    def copy(self):
        s = Sim.__new__(Sim)
        s.memo = None               # per-object cache used by Professor.manufactured, not copied
        s.home = self.home
        s.score = self.score
        s.crafted = self.crafted
        s.boats = [b[:] for b in self.boats]
        s.wh = self.wh[:]
        s.ws = self.ws[:]
        s.jobs = self.jobs[:]
        s.stocks = self.stocks[:]
        s.claims = self.claims[:]
        s.round = self.round
        s.ok = self.ok
        s.acts = self.acts          # persistent cons list (prev, order)
        return s

    def actions(self):
        out = []
        a = self.acts
        while a is not None:
            out.append(a[1])
            a = a[0]
        out.reverse()
        return out


def stock_value(s):
    """Sum over own workshop sites of min(fibre,2)*1.5 + min(timber,4)."""
    v = 0.0
    wh = s.wh
    ws = s.ws
    for site in range(10):
        if ws[site]:
            f = wh[site * 3 + 1]
            t = wh[site * 3]
            v += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)
    return v


class Professor:
    def __init__(self, style, seat=None):
        """style: id 0-4 (index into STYLES) or a (B, A, W) tuple."""
        if isinstance(style, int):
            style = STYLES[style]
        self.B, self.A, self.W = style
        self.seat = seat
        self.last_round = -1
        self.est = [4] * 10
        self.plan = deque()
        self.plan_contracts = []
        self.mp = None
        self.replans = 0

    def clone(self):
        p = Professor((self.B, self.A, self.W), self.seat)
        p.last_round = self.last_round
        p.est = self.est[:]
        p.plan = deque(self.plan)
        p.plan_contracts = self.plan_contracts[:]
        p.mp = self.mp
        return p

    # ---- Sim primitives -----------------------------------------------------------------

    def step(self, s, o, lenient=False):
        """Sim::step (0x19ec0)."""
        if not s.ok or s.round >= 160:
            s.ok = False
            return
        mp = self.mp
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
        advance_side(s)
        s.round += 1
        if (s.round & 3) == 0:
            roles = mp.roles
            st = s.stocks
            for site in range(10):
                if (roles[site] == 0 or roles[site] == 1) and st[site] < 6:
                    st[site] += 1
        s.acts = (s.acts, o)

    def travel(self, s, b, target):
        """0x1a1c0: wait until boat b is docked, then follow next hops to `target`."""
        nxt = self.mp.nxt
        while s.ok:
            boat = s.boats[b]
            if boat[2] != 0:
                self.step(s, WAIT)
                continue
            if boat[0] == target:
                return
            n = nxt[boat[0]][target]
            if n < 0:
                s.ok = False
                return
            self.step(s, o_sail(b, n))

    # ---- acquire (0x26c80 + lambda 0x2bf10) --------------------------------------------

    def acquire(self, sim, b, need, dest, unload_at_dest):
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
            cands = []
            for site in range(10):
                if unload_at_dest and dest == site:
                    continue
                if sm.wh[site * 3 + g] >= m:
                    cands.append((site, True))
            for site in range(10):
                if unload_at_dest and dest == site:
                    continue
                if roles[site] == g and m <= sm.stocks[site]:
                    cands.append((site, False))
            boat = sm.boats[b]
            cur = boat[1] if boat[2] != 0 else boat[0]
            dc = dist[cur]
            cands.sort(key=lambda c: dc[c[0]] + dist[c[0]][dest])     # stable
            for site, is_load in cands[:5]:
                t = sm.copy()
                self.travel(t, b, site)
                self.step(t, o_load(b, g, m) if is_load else o_gather(b, g, m))
                rec(t, idx + 1)

        while True:
            rec(s, 0)
            if len(order) <= 1:
                break
            # std::next_permutation
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

    # ---- supply a manufacturing site with 2 timber + 1 fibre (0x27250) --------------------

    def supply(self, sim, w):
        need_t = max(0, 2 - sim.wh[w * 3])
        need_f = max(0, 1 - sim.wh[w * 3 + 1])
        B = self.B
        best_cost = 1e30
        best = None
        nb = len(sim.boats)

        def cost(s):
            return s.round - (max(0, s.wh[w * 3 + 1] - 1) * 1.5 + max(0, s.wh[w * 3] - 2)) * B

        if need_t + need_f == 0:
            for b in range(nb):
                s = sim.copy()
                self.travel(s, b, w)
                if s.ok:
                    c = cost(s)
                    if c < best_cost:
                        best_cost = c
                        best = (s, b)
            return best
        for b in range(nb):
            r = self.acquire(sim, b, [need_t, need_f, 0], w, True)
            if r is not None:
                c = cost(r)
                if c < best_cost:
                    best_cost = c
                    best = (r, b)
            if need_t != 0 and need_f == 0:
                r = self.acquire(sim, b, [3, 0, 0], w, True)
                if r is not None:
                    c = cost(r)
                    if c < best_cost:
                        best_cost = c
                        best = (r, b)
            if need_f != 0 and need_t == 0:
                r = self.acquire(sim, b, [0, 3, 0], w, True)
                if r is not None:
                    c = cost(r)
                    if c < best_cost:
                        best_cost = c
                        best = (r, b)
        if need_t != 0 and need_f != 0 and sim.round < 50:
            for first, second in (([3, 0, 0], [0, 3, 0]), ([0, 3, 0], [3, 0, 0])):
                for b1 in range(nb):
                    r1 = self.acquire(sim, b1, first, w, True)
                    if r1 is None:
                        continue
                    for b2 in range(nb):
                        r2 = self.acquire(r1, b2, second, w, True)
                        if r2 is not None:
                            c = cost(r2)
                            if c < best_cost:
                                best_cost = c
                                best = (r2, b2)
        return best

    # ---- get one manufactured good to `dest` (0x284f0) -----------------------------------

    def manufactured(self, sim, dest):
        """The engine recomputes everything per call. Everything up to "boat b holds the good at
        site w" does not depend on `dest`, so it is cached on the (never mutated) input sim; the
        four manufactured contracts of a beam node then share it. Candidate order is unchanged."""
        best_cost = 1e30
        best = None
        nb = len(sim.boats)
        roles = self.mp.roles
        memo = sim.memo
        if memo is None:
            memo = sim.memo = {}

        def consider(s, b, best_cost, best):
            self.travel(s, b, dest)
            if s.ok:
                c = s.round - stock_value(s) * 0.5
                if c < best_cost:
                    return c, (s, b)
            return best_cost, best

        # A: a boat already carries a manufactured good
        for b in range(nb):
            if sim.boats[b][5] != 0:
                best_cost, best = consider(sim.copy(), b, best_cost, best)
        # B: pick one up where it is stored or being crafted
        for w in range(10):
            if sim.wh[w * 3 + 2] != 0 or sim.jobs[w] != 0:
                for b in range(nb):
                    key = (0, w, b)
                    if key in memo:
                        s = memo[key]
                    else:
                        s = sim.copy()
                        self.travel(s, b, w)
                        while s.ok and s.jobs[w] != 0:
                            self.step(s, WAIT)
                        if s.ok:
                            boat = s.boats[b]
                            if boat[3] + boat[4] + boat[5] < 3:
                                self.step(s, o_load(b, 2, 1))
                            else:
                                s = None
                        if s is not None and not s.ok:
                            s = None
                        memo[key] = s
                    if s is not None:
                        best_cost, best = consider(s.copy(), b, best_cost, best)
        # C: (build a workshop and) craft a new one
        for w in range(10):
            if roles[w] != 2:
                continue
            key = (1, w)
            if key in memo:
                loaded = memo[key]
            else:
                loaded = []
                s = sim.copy()
                crafted = False
                r = True
                if not s.ws[w]:
                    r = self.supply(s, w)
                    if r is not None:
                        s = r[0]
                        self.step(s, o_build_workshop(r[1]))
                if r is not None and s.ok and s.jobs[w] == 0:
                    r = self.supply(s, w)
                    if r is not None:
                        s = r[0]
                        self.step(s, o_craft(r[1]))
                        crafted = True
                if crafted:
                    for b in range(nb):
                        t = s.copy()
                        self.travel(t, b, w)
                        while t.ok:
                            if t.jobs[w] == 0:
                                boat = t.boats[b]
                                if boat[3] + boat[4] + boat[5] < 3:
                                    self.step(t, o_load(b, 2, 1))
                                    if t.ok:
                                        loaded.append((t, b))
                                break
                            self.step(t, WAIT)
                memo[key] = loaded
            for t, b in loaded:
                best_cost, best = consider(t.copy(), b, best_cost, best)
        return best

    # ---- sequential plan for one more contract (0x29690) ---------------------------------

    def prepare(self, sim, c):
        if sim.claims[c] != -1:
            return None
        mp = self.mp
        g = mp.c_good[c]
        dest = mp.c_dest[c]
        if g == 2:
            r = self.manufactured(sim, dest)
            if r is None:
                return None
            s, boat = r
        else:
            need = [0, 0, 0]
            need[g] = mp.c_qty[c]
            s = None
            boat = -1
            for b in range(len(sim.boats)):
                r = self.acquire(sim, b, need, dest, False)
                if r is not None and (s is None or r.round < s.round):
                    s = r
                    boat = b
            if s is None:
                return None
        s = s.copy()
        self.step(s, o_deliver(boat, c), lenient=True)
        return s if s.ok else None

    # ---- re-schedule the sequential action list over both boats (0x29f80) ----------------

    def interleave(self, actions, variant):
        s = self.cur.copy()
        queues = [deque(), deque(), deque()]
        for a in actions:
            if a[0] != 'wait':
                queues[a[1] if a[1] > 0 else 0].append(a)
        mp = self.mp
        while s.round < 80:
            if not (queues[0] or queues[1] or queues[2]):
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
            if chosen < 0:
                busy = False
                for boat in s.boats:
                    if boat[2] > 0:
                        busy = True
                for j in s.jobs:
                    if j > 0:
                        busy = True
                if not busy:
                    return None
                self.step(s, WAIT)
            else:
                self.step(s, queues[chosen].popleft())
            if not s.ok:
                return None
        if queues[0] or queues[1] or queues[2]:
            return None
        return s

    # ---- top level (0x3ae20) -------------------------------------------------------------

    def make_sim(self, view):
        side = view.side
        s = Sim.__new__(Sim)
        s.home = side.home
        s.score = side.score
        s.crafted = side.crafted
        s.boats = [b[:] for b in side.boats]
        s.wh = side.wh[:]
        s.ws = side.ws[:]
        s.jobs = side.jobs[:]
        s.stocks = self.est[:]
        s.claims = list(view.claims)
        s.round = view.round
        s.ok = True
        s.acts = None
        s.memo = None
        return s

    def replan(self, view):
        """Beam search over contract sequences. Returns (sim, contracts, score) or None."""
        self.replans += 1
        mp = self.mp
        cur = self.make_sim(view)
        self.cur = cur
        cur_has_ws = any(cur.ws)
        best = None
        frontier = [(cur, [], 0.0)]
        for _depth in range(4):
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
            nxt.sort(key=lambda nd: (-nd[2], nd[0].round))      # stable; ties -> earlier finish
            frontier = nxt[:8]
        return best

    def choose(self, view):
        """ReferencePlayer::choose. Returns the order for this round and updates internal state."""
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
        for s in range(10):
            v = est[s] + d
            if v > 6:
                v = 6
            if view.visible[s]:
                v = view.stocks[s]
            est[s] = v
        self.last_round = rnd
        claims = view.claims
        for c in self.plan_contracts:
            if claims[c] != -1 and claims[c] != self.seat:
                self.plan.clear()
        side = view.side
        if rnd >= 80:
            return WAIT
        # any legal delivery is taken at once (first in legal order: boat asc, contract asc)
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
        if self.plan and is_legal(mp, side, view.stocks, claims, rnd, self.plan[0]):
            return self.plan.popleft()
        self.plan.clear()
        self.plan_contracts = []
        best = self.replan(view)
        if best is not None:
            acts = best[0].actions()
            if acts:
                self.plan_contracts = list(best[1])
                self.plan = deque(acts)
                if is_legal(mp, side, view.stocks, claims, rnd, self.plan[0]):
                    return self.plan.popleft()
        self.plan.clear()
        return WAIT


# ---------------------------------------------------------------------------------------------
# Map generation (engine function 0x1e1b0), exact.
# ---------------------------------------------------------------------------------------------

def generate_map(topology, seed):
    """Returns the same dict as observation['map'] for group = 2*topology + seat."""
    state = [seed ^ 0x43414d504149474e]          # "CAMPAIGN"

    def rnd():
        state[0], v = splitmix_next(state[0])
        return v

    for _attempt in range(4096):
        routes = [[0] * 10 for _ in range(10)]

        def edge(i, j):
            length = rnd() % 3 + 1
            routes[i][j] = length
            routes[j][i] = length

        if topology == 0:                         # ring of ten
            for i in range(10):
                edge(i, (i + 1) % 10)
        elif topology == 1:                       # 2 x 5 ladder
            for base in (0, 5):
                for i in range(4):
                    edge(base + i, base + i + 1)
            for i in range(5):
                edge(i, i + 5)
        elif topology == 2:                       # two rings of five joined by 2-7
            for base in (0, 5):
                for i in range(5):
                    edge(base + i, base + (i + 1) % 5)
            edge(2, 7)
        else:                                     # two stars (hubs 0 and 5) joined by 0-5
            for i in range(1, 5):
                edge(0, i)
            for i in range(6, 10):
                edge(5, i)
            edge(0, 5)
        dist = [[(routes[i][j] if routes[i][j] != 0 and i != j else (0 if i == j else INF))
                 for j in range(10)] for i in range(10)]
        for k in range(10):
            for i in range(10):
                for j in range(10):
                    v = dist[k][j] + dist[i][k]
                    if v < dist[i][j]:
                        dist[i][j] = v
        best = -1
        homes = [0, 0]
        for i in range(9):
            for j in range(i + 1, 10):
                if best < dist[i][j]:
                    best = dist[i][j]
                    homes = [i, j]
        if rnd() & 1:
            homes.reverse()
        roles = [-1] * 10
        others = [i for i in range(10) if i != homes[0] and i != homes[1]]
        for n in range(8, 1, -1):
            r = rnd() % n
            others[n - 1], others[r] = others[r], others[n - 1]
        for k, site in enumerate(others):
            roles[site] = 0 if k < 3 else (1 if k < 6 else 2)
        contracts = []
        failed = False
        for c in range(8):
            if c < 4:
                good, qty, points, deadline = c & 1, 2, 5, 24 + 16 * c
            else:
                good, qty, points, deadline = 2, 1, 12, min(80, 24 + 16 * c - 48)
            eligible = []
            for site in others:
                if roles[site] == good:
                    continue
                ok = True
                for h in homes:
                    if good == 2:
                        t = INF
                        for w in others:
                            if roles[w] == 2:
                                t = min(t, dist[h][w] * 3 + 14 + dist[w][site])
                    else:
                        t = dist[h][site] + 2
                    if t > deadline:
                        ok = False
                if ok:
                    eligible.append(site)
            if not eligible:
                failed = True
                break
            dest = eligible[rnd() % len(eligible)]
            contracts.append(dict(deadline=deadline, destination=dest, good=good, points=points,
                                  quantity=qty))
        if failed:
            continue
        return dict(contracts=contracts, homes=homes, roles=roles, routes=routes, topology=topology)
    raise RuntimeError('map generation exhausted feasible candidates')

# ==========================================================================================
# tsched.py
# ==========================================================================================
# ---- sched: one-sided timetable scheduler for our side (one order per round slot) ----

BOAT_TOK = 8


class Sched(object):
    """Timetable under construction. boats[b] = [pos, ready, cT, cF, cM] at the end of b's chain."""
    __slots__ = ('mp', 't0', 'used', 'boats', 'lv', 'base', 'gq', 'crafts', 'ws', 'orders', 'deliv',
                 'home', 'nord')

    def copy(self):
        s = Sched.__new__(Sched)
        s.mp = self.mp
        s.t0 = self.t0
        s.used = self.used[:]
        s.boats = [b[:] for b in self.boats]
        s.lv = dict(self.lv)            # site -> (evT, evF, evM); ev = tuple of (slot, delta), immutable
        s.base = self.base
        s.gq = dict(self.gq)            # site -> tuple of (slot, q) sorted
        s.crafts = dict(self.crafts)    # site -> tuple of craft slots
        s.ws = dict(self.ws)
        s.orders = self.orders          # persistent cons list (prev, slot, order)
        s.deliv = dict(self.deliv)
        s.home = self.home
        s.nord = self.nord
        return s

    def order_list(self):
        out = []
        a = self.orders
        while a is not None:
            out.append((a[1], a[2]))
            a = a[0]
        out.reverse()
        return out

    def timetable(self):
        tt = {}
        a = self.orders
        while a is not None:
            tt[a[1]] = a[2]
            a = a[0]
        return tt

    # ---- primitives (all commit in place; callers copy first) -------------------------------

    def put(self, t, o):
        self.used[t] = 1
        self.orders = (self.orders, t, o)
        self.nord += 1

    def end_level(self, s, g):
        v = self.lv.get(s)
        if v is None:
            return 0
        n = 0
        for e in v[g]:
            n += e[1]
        return n

    def ok_from(self, s, g, q, t):
        """earliest t' >= t such that the level of g at s stays >= q from t' on; 99 if never."""
        v = self.lv.get(s)
        if v is None:
            return 99
        lev = 0
        start = -1
        for e in v[g]:
            lev += e[1]
            if lev >= q:
                if start < 0:
                    start = e[0]
            else:
                start = -1
        if start < 0:
            return 99
        return start if start > t else t

    def add_ev(self, s, g, t, d):
        v = self.lv.get(s)
        if v is None:
            v = ((), (), ())
        ev = v[g]
        i = len(ev)
        while i > 0 and ev[i - 1][0] > t:
            i -= 1
        ev = ev[:i] + ((t, d),) + ev[i:]
        if g == 0:
            self.lv[s] = (ev, v[1], v[2])
        elif g == 1:
            self.lv[s] = (v[0], ev, v[2])
        else:
            self.lv[s] = (v[0], v[1], ev)

    def go(self, b, target):
        boat = self.boats[b]
        pos = boat[0]
        if pos == target:
            return True
        t = boat[1]
        mp = self.mp
        nxt = mp.nxt
        routes = mp.routes
        used = self.used
        while pos != target:
            n = nxt[pos][target]
            while t < 80 and used[t]:
                t += 1
            if t >= 80:
                return False
            used[t] = 1
            self.orders = (self.orders, t, ('sail', b, n, -1, 0, -1))
            self.nord += 1
            t += routes[pos][n]
            pos = n
        boat[0] = pos
        boat[1] = t
        return True

    def load(self, b, g, q):
        """load q of g from our warehouse at the boat's site (earliest slot where it is there to stay)."""
        boat = self.boats[b]
        t = self.ok_from(boat[0], g, q, boat[1])
        used = self.used
        while t < 80 and used[t]:
            t += 1
        if t >= 80:
            return False
        self.add_ev(boat[0], g, t, -q)
        self.put(t, ('load', b, -1, g, q, -1))
        boat[2 + g] += q
        boat[1] = t + 1
        return True

    def stock_ok(self, s, t, q):
        st = self.base[s]
        last = self.t0
        done = False
        ev = self.gq.get(s)
        if ev is not None:
            for e in ev:
                tg = e[0]
                if not done and t <= tg:
                    k = (t >> 2) - (last >> 2)
                    if k:
                        st += k
                        if st > 6:
                            st = 6
                    st -= q
                    if st < 0:
                        return False
                    last = t
                    done = True
                k = (tg >> 2) - (last >> 2)
                if k:
                    st += k
                    if st > 6:
                        st = 6
                st -= e[1]
                if st < 0:
                    return False
                last = tg
        if not done:
            k = (t >> 2) - (last >> 2)
            if k:
                st += k
                if st > 6:
                    st = 6
            if st < q:
                return False
        return True

    def gather(self, b, g, q):
        boat = self.boats[b]
        s = boat[0]
        t = boat[1]
        used = self.used
        while True:
            while t < 80 and used[t]:
                t += 1
            if t >= 80:
                return False
            if self.stock_ok(s, t, q):
                break
            t += 1
        ev = self.gq.get(s, ())
        i = len(ev)
        while i > 0 and ev[i - 1][0] > t:
            i -= 1
        self.gq[s] = ev[:i] + ((t, q),) + ev[i:]
        self.put(t, ('gather', b, -1, g, q, -1))
        boat[2 + g] += q
        boat[1] = t + 1
        return True

    def unload(self, b, g, q):
        boat = self.boats[b]
        t = boat[1]
        used = self.used
        while t < 80 and used[t]:
            t += 1
        if t >= 80:
            return False
        self.add_ev(boat[0], g, t + 1, q)
        self.put(t, ('unload', b, -1, g, q, -1))
        boat[2 + g] -= q
        boat[1] = t + 1
        return True

    def _mat_time(self, w, t):
        """earliest t' >= t from which 2T+1F stay available at w, or 99."""
        a = self.ok_from(w, 0, 2, t)
        b = self.ok_from(w, 1, 1, t)
        return a if a > b else b

    def _consume(self, w, t):
        self.add_ev(w, 0, t, -2)
        self.add_ev(w, 1, t, -1)

    def build(self, b):
        boat = self.boats[b]
        w = boat[0]
        t = self._mat_time(w, boat[1])
        used = self.used
        while t < 80 and used[t]:
            t += 1
        if t >= 80:
            return False
        self._consume(w, t)
        self.ws[w] = t
        self.put(t, ('build_workshop', b, -1, -1, 0, -1))
        boat[1] = t + 1
        return True

    def craft(self, b):
        boat = self.boats[b]
        w = boat[0]
        t = boat[1]
        wst = self.ws.get(w)
        if wst is None:
            return False
        if t <= wst:
            t = wst + 1
        t = self.craft_slot(w, t)
        if t >= 77:
            return False
        crafts = self.crafts.get(w, ())
        self._consume(w, t)
        self.crafts[w] = crafts + (t,)
        self.add_ev(w, 2, t + 3, 1)
        self.put(t, ('craft', b, -1, -1, 0, -1))
        boat[1] = t + 1
        return True

    def deliver(self, b, c):
        boat = self.boats[b]
        t = boat[1]
        used = self.used
        while t < 80 and used[t]:
            t += 1
        mp = self.mp
        if t >= mp.c_deadline[c]:
            return False
        self.put(t, ('deliver', b, -1, -1, 0, c))
        boat[2 + mp.c_good[c]] -= mp.c_qty[c]
        boat[1] = t + 1
        self.deliv[c] = t
        return True

    def make_room(self, b, k, keep=-1):
        """unload junk at the boat's current site until k slots are free (never unloads good `keep`)."""
        boat = self.boats[b]
        while 3 - (boat[2] + boat[3] + boat[4]) < k:
            best = -1
            for g in range(3):
                if g != keep and boat[2 + g] > 0 and (best < 0 or boat[2 + g] > boat[2 + best]):
                    best = g
            if best < 0:
                return False
            if not self.unload(b, best, boat[2 + best]):
                return False
        return True

    # ---- sources ---------------------------------------------------------------------------

    def sources_at(self, pos, g, q, dest, skip, limit):
        """candidate (detour, kind, site, is_wh) to pick q of g, nearest by detour first."""
        mp = self.mp
        dist = mp.dist
        dp = dist[pos]
        out = []
        for s in self.lv:
            if s != skip and self.end_level(s, g) >= q:
                out.append((dp[s] + dist[s][dest], 0, s, True))
        roles = mp.roles
        for s in range(10):
            if roles[s] == g and s != skip:
                out.append((dp[s] + dist[s][dest], 1, s, False))
        out.sort()
        return out[:limit]

    def pick(self, b, s, is_wh, g, q):
        if not self.go(b, s):
            return False
        if is_wh:
            return self.load(b, g, q)
        return self.gather(b, g, q)

    # ---- read-only trials (pick the best chain before committing one copy) -------------------

    def t_go(self, pos, t, target):
        if pos == target:
            return t
        mp = self.mp
        nxt = mp.nxt
        routes = mp.routes
        used = self.used
        while pos != target:
            n = nxt[pos][target]
            while t < 80 and used[t]:
                t += 1
            if t >= 80:
                return 99
            t += routes[pos][n]
            pos = n
        return t

    def t_pick(self, s, is_wh, g, q, t):
        """slot at which a boat ready at s from t can take q of g, or 99."""
        used = self.used
        if is_wh:
            t = self.ok_from(s, g, q, t)
            while t < 80 and used[t]:
                t += 1
            return t if t < 80 else 99
        while True:
            while t < 80 and used[t]:
                t += 1
            if t >= 80:
                return 99
            if self.stock_ok(s, t, q):
                return t
            t += 1

    def t_free(self, t, n=1):
        """slot of the n-th consecutive order of one boat starting at t (each needs its own free slot)."""
        used = self.used
        while True:
            while t < 80 and used[t]:
                t += 1
            if t >= 80:
                return 99
            n -= 1
            if n == 0:
                return t
            t += 1

    # ---- hauling materials to a workshop site ----------------------------------------------

    def haul_plan(self, b, need, w, bound=99):
        """Best way for boat b to end at w having unloaded need=(T,F) (cargo counts).
        Returns (finish, room, picks) or None; picks = [(site, is_wh, good, qty), ...]."""
        boat = self.boats[b]
        mT = need[0] - boat[2]
        mF = need[1] - boat[3]
        if mT < 0:
            mT = 0
        if mF < 0:
            mF = 0
        over = boat[2] + boat[3] + boat[4] + mT + mF - 3
        room = 0
        pos = boat[0]
        t0 = boat[1]
        if over > 0:
            if boat[4] > 0:
                room = mT + mF
                t0 = self.t_free(t0) + 1          # one unload of the manufactured junk
                if t0 >= 99:
                    return None
            else:
                while over > 0 and mT > 0:
                    mT -= 1
                    over -= 1
                while over > 0 and mF > 0:
                    mF -= 1
                    over -= 1
        nun = (1 if (boat[2] + mT) else 0) + (1 if (boat[3] + mF) else 0)
        if nun == 0:
            return None
        best = None
        bt = bound
        dist = self.mp.dist
        if mT and mF:
            for first in (0, 1):
                g1, q1, g2, q2 = (0, mT, 1, mF) if first == 0 else (1, mF, 0, mT)
                for _, _, s1, wh1 in self.sources_at(pos, g1, q1, w, w, 2):
                    t1 = self.t_go(pos, t0, s1)
                    if t1 >= bt:
                        continue
                    t1 = self.t_pick(s1, wh1, g1, q1, t1) + 1
                    if t1 >= bt:
                        continue
                    for _, _, s2, wh2 in self.sources_at(s1, g2, q2, w, w, 2):
                        t2 = self.t_go(s1, t1, s2)
                        if t2 >= bt:
                            continue
                        t2 = self.t_pick(s2, wh2, g2, q2, t2) + 1
                        if t2 + dist[s2][w] >= bt:
                            continue
                        t2 = self.t_go(s2, t2, w)
                        if t2 >= bt:
                            continue
                        t2 = self.t_free(t2, nun) + 1
                        if t2 < bt:
                            bt = t2
                            best = (t2, room, ((s1, wh1, g1, q1), (s2, wh2, g2, q2)))
        elif mT or mF:
            g, q = (0, mT) if mT else (1, mF)
            for _, _, s1, wh1 in self.sources_at(pos, g, q, w, w, 3):
                t1 = self.t_go(pos, t0, s1)
                if t1 >= bt:
                    continue
                t1 = self.t_pick(s1, wh1, g, q, t1) + 1
                if t1 + dist[s1][w] >= bt:
                    continue
                t1 = self.t_go(s1, t1, w)
                if t1 >= bt:
                    continue
                t1 = self.t_free(t1, nun) + 1
                if t1 < bt:
                    bt = t1
                    best = (t1, room, ((s1, wh1, g, q),))
        else:
            t1 = self.t_go(pos, t0, w)
            if t1 < bt:
                t1 = self.t_free(t1, nun) + 1
                if t1 < bt:
                    best = (t1, room, ())
        return best

    def haul_commit(self, b, plan, w):
        if plan[1]:
            if not self.make_room(b, plan[1]):
                return False
        for s, is_wh, g, q in plan[2]:
            if not self.pick(b, s, is_wh, g, q):
                return False
        return self.finish_haul(b, w)

    def finish_haul(self, b, w):
        if not self.go(b, w):
            return False
        boat = self.boats[b]
        if boat[2] and not self.unload(b, 0, boat[2]):
            return False
        if boat[3] and not self.unload(b, 1, boat[3]):
            return False
        return True

    def haul(self, need, w):
        """Best boat for one load. Returns Sched (a new copy) or None."""
        best = None
        bb = -1
        bt = 99
        for b in range(len(self.boats)):
            r = self.haul_plan(b, need, w, bt)
            if r is not None and r[0] < bt:
                bt = r[0]
                best = r
                bb = b
        if best is None:
            return None
        S = self.copy()
        if not S.haul_commit(bb, best, w):
            return None
        return S

    def surplus(self, w):
        t = self.end_level(w, 0)
        f = self.end_level(w, 1)
        if t > 4:
            t = 4
        if f > 2:
            f = 2
        return t + 1.5 * f

    def craft_slot(self, w, t):
        wst = self.ws.get(w)
        if wst is None:
            return 99
        if t <= wst:
            t = wst + 1
        t = self._mat_time(w, t)
        used = self.used
        crafts = self.crafts.get(w, ())
        while True:
            while t < 77 and used[t]:
                t += 1
            if t >= 77:
                return 99
            clash = False
            for tc in crafts:
                if -3 < t - tc < 3:
                    clash = True
                    t = tc + 3 if tc + 3 > t else t + 1
                    break
            if not clash:
                return t

    def do_at(self, w, what):
        """some boat issues build (what=0) / craft (1) at w as early as possible. Returns Sched or None."""
        bb = -1
        bt = 99
        bh = 99
        dist = self.mp.dist
        for b in range(len(self.boats)):
            boat = self.boats[b]
            t = self.t_go(boat[0], boat[1], w)
            if t >= 99:
                continue
            if what == 0:
                t = self._mat_time(w, t)
                t = self.t_free(t) if t < 99 else 99
            else:
                t = self.craft_slot(w, t)
            h = dist[boat[0]][w]
            if t < bt or (t == bt and t < 99 and h < bh):
                bt = t
                bb = b
                bh = h
        if bb < 0 or bt >= 99:
            return None
        S = self.copy()
        if not S.go(bb, w):
            return None
        if not (S.build(bb) if what == 0 else S.craft(bb)):
            return None
        return S

    def ensure_craft(self, w, B):
        """Plan one more craft at w (hauls, workshop if missing). Returns Sched or None."""
        mp = self.mp
        if mp.roles[w] != 2:
            return None
        cands = []
        haveT = self.end_level(w, 0)
        haveF = self.end_level(w, 1)
        if w not in self.ws:
            if haveT >= 4 and haveF >= 2:
                loadsets = [()]
            else:
                nT = max(0, 4 - haveT)
                nF = max(0, 2 - haveF)
                loadsets = [((nT if nT < 3 else 3, 0), (nT - 3 if nT > 3 else 0, nF)),
                            ((nT - 3 if nT > 3 else 0, nF), (nT if nT < 3 else 3, 0)),
                            ((2, 1), (2, 1)),
                            ((3, 0), (0, 3), (3, 0)),
                            ((0, 3), (3, 0), (3, 0)),
                            ((3, 0), (1, 2), (3, 0))]
            for ls in loadsets:
                S = self
                ok = True
                built = False
                for need in ls:
                    if need[0] + need[1] == 0:
                        continue
                    S = S.haul(need, w)
                    if S is None:
                        ok = False
                        break
                    if not built and S.end_level(w, 0) >= 2 and S.end_level(w, 1) >= 1:
                        S2 = S.do_at(w, 0)
                        if S2 is None:
                            ok = False
                            break
                        S = S2
                        built = True
                if not ok:
                    continue
                if not built:
                    S = S.do_at(w, 0)
                    if S is None:
                        continue
                S = S.do_at(w, 1)
                if S is None:
                    continue
                cands.append(S)
        else:
            nT = max(0, 2 - haveT)
            nF = max(0, 1 - haveF)
            if nT + nF == 0:
                loadsets = [()]
            elif nF == 0:
                loadsets = [((nT, 0),), ((3, 0),)]
            elif nT == 0:
                loadsets = [((0, nF),), ((0, 3),), ((2, 1),)]
            else:
                loadsets = [((nT, nF),), ((3, 0), (0, 3)), ((0, 3), (3, 0)), ((3, 0), (nT, nF)), ((2, 1),)]
            for ls in loadsets:
                S = self
                ok = True
                for need in ls:
                    S = S.haul(need, w)
                    if S is None:
                        ok = False
                        break
                if not ok:
                    continue
                S = S.do_at(w, 1)
                if S is None:
                    continue
                cands.append(S)
        best = None
        bc = 1e9
        for S in cands:
            c = S.crafts[w][-1] - B * S.surplus(w) + 0.01 * S.nord
            if c < bc:
                bc = c
                best = S
        return best

    # ---- tokens ----------------------------------------------------------------------------

    def add_raw(self, c):
        mp = self.mp
        g = mp.c_good[c]
        q = mp.c_qty[c]
        d = mp.c_dest[c]
        dl = mp.c_deadline[c]
        best = None
        bt = dl
        for b in range(len(self.boats)):
            boat = self.boats[b]
            if boat[2 + g] >= q:
                t = self.t_free(self.t_go(boat[0], boat[1], d))
                if t < bt:
                    bt = t
                    best = (b, 0, None)
                continue
            m = q - boat[2 + g]
            t0 = boat[1]
            room = 0
            if 3 - (boat[2] + boat[3] + boat[4]) < m:
                room = m
                t0 = self.t_free(t0, 2) + 1
                if t0 >= 99:
                    continue
            for _, _, s, is_wh in self.sources_at(boat[0], g, m, d, -1, 3):
                t = self.t_go(boat[0], t0, s)
                if t >= bt:
                    continue
                t = self.t_pick(s, is_wh, g, m, t) + 1
                if t >= bt:
                    continue
                t = self.t_free(self.t_go(s, t, d))
                if t < bt:
                    bt = t
                    best = (b, room, (s, is_wh, m))
        if best is None:
            return None
        S = self.copy()
        b = best[0]
        if best[1] and not S.make_room(b, best[1], keep=g):
            return None
        if best[2] is not None:
            s, is_wh, m = best[2]
            if not S.pick(b, s, is_wh, g, m):
                return None
        if S.go(b, d) and S.deliver(b, c):
            return S
        return None

    def fetch_deliver(self, w, c):
        mp = self.mp
        d = mp.c_dest[c]
        bb = -1
        bt = mp.c_deadline[c]
        for b in range(len(self.boats)):
            boat = self.boats[b]
            t0 = boat[1]
            if 3 - (boat[2] + boat[3] + boat[4]) < 1:
                t0 = self.t_free(t0) + 1
                if t0 >= 99:
                    continue
            t = self.t_go(boat[0], t0, w)
            if t >= bt:
                continue
            t = self.t_pick(w, True, 2, 1, t) + 1
            if t >= bt:
                continue
            t = self.t_free(self.t_go(w, t, d))
            if t < bt:
                bt = t
                bb = b
        if bb < 0:
            return None
        S = self.copy()
        boat = S.boats[bb]
        if 3 - (boat[2] + boat[3] + boat[4]) < 1:
            if not S.make_room(bb, 1, keep=2):
                return None
        if S.go(bb, w) and S.load(bb, 2, 1) and S.go(bb, d) and S.deliver(bb, c):
            return S
        return None

    def add_m(self, c, B, more=0, ahead=1):
        """more = manufactured tokens still to come after this one; ahead = keep one craft in the pipeline."""
        mp = self.mp
        d = mp.c_dest[c]
        best = None
        bc = 1e9
        for b in range(len(self.boats)):
            if self.boats[b][4] > 0:
                S = self.copy()
                if S.go(b, d) and S.deliver(b, c):
                    cst = S.deliv[c] + (40.0 if more > 0 and ahead else 0.0)
                    if cst < bc:
                        bc = cst
                        best = S
        roles = mp.roles
        for w in range(10):
            if roles[w] != 2:
                continue
            have = self.end_level(w, 2)
            if have >= 1:
                S0 = self
            else:
                S0 = self.ensure_craft(w, B)
                if S0 is None:
                    continue
            bonus = 0.5 * B * S0.surplus(w) / 3.5
            SA = S0.fetch_deliver(w, c)
            if SA is not None:
                cst = SA.deliv[c] - bonus
                if more > 0 and ahead:
                    if SA.end_level(w, 2) < 1:
                        SA2 = SA.ensure_craft(w, B)
                        if SA2 is not None:
                            cst += 0.5 * SA2.crafts[w][-1]
                            SA = SA2
                        else:
                            cst += 40.0
                    else:
                        cst += 0.5 * SA.crafts[w][-1] if w in SA.crafts else 0.0
                if cst < bc:
                    bc = cst
                    best = SA
            if more > 0 and ahead and S0.end_level(w, 2) < 2:
                SB = S0.ensure_craft(w, B)
                if SB is not None:
                    tcr = SB.crafts[w][-1]
                    SB = SB.fetch_deliver(w, c)
                    if SB is not None:
                        cst = SB.deliv[c] - bonus + 0.5 * tcr
                        if cst < bc:
                            bc = cst
                            best = SB
        return best

    def add_boat(self):
        if len(self.boats) >= 3:
            return None
        a = self.ok_from(self.home, 0, 4, self.t0)
        t = self.ok_from(self.home, 1, 2, self.t0)
        if a > t:
            t = a
        S = self.copy()
        used = S.used
        while t < 80 and used[t]:
            t += 1
        if t >= 70:
            return None
        S.add_ev(S.home, 0, t, -4)
        S.add_ev(S.home, 1, t, -2)
        S.put(t, BUILD_BOAT)
        S.boats.append([S.home, t + 1, 0, 0, 0])
        return S

    def add(self, tok, B, more=0, ahead=1):
        if tok == BOAT_TOK:
            return self.add_boat()
        if tok in self.deliv:
            return None
        if self.mp.c_good[tok] == 2:
            return self.add_m(tok, B, more, ahead)
        return self.add_raw(tok)


def sched_root(mp, side, stocks, claims, rnd):
    s = Sched.__new__(Sched)
    s.mp = mp
    s.t0 = rnd
    s.used = bytearray(81)
    s.boats = [[(b[1] if b[2] != 0 else b[0]), rnd + b[2], b[3], b[4], b[5]] for b in side.boats]
    s.lv = {}
    wh = side.wh
    for site in range(10):
        if wh[site * 3] or wh[site * 3 + 1] or wh[site * 3 + 2]:
            s.lv[site] = tuple([(((rnd, wh[site * 3 + g]),) if wh[site * 3 + g] else ()) for g in range(3)])
    s.base = stocks[:]
    s.gq = {}
    s.crafts = {}
    s.ws = {}
    for site in range(10):
        if side.ws[site]:
            s.ws[site] = -1
            j = side.jobs[site]
            if j:
                s.crafts[site] = (rnd - (3 - j),)
                s.add_ev(site, 2, rnd + j, 1)
    s.orders = None
    s.deliv = {}
    for c in range(8):
        if claims[c] != -1:
            s.deliv[c] = -1
    s.home = side.home
    s.nord = 0
    return s


def decode_seq(mp, side, stocks, claims, rnd, seq, B, ahead=1):
    """Returns (Sched, kept tokens)."""
    S = sched_root(mp, side, stocks, claims, rnd)
    kept = []
    n = len(seq)
    for i in range(n):
        tok = seq[i]
        more = 0
        for j in range(i + 1, n):
            if 4 <= seq[j] < 8:
                more += 1
        T = S.add(tok, B, more, ahead)
        if T is not None:
            S = T
            kept.append(tok)
    return S, kept

# ==========================================================================================
# brain.py
# ==========================================================================================
# ---- brain: sequence planner with exact two-sided rollouts (uses names from core) ----
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

TOTAL_BUDGET = 4.0          # seconds of CPU inside agent() per game that the search may use
HARD_BUDGET = 6.5           # CPU beyond this: stop tracking, play the timetable blindly
WALL_HARD = float(_os.environ.get('MAPUTO_WALL', '8.5'))   # same, wall clock (0 = off, for loaded dev boxes)
_clock = _time.process_time
FIRST_EXTRA = 3.0           # the first game of a process pays for JIT warm-up
_FIRST = [True]
PARAMS = ((3.5, 1), (0.0, 1))
BEAM_W = 4
BEAM_D = 6
TOPK = 3


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
        self.dirty_n = 0

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
                self.dirty_n += 1
        if plan is None:
            self.plan = plan = TPlan([], 3.5, 1, {}, {})
        exact = left > 0.3 and (nh == 1 or (nh == 2 and rnd >= 4) or (nh == 3 and rnd >= 12) or rnd >= 20)
        if rnd - self.last_beam >= 6 or not live_tokens(mp, side, claims, rnd, plan.seq):
            self.beam_stale = True
        if not exact:
            # phase A: no rollouts; rank by the proxy against the plans the Professor holds right now
            self.vals = {}
            evs = self.read_plans(rnd)
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
        tend = tstart + min(0.35 if rnd else 1.0, left * 0.3)
        for h in self.hyps:
            if h.sid not in self.vals:
                m, ev = self.roll(plan, h, True)
                self.vals[h.sid] = m
                self.events[h.sid] = ev
                self.beam_stale = True
        cur = self.value(self.vals)
        while perf() < tend:
            if not self.pool:
                if not self.beam_stale:
                    break
                self.pool = self.beam(rnd, tend + 0.2)[:TOPK]
                self.beam_stale = False
                self.last_beam = rnd
                self.tested = set()
                continue
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
        for h in self.hyps:
            po = prof_choose(h.prof, h.eng)
            orders[seat] = o
            orders[ps] = po
            ok = h.eng.step(orders)
            h.ok = ok[seat] or o is WAIT
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
        if act in legal:
            return act
    except Exception:
        if DEBUG:
            raise
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
