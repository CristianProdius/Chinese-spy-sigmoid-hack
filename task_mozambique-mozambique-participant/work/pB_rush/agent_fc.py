"""pB_rush agent: Professor-aware manufacturing rush (built from core.py + brain.py)."""
"""fastcore: a fast, order-for-order identical copy of work/binary/professor.py.

Same public API as professor.py: Map, Engine (+ .clone()), Side, View, legal_actions, is_legal,
apply_order, advance_side, Professor (choose / clone / replan), view_from_observation,
order_to_json / order_from_json, generate_map, style_permutation, STYLES, WAIT, BUILD_BOAT, o_*.
Orders at the API are the same 6-tuples. Extra: ReplanCache, Tracker / Hypothesis (style tracking
and lookahead), Engine.clone(), Professor(cache=...).

Stdlib only, Python 3.8+ / PyPy 3.10. Self-contained so it can be inlined into main.py.

What is faster (behaviour is unchanged, see difftest.py):
  * The Professor's internal Sim is one flat int list (one slice per copy) and orders inside the
    planner are small ints (op | boat << 4 | arg << 6).
  * travel() is one O(1) fast-forward (other boats, jobs and stock regeneration advanced in bulk)
    instead of one full Sim.step per round. Waits are not recorded in sequential sims (interleave
    drops them anyway); the 160-round Sim limit is applied exactly.
  * Orders that are legal by construction (travel sails, loads/gathers/unloads inside acquire) skip
    the legality check. Interleave checks legality once per chosen order (the reference checks twice)
    and batches waits up to the next event that can change legality.
  * acquire / manufactured compute the finishing round (and cost) of a branch before copying the
    Sim and skip branches that cannot win (the reference copies, simulates, then compares).
  * interleave of a child node resumes from a snapshot of its parent's run (the runs are identical
    until the parent's first per-boat queue runs dry).
  * Whole replans are memoised in a ReplanCache keyed by everything replan reads (round, own side,
    stock estimates, claims), one cache per (map, style), shared by all Professor clones.
"""
from array import array
from collections import deque
from itertools import islice

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


# (surplus weight B, time exponent A, first-workshop bonus W), indexed by style id 0-4
STYLES = [
    (3.5, 0.85, 8),
    (1.8, 1.15, 0),
    (1.8, 0.85, 0),
    (3.5, 0.0, 0),
    (0.0, 0.85, 8),
]

M64 = (1 << 64) - 1


def splitmix_next(state):
    state = (state + 0x9e3779b97f4a7c15) & M64
    z = state
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
    return state, z ^ (z >> 31)


def style_permutation(seed):
    perm = [0, 1, 2, 3, 4]
    state = seed ^ 0x5354594c45534554
    for i in range(5, 1, -1):
        state, v = splitmix_next(state)
        j = v % i
        perm[i - 1], perm[j] = perm[j], perm[i - 1]
    return perm


# ---------------------------------------------------------------------------------------------
# Integer order codes (planner internals): code = op | boat << 4 | arg << 6
#   sail: arg = destination; gather/load/unload: arg = good * 4 + quantity; deliver: arg = contract
# ---------------------------------------------------------------------------------------------
OP_WAIT, OP_SAIL, OP_GATHER, OP_LOAD, OP_UNLOAD, OP_BUILD_WS, OP_CRAFT, OP_DELIVER, OP_BUILD_BOAT = range(9)
_OPNAMES = ('wait', 'sail', 'gather', 'load', 'unload', 'build_workshop', 'craft', 'deliver', 'build_boat')

CODE2ORDER = [None] * 1024
ORDER2CODE = {}


def _reg(code, o):
    CODE2ORDER[code] = o
    ORDER2CODE[o] = code


_reg(OP_WAIT, WAIT)
_reg(OP_BUILD_BOAT, BUILD_BOAT)
for _b in range(4):
    for _d in range(10):
        _reg(OP_SAIL | _b << 4 | _d << 6, o_sail(_b, _d))
    for _g in range(3):
        for _q in range(1, 4):
            _reg(OP_GATHER | _b << 4 | (_g * 4 + _q) << 6, o_gather(_b, _g, _q))
            _reg(OP_LOAD | _b << 4 | (_g * 4 + _q) << 6, o_load(_b, _g, _q))
            _reg(OP_UNLOAD | _b << 4 | (_g * 4 + _q) << 6, o_unload(_b, _g, _q))
    _reg(OP_BUILD_WS | _b << 4, o_build_workshop(_b))
    _reg(OP_CRAFT | _b << 4, o_craft(_b))
    for _c in range(16):
        _reg(OP_DELIVER | _b << 4 | _c << 6, o_deliver(_b, _c))
CODE2ORDER = tuple(CODE2ORDER)


def encode_order(o):
    """Order tuple -> int code (-1 if it has no code, e.g. a malformed order)."""
    return ORDER2CODE.get(tuple(o), -1)


def decode_order(code):
    return CODE2ORDER[code]


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
        if self.ncontracts > NCMAX:
            raise ValueError('at most %d contracts supported' % NCMAX)
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
        # ---- fastcore extras -------------------------------------------------------------
        self.raw_sites = tuple(s for s in range(n) if self.roles[s] in (0, 1))
        self.mfg_sites = tuple(s for s in range(n) if self.roles[s] == 2)
        # travel: number of rounds (sum of hop lengths along nxt) or -1 if unreachable,
        # and per boat the sail codes along the path
        self.tlen = [[0] * n for _ in range(n)]
        self.tsails = [[[None] * n for _ in range(n)] for _b in range(4)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    for b in range(4):
                        self.tsails[b][i][j] = ()
                    continue
                p = i
                hops = []
                total = 0
                ok = True
                while p != j:
                    q = nxt[p][j]
                    if q < 0:
                        ok = False
                        break
                    hops.append(q)
                    total += self.routes[p][q]
                    p = q
                    if len(hops) > 20:
                        ok = False
                        break
                self.tlen[i][j] = total if ok else -1
                for b in range(4):
                    self.tsails[b][i][j] = tuple(OP_SAIL | b << 4 | h << 6 for h in hops) if ok else None
        # acquire candidates: for (cur, dest, good) all (site, is_load) entries in the reference
        # order (loads by site, then gathers by site), stably sorted by dist[cur][s] + dist[s][dest]
        self.acq_cands = [[[None] * 3 for _ in range(n)] for _ in range(n)]
        for cur in range(n):
            for dest in range(n):
                for g in range(3):
                    ent = [(s, True) for s in range(n)] + [(s, False) for s in range(n) if self.roles[s] == g]
                    ent.sort(key=lambda e: dist[cur][e[0]] + dist[e[0]][dest])
                    self.acq_cands[cur][dest][g] = tuple(ent)
        self.replan_caches = {}

    def replan_cache(self, style, maxsize=None):
        """The shared ReplanCache of this map for a style (id or (B, A, W) triple)."""
        if isinstance(style, int):
            style = STYLES[style]
        style = tuple(style)
        c = self.replan_caches.get(style)
        if c is None:
            c = self.replan_caches[style] = ReplanCache(maxsize or DEFAULT_CACHE_SIZE)
        return c


# ---------------------------------------------------------------------------------------------
# Engine (two sides). Same structures and semantics as professor.py.
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
        for j in mp.neigh[pos]:
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
    """Engine function 0x22090. Returns False when the order fails (boat does nothing)."""
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

    def clone(self):
        s = Side.__new__(Side)
        s.home = self.home
        s.score = self.score
        s.crafted = self.crafted
        s.boats = [b[:] for b in self.boats]
        s.wh = self.wh[:]
        s.ws = self.ws[:]
        s.jobs = self.jobs[:]
        return s


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

    def clone(self):
        e = Engine.__new__(Engine)
        e.mp = self.mp
        e.round = self.round
        e.sides = [self.sides[0].clone(), self.sides[1].clone()]
        e.stocks = self.stocks[:]
        e.claims = self.claims[:]
        return e

    def visible(self, seat):
        side = self.sides[seat]
        vis = [False] * 10
        vis[side.home] = True
        ws = side.ws
        for s in self.mp.mfg_sites:
            if ws[s]:
                vis[s] = True
        for boat in side.boats:
            if boat[2] == 0:
                vis[boat[0]] = True
        return vis

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
        ws = side.ws
        for s in range(10):
            if ws[s]:
                vis[s] = True
        for boat in side.boats:
            if boat[2] == 0:
                vis[boat[0]] = True
        v.visible = vis
        st = self.stocks
        v.stocks = [st[s] if vis[s] else 4 for s in range(10)]
        v.claims = self.claims
        v.enemy_boats = [(i, boat[0], boat[1], boat[2])
                         for i, boat in enumerate(self.sides[1 - seat].boats)
                         if vis[boat[0]] or (boat[1] >= 0 and vis[boat[1]])]
        return v

    def legal(self, seat):
        if self.round >= 80:
            return []
        side = self.sides[seat]
        vis = [False] * 10
        vis[side.home] = True
        for s in range(10):
            if side.ws[s]:
                vis[s] = True
        for boat in side.boats:
            if boat[2] == 0:
                vis[boat[0]] = True
        st = self.stocks
        return legal_actions(self.mp, side, [st[s] if vis[s] else 4 for s in range(10)], self.claims,
                             self.round)

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
            st = self.stocks
            for s in self.mp.raw_sites:
                if st[s] < 6:
                    st[s] += 1
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
# The Professor's planner on a flat Sim
# ---------------------------------------------------------------------------------------------
# Flat Sim layout (one int list):
NCMAX = 8
F_R = 0          # round
F_OK = 1         # ok flag (1/0)
F_SC = 2         # score
F_CR = 3         # crafted deliveries
F_HM = 4         # home
F_NB = 5         # number of boats
F_ST = 6         # stocks[10] (the Professor's estimates)
F_CL = 16        # claims[8]
F_WH = 24        # warehouses[10][3]
F_WS = 54        # workshops[10] (0/1)
F_JB = 64        # jobs[10]
F_BT = 74        # boats: 6 ints each (position, destination, eta, cargo0, cargo1, cargo2)


class Sim:
    """v: flat state; base: full code list of an interleave run (with waits) or None;
    basenw: its non-wait codes; acts: persistent cons list (prev, code-or-tuple-of-codes) of the
    sequential (non-wait) orders added after base; memo: per-object cache of manufactured()."""
    __slots__ = ('v', 'base', 'basenw', 'acts', 'memo', 'snaps')

    def copy(self):
        s = Sim.__new__(Sim)
        s.v = self.v[:]
        s.base = self.base
        s.basenw = self.basenw
        s.acts = self.acts
        s.memo = None
        s.snaps = None
        return s

    @property
    def round(self):
        return self.v[F_R]

    @property
    def score(self):
        return self.v[F_SC]

    def seq_codes(self):
        """Non-wait codes added after base, in order."""
        out = []
        a = self.acts
        while a is not None:
            x = a[1]
            if type(x) is int:
                out.append(x)
            else:
                out.extend(reversed(x))
            a = a[0]
        out.reverse()
        return out

    def nowait_codes(self):
        seq = self.seq_codes()
        if self.basenw:
            return self.basenw + seq
        return seq

    def codes(self):
        """All recorded codes (base with waits + sequential part)."""
        seq = self.seq_codes()
        if self.base:
            return list(self.base) + seq
        return seq

    def actions(self):
        return [CODE2ORDER[c] for c in self.codes()]


def _ff(v, k, raws, mfgs):
    """Advance the Sim by k rounds of waiting (k >= 0). Returns False (and clears ok) if one of the
    k steps would start at round >= 160."""
    r = v[0]
    if r + k > 160:
        v[1] = 0
        return False
    o = F_BT
    for _i in range(v[5]):
        e = v[o + 2]
        if e:
            if e <= k:
                v[o] = v[o + 1]
                v[o + 1] = -1
                v[o + 2] = 0
            else:
                v[o + 2] = e - k
        o += 6
    for site in mfgs:
        j = v[F_JB + site]
        if j:
            if j <= k:
                v[F_JB + site] = 0
                v[F_WH + site * 3 + 2] += 1
            else:
                v[F_JB + site] = j - k
    t = ((r + k) >> 2) - (r >> 2)
    if t:
        for site in raws:
            x = v[F_ST + site]
            if x < 6:
                x += t
                v[F_ST + site] = x if x < 6 else 6
    v[0] = r + k
    return True


def _stock_value(v, mfgs):
    val = 0.0
    for site in mfgs:
        if v[F_WS + site]:
            f = v[F_WH + site * 3 + 1]
            t = v[F_WH + site * 3]
            val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)
    return val


def stock_value(s):
    """Sum over own workshop sites of min(fibre,2)*1.5 + min(timber,4) (Sim or Side)."""
    if isinstance(s, Sim):
        v = s.v
        val = 0.0
        for site in range(10):
            if v[F_WS + site]:
                f = v[F_WH + site * 3 + 1]
                t = v[F_WH + site * 3]
                val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)
        return val
    val = 0.0
    for site in range(10):
        if s.ws[site]:
            f = s.wh[site * 3 + 1]
            t = s.wh[site * 3]
            val += (2 if f > 2 else f) * 1.5 + (4 if t > 4 else t)
    return val


DEFAULT_CACHE_SIZE = 20000
BIG = 1 << 30


class ReplanCache:
    """Bounded memo of whole replans: key = the flat Sim of the replan input (round, own side,
    stock estimates, claims) packed as int16 bytes; value = (plan codes as array('h'), contracts
    tuple, score) or None. About 0.5 KB per entry. One cache per
    (map, style): get it with Map.replan_cache(style). When full, the oldest half is dropped
    (a hit moves the entry to the young end)."""
    __slots__ = ('d', 'maxsize', 'hits', 'misses')

    def __init__(self, maxsize=DEFAULT_CACHE_SIZE):
        self.d = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0

    def get(self, key, default=None):
        d = self.d
        r = d.pop(key, _MISSING)
        if r is _MISSING:
            self.misses += 1
            return default
        d[key] = r
        self.hits += 1
        return r

    def put(self, key, val):
        d = self.d
        if len(d) >= self.maxsize:
            for k in list(islice(d, max(1, len(d) // 2))):
                del d[k]
        d[key] = val

    def clear(self):
        self.d.clear()

    def __len__(self):
        return len(self.d)


_MISSING = object()


class Professor:
    def __init__(self, style, seat=None, cache=None, use_cache=True):
        """style: id 0-4 (index into STYLES) or a (B, A, W) tuple. cache: a ReplanCache to use;
        by default the map's shared cache for this style (Map.replan_cache). use_cache=False
        disables memoisation."""
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
        self.cache = cache
        self.use_cache = use_cache

    def clone(self):
        p = Professor.__new__(Professor)
        p.B = self.B
        p.A = self.A
        p.W = self.W
        p.seat = self.seat
        p.last_round = self.last_round
        p.est = self.est[:]
        p.plan = deque(self.plan)
        p.plan_contracts = self.plan_contracts[:]
        p.mp = self.mp
        p.replans = 0               # as professor.py: a clone starts its own count
        p.cache = self.cache
        p.use_cache = self.use_cache
        return p

    # ---- Sim primitives ----------------------------------------------------------------------

    def _bind(self, mp):
        """Cache map tables on self for the planner."""
        if getattr(self, '_bound', None) is mp:
            return
        self._bound = mp
        self._raws = mp.raw_sites
        self._mfgs = mp.mfg_sites
        self._dist = mp.dist
        self._tlen = mp.tlen
        self._tsails = mp.tsails
        self._roles = mp.roles
        self._routes = mp.routes
        self._cands = mp.acq_cands
        self._cdl = mp.c_deadline
        self._cdest = mp.c_dest
        self._cgood = mp.c_good
        self._cqty = mp.c_qty
        self._cpts = mp.c_points
        self._nc = mp.ncontracts

    def _legal(self, v, code):
        """Exactly is_legal() for a code on a flat Sim."""
        op = code & 15
        if op == OP_WAIT:
            return True
        if op == OP_BUILD_BOAT:
            h3 = F_WH + v[F_HM] * 3
            return v[F_NB] <= 2 and v[h3] >= 4 and v[h3 + 1] >= 2
        b = (code >> 4) & 3
        if b >= v[F_NB]:
            return False
        o = F_BT + 6 * b
        if v[o + 2] != 0:
            return False
        pos = v[o]
        arg = code >> 6
        if op == OP_SAIL:
            return self._routes[pos][arg] != 0
        if op == OP_DELIVER:
            c = arg
            return (c < self._nc and v[F_CL + c] == -1 and self._cdl[c] > v[F_R]
                    and self._cdest[c] == pos and v[o + 3 + self._cgood[c]] >= self._cqty[c])
        g = arg >> 2
        q = arg & 3
        free = 3 - (v[o + 3] + v[o + 4] + v[o + 5])
        if op == OP_GATHER:
            role = self._roles[pos]
            if role != 0 and role != 1:
                return False
            return g == role and 1 <= q <= min(v[F_ST + pos], free)
        if op == OP_LOAD:
            return 1 <= q <= min(v[F_WH + pos * 3 + g], free)
        if op == OP_UNLOAD:
            return 1 <= q <= v[o + 3 + g]
        if op == OP_BUILD_WS:
            return (self._roles[pos] == 2 and not v[F_WS + pos]
                    and v[F_WH + pos * 3] >= 2 and v[F_WH + pos * 3 + 1] >= 1)
        if op == OP_CRAFT:
            return (self._roles[pos] == 2 and v[F_WS + pos] and v[F_JB + pos] == 0
                    and v[F_WH + pos * 3] >= 2 and v[F_WH + pos * 3 + 1] >= 1)
        return False

    def _apply(self, v, code):
        """apply_order on a flat Sim (no route conflicts). False = order failed."""
        op = code & 15
        if op == OP_WAIT:
            return True
        if op == OP_BUILD_BOAT:
            h3 = F_WH + v[F_HM] * 3
            v[h3] -= 4
            v[h3 + 1] -= 2
            v.extend((v[F_HM], -1, 0, 0, 0, 0))
            v[F_NB] += 1
            return True
        b = (code >> 4) & 3
        o = F_BT + 6 * b
        pos = v[o]
        arg = code >> 6
        if op == OP_SAIL:
            v[o + 1] = arg
            v[o + 2] = self._routes[pos][arg]
            return True
        if op == OP_DELIVER:
            c = arg
            if v[F_CL + c] != -1:
                return False
            g = self._cgood[c]
            v[o + 3 + g] -= self._cqty[c]
            v[F_SC] += self._cpts[c]
            if g == 2:
                v[F_CR] += 1
            v[F_CL + c] = self.seat if self.seat is not None else 0
            return True
        g = arg >> 2
        q = arg & 3
        if op == OP_GATHER:
            if v[F_ST + pos] < q:
                return False
            v[F_ST + pos] -= q
            v[o + 3 + g] += q
            return True
        if op == OP_LOAD:
            v[F_WH + pos * 3 + g] -= q
            v[o + 3 + g] += q
            return True
        if op == OP_UNLOAD:
            v[F_WH + pos * 3 + g] += q
            v[o + 3 + g] -= q
            return True
        if op == OP_BUILD_WS:
            v[F_WH + pos * 3] -= 2
            v[F_WH + pos * 3 + 1] -= 1
            v[F_WS + pos] = 1
            return True
        if op == OP_CRAFT:
            v[F_WH + pos * 3] -= 2
            v[F_WH + pos * 3 + 1] -= 1
            v[F_JB + pos] = 3
            return True
        raise ValueError('unknown order code %r' % code)

    def _step(self, s, code):
        """Sim::step with the full legality check (non-wait orders only; waits are not recorded)."""
        v = s.v
        if not v[F_OK] or v[F_R] >= 160:
            v[F_OK] = 0
            return
        if not self._legal(v, code) or not self._apply(v, code):
            v[F_OK] = 0
            return
        _ff(v, 1, self._raws, self._mfgs)
        s.acts = (s.acts, code)

    def _step_nl(self, s, code):
        """Sim::step for an order that is legal by construction (no check; it still applies the
        160-round limit and records the order)."""
        v = s.v
        if not v[F_OK] or v[F_R] >= 160:
            v[F_OK] = 0
            return
        if not self._apply(v, code):
            v[F_OK] = 0
            return
        _ff(v, 1, self._raws, self._mfgs)
        s.acts = (s.acts, code)

    def _travel(self, s, b, target):
        """0x1a1c0 in O(1): wait until boat b docks, then sail the next-hop path to target."""
        v = s.v
        if not v[F_OK]:
            return
        o = F_BT + 6 * b
        e = v[o + 2]
        if e:
            if not _ff(v, e, self._raws, self._mfgs):
                return
        pos = v[o]
        if pos == target:
            return
        L = self._tlen[pos][target]
        if L < 0:
            v[F_OK] = 0
            return
        v[o] = target
        if not _ff(v, L, self._raws, self._mfgs):
            return
        s.acts = (s.acts, self._tsails[b][pos][target])

    def _wait_jobs(self, s, w):
        """`while s.ok and s.jobs[w] != 0: step(WAIT)`"""
        v = s.v
        if v[F_OK]:
            j = v[F_JB + w]
            if j:
                _ff(v, j, self._raws, self._mfgs)

    # ---- acquire (0x26c80 + lambda 0x2bf10) ------------------------------------------------

    def acquire(self, sim, b, need, dest, unload_at_dest, rbound=BIG, cbound=None):
        """acquire (0x26c80). Extra exact pruning: only results with round < rbound are wanted
        and, with cbound (supply), only results whose supply cost (round - surplus * B, surplus
        from the final warehouse at dest) is < cbound. The reference would return a result that
        its caller then rejects; here such a result is never built and None comes back.

        Orders here skip the legality check because they are legal by construction:
          * dump unloads: the boat is docked after travel and holds cargo0[g] > need[g];
          * loads/gathers in _rec: the boat is docked at the source after travel, the source held
            >= m when the candidate was listed (goods 0/1 in warehouses do not change while a boat
            sails, natural stock only grows), role == g for gathers, and free space >= m because
            after the dump sum(max(need, cargo)) <= 3;
          * leaf unloads: the boat is docked at dest holding max(need, cargo) >= need[g] >= 1.
        need[2] is always 0 in the Professor's calls."""
        v = sim.v
        o = F_BT + 6 * b
        n0 = need[0]
        n1 = need[1]
        n2 = need[2]
        c0 = v[o + 3]
        c1 = v[o + 4]
        c2 = v[o + 5]
        keep = (n0 if n0 > c0 else c0) + (n1 if n1 > c1 else c1) + (n2 if n2 > c2 else c2)
        if keep > 3:
            s = sim.copy()
            v = s.v
            self._travel(s, b, v[o + 1] if v[o + 2] != 0 else v[o])
            bq = b << 4
            if n0 < c0:
                self._step_nl(s, OP_UNLOAD | bq | (c0 - n0) << 6)
            if n1 < c1:
                self._step_nl(s, OP_UNLOAD | bq | (4 + c1 - n1) << 6)
            if n2 < c2:
                self._step_nl(s, OP_UNLOAD | bq | (8 + c2 - n2) << 6)
            if not v[F_OK]:
                return None
        else:
            s = sim          # rec never mutates its input
            if not v[F_OK]:
                return None
        bound = rbound if rbound < 161 else 161     # a step starting at round >= 160 fails
        if cbound is not None and cbound < 1e29:
            w3 = F_WH + dest * 3
            K = (max(0, v[w3 + 1] + n1 - 1) * 1.5 + max(0, v[w3] + n0 - 2)) * self.B
            R = int(cbound + K) - 2
            while (R - K) >= cbound:
                R -= 1
            while not ((R - K) >= cbound):
                R += 1
            if R < bound:
                bound = R
        if v[F_R] >= bound:
            return None
        m0 = n0 - v[o + 3]
        m1 = n1 - v[o + 4]
        m2 = n2 - v[o + 5]
        missing = (m0 if m0 > 0 else 0, m1 if m1 > 0 else 0, m2 if m2 > 0 else 0)
        order = [g for g in range(3) if missing[g] > 0]
        nun = (1 if n0 else 0) + (1 if n1 else 0) + (1 if n2 else 0) if unload_at_dest else 0
        best = [None, bound]      # best sim, round to beat
        while True:
            self._rec(s, 0, order, missing, b, need, dest, unload_at_dest, nun, best)
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

    def _rec(self, sm, idx, order, missing, b, need, dest, unload, nun, best):
        v = sm.v
        if not v[F_OK]:
            return
        if v[F_R] >= best[1]:
            return
        o = F_BT + 6 * b
        e = v[o + 2]
        cur = v[o + 1] if e else v[o]
        if idx == len(order):
            # finishing round: dock + travel + unloads (each of those steps checks round < 160)
            L = self._tlen[cur][dest]
            if L < 0:
                return
            if v[F_R] + e + L + nun >= best[1]:
                return
            t = sm.copy()
            self._travel(t, b, dest)
            if unload:
                bq = b << 4
                if need[0]:
                    self._step_nl(t, OP_UNLOAD | bq | need[0] << 6)
                if need[1]:
                    self._step_nl(t, OP_UNLOAD | bq | (4 + need[1]) << 6)
                if need[2]:
                    self._step_nl(t, OP_UNLOAD | bq | (8 + need[2]) << 6)
            if t.v[F_OK]:
                best[0] = t
                best[1] = t.v[F_R]
            return
        g = order[idx]
        m = missing[g]
        dcur = self._dist[cur]
        r0 = v[F_R] + e + 1
        cnt = 0
        nidx = idx + 1
        loadc = OP_LOAD | b << 4 | (g * 4 + m) << 6
        gathc = OP_GATHER | b << 4 | (g * 4 + m) << 6
        for site, is_load in self._cands[cur][dest][g]:
            if unload and site == dest:
                continue
            if is_load:
                if v[F_WH + site * 3 + g] < m:
                    continue
            elif v[F_ST + site] < m:
                continue
            cnt += 1
            if cnt > 5:
                break
            if r0 + dcur[site] >= best[1]:
                continue
            t = sm.copy()
            self._travel(t, b, site)
            self._step_nl(t, loadc if is_load else gathc)
            self._rec(t, nidx, order, missing, b, need, dest, unload, nun, best)

    # ---- supply a manufacturing site with 2 timber + 1 fibre (0x27250) --------------------

    def supply(self, sim, w):
        v = sim.v
        need_t = max(0, 2 - v[F_WH + w * 3])
        need_f = max(0, 1 - v[F_WH + w * 3 + 1])
        B = self.B
        best_cost = 1e30
        best = None
        nb = v[F_NB]
        if need_t + need_f == 0:
            for b in range(nb):
                s = sim.copy()
                self._travel(s, b, w)
                if s.v[F_OK]:
                    sv = s.v
                    c = sv[F_R] - (max(0, sv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, sv[F_WH + w * 3] - 2)) * B
                    if c < best_cost:
                        best_cost = c
                        best = (s, b)
            return best
        for b in range(nb):
            r = self.acquire(sim, b, (need_t, need_f, 0), w, True, BIG, best_cost)
            if r is not None:
                rv = r.v
                c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B
                if c < best_cost:
                    best_cost = c
                    best = (r, b)
            if need_t != 0 and need_f == 0:
                r = self.acquire(sim, b, (3, 0, 0), w, True, BIG, best_cost)
                if r is not None:
                    rv = r.v
                    c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B
                    if c < best_cost:
                        best_cost = c
                        best = (r, b)
            if need_f != 0 and need_t == 0:
                r = self.acquire(sim, b, (0, 3, 0), w, True, BIG, best_cost)
                if r is not None:
                    rv = r.v
                    c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B
                    if c < best_cost:
                        best_cost = c
                        best = (r, b)
        if need_t != 0 and need_f != 0 and v[F_R] < 50:
            for first, second in (((3, 0, 0), (0, 3, 0)), ((0, 3, 0), (3, 0, 0))):
                for b1 in range(nb):
                    r1 = self.acquire(sim, b1, first, w, True)
                    if r1 is None:
                        continue
                    for b2 in range(nb):
                        r2 = self.acquire(r1, b2, second, w, True, BIG, best_cost)
                        if r2 is not None:
                            rv = r2.v
                            c = rv[F_R] - (max(0, rv[F_WH + w * 3 + 1] - 1) * 1.5 + max(0, rv[F_WH + w * 3] - 2)) * B
                            if c < best_cost:
                                best_cost = c
                                best = (r2, b2)
        return best

    # ---- get one manufactured good to `dest` (0x284f0) ------------------------------------

    def manufactured(self, sim, dest):
        """Same candidate order as the reference. Everything up to "boat b holds the good at
        site w" is cached on the input sim (it does not depend on dest). A candidate's cost is
        known before travelling (stock_value cannot change while a boat sails), so only an
        improving candidate is copied and simulated."""
        best_cost = 1e30
        best = None
        v = sim.v
        nb = v[F_NB]
        mfgs = self._mfgs
        tlen = self._tlen
        memo = sim.memo
        if memo is None:
            memo = sim.memo = {}
        sv05 = _stock_value(v, mfgs) * 0.5

        # A: a boat already carries a manufactured good
        for b in range(nb):
            o = F_BT + 6 * b
            if v[o + 5] != 0:
                e = v[o + 2]
                L = tlen[v[o + 1] if e else v[o]][dest]
                if L < 0:
                    continue
                rf = v[F_R] + e + L
                if rf > 160:
                    continue
                c = rf - sv05
                if c < best_cost:
                    s = sim.copy()
                    self._travel(s, b, dest)
                    best_cost = c
                    best = (s, b)
        # B: pick one up where it is stored or being crafted
        for w in range(10):
            if v[F_WH + w * 3 + 2] != 0 or v[F_JB + w] != 0:
                for b in range(nb):
                    key = w * 4 + b
                    s = memo.get(key, _MISSING)
                    if s is _MISSING:
                        s = sim.copy()
                        self._travel(s, b, w)
                        self._wait_jobs(s, w)
                        if s.v[F_OK]:
                            sv = s.v
                            ob = F_BT + 6 * b
                            if sv[ob + 3] + sv[ob + 4] + sv[ob + 5] < 3:
                                self._step(s, OP_LOAD | b << 4 | 9 << 6)
                            else:
                                s = None
                        if s is not None and not s.v[F_OK]:
                            s = None
                        memo[key] = s
                    if s is not None:
                        best_cost, best = self._consider(s, b, dest, best_cost, best)
        # C: (build a workshop and) craft a new one
        for w in mfgs:
            key = 100 + w
            loaded = memo.get(key)
            if loaded is None:
                loaded = []
                s = sim.copy()
                crafted = False
                r = True
                if not s.v[F_WS + w]:
                    r = self.supply(s, w)
                    if r is not None:
                        s = r[0]
                        self._step(s, OP_BUILD_WS | r[1] << 4)
                if r is not None and s.v[F_OK] and s.v[F_JB + w] == 0:
                    r = self.supply(s, w)
                    if r is not None:
                        s = r[0]
                        self._step(s, OP_CRAFT | r[1] << 4)
                        crafted = True
                if crafted:
                    for b in range(nb):
                        t = s.copy()
                        self._travel(t, b, w)
                        if t.v[F_OK]:
                            self._wait_jobs(t, w)
                            if t.v[F_OK]:
                                tv = t.v
                                ob = F_BT + 6 * b
                                if tv[ob + 3] + tv[ob + 4] + tv[ob + 5] < 3:
                                    self._step(t, OP_LOAD | b << 4 | 9 << 6)
                                    if tv[F_OK]:
                                        loaded.append((t, b))
                memo[key] = loaded
            for t, b in loaded:
                best_cost, best = self._consider(t, b, dest, best_cost, best)
        return best

    def _consider(self, s, b, dest, best_cost, best):
        """consider(s.copy(), b): travel to dest; cost = round - 0.5 * stock_value."""
        v = s.v
        o = F_BT + 6 * b
        e = v[o + 2]
        L = self._tlen[v[o + 1] if e else v[o]][dest]
        if L < 0:
            return best_cost, best
        rf = v[F_R] + e + L
        if rf > 160:
            return best_cost, best
        c = rf - _stock_value(v, self._mfgs) * 0.5
        if c < best_cost:
            t = s.copy()
            self._travel(t, b, dest)
            return c, (t, b)
        return best_cost, best

    # ---- sequential plan for one more contract (0x29690) ------------------------------------

    def prepare(self, sim, c):
        v = sim.v
        if v[F_CL + c] != -1:
            return None
        g = self._cgood[c]
        dest = self._cdest[c]
        if g == 2:
            r = self.manufactured(sim, dest)
            if r is None:
                return None
            s, boat = r
        else:
            need = [0, 0, 0]
            need[g] = self._cqty[c]
            s = None
            boat = -1
            for b in range(v[F_NB]):
                r = self.acquire(sim, b, need, dest, False, BIG if s is None else s.v[F_R])
                if r is not None and (s is None or r.v[F_R] < s.v[F_R]):
                    s = r
                    boat = b
            if s is None:
                return None
        s = s.copy()
        # lenient deliver (no deadline check)
        sv = s.v
        if not sv[F_OK] or sv[F_R] >= 160:
            return None
        o = F_BT + 6 * boat
        if (sv[o + 2] != 0 or sv[o] != dest or sv[o + 3 + g] < self._cqty[c] or sv[F_CL + c] != -1):
            return None
        code = OP_DELIVER | boat << 4 | c << 6
        self._apply(sv, code)
        _ff(sv, 1, self._raws, self._mfgs)
        s.acts = (s.acts, code)
        return s

    # ---- re-schedule the sequential action list over the boats (0x29f80) ---------------------

    def interleave(self, codes, variant, snap=None, record=None):
        """codes: non-wait order codes (sequential plan). snap: a parent run snapshot
        (v, out, ptrs) to resume from, valid because the parent's per-boat queues are a prefix of
        these. record: list to receive this run's snapshot at the first moment a queue is empty
        (or the string 'fail' if the run failed before)."""
        qs = ([], [], [])
        for a in codes:
            qs[(a >> 4) & 3].append(a)
        q0, q1, q2 = qs
        n0 = len(q0)
        n1 = len(q1)
        n2 = len(q2)
        if snap is not None:
            sv, sout, p0, p1, p2 = snap
            s = Sim.__new__(Sim)
            s.v = v = sv[:]
            s.memo = None
            s.snaps = None
            s.acts = None
            out = sout[:]
        else:
            s = self.cur.copy()
            v = s.v
            out = []
            p0 = p1 = p2 = 0
        raws = self._raws
        mfgs = self._mfgs
        nb = v[F_NB]
        legal = self._legal
        apply = self._apply
        rec = record is not None and not record
        while v[F_R] < 80:
            e0 = p0 >= n0
            e1 = p1 >= n1
            e2 = p2 >= n2
            if rec and (e0 or (e1 and nb > 1) or (e2 and nb > 2)):
                # a child's queues are this run's queues plus more orders at the back: the
                # child's run is identical up to the first moment one of its boat queues is empty
                record.append((v[:], out[:], p0, p1, p2))
                rec = False
            if e0 and e1 and e2:
                s.base = out
                s.basenw = [c for c in out if c & 15]
                s.acts = None
                return s
            chosen = -1
            cc = 0
            for i in range(variant, variant + nb):
                bb = i % nb
                if bb == 0:
                    if p0 >= n0:
                        continue
                    a = q0[p0]
                elif bb == 1:
                    if p1 >= n1:
                        continue
                    a = q1[p1]
                else:
                    if bb > 2 or p2 >= n2:
                        continue
                    a = q2[p2]
                if legal(v, a):
                    isd = (a & 15) == OP_DELIVER
                    if chosen < 0 or isd:
                        chosen = bb
                        cc = a
                    if isd:
                        break
            if chosen < 0:
                busy = False
                k = 80 - v[F_R]
                o = F_BT
                for _i in range(nb):
                    e = v[o + 2]
                    if e > 0:
                        busy = True
                        if e < k:
                            k = e
                    o += 6
                for site in mfgs:
                    j = v[F_JB + site]
                    if j > 0:
                        busy = True
                        if j < k:
                            k = j
                if not busy:
                    if rec:
                        record.append('fail')
                    return None
                t = 4 - (v[F_R] & 3)
                if t < k:
                    k = t
                _ff(v, k, raws, mfgs)
                out.extend([0] * k)
            else:
                if chosen == 0:
                    p0 += 1
                elif chosen == 1:
                    p1 += 1
                else:
                    p2 += 1
                if not apply(v, cc):
                    v[F_OK] = 0
                    if rec:
                        record.append('fail')
                    return None
                _ff(v, 1, raws, mfgs)
                out.append(cc)
        if rec:
            record.append('fail')
        if p0 < n0 or p1 < n1 or p2 < n2:
            return None
        s.base = out
        s.basenw = [c for c in out if c & 15]
        s.acts = None
        return s

    # ---- top level (0x3ae20) ------------------------------------------------------------------

    def make_sim(self, view):
        side = view.side
        v = [view.round, 1, side.score, side.crafted, side.home, len(side.boats)]
        v.extend(self.est)
        cl = list(view.claims)
        if len(cl) < NCMAX:
            cl.extend([-1] * (NCMAX - len(cl)))
        v.extend(cl)
        v.extend(side.wh)
        v.extend([1 if x else 0 for x in side.ws])
        v.extend(side.jobs)
        for b in side.boats:
            v.extend(b)
        s = Sim.__new__(Sim)
        s.v = v
        s.base = None
        s.basenw = None
        s.acts = None
        s.memo = None
        s.snaps = None
        return s

    def replan(self, view):
        """Beam search over contract sequences. Returns (plan orders, contracts, score) or None.
        Memoised in self.cache (the map's shared cache for this style unless use_cache=False)."""
        self.replans += 1
        mp = view.mp
        self.mp = mp
        cur = self.make_sim(view)
        cache = None
        if self.use_cache:
            cache = self.cache
            if cache is None:
                cache = self.cache = mp.replan_cache((self.B, self.A, self.W))
            key = array('h', cur.v).tobytes()
            r = cache.get(key, _MISSING)
            if r is not _MISSING:
                if r is None:
                    return None
                return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])
        r = self._replan(cur, mp)
        if cache is not None:
            cache.put(key, r)
        if r is None:
            return None
        return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])

    def replan_uncached(self, view):
        cur = self.make_sim(view)
        r = self._replan(cur, view.mp)
        if r is None:
            return None
        return ([CODE2ORDER[c] for c in r[0]], list(r[1]), r[2])

    def _replan(self, cur, mp):
        """Returns (plan codes array, contracts tuple, score) or None.

        Beam nodes are (sim, contracts, score, snaps, exp). snaps: the two parent-run snapshots
        its children's interleave resumes from. exp: memo {contract: child results}, shared by the
        two variant nodes of one prepare when their states are equal: their children are then
        identical (interleave only sees per-boat order), so they are computed once."""
        self._bind(mp)
        self.cur = cur
        cv = cur.v
        mfgs = self._mfgs
        cur_has_ws = False
        for site in range(10):
            if cv[F_WS + site]:
                cur_has_ws = True
        cround = cv[F_R]
        cscore = cv[F_SC]
        A = self.A
        W = self.W
        nc = self._nc
        cdl = self._cdl
        best = None
        frontier = [(cur, (), 0.0, None, {})]
        for _depth in range(4):
            nxt = []
            for node_sim, node_contracts, _sc, snaps, exp in frontier:
                ncl = node_sim.v
                for c in range(nc):
                    if ncl[F_CL + c] != -1 or not (cround < cdl[c]):
                        continue
                    kids = exp.get(c)
                    if kids is None:
                        kids = ()
                        opt = self.prepare(node_sim, c)
                        if opt is not None:
                            acts = opt.nowait_codes()
                            rec_pair = ([], [])
                            results = []
                            for variant in (0, 1):
                                snap = None
                                if snaps is not None:
                                    snap = snaps[variant]
                                    if snap == 'fail':
                                        rec_pair[variant].append('fail')
                                        continue
                                res = self.interleave(acts, variant, snap, rec_pair[variant])
                                if res is not None:
                                    results.append(res)
                            if results:
                                child_snaps = (rec_pair[0][0] if rec_pair[0] else 'fail',
                                               rec_pair[1][0] if rec_pair[1] else 'fail')
                                kl = []
                                prev = None
                                for res in results:
                                    rv = res.v
                                    has_ws = False
                                    for site in mfgs:
                                        if rv[F_WS + site]:
                                            has_ws = True
                                    bonus = W if (not cur_has_ws and has_ws) else 0
                                    score = ((_stock_value(rv, mfgs) * 0.1 + float((rv[F_SC] - cscore) + bonus))
                                             / pow(float((rv[F_R] - cround) + 3), A))
                                    if prev is not None and prev.v == rv:
                                        cexp = kl[-1][3]
                                    else:
                                        cexp = {}
                                    prev = res
                                    kl.append((res, score, child_snaps, cexp))
                                kids = tuple(kl)
                        exp[c] = kids
                    for res, score, child_snaps, cexp in kids:
                        node = (res, node_contracts + (c,), score, child_snaps, cexp)
                        if best is None or best[2] < score:
                            best = node
                        nxt.append(node)
            if not nxt:
                break
            nxt.sort(key=_node_key)
            frontier = nxt[:8]
        self.cur = None
        if best is None:
            return None
        return (array('h', best[0].codes()), best[1], best[2])

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
        vis = view.visible
        vst = view.stocks
        for s in range(10):
            x = est[s] + d
            if x > 6:
                x = 6
            if vis[s]:
                x = vst[s]
            est[s] = x
        self.last_round = rnd
        claims = view.claims
        for c in self.plan_contracts:
            if claims[c] != -1 and claims[c] != self.seat:
                self.plan.clear()
        side = view.side
        if rnd >= 80:
            return WAIT
        cdl = mp.c_deadline
        cdest = mp.c_dest
        cgood = mp.c_good
        cqty = mp.c_qty
        for b, boat in enumerate(side.boats):
            if boat[2] != 0:
                continue
            pos = boat[0]
            for c in range(mp.ncontracts):
                if (claims[c] == -1 and cdl[c] > rnd and cdest[c] == pos
                        and boat[3 + cgood[c]] >= cqty[c]):
                    self.plan.clear()
                    self.plan_contracts = []
                    return o_deliver(b, c)
        if self.plan and is_legal(mp, side, vst, claims, rnd, self.plan[0]):
            return self.plan.popleft()
        self.plan.clear()
        self.plan_contracts = []
        best = self.replan(view)
        if best is not None:
            acts = best[0]
            if acts:
                self.plan_contracts = list(best[1])
                self.plan = deque(acts)
                if is_legal(mp, side, vst, claims, rnd, self.plan[0]):
                    return self.plan.popleft()
        self.plan.clear()
        return WAIT


def _node_key(nd):
    return (-nd[2], nd[0].v[F_R])


# ---------------------------------------------------------------------------------------------
# Style tracking: five hypotheses (Engine + Professor per style), pruned on observations
# ---------------------------------------------------------------------------------------------

class Hypothesis:
    """One style hypothesis: the full two-sided Engine and the Professor's state.
    `pending` is the Professor's order for the current engine round once computed (order())."""
    __slots__ = ('style', 'eng', 'prof', 'seat', 'pending')

    def __init__(self, style, eng, prof, seat):
        self.style = style
        self.eng = eng
        self.prof = prof
        self.seat = seat
        self.pending = None

    def order(self):
        """The Professor's order for the engine's current round (computed once)."""
        if self.pending is None and self.eng.round < 80:
            self.pending = self.prof.choose(self.eng.view(1 - self.seat))
        return self.pending

    def step(self, ours):
        """Play one round: our order (tuple) vs the Professor's. Returns the engine's [ok0, ok1]."""
        theirs = self.order()
        orders = [None, None]
        orders[self.seat] = ours
        orders[1 - self.seat] = theirs if theirs is not None else WAIT
        ok = self.eng.step(orders)
        self.pending = None
        return ok

    def clone(self):
        """Cheap copy for lookahead (engine + Professor + pending order; the cache is shared)."""
        h = Hypothesis.__new__(Hypothesis)
        h.style = self.style
        h.eng = self.eng.clone()
        h.prof = self.prof.clone()
        h.seat = self.seat
        h.pending = self.pending
        return h


def _obs_signature(obs):
    own = obs['own']
    sig = [obs['round'], obs['seat'], obs['opponent_score'], own['score'], own['crafted_deliveries'],
           own['home']]
    sig.extend(obs['claims'])
    sig.extend([1 if x else 0 for x in obs['visible']])
    sig.extend([-9 if x is None else x for x in obs['stocks']])
    for row in own['warehouses']:
        sig.extend(row)
    sig.extend([1 if x else 0 for x in own['workshops']])
    sig.extend(own['jobs'])
    sig.append(len(own['boats']))
    for b in own['boats']:
        sig.append(b['position'])
        sig.append(b['destination'])
        sig.append(b['eta'])
        sig.extend(b['cargo'])
    en = sorted((b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats'])
    sig.append(len(en))
    for t in en:
        sig.extend(t)
    return sig


def engine_signature(eng, seat):
    """Same field order as _obs_signature, from the model."""
    side = eng.sides[seat]
    other = eng.sides[1 - seat]
    vis = [False] * 10
    vis[side.home] = True
    for s in range(10):
        if side.ws[s]:
            vis[s] = True
    for b in side.boats:
        if b[2] == 0:
            vis[b[0]] = True
    sig = [eng.round, seat, other.score, side.score, side.crafted, side.home]
    sig.extend(eng.claims)
    sig.extend([1 if x else 0 for x in vis])
    st = eng.stocks
    sig.extend([st[s] if vis[s] else -9 for s in range(10)])
    sig.extend(side.wh)
    sig.extend([1 if x else 0 for x in side.ws])
    sig.extend(side.jobs)
    sig.append(len(side.boats))
    for b in side.boats:
        sig.extend(b)
    en = [(i, b[0], b[1], b[2]) for i, b in enumerate(other.boats) if vis[b[0]] or (b[1] >= 0 and vis[b[1]])]
    sig.append(len(en))
    for t in en:
        sig.extend(t)
    return sig


class Tracker:
    """Five style hypotheses fed by observations and our own orders.

        tr = Tracker(obs)             # at round 0 (or Tracker(obs, styles=[...]))
        each round:
            alive = tr.observe(obs)   # prune (compare_observation semantics), returns survivors
            ... h.order() is the Professor's order this round under hypothesis h;
                h.clone() gives an independent copy for lookahead (h.clone().step(our_order)) ...
            tr.commit(our_order)      # our order as a tuple or a JSON action dict

    A hypothesis is dropped when the observation differs from its Engine's view of our seat in
    any field compare_observation (work/binary/test_professor.py) checks: round, seat,
    opponent_score, claims, visible, visible stocks, own side (score, crafted, home, boats,
    warehouses, workshops, jobs) and the enemy boats we see. legal_actions is a function of those
    fields, so it is only compared with strict=True."""

    def __init__(self, obs, styles=(0, 1, 2, 3, 4), mp=None, strict=False, cache_size=None):
        self.seat = obs['seat']
        self.mp = mp or Map(obs['map'])
        self.strict = strict
        ps = 1 - self.seat
        self.hyps = []
        for st in styles:
            cache = self.mp.replan_cache(st, cache_size)
            self.hyps.append(Hypothesis(st, Engine(self.mp), Professor(st, ps, cache=cache), self.seat))
        self.dropped = {}          # style -> round it was dropped
        self.round = obs['round']

    @property
    def styles(self):
        return [h.style for h in self.hyps]

    def observe(self, obs):
        sig = _obs_signature(obs)
        keep = []
        for h in self.hyps:
            ok = engine_signature(h.eng, self.seat) == sig
            if ok and self.strict:
                legal = [order_to_json(o) for o in h.eng.legal(self.seat)]
                ok = legal == obs['legal_actions']
            if ok:
                keep.append(h)
            else:
                self.dropped[h.style] = obs['round']
        self.hyps = keep
        self.round = obs['round']
        for h in keep:
            h.order()
        return keep

    def commit(self, ours):
        if isinstance(ours, dict):
            ours = order_from_json(ours)
        for h in self.hyps:
            h.step(ours)


# ---------------------------------------------------------------------------------------------
# Map generation (engine function 0x1e1b0), exact.
# ---------------------------------------------------------------------------------------------

def generate_map(topology, seed):
    """Returns the same dict as observation['map'] for group = 2*topology + seat."""
    state = [seed ^ 0x43414d504149474e]

    def rnd():
        state[0], v = splitmix_next(state[0])
        return v

    for _attempt in range(4096):
        routes = [[0] * 10 for _ in range(10)]

        def edge(i, j):
            length = rnd() % 3 + 1
            routes[i][j] = length
            routes[j][i] = length

        if topology == 0:
            for i in range(10):
                edge(i, (i + 1) % 10)
        elif topology == 1:
            for base in (0, 5):
                for i in range(4):
                    edge(base + i, base + i + 1)
            for i in range(5):
                edge(i, i + 5)
        elif topology == 2:
            for base in (0, 5):
                for i in range(5):
                    edge(base + i, base + (i + 1) % 5)
            edge(2, 7)
        else:
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
                 'claims0', 'ret', 'xkey', 'ths', 'root')

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
        n.root = self.root
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
    b0.root = None
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

PARAMS = dict(beam_frac=0.4, beam_frac0=0.65, width=12, per_root=2, depth=6, nroll=6, xwidth=8, xwidth5=4, kits=(0, 1, 2, 3), iters=2, w_free=1.75, null0=1, t0_first=4.0, t0=1.6, tgame=4.2, every=6)


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
    g.plan_seq = []
    g.plan_ret = False
    g.plan_W = -1
    g.plan_kit = False
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
        frontier = []
        cnt = {}
        per = PARAMS['per_root']
        for n in nxt:
            root = n.tag.split('.')[0]
            k = cnt.get(root, 0)
            if k >= per:
                continue
            cnt[root] = k + 1
            frontier.append(n)
            if len(frontier) >= width:
                break
        pool.extend(frontier)
        if time.process_time() > t_lim:
            break
    pool.sort(key=lambda n: -n.val)
    return pool


def dbg(*a):
    if PARAMS.get('debug'):
        import sys
        sys.stderr.write(' '.join(str(x) for x in a) + '\n')


def make_roots(side, stocks, claims, rnd):
    cx = CX
    base = base_builder(side, stocks, rnd)
    base.claims0 = claims
    roots = [base]
    if not any(side.ws):
        for W in cx.mfg:
            for v in PARAMS['kits']:
                r = base.copy()
                if r.kit(W, v):
                    r.W = W
                    r.tag = 'k%d%d' % (W, v)
                    roots.append(r)
    for r in list(roots):
        r2 = r.copy()
        r2.ret = True
        r2.tag = r.tag + 'r'
        roots.append(r2)
    return roots


def build_seq(root, seq):
    n = root
    for c in seq:
        u = n.copy()
        if u.add(c):
            n = u
    if n is root:
        n = root.copy()
    n.tag = root.tag + ''.join('.%d' % c for c in n.cons)
    n.root = root
    return n


class Search(object):
    """Exact-rollout search over (root, contract sequence) plans."""

    def __init__(self, g, side, stocks, claims, rnd, hyps, Ps, t_lim):
        self.g = g
        self.side = side
        self.stocks = stocks
        self.claims = claims
        self.rnd = rnd
        self.hyps = hyps
        self.Ps = Ps
        self.t_lim = t_lim
        self.best = None
        self.nev = 0
        self.seen = {}

    def timeout(self):
        return time.process_time() > self.t_lim

    def score(self, n):
        n.res = own_sim(n.finish(), self.side, self.stocks, self.claims, self.rnd)
        n.val = proxy_multi(n.res, self.Ps, self.claims)

    def exact(self, n):
        k = (n.root.tag, tuple(n.cons))
        if k in self.seen:
            n.xkey, n.ths = self.seen[k]
            return n.xkey
        key, ths = evaluate_exact(self.g, n.finish(), self.hyps)
        self.nev += 1
        n.xkey = (key[0], key[1], n.val)
        n.ths = ths
        self.seen[k] = (n.xkey, ths)
        if self.best is None or n.xkey > self.best.xkey:
            self.best = n
        return n.xkey

    def open_contracts(self, cons):
        cx = CX
        return [c for c in range(8) if c not in cons and self.claims[c] == -1 and self.rnd < cx.dl[c]]

    def beam(self, roots, width, depth, t_lim):
        for r in roots:
            r.root = r
            self.score(r)
        roots = sorted(roots, key=lambda n: -n.val)
        frontier = []
        for r in roots:
            if time.process_time() > t_lim:
                break
            self.exact(r)
            frontier.append(r)
        frontier.sort(key=lambda n: n.xkey, reverse=True)
        frontier = frontier[:width]
        for d in range(depth):
            kids = []
            for nd in frontier:
                for c in self.open_contracts(nd.cons):
                    ch = nd.copy()
                    if not ch.add(c):
                        continue
                    ch.root = nd.root
                    self.score(ch)
                    if c not in ch.res:
                        continue
                    ch.tag = nd.tag + ('.%d' % c)
                    kids.append(ch)
            if not kids:
                break
            kids.sort(key=lambda n: -n.val)
            done = []
            for ch in kids:
                if time.process_time() > t_lim:
                    break
                self.exact(ch)
                done.append(ch)
            if not done:
                break
            done.sort(key=lambda n: n.xkey, reverse=True)
            frontier = []
            cnt = {}
            for n in done:
                rt = n.root.tag
                k = cnt.get(rt, 0)
                if k >= PARAMS['per_root']:
                    continue
                cnt[rt] = k + 1
                frontier.append(n)
                if len(frontier) >= width:
                    break
            if time.process_time() > t_lim:
                break

    def local(self, t_lim, max_eval=10 ** 9):
        """First-improvement local search on the best sequence: insert / remove / swap / move."""
        while time.process_time() < t_lim:
            b = self.best
            seq = list(b.cons)
            root = b.root
            cands = []
            for c in self.open_contracts(seq):
                for pos in range(len(seq) + 1):
                    cands.append(seq[:pos] + [c] + seq[pos:])
            for i in range(len(seq)):
                cands.append(seq[:i] + seq[i + 1:])
            for i in range(len(seq) - 1):
                t = list(seq)
                t[i], t[i + 1] = t[i + 1], t[i]
                cands.append(t)
            for i in range(len(seq)):
                for j in range(len(seq)):
                    if abs(i - j) > 1:
                        t = list(seq)
                        x = t.pop(i)
                        t.insert(j, x)
                        cands.append(t)
            nodes = []
            for sq in cands:
                n = build_seq(root, sq)
                if (root.tag, tuple(n.cons)) in self.seen:
                    continue
                self.score(n)
                nodes.append(n)
            nodes.sort(key=lambda n: -n.val)
            improved = False
            for n in nodes:
                if time.process_time() > t_lim:
                    return
                self.exact(n)
                if self.best is not b:
                    improved = True
                    break
            if not improved:
                return


def replan(g, obs, side, budget):
    """Exact-rollout search over the builder's contract sequences; keep the current plan unless a
    candidate is strictly better."""
    t_start = time.process_time()
    t_end = t_start + budget
    rnd = obs['round']
    claims = list(obs['claims'])
    hyps = sorted(g.hyps.items())
    stocks = hyps[0][1][0].stocks[:]
    cur = g.exe
    if cur is None:
        cur = Exe([[] for _ in side.boats], [[0] for _ in side.boats])
        k0, Ps = evaluate_exact(g, cur, hyps)
        curkey = (-999, -999)
    else:
        k0, Ps = evaluate_exact(g, cur, hyps)
        curkey = k0
    nh = len(hyps)
    S = Search(g, side, stocks, claims, rnd, hyps, Ps, t_end)
    roots = make_roots(side, stocks, claims, rnd)
    for r in roots:
        r.root = r
    # seed: the current plan's remaining contracts rebuilt from the matching root
    seq0 = [c for c in g.plan_seq if claims[c] == -1 and rnd < CX.dl[c]]
    if seq0:
        for r in roots:
            if r.tag.endswith('r') == g.plan_ret and (r.W == g.plan_W or r.W < 0 or not g.plan_kit):
                n = build_seq(r, seq0)
                S.score(n)
                S.exact(n)
                break
    width = PARAMS['xwidth'] if nh <= 2 else PARAMS['xwidth5']
    frac = PARAMS['beam_frac'] if seq0 else PARAMS['beam_frac0']
    S.beam(roots, width, PARAMS['depth'], t_start + budget * frac)
    if S.best is not None:
        S.local(t_end)
    bn = S.best
    tag = 'cur'
    if bn is not None and (bn.xkey[0], bn.xkey[1]) > curkey:
        exe = bn.finish()
        tail = with_tail(bn)
        if time.process_time() < t_start + budget * 1.25:
            texe = tail.finish()
            tk, tths = evaluate_exact(g, texe, hyps)
            if tk >= (bn.xkey[0], bn.xkey[1]):
                exe = texe
                tail.xkey = (tk[0], tk[1], bn.xkey[2])
                tail.ths = tths
                tail.root = bn.root
                bn = tail
        g.exe = exe
        g.plan_tag = bn.tag
        g.plan_key = bn.xkey
        g.plan_seq = list(bn.cons)
        g.plan_ret = bn.root.ret
        g.plan_W = bn.root.W
        g.plan_kit = bn.root.tag.startswith('k')
        g.P = bn.ths
        tag = bn.tag
    else:
        g.plan_key = curkey
        g.P = Ps
    dbg('replan r%d hyps=%s cur=%s -> %s %s evals=%d (%.2fs)' % (
        rnd, [h[0] for h in hyps], k0, tag, None if bn is None else bn.xkey, S.nev, time.process_time() - t_start))
    return g.plan_key


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
