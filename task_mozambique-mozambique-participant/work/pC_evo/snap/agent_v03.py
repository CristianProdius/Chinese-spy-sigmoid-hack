"""The Professor of Maputo Bay: rolling-horizon evolutionary planner (single file, stdlib only).

Tracks the five Professor styles with an exact copy of the engine and of the Professor, evolves a
macro plan (ordered contract targets + logistics options) decoded by a deterministic scheduler,
and scores plans by rollouts against every surviving style hypothesis.
"""
import json
import sys

# ==== CORE (engine rules + Professor) ====
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
    """Bounded memo of whole replans: key = flat Sim of the replan input (round, own side, stock
    estimates, claims); value = (plan codes tuple, contracts tuple, score) or None. One cache per
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
        its caller then rejects; here such a result is never built and None comes back."""
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
            key = tuple(cur.v)
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
        """Returns (plan codes tuple, contracts tuple, score) or None.

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
        return (tuple(best[0].codes()), best[1], best[2])

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


# ==== BRAIN (rolling-horizon evolutionary planner) ====
# Uses the engine/Professor core above: Map, Engine, Side, Professor, is_legal, apply_order,
# advance_side, order_to_json, order_from_json, o_* constructors, WAIT, BUILD_BOAT.
import time as _time
import random as _random

T_G, T_L, T_U, T_C, T_D = 0, 1, 2, 3, 4          # task kinds: gather, load, unload, craft, deliver

PARAMS = dict(
    scale=1.0,          # multiplies every time budget (to emulate a slower box on a fast one)
    total=3.6,          # CPU seconds per game (soft)
    first_extra=1.5,    # extra CPU seconds in the first game of a process (JIT warm-up)
    wall_hard=8.0,      # wall seconds per game after which we stop searching
    ga0=1.0,            # CPU seconds of search at round 0
    front=2.0,          # front-loading factor of the per-round slice
    elites=6,
    eps=0.3,            # a child must beat its parent by this much (phantom) to earn an exact evaluation
)

_clock = _time.process_time
_wall = _time.perf_counter
_PROCESS_GAMES = [0]
_LASTG = [None]


def copy_side(s):
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
    n.sides = [copy_side(e.sides[0]), copy_side(e.sides[1])]
    n.stocks = e.stocks[:]
    n.claims = e.claims[:]
    return n


class _RV(object):
    __slots__ = ('side', 'claims', 'round', 'mp', 'seat')


_FAST = hasattr(Professor, 'replan_uncached')      # fastcore: replan returns the order list


def new_professor(style, seat):
    if _FAST:
        return Professor(style, seat, use_cache=False)
    return Professor(style, seat)


class Hyp(object):
    __slots__ = ('style', 'eng', 'prof', 'prof0', 'pred', 'pc', 'pg')


class Game(object):
    pass


_MISS = object()


def prof_choose(G, prof, eng, tlimit):
    """Professor.choose on the engine state directly (no View), with the replan cache.
    Returns None when a new replan would be needed after `tlimit` (rollout aborted)."""
    rnd = eng.round
    mp = eng.mp
    pseat = prof.seat
    side = eng.sides[pseat]
    stocks = eng.stocks
    if rnd == 0:
        prof.last_round = -1
        prof.est = [4] * 10
        prof.plan.clear()
        prof.plan_contracts = []
    prof.mp = mp
    est = prof.est
    d = rnd // 4 if prof.last_round < 0 else rnd // 4 - (prof.last_round >> 2)
    if d:
        for s in range(10):
            v = est[s] + d
            est[s] = 6 if v > 6 else v
    est[side.home] = stocks[side.home]
    ws = side.ws
    for s in range(10):
        if ws[s]:
            est[s] = stocks[s]
    boats = side.boats
    for boat in boats:
        if boat[2] == 0:
            est[boat[0]] = stocks[boat[0]]
    prof.last_round = rnd
    claims = eng.claims
    for c in prof.plan_contracts:
        if claims[c] != -1 and claims[c] != pseat:
            prof.plan.clear()
    if rnd >= 80:
        return WAIT
    c_dest = mp.c_dest
    c_deadline = mp.c_deadline
    c_good = mp.c_good
    c_qty = mp.c_qty
    for b in range(len(boats)):
        boat = boats[b]
        if boat[2] != 0:
            continue
        pos = boat[0]
        for c in range(mp.ncontracts):
            if (claims[c] == -1 and c_dest[c] == pos and c_deadline[c] > rnd
                    and boat[3 + c_good[c]] >= c_qty[c]):
                prof.plan.clear()
                prof.plan_contracts = []
                return o_deliver(b, c)
    plan = prof.plan
    if plan and is_legal(mp, side, stocks, claims, rnd, plan[0]):
        return plan.popleft()
    plan.clear()
    prof.plan_contracts = []
    key = (prof.B, prof.A, prof.W, rnd, tuple([tuple(bt) for bt in boats]), tuple(side.wh),
           tuple(ws), tuple(side.jobs), tuple(est), tuple(claims))
    hit = G.cache.get(key, _MISS)
    if hit is _MISS:
        if tlimit is not None and _clock() > tlimit:
            return None
        v = _RV()
        v.side = side
        v.claims = claims
        v.round = rnd
        v.mp = mp
        v.seat = pseat
        G.nrep += 1
        best = prof.replan(v)
        hit = None
        if best is not None:
            acts = best[0] if _FAST else best[0].actions()
            if acts:
                hit = (tuple(acts), tuple(best[1]))
        G.cache[key] = hit
    if hit is not None:
        prof.plan_contracts = list(hit[1])
        plan.extend(hit[0])
        if is_legal(mp, side, stocks, claims, rnd, plan[0]):
            return plan.popleft()
    plan.clear()
    return WAIT


# ---------------------------------------------------------------------------------------------
# Plan = genome (macro genes) + decoded per-boat task queues
# genes: ('R', c, src, boat) | ('M', c, w, pat, haul_boat, courier) | ('S', w, good, src, boat) | ('B',)
# task: (kind, site, good, qty, contract, gene_index)
# ---------------------------------------------------------------------------------------------

class Plan(object):
    __slots__ = ('genes', 'mode', 'q', 'bb', 'pend', 'dirty', 'done', 'lastpre')

    def copy(self):
        p = Plan.__new__(Plan)
        p.genes = self.genes
        p.mode = self.mode
        p.q = [self.q[0][:], self.q[1][:], self.q[2][:]]
        p.bb = self.bb
        p.pend = self.pend
        p.dirty = self.dirty
        p.done = self.done
        p.lastpre = self.lastpre
        return p


def live_genes(G, plan, claims, rnd, side):
    mp = G.mp
    out = []
    done = plan.done
    for i, g in enumerate(plan.genes):
        k = g[0]
        if k == 'R' or k == 'M':
            c = g[1]
            if claims[c] == -1 and rnd < mp.c_deadline[c]:
                out.append(g)
        elif k == 'S':
            if i not in done:
                out.append(g)
        elif k == 'B':
            if plan.bb and len(side.boats) <= 2:
                out.append(g)
    return tuple(out)


def decode(G, genes, mode, side, stocks, claims, rnd):
    mp = G.mp
    dist = mp.dist
    roles = mp.roles
    c_good = mp.c_good
    c_dest = mp.c_dest
    c_dl = mp.c_deadline
    boats = side.boats
    nb = len(boats)
    pos = []
    tt = []
    cg = []
    for boat in boats:
        if boat[2] != 0:
            pos.append(boat[1])
            tt.append(rnd + boat[2])
        else:
            pos.append(boat[0])
            tt.append(rnd)
        cg.append([boat[3], boat[4], boat[5]])
    whp = side.wh[:]
    wsp = side.ws[:]
    stp = stocks[:]
    jobs = side.jobs
    q = [[], [], []]
    mav = []
    jfree = [rnd] * 10
    for s in range(10):
        for _ in range(whp[s * 3 + 2]):
            mav.append((s, rnd))
        if jobs[s]:
            mav.append((s, rnd + jobs[s]))
            jfree[s] = rnd + jobs[s]
    home = side.home
    h3 = home * 3
    bb = False
    r4 = rnd // 4
    mfg = G.mfg

    def find_src(g, m, frm, t0, to, forced, excl):
        """Best single place to get m units of g on the way frm -> to. Returns (d, site, isload, amount)."""
        best = None
        bd = 1000000
        part = None
        pa = 0
        pd = 1000000
        for s in range(10):
            if s == excl or (forced >= 0 and s != forced):
                continue
            d1 = dist[frm][s]
            dd = d1 + dist[s][to]
            have = whp[s * 3 + g]
            isload = True
            if have < m:
                if roles[s] == g:
                    a = stp[s] + ((t0 + d1) // 4 - r4)
                    if a > 6:
                        a = 6
                    if a > have:
                        have = a
                        isload = False
            if have >= m:
                if dd < bd:
                    bd = dd
                    best = (dd, s, isload, m)
            elif have > 0:
                if have > pa or (have == pa and dd < pd):
                    pa = have
                    pd = dd
                    part = (dd, s, isload, have)
        return best if best is not None else part

    def take(s, g, isload, amount):
        if isload:
            whp[s * 3 + g] -= amount
        else:
            stp[s] -= amount

    def plan_trip(w, nT, nF, fill, bhint, excl_boat, gi):
        """One haul trip to w. Returns (boat, dT, dF) delivered, or None."""
        best = None
        for b in range(nb):
            if b == excl_boat or (bhint >= 0 and bhint < nb and b != bhint):
                continue
            c = cg[b]
            uT = c[0] if c[0] < nT else nT
            uF = c[1] if c[1] < nF else nF
            if uT < 0:
                uT = 0
            if uF < 0:
                uF = 0
            free = 3 - (c[0] + c[1] + c[2])
            for variant in (0, 1):
                if variant == 0:
                    aT = max(0, min(nT - uT, free))
                    aF = max(0, min(nF - uF, free - aT))
                else:
                    aF = max(0, min(nF - uF, free))
                    aT = max(0, min(nT - uT, free - aF))
                    if aT + aF >= free or (nT - uT <= free and nF - uF <= free - aT):
                        if not (nT - uT + nF - uF > free):
                            continue
                if fill:
                    extra = free - aT - aF
                    if extra > 0:
                        if aT > 0 or aF == 0:
                            aT += extra
                        else:
                            aF += extra
                if aT + aF + uT + uF == 0:
                    continue
                p0 = pos[b]
                t0 = tt[b]
                # route options
                if aT > 0 and aF > 0:
                    opts = []
                    sT = find_src(0, aT, p0, t0, w, -1, w)
                    if sT is not None:
                        sF = find_src(1, aF, sT[1], t0 + dist[p0][sT[1]] + 1, w, -1, w)
                        if sF is not None:
                            opts.append((t0 + dist[p0][sT[1]] + 1 + dist[sT[1]][sF[1]] + 1 + dist[sF[1]][w],
                                         (0, sT), (1, sF)))
                    sF = find_src(1, aF, p0, t0, w, -1, w)
                    if sF is not None:
                        sT = find_src(0, aT, sF[1], t0 + dist[p0][sF[1]] + 1, w, -1, w)
                        if sT is not None:
                            opts.append((t0 + dist[p0][sF[1]] + 1 + dist[sF[1]][sT[1]] + 1 + dist[sT[1]][w],
                                         (1, sF), (0, sT)))
                    if not opts:
                        continue
                    opts.sort(key=lambda o: o[0])
                    arr, s1, s2 = opts[0]
                    picks = [s1, s2]
                elif aT > 0 or aF > 0:
                    g = 0 if aT > 0 else 1
                    sS = find_src(g, aT if g == 0 else aF, p0, t0, w, -1, w)
                    if sS is None:
                        if uT + uF == 0:
                            continue
                        picks = []
                        arr = t0 + dist[p0][w]
                    else:
                        arr = t0 + dist[p0][sS[1]] + 1 + dist[sS[1]][w]
                        picks = [(g, sS)]
                else:
                    picks = []
                    arr = t0 + dist[p0][w]
                dT = uT
                dF = uF
                for g, sS in picks:
                    if g == 0:
                        dT += sS[3]
                    else:
                        dF += sS[3]
                if fill:
                    dT = c[0] + (dT - uT)
                    dF = c[1] + (dF - uF)
                fin = arr + (1 if dT > 0 else 0) + (1 if dF > 0 else 0)
                usefulT = dT if dT < nT else nT
                usefulF = dF if dF < nF else nF
                if usefulT + usefulF <= 0:
                    continue
                key = fin - 0.01 * (dT + dF)
                if best is None or key < best[0]:
                    best = (key, b, picks, dT, dF, fin)
        if best is None:
            return None
        _, b, picks, dT, dF, fin = best
        qb = q[b]
        c = cg[b]
        for g, sS in picks:
            take(sS[1], g, sS[2], sS[3])
            qb.append((T_L if sS[2] else T_G, sS[1], g, sS[3], -1, gi))
            c[g] += sS[3]
        if dT > 0:
            qb.append((T_U, w, 0, dT, -1, gi))
            c[0] -= dT
            whp[w * 3] += dT
        if dF > 0:
            qb.append((T_U, w, 1, dF, -1, gi))
            c[1] -= dF
            whp[w * 3 + 1] += dF
        pos[b] = w
        tt[b] = fin
        return (b, dT, dF)

    def courier(c, gi, chint):
        """Assign delivery of one manufactured good to contract c. Returns est. finish or None."""
        dest = c_dest[c]
        best = None
        for b in range(nb):
            if chint >= 0 and chint < nb and b != chint:
                continue
            cb = cg[b]
            if cb[2] > 0:
                cost = tt[b] + dist[pos[b]][dest] + 1
                if best is None or cost < best[0]:
                    best = (cost, b, -1)
            elif cb[0] + cb[1] + cb[2] < 3:
                for i in range(len(mav)):
                    s, ready = mav[i]
                    t = tt[b] + dist[pos[b]][s]
                    if t < ready:
                        t = ready
                    cost = t + 1 + dist[s][dest] + 1
                    if best is None or cost < best[0]:
                        best = (cost, b, i)
        if best is None and chint >= 0:
            return courier(c, gi, -1)
        if best is None or best[0] - 1 >= c_dl[c]:
            return None
        cost, b, i = best
        if i >= 0:
            s = mav[i][0]
            del mav[i]
            q[b].append((T_L, s, 2, 1, -1, gi))
        else:
            cg[b][2] -= 1
        q[b].append((T_D, dest, 2, 1, c, gi))
        pos[b] = dest
        tt[b] = cost
        return cost

    for gi in range(len(genes)):
        gene = genes[gi]
        k = gene[0]
        if k == 'B':
            if nb <= 2 and not bb and whp[h3] >= 4 and whp[h3 + 1] >= 2:
                bb = True
                whp[h3] -= 4
                whp[h3 + 1] -= 2
                pos.append(home)
                tt.append(rnd + 1)
                cg.append([0, 0, 0])
                nb += 1
        elif k == 'R':
            c = gene[1]
            if claims[c] != -1:
                continue
            g = c_good[c]
            dest = c_dest[c]
            src = gene[2]
            bh = gene[3]
            best = None
            for b in range(nb):
                if bh >= 0 and bh < nb and b != bh:
                    continue
                cb = cg[b]
                have = cb[g]
                if have >= 2:
                    cost = tt[b] + dist[pos[b]][dest] + 1
                    if best is None or cost < best[0]:
                        best = (cost, b, None)
                else:
                    m = 2 - have
                    if 3 - (cb[0] + cb[1] + cb[2]) < m:
                        continue
                    sS = find_src(g, m, pos[b], tt[b], dest, src, -1)
                    if sS is None and src >= 0:
                        sS = find_src(g, m, pos[b], tt[b], dest, -1, -1)
                    if sS is None or sS[3] < m:
                        continue
                    cost = tt[b] + sS[0] + 2
                    if best is None or cost < best[0]:
                        best = (cost, b, sS)
            if best is None or best[0] - 1 >= c_dl[c]:
                continue
            cost, b, sS = best
            if sS is not None:
                take(sS[1], g, sS[2], sS[3])
                q[b].append((T_L if sS[2] else T_G, sS[1], g, sS[3], -1, gi))
                cg[b][g] += sS[3]
            q[b].append((T_D, dest, g, 2, c, gi))
            cg[b][g] -= 2
            pos[b] = dest
            tt[b] = cost
        elif k == 'M':
            c = gene[1]
            if claims[c] != -1:
                continue
            have_m = len(mav) > 0
            if not have_m:
                for b in range(nb):
                    if cg[b][2] > 0:
                        have_m = True
            if have_m:
                if courier(c, gi, gene[5]) is not None:
                    continue
                continue
            w = gene[2]
            if w < 0:
                w = mfg[0]
                for s in mfg:
                    if wsp[s]:
                        w = s
            pat = gene[3]
            bh = gene[4]
            # snapshot
            snap = (pos[:], tt[:], [x[:] for x in cg], whp[:], wsp[:], stp[:], [len(x) for x in q], mav[:],
                    jfree[:])
            w3 = w * 3
            build = 0 if wsp[w] else 1
            nT = 2 * (1 + build) - whp[w3]
            nF = (1 + build) - whp[w3 + 1]
            last = -1
            ok = True
            guard = 0
            excl = -1
            if pat == 2 and nT > 0 and nF > 0 and nb >= 2:
                r = plan_trip(w, nT, 0, True, bh, -1, gi)
                if r is not None:
                    last = r[0]
                    excl = r[0]
                    nT -= r[1]
                    nF -= r[2]
                    r = plan_trip(w, 0, nF, True, -1, excl, gi)
                    if r is not None:
                        if tt[r[0]] >= tt[last]:
                            last = r[0]
                        nT -= r[1]
                        nF -= r[2]
            while (nT > 0 or nF > 0) and guard < 4:
                guard += 1
                r = plan_trip(w, nT if nT > 0 else 0, nF if nF > 0 else 0, pat >= 1,
                              bh if guard == 1 else -1, -1, gi)
                if r is None:
                    ok = False
                    break
                if last < 0 or tt[r[0]] >= tt[last]:
                    last = r[0]
                nT -= r[1]
                nF -= r[2]
            if nT > 0 or nF > 0:
                ok = False
            if ok:
                if last < 0:
                    # materials already there: nearest boat crafts
                    bc = None
                    for b in range(nb):
                        if bh >= 0 and bh < nb and b != bh:
                            continue
                        cost = tt[b] + dist[pos[b]][w]
                        if bc is None or cost < bc[0]:
                            bc = (cost, b)
                    last = bc[1]
                    tt[last] = bc[0]
                    pos[last] = w
                tc = tt[last]
                if jfree[w] > tc:
                    tc = jfree[w]
                tc += build
                q[last].append((T_C, w, -1, 0, -1, gi))
                whp[w3] -= 2 * (1 + build)
                whp[w3 + 1] -= (1 + build)
                wsp[w] = True
                tt[last] = tc + 1
                jfree[w] = tc + 3
                mav.append((w, tc + 3))
                if courier(c, gi, gene[5]) is None:
                    ok = False
            if not ok:
                pos, tt, cg, whp, wsp, stp, ql, mav, jfree = snap
                pos = pos[:]
                for b in range(3):
                    del q[b][ql[b]:]
        elif k == 'S':
            w = gene[1]
            g = gene[2]
            if not wsp[w]:
                continue
            if g == 0:
                plan_trip(w, 3, 0, True, gene[4], -1, gi)
            else:
                plan_trip(w, 0, 3, True, gene[4], -1, gi)
    p = Plan.__new__(Plan)
    p.genes = genes
    p.mode = mode
    p.q = q
    p.bb = bb
    p.pend = None
    p.dirty = False
    p.done = frozenset()
    p.lastpre = False
    return p


def _craft_pending(plan, site):
    for qb in plan.q:
        for t in qb:
            if t[0] == T_C and t[1] == site:
                return True
    return False


def next_order(G, plan, b, boat, side, stocks, claims, rnd):
    """(order, pop) for docked boat b, or None when blocked / nothing to do."""
    mp = G.mp
    qb = plan.q[b]
    nxt = mp.nxt
    pos = boat[0]
    while qb:
        task = qb[0]
        kind = task[0]
        site = task[1]
        if kind == T_D:
            c = task[4]
            if claims[c] != -1 or rnd >= mp.c_deadline[c] or boat[3 + task[2]] < task[3]:
                qb.pop(0)
                plan.dirty = True
                continue
            if pos != site:
                return (o_sail(b, nxt[pos][site]), False)
            return (o_deliver(b, c), True)
        if kind == T_U:
            g = task[2]
            have = boat[3 + g]
            if have == 0:
                qb.pop(0)
                continue
            if pos != site:
                return (o_sail(b, nxt[pos][site]), False)
            qn = task[3]
            if qn == 0 or qn > have:
                qn = have
            return (o_unload(b, g, qn), True)
        if kind == T_G:
            g = task[2]
            free = 3 - (boat[3] + boat[4] + boat[5])
            if free <= 0:
                qb.pop(0)
                plan.dirty = True
                continue
            if pos != site:
                return (o_sail(b, nxt[pos][site]), False)
            want = task[3] if task[3] < free else free
            st = stocks[site]
            if st >= want:
                return (o_gather(b, g, want), True)
            plan.dirty = True
            if st > 0:
                return (o_gather(b, g, st), True)
            qb.pop(0)
            continue
        if kind == T_L:
            g = task[2]
            free = 3 - (boat[3] + boat[4] + boat[5])
            if free <= 0:
                qb.pop(0)
                plan.dirty = True
                continue
            if pos != site:
                return (o_sail(b, nxt[pos][site]), False)
            want = task[3] if task[3] < free else free
            have = side.wh[site * 3 + g]
            if have >= want:
                return (o_load(b, g, want), True)
            if g == 2:
                if side.jobs[site] > 0 or _craft_pending(plan, site):
                    return None
                qb.pop(0)
                plan.dirty = True
                continue
            plan.dirty = True
            if have > 0:
                return (o_load(b, g, have), True)
            qb.pop(0)
            continue
        if kind == T_C:
            if pos != site:
                return (o_sail(b, nxt[pos][site]), False)
            w3 = site * 3
            wh = side.wh
            if not side.ws[site]:
                if wh[w3] >= 2 and wh[w3 + 1] >= 1:
                    return (o_build_workshop(b), False)
                return None
            if side.jobs[site] == 0 and wh[w3] >= 2 and wh[w3 + 1] >= 1:
                return (o_craft(b), True)
            return None
        qb.pop(0)
    return None


def _reach(G, plan, boats, x, k, rnd):
    """Earliest round at which boat x can start task k of its queue (action slot ignored)."""
    dist = G.mp.dist
    boat = boats[x]
    qx = plan.q[x]
    if boat[2] != 0:
        t = rnd + boat[2]
        pos = boat[1]
    else:
        t = rnd
        pos = boat[0]
    for i in range(k):
        site = qx[i][1]
        t += dist[pos][site] + 1
        pos = site
    return t + dist[pos][qx[k][1]]


def _deferrable(G, plan, side, b, rnd):
    """True when boat b is only sailing towards something that cannot be ready when it arrives."""
    task = plan.q[b][0]
    kind = task[0]
    site = task[1]
    boats = side.boats
    if kind == T_L and task[2] == 2:
        if side.wh[site * 3 + 2] > 0:
            return False
        if side.jobs[site] > 0:
            ready = rnd + side.jobs[site]
        else:
            ready = -1
            for x in range(len(boats)):
                qx = plan.q[x]
                for k in range(len(qx)):
                    t = qx[k]
                    if t[0] == T_C and t[1] == site:
                        r = _reach(G, plan, boats, x, k, rnd) + 4 + (0 if side.ws[site] else 1)
                        if ready < 0 or r < ready:
                            ready = r
                        break
            if ready < 0:
                return False
        return ready - (rnd + G.mp.dist[boats[b][0]][site]) >= 2
    if kind == T_C:
        w3 = site * 3
        if side.wh[w3] >= 2 and side.wh[w3 + 1] >= 1:
            return False
        ready = -1
        for x in range(len(boats)):
            if x == b:
                continue
            qx = plan.q[x]
            for k in range(len(qx)):
                t = qx[k]
                if t[0] == T_U and t[1] == site:
                    r = _reach(G, plan, boats, x, k, rnd) + 1
                    if ready < 0 or r < ready:
                        ready = r
                    break
        if ready < 0:
            return False
        return ready - (rnd + G.mp.dist[boats[b][0]][site]) >= 2
    return False


def plan_act(G, plan, side, stocks, claims, rnd):
    """Our order for this round (always legal on the given state). Mutates the plan's queues."""
    mp = G.mp
    boats = side.boats
    pend = plan.pend
    if pend is not None:
        plan.pend = None
        b, task, before = pend
        if boats[b][3 + task[2]] == before:
            plan.q[b].insert(0, task)
    if plan.dirty:
        np = decode(G, live_genes(G, plan, claims, rnd, side), plan.mode, side, stocks, claims, rnd)
        plan.genes = np.genes
        plan.q = np.q
        plan.bb = np.bb
        plan.done = np.done
        plan.dirty = False
    if plan.bb:
        plan.bb = False
        h3 = side.home * 3
        if len(boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2:
            return BUILD_BOAT
    nb = len(boats)
    cands = None
    for _attempt in range(8):
        cands = []
        blocked = -1
        sailing = False
        for b in range(nb):
            boat = boats[b]
            if boat[2] != 0:
                sailing = True
                continue
            if not plan.q[b]:
                continue
            r = next_order(G, plan, b, boat, side, stocks, claims, rnd)
            if r is None:
                if plan.q[b] and blocked < 0:
                    blocked = b
                continue
            cands.append((b, r[0], r[1]))
        if cands:
            break
        if blocked < 0 or sailing:
            return WAIT
        busy = False
        for j in side.jobs:
            if j:
                busy = True
        if busy:
            return WAIT
        plan.q[blocked].pop(0)
        plan.dirty = True
    if not cands:
        return WAIT
    q = plan.q
    ch = None
    for cd in cands:
        if cd[1][0] == 'deliver':
            if ch is None or mp.c_points[cd[1][5]] > mp.c_points[ch[1][5]]:
                ch = cd
    if ch is None:
        if len(cands) > 1:
            keep = [cd for cd in cands if not (cd[1][0] == 'sail' and _deferrable(G, plan, side, cd[0], rnd))]
            if keep:
                cands = keep
        lo = None
        lop = 0
        for cd in cands:
            pr = q[cd[0]][0][5]
            if lo is None or pr < lop:
                lo = cd
                lop = pr
        ch = lo
        pre = False
        if plan.mode == 0 and not plan.lastpre:
            o = lo[1]
            if not (o[0] == 'sail' and mp.routes[boats[lo[0]][0]][o[2]] >= 2):
                ls = None
                lsp = 0
                for cd in cands:
                    o = cd[1]
                    if o[0] == 'sail' and mp.routes[boats[cd[0]][0]][o[2]] >= 2:
                        pr = q[cd[0]][0][5]
                        if ls is None or pr < lsp:
                            ls = cd
                            lsp = pr
                if ls is not None:
                    ch = ls
                    pre = True
        plan.lastpre = pre
    b, o, pop = ch
    if pop:
        task = q[b].pop(0)
        if o[0] == 'gather':
            plan.pend = (b, task, boats[b][3 + task[2]])
        elif task[0] == T_U:
            gi = task[5]
            if gi < len(plan.genes) and plan.genes[gi][0] == 'S':
                plan.done = plan.done | frozenset((gi,))
    return o


# ---------------------------------------------------------------------------------------------
# Rollouts
# ---------------------------------------------------------------------------------------------

_DL_ROUNDS = frozenset((24, 40, 56, 72))


def _any_open(mp, claims, rnd):
    dl = mp.c_deadline
    for c in range(mp.ncontracts):
        if claims[c] == -1 and rnd < dl[c]:
            return True
    return False


def exact_rollout(G, hyp, plan, tlimit):
    """Exact game to the end against hypothesis `hyp`. Returns None when aborted on time, else
    (margin, us, them, tempo, pc, pg). Stops as soon as no contract is left."""
    eng = clone_engine(hyp.eng)
    prof = hyp.prof0.clone()
    seat = G.seat
    pseat = 1 - seat
    mp = G.mp
    us = eng.sides[seat]
    them = eng.sides[pseat]
    pc = []
    pg = []
    tempo = 0
    plan = plan.copy() if plan is not None else None
    stocks = eng.stocks
    claims = eng.claims
    orders = [None, None]
    if not _any_open(mp, claims, eng.round):
        return (us.score - them.score, us.score, them.score, 0, pc, pg)
    while eng.round < 80:
        po = prof_choose(G, prof, eng, tlimit)
        if po is None:
            return None
        r = eng.round
        mo = plan_act(G, plan, us, stocks, claims, r) if plan is not None else WAIT
        orders[seat] = mo
        orders[pseat] = po
        s0 = us.score
        p0 = them.score
        ok = eng.step(orders)
        ch = False
        if us.score != s0:
            tempo += (us.score - s0) * (80 - r)
            ch = True
        if them.score != p0:
            pc.append((r, po[5]))
            ch = True
        elif po[0] == 'gather' and ok[pseat]:
            pg.append((r, them.boats[po[1]][0], po[4]))
        if ch or eng.round in _DL_ROUNDS:
            if not _any_open(mp, claims, eng.round):
                break
    return (us.score - them.score, us.score, them.score, tempo, pc, pg)


def phantom_rollout(G, hyp, plan, pc, pg):
    """Cheap estimate: our side simulated exactly, the Professor replaced by a reference claim
    schedule `pc` and gather list `pg` (from an exact rollout of a similar plan) with a simple
    redirect rule for goods whose contract we took first."""
    eng = hyp.eng
    mp = G.mp
    seat = G.seat
    pseat = 1 - seat
    side = copy_side(eng.sides[seat])
    stocks = eng.stocks[:]
    claims = eng.claims[:]
    rnd = eng.round
    pscore = eng.sides[pseat].score
    npc = len(pc)
    npg = len(pg)
    ic = 0
    ig = 0
    while ic < npc and pc[ic][0] < rnd:
        ic += 1
    while ig < npg and pg[ig][0] < rnd:
        ig += 1
    spares = None
    plan = plan.copy()
    c_points = mp.c_points
    c_good = mp.c_good
    c_dest = mp.c_dest
    c_dl = mp.c_deadline
    dist = mp.dist
    roles = mp.roles
    raws = G.raws
    tempo = 0
    q = plan.q
    for t in range(rnd, 80):
        if q[0] or q[1] or q[2] or plan.bb or plan.dirty or plan.pend is not None:
            o = plan_act(G, plan, side, stocks, claims, t)
            q = plan.q
        else:
            o = WAIT
        first = (t % 2 == seat)
        s0 = side.score
        ch = False
        if first and o is not WAIT:
            apply_order(mp, side, stocks, claims, seat, o, None)
        while ig < npg and pg[ig][0] == t:
            e = pg[ig]
            ig += 1
            if stocks[e[1]] >= e[2]:
                stocks[e[1]] -= e[2]
        while ic < npc and pc[ic][0] == t:
            c = pc[ic][1]
            ic += 1
            ch = True
            if claims[c] == -1:
                claims[c] = pseat
                pscore += c_points[c]
            else:
                if spares is None:
                    spares = []
                spares.append((t, c_good[c], c_dest[c]))
        if spares:
            i = 0
            while i < len(spares):
                t0, g, frm = spares[i]
                hit = -1
                for c in range(8):
                    if (claims[c] == -1 and c_good[c] == g and t < c_dl[c]
                            and t >= t0 + dist[frm][c_dest[c]] + 1):
                        hit = c
                        break
                if hit >= 0:
                    claims[hit] = pseat
                    pscore += c_points[hit]
                    del spares[i]
                    ch = True
                else:
                    i += 1
        if not first and o is not WAIT:
            if o[0] == 'gather':
                if stocks[side.boats[o[1]][0]] >= o[4]:
                    apply_order(mp, side, stocks, claims, seat, o, None)
            else:
                apply_order(mp, side, stocks, claims, seat, o, None)
        if side.score != s0:
            tempo += (side.score - s0) * (80 - t)
            ch = True
        advance_side(side)
        t1 = t + 1
        if (t1 & 3) == 0:
            for s in raws:
                if stocks[s] < 6:
                    stocks[s] += 1
        if ch or t1 in _DL_ROUNDS:
            if not _any_open(mp, claims, t1):
                break
    return (side.score - pscore, side.score, pscore, tempo)


def value_of(res):
    """Aggregate per-hypothesis results (margin, us, them, tempo, ...) into one number."""
    n = len(res)
    w = 0.0
    mn = 1000
    sm = 0.0
    tp = 0.0
    for r in res:
        m = r[0]
        if m > 0:
            w += 1.0
        elif m == 0:
            w += 0.5
        if m < mn:
            mn = m
        sm += m
        tp += r[3]
    return 1000.0 * w / n + mn + 0.02 * sm / n + 0.0004 * tp / n


class Cand(object):
    """A plan with its exact evaluation: per-hypothesis results and the Professor's exact
    reaction (claim schedule + gathers), which anchors the phantom fitness of its children."""
    __slots__ = ('v', 'genome', 'plan', 'styles', 'res')


def make_cand(G, genome, plan, res):
    c = Cand()
    c.genome = genome
    c.plan = plan
    c.styles = [h.style for h in G.hyps]
    c.res = res
    c.v = value_of(res)
    return c


def exact_eval(G, plan, tlimit):
    res = []
    for h in G.hyps:
        r = exact_rollout(G, h, plan, tlimit)
        if r is None:
            return None
        res.append(r)
    return res


def phantom_eval(G, plan, parent, bound):
    """Phantom value against the parent's exact Professor trajectories. Hardest hypothesis first;
    gives up (None) as soon as the value cannot exceed `bound`."""
    hy = G.hyps
    n = len(hy)
    pres = parent.res
    order = sorted(range(n), key=lambda i: pres[i][0])
    w = 0.0
    mn = 1000
    sm = 0.0
    tp = 0.0
    for k in range(n):
        i = order[k]
        pr = pres[i]
        r = phantom_rollout(G, hy[i], plan, pr[4], pr[5])
        m = r[0]
        if m > 0:
            w += 1.0
        elif m == 0:
            w += 0.5
        if m < mn:
            mn = m
        sm += m
        tp += r[3]
        rem = n - k - 1
        if rem and bound is not None:
            ub = 1000.0 * (w + rem) / n + mn + 0.02 * (sm + 68 * rem) / n + 0.0004 * (tp + 5440 * rem) / n
            if ub <= bound:
                return None
    return 1000.0 * w / n + mn + 0.02 * sm / n + 0.0004 * tp / n



# ---------------------------------------------------------------------------------------------
# Genome operators
# ---------------------------------------------------------------------------------------------

def seed_genomes(G, side, claims, rnd):
    mp = G.mp
    mfg = G.mfg
    openc = [c for c in range(8) if claims[c] == -1 and rnd < mp.c_deadline[c]]
    raws = [c for c in openc if c < 4]
    ms = [c for c in openc if c >= 4]
    h3 = side.home * 3
    can_boat = len(side.boats) <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2
    out = []
    for w in mfg:
        for pat in (0, 1, 2):
            mg = [('M', c, w, pat, -1, -1) for c in ms]
            rg = [('R', c, -1, -1) for c in raws]
            orders = [
                mg + rg,
                rg + mg,
                rg[:1] + mg + rg[1:],
                rg[:2] + mg + rg[2:],
                mg[:1] + rg[:2] + mg[1:] + rg[2:],
                mg[:1] + rg[:1] + mg[1:2] + rg[1:2] + mg[2:3] + rg[2:3] + mg[3:] + rg[3:],
                mg[:2] + rg + mg[2:],
                mg,
            ]
            for o in orders:
                out.append((tuple(o), 0))
                if can_boat:
                    out.append(((('B',),) + tuple(o), 0))
    return out


def mutate(G, genome, rng, side, claims, rnd):
    mp = G.mp
    genes = list(genome[0])
    mode = genome[1]
    n = len(genes)
    op = rng.randrange(10)
    nb = len(side.boats)
    if op == 0 and n >= 2:
        i = rng.randrange(n)
        j = rng.randrange(n)
        genes[i], genes[j] = genes[j], genes[i]
    elif op == 1 and n >= 2:
        i = rng.randrange(n)
        g = genes.pop(i)
        genes.insert(rng.randrange(n), g)
    elif op == 2 and n >= 1:
        genes.pop(rng.randrange(n))
    elif op == 3 or op == 4:
        present = set(g[1] for g in genes if g[0] in ('R', 'M'))
        cand = [c for c in range(8) if c not in present and claims[c] == -1 and rnd < mp.c_deadline[c]]
        if cand:
            c = rng.choice(cand)
            if c < 4:
                g = ('R', c, -1, -1)
            else:
                g = ('M', c, rng.choice(G.mfg + [-1]), rng.randrange(3), -1, -1)
            genes.insert(rng.randrange(n + 1), g)
        elif n >= 2:
            i = rng.randrange(n)
            g = genes.pop(i)
            genes.insert(rng.randrange(n), g)
    elif op == 5 or op == 6:
        if n:
            i = rng.randrange(n)
            g = genes[i]
            if g[0] == 'R':
                if rng.random() < 0.5:
                    srcs = [s for s in range(10) if mp.roles[s] == mp.c_good[g[1]]] + [side.home, -1]
                    genes[i] = ('R', g[1], rng.choice(srcs), g[3])
                else:
                    genes[i] = ('R', g[1], g[2], rng.randrange(-1, 3))
            elif g[0] == 'M':
                r = rng.randrange(4)
                if r == 0:
                    w = rng.choice(G.mfg)
                    # move every later M gene to the same workshop too (half the time)
                    genes[i] = ('M', g[1], w, g[3], g[4], g[5])
                    if rng.random() < 0.5:
                        for j in range(n):
                            h = genes[j]
                            if h[0] == 'M':
                                genes[j] = ('M', h[1], w, h[3], h[4], h[5])
                elif r == 1:
                    genes[i] = ('M', g[1], g[2], rng.randrange(3), g[4], g[5])
                elif r == 2:
                    genes[i] = ('M', g[1], g[2], g[3], rng.randrange(-1, 3), g[5])
                else:
                    genes[i] = ('M', g[1], g[2], g[3], g[4], rng.randrange(-1, 3))
            elif g[0] == 'S':
                genes[i] = ('S', g[1], rng.randrange(2), -1, rng.randrange(-1, 3))
    elif op == 7:
        ws = [g[2] for g in genes if g[0] == 'M' and g[2] >= 0]
        w = rng.choice(ws) if ws else rng.choice(G.mfg)
        genes.insert(rng.randrange(n + 1), ('S', w, rng.randrange(2), -1, -1))
    elif op == 8:
        if genes and genes[0][0] == 'B':
            genes.pop(0)
        else:
            h3 = side.home * 3
            if nb <= 2 and side.wh[h3] >= 4 and side.wh[h3 + 1] >= 2:
                genes.insert(0, ('B',))
            elif n >= 2:
                i = rng.randrange(n - 1)
                genes[i], genes[i + 1] = genes[i + 1], genes[i]
    else:
        mode = 1 - mode
    return (tuple(genes), mode)


def crossover(a, b, rng):
    ga = a[0]
    gb = b[0]
    if not ga or not gb:
        return a
    cut = rng.randrange(1, len(ga) + 1)
    head = list(ga[:cut])
    have = set(g[1] for g in head if g[0] in ('R', 'M'))
    hasb = any(g[0] == 'B' for g in head)
    for g in gb:
        if g[0] in ('R', 'M'):
            if g[1] not in have:
                head.append(g)
                have.add(g[1])
        elif g[0] == 'B':
            if not hasb:
                head.insert(0, g)
                hasb = True
    return (tuple(head), a[1] if rng.random() < 0.5 else b[1])


# ---------------------------------------------------------------------------------------------
# Tracking and the main decision
# ---------------------------------------------------------------------------------------------

def obs_matches(obs, eng, seat):
    if obs['claims'] != eng.claims:
        return False
    side = eng.sides[seat]
    other = eng.sides[1 - seat]
    if obs['opponent_score'] != other.score:
        return False
    own = obs['own']
    if own['score'] != side.score:
        return False
    ob = own['boats']
    if len(ob) != len(side.boats):
        return False
    vis = [False] * 10
    vis[side.home] = True
    for s in range(10):
        if side.ws[s]:
            vis[s] = True
    for i, b in enumerate(side.boats):
        o = ob[i]
        if o['position'] != b[0] or o['destination'] != b[1] or o['eta'] != b[2] or o['cargo'] != b[3:6]:
            return False
        if b[2] == 0:
            vis[b[0]] = True
    wh = own['warehouses']
    for s in range(10):
        if wh[s] != side.wh[3 * s:3 * s + 3]:
            return False
        if bool(own['workshops'][s]) != bool(side.ws[s]):
            return False
        if own['jobs'][s] != side.jobs[s]:
            return False
    st = obs['stocks']
    for s in range(10):
        if vis[s]:
            if st[s] != eng.stocks[s]:
                return False
    enemy = sorted((i, b[0], b[1], b[2]) for i, b in enumerate(other.boats)
                   if vis[b[0]] or (b[1] >= 0 and vis[b[1]]))
    real = sorted((b['boat'], b['position'], b['destination'], b['eta']) for b in obs['enemy_boats'])
    return enemy == real


def engine_from_obs(obs, mp, seat):
    """Fallback state when no hypothesis survives: our side from the observation, dummy opponent."""
    eng = Engine(mp)
    eng.round = obs['round']
    own = obs['own']
    side = eng.sides[seat]
    side.score = own['score']
    side.crafted = own['crafted_deliveries']
    side.boats = [[b['position'], b['destination'], b['eta']] + list(b['cargo']) for b in own['boats']]
    side.wh = [x for row in own['warehouses'] for x in row]
    side.ws = [bool(x) for x in own['workshops']]
    side.jobs = list(own['jobs'])
    eng.sides[1 - seat].score = obs['opponent_score']
    eng.stocks = [(s if s is not None else (4 if mp.roles[i] in (0, 1) else 0)) for i, s in enumerate(obs['stocks'])]
    eng.claims = list(obs['claims'])
    return eng


def new_game(obs):
    G = Game()
    G.mp = Map(obs['map'])
    G.seat = obs['seat']
    G.mfg = [s for s in range(10) if G.mp.roles[s] == 2]
    G.cache = {}
    G.nrep = 0
    G.hyps = []
    for st in range(5):
        h = Hyp()
        h.style = st
        h.eng = Engine(G.mp)
        h.prof = new_professor(st, 1 - G.seat)
        h.pc = []
        h.pg = []
        G.hyps.append(h)
    G.plan = None
    G.inc = None             # Cand: the incumbent plan with its exact evaluation
    G.raws = [s for s in range(10) if G.mp.roles[s] in (0, 1)]
    G.elites = []            # genomes carried to the next round
    G.used = 0.0             # CPU seconds used this game
    G.wused = 0.0            # wall seconds used this game
    G.rng = _random.Random(12345)
    G.fb = None
    G.log = []
    G.first = (_PROCESS_GAMES[0] == 0)
    _PROCESS_GAMES[0] += 1
    G.total = (PARAMS['total'] + (PARAMS['first_extra'] if G.first else 0.0)) * PARAMS['scale']
    G.stats = dict(ph=0, ex=0, exab=0, sw=0, t0=0.0, ttrack=0.0, tex=0.0, tga=0.0)
    _LASTG[0] = G
    return G


def plan_sig(plan):
    q = plan.q
    return (tuple(q[0]), tuple(q[1]), tuple(q[2]), plan.bb, plan.mode)


def search(G, side, stocks, claims, rnd, tend, pool, genomes, nseed_exact, ex_cap):
    """Surrogate-assisted evolution. `pool` holds exactly evaluated candidates (pool[0] is the
    anchor: the incumbent, or the empty plan at round 0). `genomes` are tried first (seeds, last
    round's elites). A child is scored with the phantom fitness against its parent's exact
    Professor trajectory and promoted to an exact evaluation only when that beats the parent."""
    rng = G.rng
    stats = G.stats
    seen = set()
    seenp = set()
    anchor = pool[0]
    eps = PARAMS['eps']
    for c in pool:
        seen.add(c.genome)
        if c.plan is not None:
            seenp.add(plan_sig(c.plan))

    def promote(genome, plan):
        res = exact_eval(G, plan, _clock() + ex_cap)
        stats['ex'] += 1
        if res is None:
            stats['exab'] += 1
            return None
        c = make_cand(G, genome, plan, res)
        pool.append(c)
        return c

    def consider(genome, parent, bound):
        if genome in seen:
            return None
        seen.add(genome)
        plan = decode(G, genome[0], genome[1], side, stocks, claims, rnd)
        sig = plan_sig(plan)
        if sig in seenp:
            return None
        seenp.add(sig)
        v = phantom_eval(G, plan, parent, bound)
        stats['ph'] += 1
        if v is None:
            return None
        return (v, genome, plan)

    # 1. seeds / carried elites: phantom against the anchor, the best few get an exact evaluation
    if genomes:
        scored = []
        for genome in genomes:
            if _clock() > tend:
                break
            r = consider(genome, anchor, None if nseed_exact else anchor.v + eps)
            if r is not None:
                scored.append(r)
        scored.sort(key=lambda x: -x[0])
        k = nseed_exact if nseed_exact else 2
        for v, genome, plan in scored[:k]:
            if _clock() > tend:
                break
            if v > anchor.v + eps:
                promote(genome, plan)
    # 2. evolution
    nel = PARAMS['elites']
    it = 0
    while _clock() < tend:
        it += 1
        if it > 400 and len(seen) < 3:
            break
        pool.sort(key=lambda c: -c.v)
        k = len(pool) if len(pool) < nel else nel
        pa = pool[min(int(rng.random() * rng.random() * k), k - 1)]
        if pa.plan is None:
            if len(pool) > 1:
                pa = pool[0] if pool[0].plan is not None else pool[1]
            else:
                break
        r = rng.random()
        if r < 0.12 and k >= 2:
            pb = pool[rng.randrange(k)]
            if pb.plan is None or pb is pa:
                continue
            child = crossover(pa.genome, pb.genome, rng)
        else:
            child = mutate(G, pa.genome, rng, side, claims, rnd)
            if r > 0.6:
                child = mutate(G, child, rng, side, claims, rnd)
                if r > 0.9:
                    child = mutate(G, child, rng, side, claims, rnd)
        res = consider(child, pa, pa.v + eps)
        if res is None or res[0] <= pa.v + eps:
            continue
        promote(res[1], res[2])
    pool.sort(key=lambda c: -c.v)
    return pool


def filter_cand(G, cand):
    """Drop the results of dead hypotheses from the incumbent's stored evaluation."""
    alive = [h.style for h in G.hyps]
    if cand.styles == alive:
        return True
    res = []
    for st in alive:
        if st not in cand.styles:
            return False
        res.append(cand.res[cand.styles.index(st)])
    cand.styles = alive
    cand.res = res
    cand.v = value_of(res)
    return True


def brain(obs, memory):
    t_cpu0 = _clock()
    t_wall0 = _wall()
    rnd = obs['round']
    G = memory.get('G')
    if G is None or rnd == 0:
        G = new_game(obs)
        memory['G'] = G
    seat = G.seat
    # ---- tracking -------------------------------------------------------------------------
    if G.hyps:
        G.hyps = [h for h in G.hyps if obs_matches(obs, h.eng, seat)]
    if not G.hyps:
        return fallback_brain(G, obs)
    for h in G.hyps:
        h.prof0 = h.prof.clone()
        h.pred = prof_choose(G, h.prof, h.eng, None)
    eng = G.hyps[0].eng
    side = eng.sides[seat]
    stocks = eng.stocks
    claims = eng.claims
    left = 80 - rnd
    scale = PARAMS['scale']
    budget_ok = (G.wused + (_wall() - t_wall0)) < PARAMS['wall_hard']
    rem = G.total - (G.used + (_clock() - t_cpu0))
    G.stats['ttrack'] += _clock() - t_cpu0
    t1 = _clock()
    if G.inc is None:
        # anchor: the Professor's future when we do nothing
        res = exact_eval(G, None, None)
        G.stats['t0'] = _clock() - t_cpu0
        null = make_cand(G, ((), 0), None, res)
        pool = search(G, side, stocks, claims, rnd, _clock() + PARAMS['ga0'] * scale, [null],
                      seed_genomes(G, side, claims, rnd), 3, 10.0)
        best = pool[0]
        if best.plan is None:
            # nothing verified in time: take the first seed as it is
            g0 = seed_genomes(G, side, claims, rnd)[0]
            p0 = decode(G, g0[0], g0[1], side, stocks, claims, rnd)
            best = make_cand(G, g0, p0, exact_eval(G, p0, None))
        G.inc = best
        G.plan = best.plan
        G.elites = [c.genome for c in pool[1:PARAMS['elites']] if c.plan is not None]
        if PARAMS.get('debug'):
            G.log.append((rnd, None, best.v, len(pool)))
    elif budget_ok and rem > 0.01 * scale and left > 1 and _any_open(G.mp, claims, rnd):
        inc = G.inc
        ok = filter_cand(G, inc)
        if (not ok) or G.plan.dirty or PARAMS.get('paranoid'):
            # the stored evaluation no longer describes the live plan: evaluate it again
            res = exact_eval(G, G.plan, None)
            if PARAMS.get('paranoid') and ok and not G.plan.dirty:
                assert [r[0] for r in res] == [r[0] for r in inc.res], (rnd, [r[0] for r in res], [r[0] for r in inc.res])
            inc = make_cand(G, (live_genes(G, G.plan, claims, rnd, side), G.plan.mode), G.plan, res)
            G.inc = inc
        else:
            inc.genome = (live_genes(G, G.plan, claims, rnd, side), G.plan.mode)
            inc.plan = G.plan
        slice_ = rem / max(4.0, float(left)) * PARAMS['front']
        v0 = inc.v
        extra = []
        tmp = Plan.__new__(Plan)
        for g in G.elites:
            tmp.genes = g[0]
            tmp.done = frozenset()
            tmp.bb = True
            extra.append((live_genes(G, tmp, claims, rnd, side), g[1]))
        pool = search(G, side, stocks, claims, rnd, _clock() + slice_, [inc], extra, 0,
                      max(2.0 * slice_, 0.1 * scale))
        best = pool[0]
        if best is not inc and best.v > v0 + 1e-9:
            G.inc = best
            G.plan = best.plan
            G.stats['sw'] += 1
        G.elites = [c.genome for c in pool[:PARAMS['elites']] if c is not G.inc]
        if PARAMS.get('debug'):
            G.log.append((rnd, v0, G.inc.v, len(pool)))
    G.stats['tga'] += _clock() - t1
    order = plan_act(G, G.plan, side, stocks, claims, rnd)
    act = order_to_json(order)
    if act not in obs['legal_actions']:
        G.plan.dirty = True
        order = WAIT
        act = order_to_json(WAIT)
    for h in G.hyps:
        orders = [None, None]
        orders[seat] = order
        orders[1 - seat] = h.pred
        h.eng.step(orders)
    G.used += _clock() - t_cpu0
    G.wused += _wall() - t_wall0
    return act



def fallback_brain(G, obs):
    """No hypothesis left (should not happen): keep executing the plan on the observed state."""
    seat = G.seat
    eng = engine_from_obs(obs, G.mp, seat)
    side = eng.sides[seat]
    if G.plan is None:
        G.plan = decode(G, seed_genomes(G, side, eng.claims, eng.round)[0][0], 0, side, eng.stocks,
                        eng.claims, eng.round)
    G.plan.pend = None
    G.plan.dirty = True
    order = plan_act(G, G.plan, side, eng.stocks, eng.claims, eng.round)
    act = order_to_json(order)
    if act not in obs['legal_actions']:
        act = obs['legal_actions'][0]
    return act


def agent(observation, memory):
    """Return one entry of observation['legal_actions']. `memory` resets each game."""
    legal = observation['legal_actions']
    try:
        act = brain(observation, memory)
    except Exception:
        if PARAMS.get('debug'):
            raise
        act = None
        try:
            G = memory.get('G')
            if G is not None:
                G.hyps = []
                act = fallback_brain(G, observation)
        except Exception:
            act = None
    if act not in legal:
        act = legal[0]
    return act


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
