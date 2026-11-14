"""Your submission. Upload only this file; keep it self-contained (standard library only).

The evaluator runs `python main.py`, sends one JSON line {"observation": ...} per
decision on stdin and reads one JSON action per line from stdout. Leave the loop
at the bottom as it is and put your strategy in agent().
"""
import json
import sys


# ==========================================================================================
# ../fast/fastcore.py
# ==========================================================================================
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

# ==========================================================================================
# tsched.py
# ==========================================================================================
# ---- sched: one-sided timetable scheduler for our side (one order per round slot) ----

BOAT_TOK = 8
_MAPC = [None, {}, []]          # per-map caches: map object, natural sources by (pos, dest, good), mfg sites


class Sched(object):
    """Timetable under construction. boats[b] = [pos, ready, cT, cF, cM] at the end of b's chain."""
    __slots__ = ('mp', 't0', 'used', 'boats', 'lv', 'base', 'gq', 'crafts', 'ws', 'orders', 'deliv',
                 'home', 'nord', 'el', 'memo')

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
        s.el = self.el[:]               # cached end levels, site * 3 + good
        s.memo = None                   # per-object cache of sub-plans (never copied)
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
        return self.el[s * 3 + g]

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
        self.el[s * 3 + g] += d
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
        if _MAPC[0] is not mp:
            _MAPC[0] = mp
            _MAPC[1] = {}
            _MAPC[2] = [w for w in range(10) if mp.roles[w] == 2]
        cache = _MAPC[1]
        key = (pos * 10 + dest) * 2 + g
        nat = cache.get(key)
        dist = mp.dist
        dp = dist[pos]
        if nat is None:
            nat = []
            roles = mp.roles
            for s in range(10):
                if roles[s] == g:
                    nat.append((dp[s] + dist[s][dest], 1, s, False))
            nat.sort()
            cache[key] = nat
        out = None
        el = self.el
        for s in self.lv:
            if s != skip and el[s * 3 + g] >= q:
                if out is None:
                    out = list(nat)
                out.append((dp[s] + dist[s][dest], 0, s, True))
        if out is None:
            return nat[:limit]
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
        """Best boat for one load. Returns Sched (a new copy) or None. Memoised per object."""
        memo = self.memo
        if memo is None:
            memo = self.memo = {}
        key = (need[0], need[1], w)
        if key in memo:
            return memo[key]
        r = memo[key] = self.haul_(need, w)
        return r

    def haul_(self, need, w):
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
        """Plan one more craft at w (hauls, workshop if missing). Returns Sched or None. Memoised."""
        memo = self.memo
        if memo is None:
            memo = self.memo = {}
        key = (-1, w, B)
        if key in memo:
            return memo[key]
        r = memo[key] = self.ensure_craft_(w, B)
        return r

    def ensure_craft_(self, w, B):
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
                            ((2, 1), (2, 1))]
                if B > 0:
                    loadsets.append(((3, 0), (0, 3), (3, 0)))
                    loadsets.append(((3, 0), (1, 2), (3, 0)))
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
                loadsets = [((nT, 0),), ((3, 0),)] if (B > 0 and nT < 3) else [((nT, 0),)]
            elif nT == 0:
                loadsets = [((0, nF),), ((0, 3),)] if B > 0 else [((0, nF),)]
            elif B > 0:
                loadsets = [((nT, nF),), ((3, 0), (0, 3)), ((0, 3), (3, 0))]
            else:
                loadsets = [((nT, nF),)]
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
        """more = manufactured tokens still to come after this one; ahead = keep one craft in the pipeline
        when that costs the current delivery at most one round."""
        mp = self.mp
        d = mp.c_dest[c]
        best = None
        bc = 1e9
        for b in range(len(self.boats)):
            if self.boats[b][4] > 0:
                S = self.copy()
                if S.go(b, d) and S.deliver(b, c):
                    cst = S.deliv[c]
                    if cst < bc:
                        bc = cst
                        best = S
        el = self.el
        have_ws = len(self.ws) > 0
        if _MAPC[0] is not mp:
            _MAPC[0] = mp
            _MAPC[1] = {}
            _MAPC[2] = [w for w in range(10) if mp.roles[w] == 2]
        for w in _MAPC[2]:
            if have_ws and w not in self.ws and el[w * 3 + 2] < 1:
                continue
            if el[w * 3 + 2] >= 1:
                S0 = self
            else:
                S0 = self.ensure_craft(w, B)
                if S0 is None:
                    continue
            SA = S0.fetch_deliver(w, c)
            if SA is None:
                continue
            if more > 0 and ahead and S0.el[w * 3 + 2] < 2:
                SB = S0.ensure_craft(w, B)
                if SB is not None:
                    SB = SB.fetch_deliver(w, c)
                    if SB is not None and SB.deliv[c] <= SA.deliv[c] + 1:
                        SA = SB
            cst = SA.deliv[c] - 0.5 * B * SA.surplus(w) / 3.5 - (2.0 if w in self.ws else 0.0)
            if cst < bc:
                bc = cst
                best = SA
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
    s.el = wh[:]
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
    s.memo = None
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
