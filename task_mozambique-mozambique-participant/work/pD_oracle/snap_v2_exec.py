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
    horizon=80, iters=3,
    replan_after_delivery=True,
    ext_depth=2, ext_width=4, ext_max=3,
    # candidate generators: (planner style (B, A, W), steal bonus, use predicted deadlines, top-k)
    cfgs=[((1.8, 0.85, 0), 0.6, True, 2), ((3.5, 0.0, 0), 0.6, True, 2),
          ((0.0, 0.85, 8), 0.6, True, 2), ((1.8, 1.15, 0), 0.6, True, 1),
          ((1.8, 0.85, 0), 0.0, False, 1)],
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
                _v = [(tuple(a), b, c, d) for a, b, c, d in _v]
            PARAMS[_k] = _v
except Exception:  # noqa: BLE001
    pass


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
        return self.stuck >= 4


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


def rollout(eng, prof, plan, seat, hz=80):
    """Plays the game exactly from the current state up to round hz: the opponent (prof, a
    hypothesis) against our side executing `plan` with Exec; once the plan is over (or dead) our
    side only delivers what it can and otherwise waits."""
    e = eng_copy(eng)
    p = prof.clone()
    ps = 1 - seat
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
        self.hyps = [h for h in self.hyps if not obs_mismatch(obs, h.eng, seat)]
        if not self.hyps:
            return self.fallback(obs)
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
            out[h.style] = rollout(h.eng, h.prof, plan, self.seat, hz)
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
            key = (min(margins), sum(margins), -i)
            cands.append((acts, cs, sc))
            seen[acts] = preds
            if DEBUG:
                dr = [(rnd + j, o[5]) for j, o in enumerate(acts) if o[0] == 'deliver']
                print('    cand %d head=%s delivers=%s margins=%s' % (i, cs, dr, margins))
            if best[0] is None or key > best[0][0]:
                best[0] = (key, acts, cs, preds)
            return preds

        if old and old[0] in set(legal_actions(mp, view.side, stocks, view.claims, rnd)):
            consider(old, list(self.plan_c), 1e9)
        t0 = time.process_time()
        cfgs = PARAMS['cfgs'][:1] if cheap else PARAMS['cfgs']
        for cfg in cfgs:
            style, lam, use_eff, k = cfg
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
                    acts = self.extend(pl, nd[0], list(nd[0].actions()))
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
