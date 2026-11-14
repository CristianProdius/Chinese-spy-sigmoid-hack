"""The Professor of Maputo Bay - oracle agent (exact opponent model + foresight planner)."""
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
_FASTCORE_SRC = '"""fastcore: a fast, order-for-order identical copy of work/binary/professor.py.\n\nSame public API as professor.py: Map, Engine (+ .clone()), Side, View, legal_actions, is_legal,\napply_order, advance_side, Professor (choose / clone / replan), view_from_observation,\norder_to_json / order_from_json, generate_map, style_permutation, STYLES, WAIT, BUILD_BOAT, o_*.\nOrders at the API are the same 6-tuples. Extra: ReplanCache, Tracker / Hypothesis (style tracking\nand lookahead), Engine.clone(), Professor(cache=...).\n\nStdlib only, Python 3.8+ / PyPy 3.10. Self-contained so it can be inlined into main.py.\n\nWhat is faster (behaviour is unchanged, see difftest.py):\n  * The Professor\'s internal Sim is one flat int list (one slice per copy) and orders inside the\n    planner are small ints (op | boat << 4 | arg << 6).\n  * travel() is one O(1) fast-forward (other boats, jobs and stock regeneration advanced in bulk)\n    instead of one full Sim.step per round. Waits are not recorded in sequential sims (interleave\n    drops them anyway); the 160-round Sim limit is applied exactly.\n  * Orders that are legal by construction (travel sails, loads/gathers/unloads inside acquire) skip\n    the legality check. Interleave checks legality once per chosen order (the reference checks twice)\n    and batches waits up to the next event that can change legality.\n  * acquire / manufactured compute the finishing round (and cost) of a branch before copying the\n    Sim and skip branches that cannot win (the reference copies, simulates, then compares).\n  * interleave of a child node resumes from a snapshot of its parent\'s run (the runs are identical\n    until the parent\'s first per-boat queue runs dry).\n  * Whole replans are memoised in a ReplanCache keyed by everything replan reads (round, own side,\n    stock estimates, claims), one cache per (map, style), shared by all Professor clones.\n"""\nfrom array import array\nfrom collections import deque\nfrom itertools import islice\n\nINF = 100000\n\nWAIT = (\'wait\', -1, -1, -1, 0, -1)\nBUILD_BOAT = (\'build_boat\', -1, -1, -1, 0, -1)\n\n\ndef o_sail(b, d): return (\'sail\', b, d, -1, 0, -1)\ndef o_gather(b, g, q): return (\'gather\', b, -1, g, q, -1)\ndef o_load(b, g, q): return (\'load\', b, -1, g, q, -1)\ndef o_unload(b, g, q): return (\'unload\', b, -1, g, q, -1)\ndef o_build_workshop(b): return (\'build_workshop\', b, -1, -1, 0, -1)\ndef o_craft(b): return (\'craft\', b, -1, -1, 0, -1)\ndef o_deliver(b, c): return (\'deliver\', b, -1, -1, 0, c)\n\n\ndef order_to_json(o):\n    op = o[0]\n    if op in (\'wait\', \'build_boat\'):\n        return {\'op\': op}\n    if op == \'sail\':\n        return {\'op\': op, \'boat\': o[1], \'destination\': o[2]}\n    if op in (\'gather\', \'load\', \'unload\'):\n        return {\'op\': op, \'boat\': o[1], \'good\': o[3], \'quantity\': o[4]}\n    if op in (\'build_workshop\', \'craft\'):\n        return {\'op\': op, \'boat\': o[1]}\n    if op == \'deliver\':\n        return {\'op\': op, \'boat\': o[1], \'contract\': o[5]}\n    raise ValueError(o)\n\n\ndef order_from_json(a):\n    op = a[\'op\']\n    if op == \'wait\':\n        return WAIT\n    if op == \'build_boat\':\n        return BUILD_BOAT\n    if op == \'sail\':\n        return o_sail(a[\'boat\'], a[\'destination\'])\n    if op in (\'gather\', \'load\', \'unload\'):\n        return (op, a[\'boat\'], -1, a[\'good\'], a[\'quantity\'], -1)\n    if op in (\'build_workshop\', \'craft\'):\n        return (op, a[\'boat\'], -1, -1, 0, -1)\n    if op == \'deliver\':\n        return o_deliver(a[\'boat\'], a[\'contract\'])\n    raise ValueError(a)\n\n\n# (surplus weight B, time exponent A, first-workshop bonus W), indexed by style id 0-4\nSTYLES = [\n    (3.5, 0.85, 8),\n    (1.8, 1.15, 0),\n    (1.8, 0.85, 0),\n    (3.5, 0.0, 0),\n    (0.0, 0.85, 8),\n]\n\nM64 = (1 << 64) - 1\n\n\ndef splitmix_next(state):\n    state = (state + 0x9e3779b97f4a7c15) & M64\n    z = state\n    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64\n    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64\n    return state, z ^ (z >> 31)\n\n\ndef style_permutation(seed):\n    perm = [0, 1, 2, 3, 4]\n    state = seed ^ 0x5354594c45534554\n    for i in range(5, 1, -1):\n        state, v = splitmix_next(state)\n        j = v % i\n        perm[i - 1], perm[j] = perm[j], perm[i - 1]\n    return perm\n\n\n# ---------------------------------------------------------------------------------------------\n# Integer order codes (planner internals): code = op | boat << 4 | arg << 6\n#   sail: arg = destination; gather/load/unload: arg = good * 4 + quantity; deliver: arg = contract\n# ---------------------------------------------------------------------------------------------\nOP_WAIT, OP_SAIL, OP_GATHER, OP_LOAD, OP_UNLOAD, OP_BUILD_WS, OP_CRAFT, OP_DELIVER, OP_BUILD_BOAT = range(9)\n_OPNAMES = (\'wait\', \'sail\', \'gather\', \'load\', \'unload\', \'build_workshop\', \'craft\', \'deliver\', \'build_boat\')\n\nCODE2ORDER = [None] * 1024\nORDER2CODE = {}\n\n\ndef _reg(code, o):\n    CODE2ORDER[code] = o\n    ORDER2CODE[o] = code\n\n\n_reg(OP_WAIT, WAIT)\n_reg(OP_BUILD_BOAT, BUILD_BOAT)\nfor _b in range(4):\n    for _d in range(10):\n        _reg(OP_SAIL | _b << 4 | _d << 6, o_sail(_b, _d))\n    for _g in range(3):\n        for _q in range(1, 4):\n            _reg(OP_GATHER | _b << 4 | (_g * 4 + _q) << 6, o_gather(_b, _g, _q))\n            _reg(OP_LOAD | _b << 4 | (_g * 4 + _q) << 6, o_load(_b, _g, _q))\n            _reg(OP_UNLOAD | _b << 4 | (_g * 4 + _q) << 6, o_unload(_b, _g, _q))\n    _reg(OP_BUILD_WS | _b << 4, o_build_workshop(_b))\n    _reg(OP_CRAFT | _b << 4, o_craft(_b))\n    for _c in range(16):\n        _reg(OP_DELIVER | _b << 4 | _c << 6, o_deliver(_b, _c))\nCODE2ORDER = tuple(CODE2ORDER)\n\n\ndef encode_order(o):\n    """Order tuple -> int code (-1 if it has no code, e.g. a malformed order)."""\n    return ORDER2CODE.get(tuple(o), -1)\n\n\ndef decode_order(code):\n    return CODE2ORDER[code]\n\n\nclass Map:\n    """Static map data plus the engine\'s all-pairs distances and next hops (Floyd-Warshall)."""\n\n    def __init__(self, m):\n        self.topology = m.get(\'topology\', 0)\n        self.roles = list(m[\'roles\'])\n        self.homes = list(m[\'homes\'])\n        self.routes = [list(r) for r in m[\'routes\']]\n        cs = m[\'contracts\']\n        self.c_good = [c[\'good\'] for c in cs]\n        self.c_qty = [c[\'quantity\'] for c in cs]\n        self.c_dest = [c[\'destination\'] for c in cs]\n        self.c_points = [c[\'points\'] for c in cs]\n        self.c_deadline = [c[\'deadline\'] for c in cs]\n        self.ncontracts = len(cs)\n        if self.ncontracts > NCMAX:\n            raise ValueError(\'at most %d contracts supported\' % NCMAX)\n        n = 10\n        dist = [[(self.routes[i][j] if self.routes[i][j] != 0 and i != j else (0 if i == j else INF))\n                 for j in range(n)] for i in range(n)]\n        nxt = [[(j if self.routes[i][j] != 0 else -1) for j in range(n)] for i in range(n)]\n        for k in range(n):\n            dk = dist[k]\n            for i in range(n):\n                di = dist[i]\n                dik = di[k]\n                ni = nxt[i]\n                for j in range(n):\n                    v = dk[j] + dik\n                    if v < di[j]:\n                        di[j] = v\n                        ni[j] = ni[k]\n        self.dist = dist\n        self.nxt = nxt\n        self.neigh = [[j for j in range(n) if self.routes[i][j] != 0] for i in range(n)]\n        # ---- fastcore extras -------------------------------------------------------------\n        self.raw_sites = tuple(s for s in range(n) if self.roles[s] in (0, 1))\n        self.mfg_sites = tuple(s for s in range(n) if self.roles[s] == 2)\n        # travel: number of rounds (sum of hop lengths along nxt) or -1 if unreachable,\n        # and per boat the sail codes along the path\n        self.tlen = [[0] * n for _ in range(n)]\n        self.tsails = [[[None] * n for _ in range(n)] for _b in range(4)]\n        for i in range(n):\n            for j in range(n):\n                if i == j:\n                    for b in range(4):\n                        self.tsails[b][i][j] = ()\n                    continue\n                p = i\n                hops = []\n                total = 0\n                ok = True\n                while p != j:\n                    q = nxt[p][j]\n                    if q < 0:\n                        ok = False\n                        break\n                    hops.append(q)\n                    total += self.routes[p][q]\n                    p = q\n                    if len(hops) > 20:\n                        ok = False\n                        break\n                self.tlen[i][j] = total if ok else -1\n                for b in range(4):\n                    self.tsails[b][i][j] = tuple(OP_SAIL | b << 4 | h << 6 for h in hops) if ok else None\n        # acquire candidates: for (cur, dest, good) all (site, is_load) entries in the reference\n        # order (loads by site, then gathers by site), stably sorted by dist[cur][s] + dist[s][dest]\n        self.acq_cands = [[[None] * 3 for _ in range(n)] for _ in range(n)]\n        for cur in range(n):\n            for dest in range(n):\n                for g in range(3):\n                    ent = [(s, True) for s in range(n)] + [(s, False) for s in range(n) if self.roles[s] == g]\n                    ent.sort(key=lambda e: dist[cur][e[0]] + dist[e[0]][dest])\n                    self.acq_cands[cur][dest][g] = tuple(ent)\n        self.replan_caches = {}\n\n    def replan_cache(self, style, maxsize=None):\n        """The shared ReplanCache of this map for a style (id or (B, A, W) triple)."""\n        if isinstance(style, int):\n            style = STYLES[style]\n        style = tuple(style)\n        c = self.replan_caches.get(style)\n        if c is None:\n            c = self.replan_caches[style] = ReplanCache(maxsize or DEFAULT_CACHE_SIZE)\n        return c\n\n\n# ---------------------------------------------------------------------------------------------\n# Engine (two sides). Same structures and semantics as professor.py.\n# ---------------------------------------------------------------------------------------------\n\ndef is_legal(mp, side, stocks, claims, rnd, o):\n    """Exactly `o in legal_actions(...)` (engine function 0x21660)."""\n    op = o[0]\n    if op == \'wait\':\n        return True\n    if op == \'build_boat\':\n        h3 = side.home * 3\n        return len(side.boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2\n    b = o[1]\n    if b < 0 or b >= len(side.boats):\n        return False\n    boat = side.boats[b]\n    if boat[2] != 0:\n        return False\n    pos = boat[0]\n    if op == \'sail\':\n        d = o[2]\n        return 0 <= d < 10 and mp.routes[pos][d] != 0\n    free = 3 - (boat[3] + boat[4] + boat[5])\n    if op == \'gather\':\n        role = mp.roles[pos]\n        if role != 0 and role != 1:\n            return False\n        return o[3] == role and 1 <= o[4] <= min(stocks[pos], free)\n    if op == \'load\':\n        g = o[3]\n        return 0 <= g < 3 and 1 <= o[4] <= min(side.wh[pos * 3 + g], free)\n    if op == \'unload\':\n        g = o[3]\n        return 0 <= g < 3 and 1 <= o[4] <= boat[3 + g]\n    if op == \'build_workshop\':\n        return (mp.roles[pos] == 2 and not side.ws[pos]\n                and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1)\n    if op == \'craft\':\n        return (mp.roles[pos] == 2 and side.ws[pos] and side.jobs[pos] == 0\n                and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1)\n    if op == \'deliver\':\n        c = o[5]\n        return (0 <= c < mp.ncontracts and claims[c] == -1 and mp.c_deadline[c] > rnd\n                and mp.c_dest[c] == pos and boat[3 + mp.c_good[c]] >= mp.c_qty[c])\n    return False\n\n\ndef legal_actions(mp, side, stocks, claims, rnd):\n    """Legal orders in the engine\'s order (0x21660)."""\n    out = [WAIT]\n    for b, boat in enumerate(side.boats):\n        if boat[2] != 0:\n            continue\n        pos = boat[0]\n        free = 3 - (boat[3] + boat[4] + boat[5])\n        for j in mp.neigh[pos]:\n            out.append(o_sail(b, j))\n        role = mp.roles[pos]\n        if role == 0 or role == 1:\n            for q in range(1, min(stocks[pos], free) + 1):\n                out.append(o_gather(b, role, q))\n        for g in range(3):\n            for q in range(1, min(side.wh[pos * 3 + g], free) + 1):\n                out.append(o_load(b, g, q))\n            for q in range(1, boat[3 + g] + 1):\n                out.append(o_unload(b, g, q))\n        if role == 2 and side.wh[pos * 3] >= 2 and side.wh[pos * 3 + 1] >= 1:\n            if not side.ws[pos]:\n                out.append(o_build_workshop(b))\n            elif side.jobs[pos] == 0:\n                out.append(o_craft(b))\n        for c in range(mp.ncontracts):\n            if (claims[c] == -1 and mp.c_deadline[c] > rnd and mp.c_dest[c] == pos\n                    and boat[3 + mp.c_good[c]] >= mp.c_qty[c]):\n                out.append(o_deliver(b, c))\n    h3 = side.home * 3\n    if len(side.boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2:\n        out.append(BUILD_BOAT)\n    return out\n\n\ndef apply_order(mp, side, stocks, claims, seat, o, used_routes):\n    """Engine function 0x22090. Returns False when the order fails (boat does nothing)."""\n    op = o[0]\n    if op == \'wait\':\n        return True\n    if op == \'build_boat\':\n        h3 = side.home * 3\n        side.wh[h3] -= 4\n        side.wh[h3 + 1] -= 2\n        side.boats.append([side.home, -1, 0, 0, 0, 0])\n        return True\n    boat = side.boats[o[1]]\n    pos = boat[0]\n    if op == \'sail\':\n        d = o[2]\n        if used_routes is not None:\n            if (pos, d) in used_routes:\n                return False\n            used_routes.add((pos, d))\n            used_routes.add((d, pos))\n        boat[1] = d\n        boat[2] = mp.routes[pos][d]\n        return True\n    if op == \'gather\':\n        q = o[4]\n        if stocks[pos] < q:\n            return False\n        stocks[pos] -= q\n        boat[3 + o[3]] += q\n        return True\n    if op == \'load\':\n        side.wh[pos * 3 + o[3]] -= o[4]\n        boat[3 + o[3]] += o[4]\n        return True\n    if op == \'unload\':\n        side.wh[pos * 3 + o[3]] += o[4]\n        boat[3 + o[3]] -= o[4]\n        return True\n    if op == \'build_workshop\':\n        side.wh[pos * 3] -= 2\n        side.wh[pos * 3 + 1] -= 1\n        side.ws[pos] = True\n        return True\n    if op == \'craft\':\n        side.wh[pos * 3] -= 2\n        side.wh[pos * 3 + 1] -= 1\n        side.jobs[pos] = 3\n        return True\n    if op == \'deliver\':\n        c = o[5]\n        if claims[c] != -1:\n            return False\n        g = mp.c_good[c]\n        boat[3 + g] -= mp.c_qty[c]\n        side.score += mp.c_points[c]\n        if g == 2:\n            side.crafted += 1\n        claims[c] = seat\n        return True\n    raise ValueError(\'unknown order %r\' % (o,))\n\n\ndef advance_side(side):\n    for boat in side.boats:\n        if boat[2] != 0:\n            boat[2] -= 1\n            if boat[2] == 0:\n                boat[0] = boat[1]\n                boat[1] = -1\n    jobs = side.jobs\n    for s in range(10):\n        if jobs[s] != 0:\n            jobs[s] -= 1\n            if jobs[s] == 0:\n                side.wh[s * 3 + 2] += 1\n\n\nclass Side:\n    __slots__ = (\'home\', \'score\', \'crafted\', \'boats\', \'wh\', \'ws\', \'jobs\')\n\n    def __init__(self, home):\n        self.home = home\n        self.score = 0\n        self.crafted = 0\n        self.boats = [[home, -1, 0, 0, 0, 0], [home, -1, 0, 0, 0, 0]]\n        self.wh = [0] * 30\n        self.wh[home * 3] = 5\n        self.wh[home * 3 + 1] = 3\n        self.ws = [False] * 10\n        self.jobs = [0] * 10\n\n    def clone(self):\n        s = Side.__new__(Side)\n        s.home = self.home\n        s.score = self.score\n        s.crafted = self.crafted\n        s.boats = [b[:] for b in self.boats]\n        s.wh = self.wh[:]\n        s.ws = self.ws[:]\n        s.jobs = self.jobs[:]\n        return s\n\n\nclass View:\n    """What a seat is given each round (engine struct built by 0x311e0)."""\n    __slots__ = (\'mp\', \'side\', \'round\', \'seat\', \'opponent_score\', \'stocks\', \'visible\', \'claims\',\n                 \'enemy_boats\')\n\n\nclass Engine:\n    """Full two-sided game state (engine struct at game+8)."""\n\n    def __init__(self, mp):\n        self.mp = mp\n        self.round = 0\n        self.sides = [Side(mp.homes[0]), Side(mp.homes[1])]\n        self.stocks = [4 if r in (0, 1) else 0 for r in mp.roles]\n        self.claims = [-1] * mp.ncontracts\n\n    def clone(self):\n        e = Engine.__new__(Engine)\n        e.mp = self.mp\n        e.round = self.round\n        e.sides = [self.sides[0].clone(), self.sides[1].clone()]\n        e.stocks = self.stocks[:]\n        e.claims = self.claims[:]\n        return e\n\n    def visible(self, seat):\n        side = self.sides[seat]\n        vis = [False] * 10\n        vis[side.home] = True\n        ws = side.ws\n        for s in self.mp.mfg_sites:\n            if ws[s]:\n                vis[s] = True\n        for boat in side.boats:\n            if boat[2] == 0:\n                vis[boat[0]] = True\n        return vis\n\n    def view(self, seat):\n        v = View()\n        side = self.sides[seat]\n        v.mp = self.mp\n        v.side = side\n        v.round = self.round\n        v.seat = seat\n        v.opponent_score = self.sides[1 - seat].score\n        vis = [False] * 10\n        vis[side.home] = True\n        ws = side.ws\n        for s in range(10):\n            if ws[s]:\n                vis[s] = True\n        for boat in side.boats:\n            if boat[2] == 0:\n                vis[boat[0]] = True\n        v.visible = vis\n        st = self.stocks\n        v.stocks = [st[s] if vis[s] else 4 for s in range(10)]\n        v.claims = self.claims\n        v.enemy_boats = [(i, boat[0], boat[1], boat[2])\n                         for i, boat in enumerate(self.sides[1 - seat].boats)\n                         if vis[boat[0]] or (boat[1] >= 0 and vis[boat[1]])]\n        return v\n\n    def legal(self, seat):\n        if self.round >= 80:\n            return []\n        side = self.sides[seat]\n        vis = [False] * 10\n        vis[side.home] = True\n        for s in range(10):\n            if side.ws[s]:\n                vis[s] = True\n        for boat in side.boats:\n            if boat[2] == 0:\n                vis[boat[0]] = True\n        st = self.stocks\n        return legal_actions(self.mp, side, [st[s] if vis[s] else 4 for s in range(10)], self.claims,\n                             self.round)\n\n    def step(self, orders):\n        """orders[seat]. Seat round%2 resolves first. Returns [ok0, ok1]."""\n        first = self.round % 2\n        used = set()\n        ok = [True, True]\n        for seat in (first, 1 - first):\n            ok[seat] = apply_order(self.mp, self.sides[seat], self.stocks, self.claims, seat,\n                                   orders[seat], used)\n        advance_side(self.sides[0])\n        advance_side(self.sides[1])\n        self.round += 1\n        if self.round % 4 == 0:\n            st = self.stocks\n            for s in self.mp.raw_sites:\n                if st[s] < 6:\n                    st[s] += 1\n        return ok\n\n\ndef view_from_observation(obs, mp=None):\n    """Build a View from the JSON observation the agent receives."""\n    v = View()\n    v.mp = mp or Map(obs[\'map\'])\n    own = obs[\'own\']\n    side = Side(own[\'home\'])\n    side.score = own[\'score\']\n    side.crafted = own[\'crafted_deliveries\']\n    side.boats = [[b[\'position\'], b[\'destination\'], b[\'eta\']] + list(b[\'cargo\']) for b in own[\'boats\']]\n    side.wh = [x for row in own[\'warehouses\'] for x in row]\n    side.ws = [bool(x) for x in own[\'workshops\']]\n    side.jobs = list(own[\'jobs\'])\n    v.side = side\n    v.round = obs[\'round\']\n    v.seat = obs[\'seat\']\n    v.opponent_score = obs[\'opponent_score\']\n    v.visible = [bool(x) for x in obs[\'visible\']]\n    v.stocks = [(s if s is not None else 4) for s in obs[\'stocks\']]\n    v.claims = list(obs[\'claims\'])\n    v.enemy_boats = [(b[\'boat\'], b[\'position\'], b[\'destination\'], b[\'eta\']) for b in obs[\'enemy_boats\']]\n    return v\n\n\n# ---------------------------------------------------------------------------------------------\n# The Professor\'s planner on a flat Sim\n# ---------------------------------------------------------------------------------------------\n# Flat Sim layout (one int list):\nNCMAX = 8\nF_R = 0          # round\nF_OK = 1         # ok flag (1/0)\nF_SC = 2         # score\nF_CR = 3         # crafted deliveries\nF_HM = 4         # home\nF_NB = 5         # number of boats\nF_ST = 6         # stocks[10] (the Professor\'s estimates)\nF_CL = 16        # claims[8]\nF_WH = 24        # warehouses[10][3]\nF_WS = 54        # workshops[10] (0/1)\nF_JB = 64        # jobs[10]\nF_BT = 74        # boats: 6 ints each (position, destination, eta, cargo0, cargo1, cargo2)\n\n\nclass Sim:\n    """v: flat state; base: full code list of an interleave run (with waits) or None;\n    basenw: its non-wait codes; acts: persistent cons list (prev, code-or-tuple-of-codes) of the\n    sequential (non-wait) orders added after base; memo: per-object cache of manufactured()."""\n    __slots__ = (\'v\', \'base\', \'basenw\', \'acts\', \'memo\', \'snaps\')\n\n    def copy(self):\n        s = Sim.__new__(Sim)\n        s.v = self.v[:]\n        s.base = self.base\n        s.basenw = self.basenw\n        s.acts = self.acts\n        s.memo = None\n        s.snaps = None\n        return s\n\n    @property\n    def round(self):\n        return self.v[F_R]\n\n    @property\n    def score(self):\n        return self.v[F_SC]\n\n    def seq_codes(self):\n        """Non-wait codes added after base, in order."""\n        out = []\n        a = self.acts\n        while a is not None:\n            x = a[1]\n            if type(x) is int:\n                out.append(x)\n            else:\n                out.extend(reversed(x))\n            a = a[0]\n        out.reverse()\n        return out\n\n    def nowait_codes(self):\n        seq = self.seq_codes()\n        if self.basenw:\n            return self.basenw + seq\n        return seq\n\n    def codes(self):\n        """All recorded codes (base with waits + sequential part)."""\n        seq = self.seq_codes()\n        if self.base:\n            return list(self.base) + seq\n        return seq\n\n    def actions(self):\n        return [CODE2ORDER[c] for c in self.codes()]\n\n\ndef _ff(v, k, raws, mfgs):\n    """Advance the Sim by k rounds of waiting (k >= 0). Returns False (and clears ok) if one of the\n    k steps would start at round >= 160."""\n    r = v[0]\n    if r + k > 160:\n        v[1] = 0\n        return False\n    o = F_BT\n    for _i in range(v[5]):\n        e = v[o + 2]\n        if e:\n            if e <= k:\n                v[o] = v[o + 1]\n                v[o + 1] = -1\n                v[o + 2] = 0\n            else:\n                v[o + 2] = e - k\n        o += 6\n    for site in mfgs:\n        j = v[F_JB + site]\n        if j:\n            if j <= k:\n                v[F_JB + site] = 0\n                v[F_WH + site * 3 + 2] += 1\n            else:\n                v[F_JB + site] = j - k\n    t = ((r + k) >> 2) - (r >> 2)\n    if t:\n        for site in raws:\n            x = v[F_ST + site]\n            if x < 6:\n                x += t\n                v[F_ST + site] = x if x < 6 else 6\n    v[0] = r + k\n    return True\n\n\ndef _stock_value(v, mfgs):\n    val = 0.0\n    for site in mfgs:\n        if v[F_WS + site]:\n            f = v[F_WH + site * 3 + 1]\n            t = v[F_WH + site * 3]\n            val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)\n    return val\n\n\ndef stock_value(s):\n    """Sum over own workshop sites of min(fibre,2)*1.5 + min(timber,4) (Sim or Side)."""\n    if isinstance(s, Sim):\n        v = s.v\n        val = 0.0\n        for site in range(10):\n            if v[F_WS + site]:\n                f = v[F_WH + site * 3 + 1]\n                t = v[F_WH + site * 3]\n                val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)\n        return val\n    val = 0.0\n    for site in range(10):\n        if s.ws[site]:\n            f = s.wh[site * 3 + 1]\n            t = s.wh[site * 3]\n            val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)\n    return val\n\n\nDEFAULT_CACHE_SIZE = 20000\nBIG = 1 << 30\n\n\nclass ReplanCache:\n    """Bounded memo of whole replans: key = the flat Sim of the replan input (round, own side,\n    stock estimates, claims) packed as int16 bytes; value = (plan codes as array(\'h\'), contracts\n    tuple, score) or None. About 0.5 KB per entry. One cache per\n    (map, style): get it with Map.replan_cache(style). When full, the oldest half is dropped\n    (a hit moves the entry to the young end)."""\n    __slots__ = (\'d\', \'maxsize\', \'hits\', \'misses\')\n\n    def __init__(self, maxsize=DEFAULT_CACHE_SIZE):\n        self.d = {}\n        self.maxsize = maxsize\n        self.hits = 0\n        self.misses = 0\n\n    def get(self, key, default=None):\n        d = self.d\n        r = d.pop(key, _MISSING)\n        if r is _MISSING:\n            self.misses += 1\n            return default\n        d[key] = r\n        self.hits += 1\n        return r\n\n    def put(self, key, val):\n        d = self.d\n        if len(d) >= self.maxsize:\n            for k in list(islice(d, max(1, len(d) // 2))):\n                del d[k]\n        d[key] = val\n\n    def clear(self):\n        self.d.clear()\n\n    def __len__(self):\n        return len(self.d)\n\n\n_MISSING = object()\n\n\nclass Professor:\n    def __init__(self, style, seat=None, cache=None, use_cache=True):\n        """style: id 0-4 (index into STYLES) or a (B, A, W) tuple. cache: a ReplanCache to use;\n        by default the map\'s shared cache for this style (Map.replan_cache). use_cache=False\n        disables memoisation."""\n        if isinstance(style, int):\n            style = STYLES[style]\n        self.B, self.A, self.W = style\n        self.seat = seat\n        self.last_round = -1\n        self.est = [4] * 10\n        self.plan = deque()\n        self.plan_contracts = []\n        self.mp = None\n        self.replans = 0\n        self.cache = cache\n        self.use_cache = use_cache\n\n    def clone(self):\n        p = Professor.__new__(Professor)\n        p.B = self.B\n        p.A = self.A\n        p.W = self.W\n        p.seat = self.seat\n        p.last_round = self.last_round\n        p.est = self.est[:]\n        p.plan = deque(self.plan)\n        p.plan_contracts = self.plan_contracts[:]\n        p.mp = self.mp\n        p.replans = 0               # as professor.py: a clone starts its own count\n        p.cache = self.cache\n        p.use_cache = self.use_cache\n        return p\n\n    # ---- Sim primitives ----------------------------------------------------------------------\n\n    def _bind(self, mp):\n        """Cache map tables on self for the planner."""\n        if getattr(self, \'_bound\', None) is mp:\n            return\n        self._bound = mp\n        self._raws = mp.raw_sites\n        self._mfgs = mp.mfg_sites\n        self._dist = mp.dist\n        self._tlen = mp.tlen\n        self._tsails = mp.tsails\n        self._roles = mp.roles\n        self._routes = mp.routes\n        self._cands = mp.acq_cands\n        self._cdl = mp.c_deadline\n        self._cdest = mp.c_dest\n        self._cgood = mp.c_good\n        self._cqty = mp.c_qty\n        self._cpts = mp.c_points\n        self._nc = mp.ncontracts\n\n    def _legal(self, v, code):\n        """Exactly is_legal() for a code on a flat Sim."""\n        op = code & 15\n        if op == OP_WAIT:\n            return True\n        if op == OP_BUILD_BOAT:\n            h3 = F_WH + v[F_HM] * 3\n            return v[F_NB] <= 2 and v[h3] >= 4 and v[h3 + 1] >= 2\n        b = (code >> 4) & 3\n        if b >= v[F_NB]:\n            return False\n        o = F_BT + 6 * b\n        if v[o + 2] != 0:\n            return False\n        pos = v[o]\n        arg = code >> 6\n        if op == OP_SAIL:\n            return self._routes[pos][arg] != 0\n        if op == OP_DELIVER:\n            c = arg\n            return (c < self._nc and v[F_CL + c] == -1 and self._cdl[c] > v[F_R]\n                    and self._cdest[c] == pos and v[o + 3 + self._cgood[c]] >= self._cqty[c])\n        g = arg >> 2\n        q = arg & 3\n        free = 3 - (v[o + 3] + v[o + 4] + v[o + 5])\n        if op == OP_GATHER:\n            role = self._roles[pos]\n            if role != 0 and role != 1:\n                return False\n            return g == role and 1 <= q <= min(v[F_ST + pos], free)\n        if op == OP_LOAD:\n            return 1 <= q <= min(v[F_WH + pos * 3 + g], free)\n        if op == OP_UNLOAD:\n            return 1 <= q <= v[o + 3 + g]\n        if op == OP_BUILD_WS:\n            return (self._roles[pos] == 2 and not v[F_WS + pos]\n                    and v[F_WH + pos * 3] >= 2 and v[F_WH + pos * 3 + 1] >= 1)\n        if op == OP_CRAFT:\n            return (self._roles[pos] == 2 and v[F_WS + pos] and v[F_JB + pos] == 0\n                    and v[F_WH + pos * 3] >= 2 and v[F_WH + pos * 3 + 1] >= 1)\n        return False\n\n    def _apply(self, v, code):\n        """apply_order on a flat Sim (no route conflicts). False = order failed."""\n        op = code & 15\n        if op == OP_WAIT:\n            return True\n        if op == OP_BUILD_BOAT:\n            h3 = F_WH + v[F_HM] * 3\n            v[h3] -= 4\n            v[h3 + 1] -= 2\n            v.extend((v[F_HM], -1, 0, 0, 0, 0))\n            v[F_NB] += 1\n            return True\n        b = (code >> 4) & 3\n        o = F_BT + 6 * b\n        pos = v[o]\n        arg = code >> 6\n        if op == OP_SAIL:\n            v[o + 1] = arg\n            v[o + 2] = self._routes[pos][arg]\n            return True\n        if op == OP_DELIVER:\n            c = arg\n            if v[F_CL + c] != -1:\n                return False\n            g = self._cgood[c]\n            v[o + 3 + g] -= self._cqty[c]\n            v[F_SC] += self._cpts[c]\n            if g == 2:\n                v[F_CR] += 1\n            v[F_CL + c] = self.seat if self.seat is not None else 0\n            return True\n        g = arg >> 2\n        q = arg & 3\n        if op == OP_GATHER:\n            if v[F_ST + pos] < q:\n                return False\n            v[F_ST + pos] -= q\n            v[o + 3 + g] += q\n            return True\n        if op == OP_LOAD:\n            v[F_WH + pos * 3 + g] -= q\n            v[o + 3 + g] += q\n            return True\n        if op == OP_UNLOAD:\n            v[F_WH + pos * 3 + g] += q\n            v[o + 3 + g] -= q\n            return True\n        if op == OP_BUILD_WS:\n            v[F_WH + pos * 3] -= 2\n            v[F_WH + pos * 3 + 1] -= 1\n            v[F_WS + pos] = 1\n            return True\n        if op == OP_CRAFT:\n            v[F_WH + pos * 3] -= 2\n            v[F_WH + pos * 3 + 1] -= 1\n            v[F_JB + pos] = 3\n            return True\n        raise ValueError(\'unknown order code %r\' % code)\n\n    def _step(self, s, code):\n        """Sim::step with the full legality check (non-wait orders only; waits are not recorded)."""\n        v = s.v\n        if not v[F_OK] or v[F_R] >= 160:\n            v[F_OK] = 0\n            return\n        if not self._legal(v, code) or not self._apply(v, code):\n            v[F_OK] = 0\n            return\n        _ff(v, 1, self._raws, self._mfgs)\n        s.acts = (s.acts, code)\n\n    def _step_nl(self, s, code):\n        """Sim::step for an order that is legal by construction (no check; it still applies the\n        160-round limit and records the order)."""\n        v = s.v\n        if not v[F_OK] or v[F_R] >= 160:\n            v[F_OK] = 0\n            return\n        if not self._apply(v, code):\n            v[F_OK] = 0\n            return\n        _ff(v, 1, self._raws, self._mfgs)\n        s.acts = (s.acts, code)\n\n    def _travel(self, s, b, target):\n        """0x1a1c0 in O(1): wait until boat b docks, then sail the next-hop path to target."""\n        v = s.v\n        if not v[F_OK]:\n            return\n        o = F_BT + 6 * b\n        e = v[o + 2]\n        if e:\n            if not _ff(v, e, self._raws, self._mfgs):\n                return\n        pos = v[o]\n        if pos == target:\n            return\n        L = self._tlen[pos][target]\n        if L < 0:\n            v[F_OK] = 0\n            return\n        v[o] = target\n        if not _ff(v, L, self._raws, self._mfgs):\n            return\n        s.acts = (s.acts, self._tsails[b][pos][target])\n\n    def _wait_jobs(self, s, w):\n        """`while s.ok and s.jobs[w] != 0: step(WAIT)`"""\n        v = s.v\n        if v[F_OK]:\n            j = v[F_JB + w]\n            if j:\n                _ff(v, j, self._raws, self._mfgs)\n\n    # ---- acquire (0x26c80 + lambda 0x2bf10) ------------------------------------------------\n\n    def acquire(self, sim, b, need, dest, unload_at_dest, rbound=BIG, cbound=None):\n        """acquire (0x26c80). Extra exact pruning: only results with round < rbound are wanted\n        and, with cbound (supply), only results whose supply cost (round - surplus * B, surplus\n        from the final warehouse at dest) is < cbound. The reference would return a result that\n        its caller then rejects; here such a result is never built and None comes back.\n\n        Orders here skip the legality check because they are legal by construction:\n          * dump unloads: the boat is docked after travel and holds cargo0[g] > need[g];\n          * loads/gathers in _rec: the boat is docked at the source after travel, the source held\n            >= m when the candidate was listed (goods 0/1 in warehouses do not change while a boat\n            sails, natural stock only grows), role == g for gathers, and free space >= m because\n            after the dump sum(max(need, cargo)) <= 3;\n          * leaf unloads: the boat is docked at dest holding max(need, cargo) >= need[g] >= 1.\n        need[2] is always 0 in the Professor\'s calls."""\n        v = sim.v\n        o = F_BT + 6 * b\n        n0 = need[0]\n        n1 = need[1]\n        n2 = need[2]\n        c0 = v[o + 3]\n        c1 = v[o + 4]\n        c2 = v[o + 5]\n        keep = (n0 if n0 > c0 else c0) + (n1 if n1 > c1 else c1) + (n2 if n2 > c2 else c2)\n        if keep > 3:\n            s = sim.copy()\n            v = s.v\n            self._travel(s, b, v[o + 1] if v[o + 2] != 0 else v[o])\n            bq = b << 4\n            if n0 < c0:\n                self._step_nl(s, OP_UNLOAD | bq | (c0 - n0) << 6)\n            if n1 < c1:\n                self._step_nl(s, OP_UNLOAD | bq | (4 + c1 - n1) << 6)\n            if n2 < c2:\n                self._step_nl(s, OP_UNLOAD | bq | (8 + c2 - n2) << 6)\n            if not v[F_OK]:\n                return None\n        else:\n            s = sim          # rec never mutates its input\n            if not v[F_OK]:\n                return None\n        bound = rbound if rbound < 161 else 161     # a step starting at round >= 160 fails\n        if cbound is not None and cbound < 1e29:\n            w3 = F_WH + dest * 3\n            K = (max(0, v[w3 + 1] + n1 - 1) * 1.5 + max(0, v[w3] + n0 - 2)) * self.B\n            R = int(cbound + K) - 2\n            while (R - K) >= cbound:\n                R -= 1\n            while not ((R - K) >= cbound):\n                R += 1\n            if R < bound:\n                bound = R\n        if v[F_R] >= bound:\n            return None\n        m0 = n0 - v[o + 3]\n        m1 = n1 - v[o + 4]\n        m2 = n2 - v[o + 5]\n        missing = (m0 if m0 > 0 else 0, m1 if m1 > 0 else 0, m2 if m2 > 0 else 0)\n        order = [g for g in range(3) if missing[g] > 0]\n        nun = (1 if n0 else 0) + (1 if n1 else 0) + (1 if n2 else 0) if unload_at_dest else 0\n        best = [None, bound]      # best sim, round to beat\n        while True:\n            self._rec(s, 0, order, missing, b, need, dest, unload_at_dest, nun, best)\n            if len(order) <= 1:\n                break\n            i = len(order) - 2\n            while i >= 0 and order[i] >= order[i + 1]:\n                i -= 1\n            if i < 0:\n                break\n            j = len(order) - 1\n            while order[j] <= order[i]:\n                j -= 1\n            order[i], order[j] = order[j], order[i]\n            order[i + 1:] = reversed(order[i + 1:])\n        return best[0]\n\n    def _rec(self, sm, idx, order, missing, b, need, dest, unload, nun, best):\n        v = sm.v\n        if not v[F_OK]:\n            return\n        if v[F_R] >= best[1]:\n            return\n        o = F_BT + 6 * b\n        e = v[o + 2]\n        cur = v[o + 1] if e else v[o]\n        if idx == len(order):\n            # finishing round: dock + travel + unloads (each of those steps checks round < 160)\n            L = self._tlen[cur][dest]\n            if L < 0:\n                return\n            if v[F_R] + e + L + nun >= best[1]:\n                return\n            t = sm.copy()\n            self._travel(t, b, dest)\n            if unload:\n                bq = b << 4\n                if need[0]:\n                    self._step_nl(t, OP_UNLOAD | bq | need[0] << 6)\n                if need[1]:\n                    self._step_nl(t, OP_UNLOAD | bq | (4 + need[1]) << 6)\n                if need[2]:\n                    self._step_nl(t, OP_UNLOAD | bq | (8 + need[2]) << 6)\n            if t.v[F_OK]:\n                best[0] = t\n                best[1] = t.v[F_R]\n            return\n        g = order[idx]\n        m = missing[g]\n        dcur = self._dist[cur]\n        r0 = v[F_R] + e + 1\n        cnt = 0\n        nidx = idx + 1\n        loadc = OP_LOAD | b << 4 | (g * 4 + m) << 6\n        gathc = OP_GATHER | b << 4 | (g * 4 + m) << 6\n        for site, is_load in self._cands[cur][dest][g]:\n            if unload and site == dest:\n                continue\n            if is_load:\n                if v[F_WH + site * 3 + g] < m:\n                    continue\n            elif v[F_ST + site] < m:\n                continue\n            cnt += 1\n            if cnt > 5:\n                break\n            if r0 + dcur[site] >= best[1]:\n                continue\n            t = sm.copy()\n            self._travel(t, b, site)\n            self._step_nl(t, loadc if is_load else gathc)\n            self._rec(t, nidx, order, missing, b, need, dest, unload, nun, best)\n\n    # ---- supply a manufacturing site with 2 timber + 1 fibre (0x27250) --------------------\n\n    def supply(self, sim, w):\n        v = sim.v\n        need_t = max(0, 2 - v[F_WH + w * 3])\n        need_f = max(0, 1 - v[F_WH + w * 3 + 1])\n        B = self.B\n        best_cost = 1e30\n        best = None\n        nb = v[F_NB]\n        if need_t + need_f == 0:\n            for b in range(nb):\n                s = sim.copy()\n                self._travel(s, b, w)\n                if s.v[F_OK]:\n                    sv = s.v\n                    c = sv[F_R] - (max(0, sv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, sv[F_WH + w * 3] - 2)) * B\n                    if c < best_cost:\n                        best_cost = c\n                        best = (s, b)\n            return best\n        for b in range(nb):\n            r = self.acquire(sim, b, (need_t, need_f, 0), w, True, BIG, best_cost)\n            if r is not None:\n                rv = r.v\n                c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B\n                if c < best_cost:\n                    best_cost = c\n                    best = (r, b)\n            if need_t != 0 and need_f == 0:\n                r = self.acquire(sim, b, (3, 0, 0), w, True, BIG, best_cost)\n                if r is not None:\n                    rv = r.v\n                    c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B\n                    if c < best_cost:\n                        best_cost = c\n                        best = (r, b)\n            if need_f != 0 and need_t == 0:\n                r = self.acquire(sim, b, (0, 3, 0), w, True, BIG, best_cost)\n                if r is not None:\n                    rv = r.v\n                    c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B\n                    if c < best_cost:\n                        best_cost = c\n                        best = (r, b)\n        if need_t != 0 and need_f != 0 and v[F_R] < 50:\n            for first, second in (((3, 0, 0), (0, 3, 0)), ((0, 3, 0), (3, 0, 0))):\n                for b1 in range(nb):\n                    r1 = self.acquire(sim, b1, first, w, True)\n                    if r1 is None:\n                        continue\n                    for b2 in range(nb):\n                        r2 = self.acquire(r1, b2, second, w, True, BIG, best_cost)\n                        if r2 is not None:\n                            rv = r2.v\n                            c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B\n                            if c < best_cost:\n                                best_cost = c\n                                best = (r2, b2)\n        return best\n\n    # ---- get one manufactured good to `dest` (0x284f0) ------------------------------------\n\n    def manufactured(self, sim, dest):\n        """Same candidate order as the reference. Everything up to "boat b holds the good at\n        site w" is cached on the input sim (it does not depend on dest). A candidate\'s cost is\n        known before travelling (stock_value cannot change while a boat sails), so only an\n        improving candidate is copied and simulated."""\n        best_cost = 1e30\n        best = None\n        v = sim.v\n        nb = v[F_NB]\n        mfgs = self._mfgs\n        tlen = self._tlen\n        memo = sim.memo\n        if memo is None:\n            memo = sim.memo = {}\n        sv05 = _stock_value(v, mfgs) * 0.5\n\n        # A: a boat already carries a manufactured good\n        for b in range(nb):\n            o = F_BT + 6 * b\n            if v[o + 5] != 0:\n                e = v[o + 2]\n                L = tlen[v[o + 1] if e else v[o]][dest]\n                if L < 0:\n                    continue\n                rf = v[F_R] + e + L\n                if rf > 160:\n                    continue\n                c = rf - sv05\n                if c < best_cost:\n                    s = sim.copy()\n                    self._travel(s, b, dest)\n                    best_cost = c\n                    best = (s, b)\n        # B: pick one up where it is stored or being crafted\n        for w in range(10):\n            if v[F_WH + w * 3 + 2] != 0 or v[F_JB + w] != 0:\n                for b in range(nb):\n                    key = w * 4 + b\n                    s = memo.get(key, _MISSING)\n                    if s is _MISSING:\n                        s = sim.copy()\n                        self._travel(s, b, w)\n                        self._wait_jobs(s, w)\n                        if s.v[F_OK]:\n                            sv = s.v\n                            ob = F_BT + 6 * b\n                            if sv[ob + 3] + sv[ob + 4] + sv[ob + 5] < 3:\n                                self._step(s, OP_LOAD | b << 4 | 9 << 6)\n                            else:\n                                s = None\n                        if s is not None and not s.v[F_OK]:\n                            s = None\n                        memo[key] = s\n                    if s is not None:\n                        best_cost, best = self._consider(s, b, dest, best_cost, best)\n        # C: (build a workshop and) craft a new one\n        for w in mfgs:\n            key = 100 + w\n            loaded = memo.get(key)\n            if loaded is None:\n                loaded = []\n                s = sim.copy()\n                crafted = False\n                r = True\n                if not s.v[F_WS + w]:\n                    r = self.supply(s, w)\n                    if r is not None:\n                        s = r[0]\n                        self._step(s, OP_BUILD_WS | r[1] << 4)\n                if r is not None and s.v[F_OK] and s.v[F_JB + w] == 0:\n                    r = self.supply(s, w)\n                    if r is not None:\n                        s = r[0]\n                        self._step(s, OP_CRAFT | r[1] << 4)\n                        crafted = True\n                if crafted:\n                    for b in range(nb):\n                        t = s.copy()\n                        self._travel(t, b, w)\n                        if t.v[F_OK]:\n                            self._wait_jobs(t, w)\n                            if t.v[F_OK]:\n                                tv = t.v\n                                ob = F_BT + 6 * b\n                                if tv[ob + 3] + tv[ob + 4] + tv[ob + 5] < 3:\n                                    self._step(t, OP_LOAD | b << 4 | 9 << 6)\n                                    if tv[F_OK]:\n                                        loaded.append((t, b))\n                memo[key] = loaded\n            for t, b in loaded:\n                best_cost, best = self._consider(t, b, dest, best_cost, best)\n        return best\n\n    def _consider(self, s, b, dest, best_cost, best):\n        """consider(s.copy(), b): travel to dest; cost = round - 0.5 * stock_value."""\n        v = s.v\n        o = F_BT + 6 * b\n        e = v[o + 2]\n        L = self._tlen[v[o + 1] if e else v[o]][dest]\n        if L < 0:\n            return best_cost, best\n        rf = v[F_R] + e + L\n        if rf > 160:\n            return best_cost, best\n        c = rf - _stock_value(v, self._mfgs) * 0.5\n        if c < best_cost:\n            t = s.copy()\n            self._travel(t, b, dest)\n            return c, (t, b)\n        return best_cost, best\n\n    # ---- sequential plan for one more contract (0x29690) ------------------------------------\n\n    def prepare(self, sim, c):\n        v = sim.v\n        if v[F_CL + c] != -1:\n            return None\n        g = self._cgood[c]\n        dest = self._cdest[c]\n        if g == 2:\n            r = self.manufactured(sim, dest)\n            if r is None:\n                return None\n            s, boat = r\n        else:\n            need = [0, 0, 0]\n            need[g] = self._cqty[c]\n            s = None\n            boat = -1\n            for b in range(v[F_NB]):\n                r = self.acquire(sim, b, need, dest, False, BIG if s is None else s.v[F_R])\n                if r is not None and (s is None or r.v[F_R] < s.v[F_R]):\n                    s = r\n                    boat = b\n            if s is None:\n                return None\n        s = s.copy()\n        # lenient deliver (no deadline check)\n        sv = s.v\n        if not sv[F_OK] or sv[F_R] >= 160:\n            return None\n        o = F_BT + 6 * boat\n        if (sv[o + 2] != 0 or sv[o] != dest or sv[o + 3 + g] < self._cqty[c] or sv[F_CL + c] != -1):\n            return None\n        code = OP_DELIVER | boat << 4 | c << 6\n        self._apply(sv, code)\n        _ff(sv, 1, self._raws, self._mfgs)\n        s.acts = (s.acts, code)\n        return s\n\n    # ---- re-schedule the sequential action list over the boats (0x29f80) ---------------------\n\n    def interleave(self, codes, variant, snap=None, record=None):\n        """codes: non-wait order codes (sequential plan). snap: a parent run snapshot\n        (v, out, ptrs) to resume from, valid because the parent\'s per-boat queues are a prefix of\n        these. record: list to receive this run\'s snapshot at the first moment a queue is empty\n        (or the string \'fail\' if the run failed before)."""\n        qs = ([], [], [])\n        for a in codes:\n            qs[(a >> 4) & 3].append(a)\n        q0, q1, q2 = qs\n        n0 = len(q0)\n        n1 = len(q1)\n        n2 = len(q2)\n        if snap is not None:\n            sv, sout, p0, p1, p2 = snap\n            s = Sim.__new__(Sim)\n            s.v = v = sv[:]\n            s.memo = None\n            s.snaps = None\n            s.acts = None\n            out = sout[:]\n        else:\n            s = self.cur.copy()\n            v = s.v\n            out = []\n            p0 = p1 = p2 = 0\n        raws = self._raws\n        mfgs = self._mfgs\n        nb = v[F_NB]\n        legal = self._legal\n        apply = self._apply\n        rec = record is not None and not record\n        while v[F_R] < 80:\n            e0 = p0 >= n0\n            e1 = p1 >= n1\n            e2 = p2 >= n2\n            if rec and (e0 or (e1 and nb > 1) or (e2 and nb > 2)):\n                # a child\'s queues are this run\'s queues plus more orders at the back: the\n                # child\'s run is identical up to the first moment one of its boat queues is empty\n                record.append((v[:], out[:], p0, p1, p2))\n                rec = False\n            if e0 and e1 and e2:\n                s.base = out\n                s.basenw = [c for c in out if c & 15]\n                s.acts = None\n                return s\n            chosen = -1\n            cc = 0\n            for i in range(variant, variant + nb):\n                bb = i % nb\n                if bb == 0:\n                    if p0 >= n0:\n                        continue\n                    a = q0[p0]\n                elif bb == 1:\n                    if p1 >= n1:\n                        continue\n                    a = q1[p1]\n                else:\n                    if bb > 2 or p2 >= n2:\n                        continue\n                    a = q2[p2]\n                if legal(v, a):\n                    isd = (a & 15) == OP_DELIVER\n                    if chosen < 0 or isd:\n                        chosen = bb\n                        cc = a\n                    if isd:\n                        break\n            if chosen < 0:\n                busy = False\n                k = 80 - v[F_R]\n                o = F_BT\n                for _i in range(nb):\n                    e = v[o + 2]\n                    if e > 0:\n                        busy = True\n                        if e < k:\n                            k = e\n                    o += 6\n                for site in mfgs:\n                    j = v[F_JB + site]\n                    if j > 0:\n                        busy = True\n                        if j < k:\n                            k = j\n                if not busy:\n                    if rec:\n                        record.append(\'fail\')\n                    return None\n                t = 4 - (v[F_R] & 3)\n                if t < k:\n                    k = t\n                _ff(v, k, raws, mfgs)\n                out.extend([0] * k)\n            else:\n                if chosen == 0:\n                    p0 += 1\n                elif chosen == 1:\n                    p1 += 1\n                else:\n                    p2 += 1\n                if not apply(v, cc):\n                    v[F_OK] = 0\n                    if rec:\n                        record.append(\'fail\')\n                    return None\n                _ff(v, 1, raws, mfgs)\n                out.append(cc)\n        if rec:\n            record.append(\'fail\')\n        if p0 < n0 or p1 < n1 or p2 < n2:\n            return None\n        s.base = out\n        s.basenw = [c for c in out if c & 15]\n        s.acts = None\n        return s\n\n    # ---- top level (0x3ae20) ------------------------------------------------------------------\n\n    def make_sim(self, view):\n        side = view.side\n        v = [view.round, 1, side.score, side.crafted, side.home, len(side.boats)]\n        v.extend(self.est)\n        cl = list(view.claims)\n        if len(cl) < NCMAX:\n            cl.extend([-1] * (NCMAX - len(cl)))\n        v.extend(cl)\n        v.extend(side.wh)\n        v.extend([1 if x else 0 for x in side.ws])\n        v.extend(side.jobs)\n        for b in side.boats:\n            v.extend(b)\n        s = Sim.__new__(Sim)\n        s.v = v\n        s.base = None\n        s.basenw = None\n        s.acts = None\n        s.memo = None\n        s.snaps = None\n        return s\n\n    def replan(self, view):\n        """Beam search over contract sequences. Returns (plan orders, contracts, score) or None.\n        Memoised in self.cache (the map\'s shared cache for this style unless use_cache=False)."""\n        self.replans += 1\n        mp = view.mp\n        self.mp = mp\n        cur = self.make_sim(view)\n        cache = None\n        if self.use_cache:\n            cache = self.cache\n            if cache is None:\n                cache = self.cache = mp.replan_cache((self.B, self.A, self.W))\n            key = array(\'h\', cur.v).tobytes()\n            r = cache.get(key, _MISSING)\n            if r is not _MISSING:\n                if r is None:\n                    return None\n                return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])\n        r = self._replan(cur, mp)\n        if cache is not None:\n            cache.put(key, r)\n        if r is None:\n            return None\n        return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])\n\n    def replan_uncached(self, view):\n        cur = self.make_sim(view)\n        r = self._replan(cur, view.mp)\n        if r is None:\n            return None\n        return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])\n\n    def _replan(self, cur, mp):\n        """Returns (plan codes array, contracts tuple, score) or None.\n\n        Beam nodes are (sim, contracts, score, snaps, exp). snaps: the two parent-run snapshots\n        its children\'s interleave resumes from. exp: memo {contract: child results}, shared by the\n        two variant nodes of one prepare when their states are equal: their children are then\n        identical (interleave only sees per-boat order), so they are computed once."""\n        self._bind(mp)\n        self.cur = cur\n        cv = cur.v\n        mfgs = self._mfgs\n        cur_has_ws = False\n        for site in range(10):\n            if cv[F_WS + site]:\n                cur_has_ws = True\n        cround = cv[F_R]\n        cscore = cv[F_SC]\n        A = self.A\n        W = self.W\n        nc = self._nc\n        cdl = self._cdl\n        best = None\n        frontier = [(cur, (), 0.0, None, {})]\n        for _depth in range(4):\n            nxt = []\n            for node_sim, node_contracts, _sc, snaps, exp in frontier:\n                ncl = node_sim.v\n                for c in range(nc):\n                    if ncl[F_CL + c] != -1 or not (cround < cdl[c]):\n                        continue\n                    kids = exp.get(c)\n                    if kids is None:\n                        kids = ()\n                        opt = self.prepare(node_sim, c)\n                        if opt is not None:\n                            acts = opt.nowait_codes()\n                            rec_pair = ([], [])\n                            results = []\n                            for variant in (0, 1):\n                                snap = None\n                                if snaps is not None:\n                                    snap = snaps[variant]\n                                    if snap == \'fail\':\n                                        rec_pair[variant].append(\'fail\')\n                                        continue\n                                res = self.interleave(acts, variant, snap, rec_pair[variant])\n                                if res is not None:\n                                    results.append(res)\n                            if results:\n                                child_snaps = (rec_pair[0][0] if rec_pair[0] else \'fail\',\n                                               rec_pair[1][0] if rec_pair[1] else \'fail\')\n                                kl = []\n                                prev = None\n                                for res in results:\n                                    rv = res.v\n                                    has_ws = False\n                                    for site in mfgs:\n                                        if rv[F_WS + site]:\n                                            has_ws = True\n                                    bonus = W if (not cur_has_ws and has_ws) else 0\n                                    score = ((_stock_value(rv, mfgs) * 0.1 + float((rv[F_SC] - cscore) + bonus))\n                                             / pow(float((rv[F_R] - cround) + 3), A))\n                                    if prev is not None and prev.v == rv:\n                                        cexp = kl[-1][3]\n                                    else:\n                                        cexp = {}\n                                    prev = res\n                                    kl.append((res, score, child_snaps, cexp))\n                                kids = tuple(kl)\n                        exp[c] = kids\n                    for res, score, child_snaps, cexp in kids:\n                        node = (res, node_contracts + (c,), score, child_snaps, cexp)\n                        if best is None or best[2] < score:\n                            best = node\n                        nxt.append(node)\n            if not nxt:\n                break\n            nxt.sort(key=_node_key)\n            frontier = nxt[:8]\n        self.cur = None\n        if best is None:\n            return None\n        return (array(\'h\', best[0].codes()), best[1], best[2])\n\n    def choose(self, view):\n        """ReferencePlayer::choose. Returns the order for this round and updates internal state."""\n        rnd = view.round\n        if rnd == 0:\n            self.last_round = -1\n            self.est = [4] * 10\n            self.plan.clear()\n            self.plan_contracts = []\n        self.mp = mp = view.mp\n        self.seat = view.seat\n        d = rnd // 4 if self.last_round < 0 else rnd // 4 - (self.last_round >> 2)\n        est = self.est\n        vis = view.visible\n        vst = view.stocks\n        for s in range(10):\n            x = est[s] + d\n            if x > 6:\n                x = 6\n            if vis[s]:\n                x = vst[s]\n            est[s] = x\n        self.last_round = rnd\n        claims = view.claims\n        for c in self.plan_contracts:\n            if claims[c] != -1 and claims[c] != self.seat:\n                self.plan.clear()\n        side = view.side\n        if rnd >= 80:\n            return WAIT\n        cdl = mp.c_deadline\n        cdest = mp.c_dest\n        cgood = mp.c_good\n        cqty = mp.c_qty\n        for b, boat in enumerate(side.boats):\n            if boat[2] != 0:\n                continue\n            pos = boat[0]\n            for c in range(mp.ncontracts):\n                if (claims[c] == -1 and cdl[c] > rnd and cdest[c] == pos\n                        and boat[3 + cgood[c]] >= cqty[c]):\n                    self.plan.clear()\n                    self.plan_contracts = []\n                    return o_deliver(b, c)\n        if self.plan and is_legal(mp, side, vst, claims, rnd, self.plan[0]):\n            return self.plan.popleft()\n        self.plan.clear()\n        self.plan_contracts = []\n        best = self.replan(view)\n        if best is not None:\n            acts = best[0]\n            if acts:\n                self.plan_contracts = list(best[1])\n                self.plan = deque(acts)\n                if is_legal(mp, side, vst, claims, rnd, self.plan[0]):\n                    return self.plan.popleft()\n        self.plan.clear()\n        return WAIT\n\n\ndef _node_key(nd):\n    return (-nd[2], nd[0].v[F_R])\n\n\n# ---------------------------------------------------------------------------------------------\n# Style tracking: five hypotheses (Engine + Professor per style), pruned on observations\n# ---------------------------------------------------------------------------------------------\n\nclass Hypothesis:\n    """One style hypothesis: the full two-sided Engine and the Professor\'s state.\n    `pending` is the Professor\'s order for the current engine round once computed (order())."""\n    __slots__ = (\'style\', \'eng\', \'prof\', \'seat\', \'pending\')\n\n    def __init__(self, style, eng, prof, seat):\n        self.style = style\n        self.eng = eng\n        self.prof = prof\n        self.seat = seat\n        self.pending = None\n\n    def order(self):\n        """The Professor\'s order for the engine\'s current round (computed once)."""\n        if self.pending is None and self.eng.round < 80:\n            self.pending = self.prof.choose(self.eng.view(1 - self.seat))\n        return self.pending\n\n    def step(self, ours):\n        """Play one round: our order (tuple) vs the Professor\'s. Returns the engine\'s [ok0, ok1]."""\n        theirs = self.order()\n        orders = [None, None]\n        orders[self.seat] = ours\n        orders[1 - self.seat] = theirs if theirs is not None else WAIT\n        ok = self.eng.step(orders)\n        self.pending = None\n        return ok\n\n    def clone(self):\n        """Cheap copy for lookahead (engine + Professor + pending order; the cache is shared)."""\n        h = Hypothesis.__new__(Hypothesis)\n        h.style = self.style\n        h.eng = self.eng.clone()\n        h.prof = self.prof.clone()\n        h.seat = self.seat\n        h.pending = self.pending\n        return h\n\n\ndef _obs_signature(obs):\n    own = obs[\'own\']\n    sig = [obs[\'round\'], obs[\'seat\'], obs[\'opponent_score\'], own[\'score\'], own[\'crafted_deliveries\'],\n           own[\'home\']]\n    sig.extend(obs[\'claims\'])\n    sig.extend([1 if x else 0 for x in obs[\'visible\']])\n    sig.extend([-9 if x is None else x for x in obs[\'stocks\']])\n    for row in own[\'warehouses\']:\n        sig.extend(row)\n    sig.extend([1 if x else 0 for x in own[\'workshops\']])\n    sig.extend(own[\'jobs\'])\n    sig.append(len(own[\'boats\']))\n    for b in own[\'boats\']:\n        sig.append(b[\'position\'])\n        sig.append(b[\'destination\'])\n        sig.append(b[\'eta\'])\n        sig.extend(b[\'cargo\'])\n    en = sorted((b[\'boat\'], b[\'position\'], b[\'destination\'], b[\'eta\']) for b in obs[\'enemy_boats\'])\n    sig.append(len(en))\n    for t in en:\n        sig.extend(t)\n    return sig\n\n\ndef engine_signature(eng, seat):\n    """Same field order as _obs_signature, from the model."""\n    side = eng.sides[seat]\n    other = eng.sides[1 - seat]\n    vis = [False] * 10\n    vis[side.home] = True\n    for s in range(10):\n        if side.ws[s]:\n            vis[s] = True\n    for b in side.boats:\n        if b[2] == 0:\n            vis[b[0]] = True\n    sig = [eng.round, seat, other.score, side.score, side.crafted, side.home]\n    sig.extend(eng.claims)\n    sig.extend([1 if x else 0 for x in vis])\n    st = eng.stocks\n    sig.extend([st[s] if vis[s] else -9 for s in range(10)])\n    sig.extend(side.wh)\n    sig.extend([1 if x else 0 for x in side.ws])\n    sig.extend(side.jobs)\n    sig.append(len(side.boats))\n    for b in side.boats:\n        sig.extend(b)\n    en = [(i, b[0], b[1], b[2]) for i, b in enumerate(other.boats) if vis[b[0]] or (b[1] >= 0 and vis[b[1]])]\n    sig.append(len(en))\n    for t in en:\n        sig.extend(t)\n    return sig\n\n\nclass Tracker:\n    """Five style hypotheses fed by observations and our own orders.\n\n        tr = Tracker(obs)             # at round 0 (or Tracker(obs, styles=[...]))\n        each round:\n            alive = tr.observe(obs)   # prune (compare_observation semantics), returns survivors\n            ... h.order() is the Professor\'s order this round under hypothesis h;\n                h.clone() gives an independent copy for lookahead (h.clone().step(our_order)) ...\n            tr.commit(our_order)      # our order as a tuple or a JSON action dict\n\n    A hypothesis is dropped when the observation differs from its Engine\'s view of our seat in\n    any field compare_observation (work/binary/test_professor.py) checks: round, seat,\n    opponent_score, claims, visible, visible stocks, own side (score, crafted, home, boats,\n    warehouses, workshops, jobs) and the enemy boats we see. legal_actions is a function of those\n    fields, so it is only compared with strict=True."""\n\n    def __init__(self, obs, styles=(0, 1, 2, 3, 4), mp=None, strict=False, cache_size=None):\n        self.seat = obs[\'seat\']\n        self.mp = mp or Map(obs[\'map\'])\n        self.strict = strict\n        ps = 1 - self.seat\n        self.hyps = []\n        for st in styles:\n            cache = self.mp.replan_cache(st, cache_size)\n            self.hyps.append(Hypothesis(st, Engine(self.mp), Professor(st, ps, cache=cache), self.seat))\n        self.dropped = {}          # style -> round it was dropped\n        self.round = obs[\'round\']\n\n    @property\n    def styles(self):\n        return [h.style for h in self.hyps]\n\n    def observe(self, obs):\n        sig = _obs_signature(obs)\n        keep = []\n        for h in self.hyps:\n            ok = engine_signature(h.eng, self.seat) == sig\n            if ok and self.strict:\n                legal = [order_to_json(o) for o in h.eng.legal(self.seat)]\n                ok = legal == obs[\'legal_actions\']\n            if ok:\n                keep.append(h)\n            else:\n                self.dropped[h.style] = obs[\'round\']\n        self.hyps = keep\n        self.round = obs[\'round\']\n        for h in keep:\n            h.order()\n        return keep\n\n    def commit(self, ours):\n        if isinstance(ours, dict):\n            ours = order_from_json(ours)\n        for h in self.hyps:\n            h.step(ours)\n\n\n# ---------------------------------------------------------------------------------------------\n# Map generation (engine function 0x1e1b0), exact.\n# ---------------------------------------------------------------------------------------------\n\ndef generate_map(topology, seed):\n    """Returns the same dict as observation[\'map\'] for group = 2*topology + seat."""\n    state = [seed ^ 0x43414d504149474e]\n\n    def rnd():\n        state[0], v = splitmix_next(state[0])\n        return v\n\n    for _attempt in range(4096):\n        routes = [[0] * 10 for _ in range(10)]\n\n        def edge(i, j):\n            length = rnd() % 3 + 1\n            routes[i][j] = length\n            routes[j][i] = length\n\n        if topology == 0:\n            for i in range(10):\n                edge(i, (i + 1) % 10)\n        elif topology == 1:\n            for base in (0, 5):\n                for i in range(4):\n                    edge(base + i, base + i + 1)\n            for i in range(5):\n                edge(i, i + 5)\n        elif topology == 2:\n            for base in (0, 5):\n                for i in range(5):\n                    edge(base + i, base + (i + 1) % 5)\n            edge(2, 7)\n        else:\n            for i in range(1, 5):\n                edge(0, i)\n            for i in range(6, 10):\n                edge(5, i)\n            edge(0, 5)\n        dist = [[(routes[i][j] if routes[i][j] != 0 and i != j else (0 if i == j else INF))\n                 for j in range(10)] for i in range(10)]\n        for k in range(10):\n            for i in range(10):\n                for j in range(10):\n                    v = dist[k][j] + dist[i][k]\n                    if v < dist[i][j]:\n                        dist[i][j] = v\n        best = -1\n        homes = [0, 0]\n        for i in range(9):\n            for j in range(i + 1, 10):\n                if best < dist[i][j]:\n                    best = dist[i][j]\n                    homes = [i, j]\n        if rnd() & 1:\n            homes.reverse()\n        roles = [-1] * 10\n        others = [i for i in range(10) if i != homes[0] and i != homes[1]]\n        for n in range(8, 1, -1):\n            r = rnd() % n\n            others[n - 1], others[r] = others[r], others[n - 1]\n        for k, site in enumerate(others):\n            roles[site] = 0 if k < 3 else (1 if k < 6 else 2)\n        contracts = []\n        failed = False\n        for c in range(8):\n            if c < 4:\n                good, qty, points, deadline = c & 1, 2, 5, 24 + 16 * c\n            else:\n                good, qty, points, deadline = 2, 1, 12, min(80, 24 + 16 * c - 48)\n            eligible = []\n            for site in others:\n                if roles[site] == good:\n                    continue\n                ok = True\n                for h in homes:\n                    if good == 2:\n                        t = INF\n                        for w in others:\n                            if roles[w] == 2:\n                                t = min(t, dist[h][w] * 3 + 14 + dist[w][site])\n                    else:\n                        t = dist[h][site] + 2\n                    if t > deadline:\n                        ok = False\n                if ok:\n                    eligible.append(site)\n            if not eligible:\n                failed = True\n                break\n            dest = eligible[rnd() % len(eligible)]\n            contracts.append(dict(deadline=deadline, destination=dest, good=good, points=points,\n                                  quantity=qty))\n        if failed:\n            continue\n        return dict(contracts=contracts, homes=homes, roles=roles, routes=routes, topology=topology)\n    raise RuntimeError(\'map generation exhausted feasible candidates\')\n'

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
