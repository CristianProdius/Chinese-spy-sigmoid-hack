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
