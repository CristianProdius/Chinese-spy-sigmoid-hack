"""pB_rush agent: Professor-aware manufacturing rush (built from core.py + brain.py)."""
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


# ==== pB_rush brain (appended after the engine/Professor core by build.py) ====
import time

# ---------------------------------------------------------------------------------------------
# Helpers on the core model
# ---------------------------------------------------------------------------------------------

def side_clone(s):
    n = Side.__new__(Side)
    n.home = s.home
    n.score = s.score
    n.crafted = s.crafted
    n.boats = [b[:] for b in s.boats]
    n.wh = s.wh[:]
    n.ws = s.ws[:]
    n.jobs = s.jobs[:]
    return n


def eng_clone(e):
    n = Engine.__new__(Engine)
    n.mp = e.mp
    n.round = e.round
    n.stocks = e.stocks[:]
    n.claims = e.claims[:]
    n.sides = [side_clone(e.sides[0]), side_clone(e.sides[1])]
    return n


# Replan cache: a replan is a pure function of (style, round, own side minus score, est, claims).
_RC = {}
_RC_STATS = [0, 0]
_orig_replan = Professor.replan


class _Best(object):
    __slots__ = ('a',)

    def __init__(self, a):
        self.a = a

    def actions(self):
        return self.a


def _cached_replan(self, view):
    side = view.side
    key = (self.A, self.B, self.W, view.round, tuple([tuple(b) for b in side.boats]),
           tuple(side.wh), tuple(side.ws), tuple(side.jobs), tuple(self.est), tuple(view.claims))
    r = _RC.get(key, 0)
    if r == 0:
        _RC_STATS[1] += 1
        best = _orig_replan(self, view)
        r = None if best is None else (_Best(best[0].actions()), list(best[1]), best[2])
        _RC[key] = r
    else:
        _RC_STATS[0] += 1
    return r


if 'ReplanCache' not in globals():
    Professor.replan = _cached_replan

T_, F_, M_ = 0, 1, 2


class Ctx(object):
    pass


CX = Ctx()


def setup_ctx(mp, seat):
    cx = CX
    cx.mp = mp
    cx.seat = seat
    cx.ps = 1 - seat
    cx.dist = mp.dist
    cx.nxt = mp.nxt
    cx.roles = mp.roles
    cx.routes = mp.routes
    cx.home = mp.homes[seat]
    cx.phome = mp.homes[1 - seat]
    cx.good = mp.c_good
    cx.dest = mp.c_dest
    cx.qty = mp.c_qty
    cx.pts = mp.c_points
    cx.dl = mp.c_deadline
    cx.mfg = [s for s in range(10) if mp.roles[s] == 2]
    cx.src = [[s for s in range(10) if mp.roles[s] == g] for g in (0, 1)]
    hops = [[0] * 10 for _ in range(10)]
    for i in range(10):
        for j in range(10):
            n = 0
            p = i
            while p != j and n < 20:
                p = mp.nxt[p][j]
                n += 1
            hops[i][j] = n
    cx.hops = hops


# ---------------------------------------------------------------------------------------------
# Plan executor. A plan is one queue of semantic steps per boat:
#   ('goto', b, X)                 sail hop by hop until docked at X (re-issues after a lost sail)
#   ('gather', b, g, q, qmin)      gather min(q, stock, free) once it is >= qmin
#   ('load', b, g, q, qmin)        load from own warehouse here, same rule
#   ('unload', b, g)               unload all of good g (skipped if none)
#   ('build', b) ('craft', b)      when legal
#   ('deliver', b, c)              skipped once claimed / expired / impossible
#   ('boat', b)                    build_boat when legal
# Each round the executor runs the docked boat whose front step is executable with the highest
# priority (any deliver first, then the longest remaining queue).
# ---------------------------------------------------------------------------------------------

class Exe(object):
    __slots__ = ('q', 'rem', 'ptr', 'last')

    def __init__(self, q, rem):
        self.q = q
        self.rem = rem
        self.ptr = [0] * len(q)
        self.last = None

    def clone(self):
        e = Exe.__new__(Exe)
        e.q = self.q
        e.rem = self.rem
        e.ptr = self.ptr[:]
        e.last = self.last
        return e

    def done(self):
        q = self.q
        p = self.ptr
        for b in range(len(q)):
            if p[b] < len(q[b]):
                return False
        return True

    def decide(self, side, stocks, claims, rnd):
        cx = CX
        boats = side.boats
        last = self.last
        if last is not None:
            b, idx, g, prev = last
            if b < len(boats) and boats[b][3 + g] <= prev:
                self.ptr[b] = idx                       # gather failed (stock taken): retry
            self.last = None
        q = self.q
        ptr = self.ptr
        nq = len(q)
        best = None
        bestkey = -1
        bestb = -1
        roles = cx.roles
        wh = side.wh
        for b in range(len(boats)):
            if b >= nq:
                break
            boat = boats[b]
            if boat[2] != 0:
                continue
            qb = q[b]
            i = ptr[b]
            n = len(qb)
            order = None
            pos = boat[0]
            while i < n:
                st = qb[i]
                k = st[0]
                if k == 'goto':
                    X = st[2]
                    if pos == X:
                        i += 1
                        continue
                    order = ('sail', b, cx.nxt[pos][X], -1, 0, -1)
                    break
                if k == 'gather':
                    g = st[2]
                    free = 3 - boat[3] - boat[4] - boat[5]
                    a = stocks[pos] if roles[pos] == g else 0
                    m = st[3]
                    if a < m:
                        m = a
                    if free < m:
                        m = free
                    if m >= st[4] and m >= 1:
                        order = ('gather', b, -1, g, m, -1)
                    elif free == 0:
                        i += 1
                        continue
                    break
                if k == 'load':
                    g = st[2]
                    free = 3 - boat[3] - boat[4] - boat[5]
                    m = st[3]
                    a = wh[pos * 3 + g]
                    if a < m:
                        m = a
                    if free < m:
                        m = free
                    if m >= st[4] and m >= 1:
                        order = ('load', b, -1, g, m, -1)
                    elif free == 0:
                        i += 1
                        continue
                    break
                if k == 'unload':
                    g = st[2]
                    if boat[3 + g] > 0:
                        order = ('unload', b, -1, g, boat[3 + g], -1)
                        break
                    i += 1
                    continue
                if k == 'deliver':
                    c = st[2]
                    if claims[c] != -1 or rnd >= cx.dl[c]:
                        i += 1
                        continue
                    if pos != cx.dest[c]:
                        i += 1          # misplaced deliver (plan broken): skip
                        continue
                    if boat[3 + cx.good[c]] < cx.qty[c]:
                        i += 1
                        continue
                    order = ('deliver', b, -1, -1, 0, c)
                    break
                if k == 'craft':
                    if (roles[pos] == 2 and side.ws[pos] and side.jobs[pos] == 0
                            and wh[pos * 3] >= 2 and wh[pos * 3 + 1] >= 1):
                        order = ('craft', b, -1, -1, 0, -1)
                    break
                if k == 'build':
                    if side.ws[pos]:
                        i += 1
                        continue
                    if roles[pos] == 2 and wh[pos * 3] >= 2 and wh[pos * 3 + 1] >= 1:
                        order = ('build_workshop', b, -1, -1, 0, -1)
                    break
                if k == 'boat':
                    if len(boats) >= 3:
                        i += 1
                        continue
                    h3 = side.home * 3
                    if wh[h3] >= 4 and wh[h3 + 1] >= 2:
                        order = BUILD_BOAT
                    break
                i += 1      # unknown step
            ptr[b] = i
            if order is not None:
                key = self.rem[b][i]
                k0 = order[0]
                if k0 == 'deliver':
                    key += 10000000
                elif k0 == 'sail' or k0 == 'craft':
                    if key >= 1000000:
                        key += 100000
                if key > bestkey:
                    bestkey = key
                    best = order
                    bestb = b
        if best is None:
            return WAIT
        k = best[0]
        i = ptr[bestb]
        if k == 'sail':
            pass                                  # goto stays until docked
        else:
            ptr[bestb] = i + 1
            if k == 'gather':
                self.last = (bestb, i, best[3], boats[bestb][3 + best[3]])
        return best


def queue_rem(qs, seqs, nmain):
    """Static priority per step: main-plan steps (seq < nmain) first, then construction order.
    The executor adds a bonus for delivers (always first) and for main-plan sails/crafts."""
    rems = []
    for b, qb in enumerate(qs):
        sq = seqs[b]
        rem = [0] * (len(qb) + 1)
        for i in range(len(qb)):
            s = sq[i]
            rem[i] = (1000000 if s < nmain else 0) + 50000 - s
        rems.append(rem)
    return rems


# ---------------------------------------------------------------------------------------------
# Plan builder: appends projects (kit, supply, craft, M delivery, raw delivery) to boat queues,
# tracking a rough per-boat clock and the logical warehouse contents.
# ---------------------------------------------------------------------------------------------

class Bld(object):
    __slots__ = ('bp', 'bt', 'bc', 'q', 'wh', 'ws', 'W', 'mfree', 'jobfree', 'matt', 'used',
                 'cons', 'val', 'r0', 'stock0', 'tag', 'res', 'starts', 'nb', 'sq', 'nseq', 'nmain',
                 'claims0', 'ret')

    def copy(self):
        n = Bld.__new__(Bld)
        n.bp = self.bp[:]
        n.bt = self.bt[:]
        n.bc = [c[:] for c in self.bc]
        n.q = [x[:] for x in self.q]
        n.sq = [x[:] for x in self.sq]
        n.nseq = self.nseq
        n.nmain = self.nmain
        n.claims0 = self.claims0
        n.ret = self.ret
        n.wh = self.wh[:]
        n.ws = self.ws[:]
        n.W = self.W
        n.mfree = self.mfree[:]
        n.jobfree = dict(self.jobfree)
        n.matt = dict(self.matt)
        n.used = self.used[:]
        n.cons = self.cons[:]
        n.val = self.val
        n.r0 = self.r0
        n.stock0 = self.stock0
        n.tag = self.tag
        n.res = None
        n.starts = self.starts
        n.nb = self.nb
        return n

    # -- primitives --
    def goto(self, b, X):
        p = self.bp[b]
        if p != X:
            self.q[b].append(('goto', b, X))
            self.sq[b].append(self.nseq)
            self.nseq += 1
            self.bt[b] += CX.dist[p][X] + 0.3 * (CX.hops[p][X] - 1)
            self.bp[b] = X

    def act(self, b, st):
        self.q[b].append(st)
        self.sq[b].append(self.nseq)
        self.nseq += 1
        self.bt[b] += 1

    def proj_stock(self, s, t):
        r0 = self.r0
        v = self.stock0[s] + (int(t) // 4 - r0 // 4)
        if v > 6:
            v = 6
        return v - self.used[s]

    def free(self, b):
        c = self.bc[b]
        return 3 - c[0] - c[1] - c[2]

    # -- supply good g to workshop site W (need >= 1 units) --
    def supply(self, g, need, W, ban=-1):
        cx = CX
        dist = cx.dist
        best = None
        bestv = 1e9
        for b in range(self.nb):
            if b == ban:
                continue
            have = self.bc[b][g]
            fr = self.free(b)
            pos = self.bp[b]
            t0 = self.bt[b]
            if have >= need:
                t = t0 + dist[pos][W] + 1
                v = t - 0.4 * have
                if v < bestv:
                    bestv = v
                    best = (b, -1, 0, False, t)
            if fr <= 0:
                continue
            # own warehouses
            for s in range(10):
                if s == W:
                    continue
                a = self.wh[s * 3 + g]
                if a + have < need:
                    continue
                qq = min(3, fr, a)
                t = t0 + dist[pos][s] + 1 + dist[s][W] + 1
                v = t - 0.4 * (qq + have)
                if v < bestv:
                    bestv = v
                    best = (b, s, qq, True, t)
            for s in cx.src[g]:
                ta = t0 + dist[pos][s]
                a = self.proj_stock(s, ta)
                if a + have < need:
                    continue
                qq = min(3, fr, a)
                t = ta + 1 + dist[s][W] + 1
                v = t - 0.4 * (qq + have)
                if v < bestv:
                    bestv = v
                    best = (b, s, qq, False, t)
        if best is None:
            return False
        b, s, qq, is_load, t = best
        if s >= 0:
            self.goto(b, s)
            qmin = max(1, need - self.bc[b][g])
            if is_load:
                self.act(b, ('load', b, g, qq, qmin))
                self.wh[s * 3 + g] -= qq
            else:
                self.act(b, ('gather', b, g, qq, qmin))
                self.used[s] += qq
            self.bc[b][g] += qq
        self.goto(b, W)
        self.act(b, ('unload', b, g))
        self.wh[W * 3 + g] += self.bc[b][g]
        self.bc[b][g] = 0
        if self.bt[b] > self.matt.get(W, 0):
            self.matt[W] = self.bt[b]
        return True

    def ensure(self, W, nt, nf):
        if self.wh[W * 3] < nt:
            if not self.supply(0, nt - self.wh[W * 3], W):
                return False
        if self.wh[W * 3 + 1] < nf:
            if not self.supply(1, nf - self.wh[W * 3 + 1], W):
                return False
        return True

    def crafter(self, W):
        cx = CX
        best = -1
        bt = 1e9
        for b in range(self.nb):
            t = self.bt[b] + cx.dist[self.bp[b]][W]
            if t < bt:
                bt = t
                best = b
        return best

    def build_ws(self, W):
        if not self.ensure(W, 2, 1):
            return False
        b = self.crafter(W)
        self.goto(b, W)
        t = max(self.bt[b], self.matt.get(W, 0))
        self.bt[b] = t
        self.act(b, ('build', b))
        self.wh[W * 3] -= 2
        self.wh[W * 3 + 1] -= 1
        self.ws[W] = True
        return True

    def craft(self, W):
        if not self.ws[W]:
            if not self.build_ws(W):
                return False
        if not self.ensure(W, 2, 1):
            return False
        b = self.crafter(W)
        self.goto(b, W)
        t = max(self.bt[b], self.matt.get(W, 0), self.jobfree.get(W, 0))
        self.bt[b] = t
        self.act(b, ('craft', b))
        self.wh[W * 3] -= 2
        self.wh[W * 3 + 1] -= 1
        self.jobfree[W] = t + 3
        self.mfree.append((W, t + 3))
        return True

    def kit(self, W, variant):
        """Opening: both boats at home with the home stock. Builds the workshop and crafts once."""
        cx = CX
        h = cx.home
        wh = self.wh
        if self.bp[0] != h or self.bp[1] != h or self.bc[0] != [0, 0, 0] or self.bc[1] != [0, 0, 0]:
            return False
        if variant == 0:            # b0 3T ; b1 1T+2F ; b1 builds and crafts
            if wh[h * 3] < 4 or wh[h * 3 + 1] < 2:
                return False
            self.act(0, ('load', 0, 0, 3, 3))
            self.act(1, ('load', 1, 0, 1, 1))
            self.act(1, ('load', 1, 1, 2, 2))
            wh[h * 3] -= 4
            wh[h * 3 + 1] -= 2
            self.goto(0, W)
            self.goto(1, W)
            self.act(0, ('unload', 0, 0))
            self.act(1, ('unload', 1, 0))
            self.act(1, ('unload', 1, 1))
            t = max(self.bt[0], self.bt[1])
            self.bt[1] = t
            self.act(1, ('build', 1))
            self.act(1, ('craft', 1))
            self.ws[W] = True
            self.jobfree[W] = self.bt[1] + 2
            self.mfree.append((W, self.bt[1] + 2))
            self.matt[W] = t
            return True
        if variant == 1:            # b0 2T+1F builds ; b1 2T+1F crafts
            if wh[h * 3] < 4 or wh[h * 3 + 1] < 2:
                return False
            for b in (0, 1):
                self.act(b, ('load', b, 0, 2, 2))
                self.act(b, ('load', b, 1, 1, 1))
            wh[h * 3] -= 4
            wh[h * 3 + 1] -= 2
            self.goto(0, W)
            self.goto(1, W)
            self.act(0, ('unload', 0, 0))
            self.act(0, ('unload', 0, 1))
            self.act(0, ('build', 0))
            self.act(1, ('unload', 1, 0))
            self.act(1, ('unload', 1, 1))
            t = max(self.bt[0], self.bt[1])
            self.bt[1] = t
            self.act(1, ('craft', 1))
            self.ws[W] = True
            self.jobfree[W] = self.bt[1] + 2
            self.mfree.append((W, self.bt[1] + 2))
            self.matt[W] = t
            return True
        if variant == 2:            # b0 alone: 2T+1F, builds; b1 stays free (raw from home)
            if wh[h * 3] < 2 or wh[h * 3 + 1] < 1:
                return False
            self.act(0, ('load', 0, 0, 2, 2))
            self.act(0, ('load', 0, 1, 1, 1))
            wh[h * 3] -= 2
            wh[h * 3 + 1] -= 1
            self.goto(0, W)
            self.act(0, ('unload', 0, 0))
            self.act(0, ('unload', 0, 1))
            self.act(0, ('build', 0))
            self.ws[W] = True
            self.matt[W] = self.bt[0]
            return True
        if variant == 3:            # b0 3T, b1 3F (full single loads); first craft needs 1 more T
            if wh[h * 3] < 3 or wh[h * 3 + 1] < 3:
                return False
            self.act(0, ('load', 0, 0, 3, 3))
            self.act(1, ('load', 1, 1, 3, 3))
            wh[h * 3] -= 3
            wh[h * 3 + 1] -= 3
            self.goto(0, W)
            self.goto(1, W)
            self.act(0, ('unload', 0, 0))
            self.act(1, ('unload', 1, 1))
            t = max(self.bt[0], self.bt[1])
            self.bt[1] = t
            self.act(1, ('build', 1))
            self.wh[W * 3] += 1
            self.wh[W * 3 + 1] += 2
            self.ws[W] = True
            self.matt[W] = t
            return True
        return False

    # -- contracts --
    def add_M(self, c):
        cx = CX
        dist = cx.dist
        d = cx.dest[c]
        # a boat already carrying a spare manufactured good
        best = None
        bestt = 1e9
        for b in range(self.nb):
            if self.bc[b][2] > 0:
                t = self.bt[b] + dist[self.bp[b]][d]
                if t < bestt:
                    bestt = t
                    best = (b, -1, 0)
        if best is None:
            if not self.mfree:
                W = self.W
                if W < 0:
                    W = self.pick_W()
                    self.W = W
                if not self.craft(W):
                    return False
            # pick up the earliest available manufactured good
            k = min(range(len(self.mfree)), key=lambda i: self.mfree[i][1])
            w, tr = self.mfree[k]
            for b in range(self.nb):
                if self.free(b) < 1:
                    continue
                ta = self.bt[b] + dist[self.bp[b]][w]
                if ta < tr:
                    ta = tr
                t = ta + 1 + dist[w][d]
                if t < bestt:
                    bestt = t
                    best = (b, w, k)
            if best is None:
                return False
            b, w, k = best
            self.mfree.pop(k)
            self.goto(b, w)
            if self.bt[b] < tr:
                self.bt[b] = tr
            self.act(b, ('load', b, 2, 1, 1))
            self.bc[b][2] += 1
        b = best[0]
        self.goto(b, d)
        self.act(b, ('deliver', b, c))
        self.bc[b][2] -= 1
        self.cons.append(c)
        if self.ret:
            self.gather_return(b, d)
        return True

    def gather_return(self, b, d):
        """After a delivery at a raw site: fill up there and bring it to the workshop."""
        g = CX.roles[d]
        W = self.W
        if (g != 0 and g != 1) or W < 0:
            return
        fr = self.free(b)
        a = self.proj_stock(d, self.bt[b])
        qq = min(3, fr, a)
        if qq < 1:
            return
        self.act(b, ('gather', b, g, qq, 1))
        self.used[d] += qq
        self.bc[b][g] += qq
        self.goto(b, W)
        self.act(b, ('unload', b, g))
        self.wh[W * 3 + g] += self.bc[b][g]
        self.bc[b][g] = 0
        if self.bt[b] > self.matt.get(W, 0):
            self.matt[W] = self.bt[b]

    def pick_W(self):
        cx = CX
        h = cx.home
        return min(cx.mfg, key=lambda w: cx.dist[h][w])

    def add_raw(self, c):
        cx = CX
        dist = cx.dist
        g = cx.good[c]
        d = cx.dest[c]
        qn = cx.qty[c]
        best = None
        bestt = 1e9
        for b in range(self.nb):
            pos = self.bp[b]
            have = self.bc[b][g]
            t0 = self.bt[b]
            if have >= qn:
                t = t0 + dist[pos][d] + 1
                if t < bestt:
                    bestt = t
                    best = (b, -1, False, 0)
                continue
            fr = self.free(b)
            needq = qn - have
            if fr < needq:
                continue
            for s in range(10):
                if self.wh[s * 3 + g] >= needq:
                    t = t0 + dist[pos][s] + 1 + dist[s][d] + 1
                    if t < bestt:
                        bestt = t
                        best = (b, s, True, needq)
            for s in cx.src[g]:
                ta = t0 + dist[pos][s]
                if self.proj_stock(s, ta) >= needq:
                    t = ta + 1 + dist[s][d] + 1
                    if t < bestt:
                        bestt = t
                        best = (b, s, False, needq)
        if best is None:
            return False
        b, s, is_load, needq = best
        if s >= 0:
            self.goto(b, s)
            if is_load:
                self.act(b, ('load', b, g, needq, needq))
                self.wh[s * 3 + g] -= needq
            else:
                self.act(b, ('gather', b, g, needq, needq))
                self.used[s] += needq
            self.bc[b][g] += needq
        self.goto(b, d)
        self.act(b, ('deliver', b, c))
        self.bc[b][g] -= qn
        self.cons.append(c)
        if self.ret:
            self.gather_return(b, d)
        return True

    def add(self, c):
        if CX.good[c] == 2:
            return self.add_M(c)
        return self.add_raw(c)

    def finish(self):
        nm = self.nmain if self.nmain >= 0 else self.nseq
        return Exe(self.q, queue_rem(self.q, self.sq, nm))


def base_builder(side, stocks, rnd):
    """Builder at the real current state. Sailing boats start at their destination."""
    cx = CX
    b0 = Bld.__new__(Bld)
    nb = len(side.boats)
    b0.nb = nb
    b0.bp = []
    b0.bt = []
    b0.bc = []
    b0.starts = []
    for boat in side.boats:
        if boat[2] != 0:
            b0.bp.append(boat[1])
            b0.bt.append(rnd + boat[2])
            b0.starts.append(boat[1])
        else:
            b0.bp.append(boat[0])
            b0.bt.append(rnd)
            b0.starts.append(boat[0])
        b0.bc.append([boat[3], boat[4], boat[5]])
    b0.q = [[] for _ in range(nb)]
    b0.sq = [[] for _ in range(nb)]
    b0.nseq = 0
    b0.nmain = -1
    b0.ret = False
    b0.claims0 = None
    b0.wh = side.wh[:]
    b0.ws = side.ws[:]
    b0.W = -1
    for w in cx.mfg:
        if side.ws[w]:
            b0.W = w
            break
    b0.mfree = []
    b0.jobfree = {}
    b0.matt = {}
    for w in cx.mfg:
        for _ in range(side.wh[w * 3 + 2]):
            b0.mfree.append((w, rnd))
        if side.jobs[w] > 0:
            b0.mfree.append((w, rnd + side.jobs[w]))
            b0.jobfree[w] = rnd + side.jobs[w]
    b0.used = [0] * 10
    b0.cons = []
    b0.val = 0.0
    b0.r0 = rnd
    b0.stock0 = stocks[:]
    b0.tag = ''
    b0.res = None
    return b0


# ---------------------------------------------------------------------------------------------
# Own-side simulation (no opponent) to time a plan
# ---------------------------------------------------------------------------------------------

def own_sim(exe, side0, stocks0, claims0, rnd):
    cx = CX
    mp = cx.mp
    seat = cx.seat
    side = side_clone(side0)
    stocks = stocks0[:]
    claims = claims0[:]
    deliv = {}
    roles = mp.roles
    idle = 0
    while rnd < 80:
        o = exe.decide(side, stocks, claims, rnd)
        if o[0] != 'wait':
            apply_order(mp, side, stocks, claims, seat, o, None)
            if o[0] == 'deliver':
                deliv[o[5]] = rnd
            idle = 0
        else:
            idle += 1
            if exe.done():
                break
        advance_side(side)
        rnd += 1
        if (rnd & 3) == 0:
            for s in range(10):
                if (roles[s] == 0 or roles[s] == 1) and stocks[s] < 6:
                    stocks[s] += 1
        if idle > 12:
            break
    return deliv


def proxy_value(deliv, P, claims):
    """Margin proxy. P[c] = earliest predicted Professor claim round (99 = never)."""
    cx = CX
    seat = cx.seat
    v = 0.0
    for c in range(8):
        if claims[c] != -1:
            continue
        r = deliv.get(c, -1)
        p = P[c]
        if r >= 0 and (r < p or (r == p and (r & 1) == seat)):
            v += cx.pts[c] * (2.0 if p < 99 else PARAMS['w_free']) - 0.02 * r
        elif r >= 0:
            v -= 0.5
    return v


# ---------------------------------------------------------------------------------------------
# Exact rollout against one hypothesis
# ---------------------------------------------------------------------------------------------

def rollout(eng0, prof0, exe0, until=80):
    """Exact two-sided rollout. Returns (us, them, threat[8], claims) where threat[c] is the
    earliest round at which the Professor delivered or planned to deliver contract c."""
    cx = CX
    seat = cx.seat
    ps = cx.ps
    eng = eng_clone(eng0)
    prof = prof0.clone()
    exe = exe0.clone()
    threat = [99] * 8
    orders = [None, None]
    lastplan = None
    while eng.round < until:
        r = eng.round
        mine = exe.decide(eng.sides[seat], eng.stocks, eng.claims, r)
        po = prof.choose(eng.view(ps))
        if po[0] == 'deliver':
            c = po[5]
            if r < threat[c]:
                threat[c] = r
        pl = prof.plan
        if pl is not lastplan:
            lastplan = pl
            i = r + 1
            for o in pl:
                if o[0] == 'deliver':
                    c = o[5]
                    if i < threat[c]:
                        threat[c] = i
                i += 1
        orders[seat] = mine
        orders[ps] = po
        eng.step(orders)
    return eng.sides[seat].score, eng.sides[ps].score, threat, eng.claims[:]


# ---------------------------------------------------------------------------------------------
# Game state kept in memory
# ---------------------------------------------------------------------------------------------

def obs_matches(obs, eng, seat):
    if obs['claims'] != eng.claims:
        return False
    other = eng.sides[1 - seat]
    if obs['opponent_score'] != other.score:
        return False
    side = eng.sides[seat]
    own = obs['own']
    if own['score'] != side.score:
        return False
    ob = own['boats']
    if len(ob) != len(side.boats):
        return False
    vis = [False] * 10
    vis[side.home] = True
    for i, b in enumerate(ob):
        sb = side.boats[i]
        if (b['position'] != sb[0] or b['destination'] != sb[1] or b['eta'] != sb[2]
                or b['cargo'] != sb[3:6]):
            return False
        if sb[2] == 0:
            vis[sb[0]] = True
    for s in range(10):
        if side.ws[s]:
            vis[s] = True
    ow = own['warehouses']
    for s in range(10):
        if ow[s] != side.wh[s * 3:s * 3 + 3]:
            return False
    st = obs['stocks']
    for s in range(10):
        if vis[s] and st[s] != eng.stocks[s]:
            return False
    pred = []
    for i, b in enumerate(other.boats):
        if vis[b[0]] or (b[1] >= 0 and vis[b[1]]):
            pred.append((i, b[0], b[1], b[2]))
    real = sorted((b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats'])
    return real == pred


class Game(object):
    pass


GLOBAL = {'games': 0, 'mapkey': None}

PARAMS = dict(width=6, depth=7, nroll=6, iters=2, w_free=1.75, null0=1, t0_first=4.0, t0=1.6, tgame=4.2, every=6)


def new_game(obs):
    g = Game()
    mk = repr(obs['map'])
    if GLOBAL.get('mapkey') == mk and GLOBAL.get('mp') is not None:
        mp = GLOBAL['mp']
    else:
        mp = Map(obs['map'])
        GLOBAL['mp'] = mp
    seat = obs['seat']
    setup_ctx(mp, seat)
    g.mp = mp
    g.seat = seat
    g.hyps = {}
    for s in range(5):
        g.hyps[s] = [Engine(mp), Professor(s, 1 - seat)]
    g.exe = None
    g.plan_tag = ''
    g.P = []
    g.t_used = 0.0
    g.last_replan = -99
    g.nhyp_at_plan = 5
    g.first = GLOBAL['games'] == 0
    GLOBAL['games'] += 1
    if GLOBAL['mapkey'] != mk:
        _RC.clear()
        GLOBAL['mapkey'] = mk
    if len(_RC) > 200000:
        _RC.clear()
    g.dead = False
    return g


def obs_side(obs):
    own = obs['own']
    side = Side(own['home'])
    side.score = own['score']
    side.crafted = own['crafted_deliveries']
    side.boats = [[b['position'], b['destination'], b['eta']] + list(b['cargo']) for b in own['boats']]
    side.wh = [x for row in own['warehouses'] for x in row]
    side.ws = [bool(x) for x in own['workshops']]
    side.jobs = list(own['jobs'])
    return side


def evaluate_exact(g, exe, hyps):
    """Returns (key, threats) with key = (min margin, mean margin) over the hypotheses and
    threats[h] the Professor's threat rounds per contract under hypothesis h."""
    ms = []
    ths = []
    for s, (eng, prof) in hyps:
        us, them, th, cl = rollout(eng, prof, exe)
        ms.append(us - them)
        ths.append(th)
    return (min(ms), sum(ms) / float(len(ms))), ths


def first_plan_threat(hyps):
    """Threat rounds from each hypothesis' current plan only (cheap, no full rollout)."""
    ths = []
    for s, (eng, prof) in hyps:
        p = prof.clone()
        r = eng.round
        th = [99] * 8
        po = p.choose(eng.view(CX.ps))
        if po[0] == 'deliver':
            th[po[5]] = r
        i = r + 1
        for o in p.plan:
            if o[0] == 'deliver' and i < th[o[5]]:
                th[o[5]] = i
            i += 1
        ths.append(th)
    return ths


def proxy_multi(deliv, Ps, claims):
    v = [proxy_value(deliv, P, claims) for P in Ps]
    return min(v) + 0.05 * sum(v) / len(v)


def with_tail(n):
    """Copy of plan n with every other open contract appended at low priority (keeps the
    pipeline busy if the Professor turns out slower than its threat times)."""
    cx = CX
    t = n.copy()
    t.nmain = t.nseq
    open_c = [c for c in range(8) if c not in t.cons and n.res is not None]
    open_c.sort(key=lambda c: (cx.good[c] != 2, cx.dl[c]))
    for c in open_c:
        if t.claims0[c] != -1 or t.r0 >= cx.dl[c]:
            continue
        u = t.copy()
        if u.add(c):
            t = u
    t.tag = n.tag + '+t'
    return t


def beam(g, side, stocks, claims, rnd, P, t_lim):
    cx = CX
    roots = []
    base = base_builder(side, stocks, rnd)
    base.claims0 = claims
    roots.append(base)
    if not any(side.ws):
        for W in cx.mfg:
            for v in (0, 1, 2, 3):
                r = base.copy()
                if r.kit(W, v):
                    r.W = W
                    r.tag = 'k%d%d' % (W, v)
                    roots.append(r)
    for r in list(roots):
        if r.W >= 0 or r is base:
            r2 = r.copy()
            r2.ret = True
            r2.tag = r.tag + 'r'
            roots.append(r2)
    for r in roots:
        r.res = own_sim(r.finish(), side, stocks, claims, rnd)
        r.val = proxy_multi(r.res, P, claims)
    frontier = roots
    pool = list(roots)
    width = PARAMS['width']
    for depth in range(PARAMS['depth']):
        nxt = []
        for nd in frontier:
            for c in range(8):
                if c in nd.cons or claims[c] != -1 or rnd >= cx.dl[c]:
                    continue
                ch = nd.copy()
                if not ch.add(c):
                    continue
                ch.res = own_sim(ch.finish(), side, stocks, claims, rnd)
                ch.val = proxy_multi(ch.res, P, claims)
                ch.tag = nd.tag + ('.%d' % c)
                nxt.append(ch)
            if time.process_time() > t_lim:
                break
        if not nxt:
            break
        nxt.sort(key=lambda n: -n.val)
        frontier = nxt[:width]
        pool.extend(frontier)
        if time.process_time() > t_lim:
            break
    pool.sort(key=lambda n: -n.val)
    return pool


def dbg(*a):
    if PARAMS.get('debug'):
        import sys
        sys.stderr.write(' '.join(str(x) for x in a) + '\n')


def replan(g, obs, side, budget):
    """Search plans with the builder + own sim (proxy), then pick by exact rollouts."""
    t_start = time.process_time()
    rnd = obs['round']
    claims = list(obs['claims'])
    hyps = sorted(g.hyps.items())
    stocks = hyps[0][1][0].stocks[:]
    cur = g.exe
    if cur is None:
        cur = Exe([[] for _ in side.boats], [[0] for _ in side.boats])
        if PARAMS['null0']:
            k0, Ps = evaluate_exact(g, cur, hyps)
        else:
            Ps = first_plan_threat(hyps)
        best = ('cur', cur, (-999, -999), Ps)
    else:
        curkey, Ps = evaluate_exact(g, cur, hyps)
        best = ('cur', cur, curkey, Ps)
    dbg('replan r%d hyps=%s cur=%s P=%s' % (rnd, [h[0] for h in hyps], best[2], Ps))
    tried = set()
    for it in range(PARAMS['iters']):
        now = time.process_time()
        left = t_start + budget - now
        if left < budget * 0.15:
            break
        pool = beam(g, side, stocks, claims, rnd, Ps, now + left * 0.45)
        cands = []
        seen = set()
        for n in pool:
            k = (n.tag[:3],) + tuple(n.cons[:2])
            if k in seen or tuple(n.cons) + (n.tag[:3],) in tried:
                continue
            seen.add(k)
            tried.add(tuple(n.cons) + (n.tag[:3],))
            cands.append(n)
            if len(cands) >= PARAMS['nroll']:
                break
        opts = []
        for n in cands:
            opts.append(n)
            opts.append(with_tail(n))
        for n in opts:
            if time.process_time() > t_start + budget and best[0] != 'cur':
                break
            exe = n.finish()
            key, ths = evaluate_exact(g, exe, hyps)
            dbg('   it%d %-28s proxy=%6.2f exact=%s deliv=%s' % (it, n.tag, n.val, key, sorted((r, c) for c, r in (n.res or {}).items())))
            if key > best[2]:
                best = (n.tag, exe, key, ths)
        changed = False
        bP = best[3]
        newPs = []
        for h in range(len(Ps)):
            row = list(Ps[h])
            for c in range(8):
                if bP[h][c] < row[c]:
                    row[c] = bP[h][c]
                    changed = True
            newPs.append(row)
        if not changed:
            break
        Ps = newPs
    tag, exe, key, ths = best
    dbg('  -> %s %s (%.2fs)' % (tag, key, time.process_time() - t_start))
    g.P = ths
    g.exe = exe if tag == 'cur' else exe.clone()
    if tag != 'cur':
        g.plan_tag = tag
    g.plan_key = key
    return key


def brain(obs, memory):
    t0 = time.process_time()
    rnd = obs['round']
    g = memory.get('g')
    if g is None or rnd == 0:
        g = new_game(obs)
        memory['g'] = g
    seat = g.seat
    # 1. prune hypotheses with the new observation
    if rnd > 0 and not g.dead:
        for s in list(g.hyps):
            if not obs_matches(obs, g.hyps[s][0], seat):
                del g.hyps[s]
        if not g.hyps:
            g.dead = True
    side = obs_side(obs)
    # 2. (re)plan
    nh = len(g.hyps)
    if not g.dead:
        budget_left = PARAMS['tgame'] + (6.0 if g.first else 0.0) - g.t_used
        need = (g.exe is None or nh < g.nhyp_at_plan or g.exe.done()
                or (rnd - g.last_replan >= PARAMS['every'] and rnd < 74))
        if need and budget_left > 0.3:
            if rnd == 0:
                b = PARAMS['t0_first'] if g.first else PARAMS['t0']
            else:
                b = min(0.6, budget_left / 5.0)
            replan(g, obs, side, b)
            g.last_replan = rnd
            g.nhyp_at_plan = nh
    if g.exe is None:
        g.exe = Exe([[] for _ in side.boats], [[0] for _ in side.boats])
    # 3. our order
    stocks = [x if x is not None else 0 for x in obs['stocks']]
    mine = g.exe.decide(side, stocks, obs['claims'], rnd)
    act = order_to_json(mine)
    if act not in obs['legal_actions']:
        g.bad = getattr(g, 'bad', 0) + 1
        act = fallback(obs)
        mine = order_from_json(act)
    # 4. advance hypotheses
    if not g.dead:
        orders = [None, None]
        orders[seat] = mine
        for s, (eng, prof) in g.hyps.items():
            orders[1 - seat] = prof.choose(eng.view(1 - seat))
            eng.step(orders)
    g.t_used += time.process_time() - t0
    return act


def fallback(obs):
    legal = obs['legal_actions']
    for a in legal:
        if a.get('op') == 'deliver':
            return a
    return legal[0]


def agent(observation, memory):
    try:
        act = brain(observation, memory)
        if act in observation['legal_actions']:
            return act
        g = memory.get('g')
        if g is not None:
            g.bad = getattr(g, 'bad', 0) + 1
    except Exception:
        import traceback
        memory['err'] = traceback.format_exc()
        if memory.get('debug'):
            raise
    return fallback(observation)


def serve():
    import json
    import sys
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
