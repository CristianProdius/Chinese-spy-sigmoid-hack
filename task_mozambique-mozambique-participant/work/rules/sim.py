"""Pure-Python simulator of the Mozambique / "Professor of Maputo Bay" game (both sides).

Stdlib only, PyPy friendly (plain lists and ints, no classes on the hot path except State).
See RULES.md for the rules this encodes and how each was established.

Actions are tuples  (op, boat, x, y):
    WAIT  (0,-1,0,0)              SAIL   (1,b,dest,0)      GATHER (2,b,good,q)
    LOAD  (3,b,good,q)            UNLOAD (4,b,good,q)      BUILD_WORKSHOP (5,b,0,0)
    CRAFT (6,b,0,0)               DELIVER (7,b,contract,0) BUILD_BOAT (8,-1,0,0)
to_dict()/from_dict() convert to/from the engine's JSON action dicts.

Typical use:
    st = State.from_observation(obs)      # round-0 observation of either seat (map + start)
    la = legal_actions(st, seat)          # same list and order as the engine's legal_actions
    step(st, act0, act1)                  # resolve one round (act0 = seat 0's action)
    o  = observation(st, seat)            # engine-format observation dict for that seat
"""

WAIT, SAIL, GATHER, LOAD, UNLOAD, BUILD_WORKSHOP, CRAFT, DELIVER, BUILD_BOAT = range(9)
OPS = ('wait', 'sail', 'gather', 'load', 'unload', 'build_workshop', 'craft', 'deliver', 'build_boat')
OPCODE = {name: i for i, name in enumerate(OPS)}

ROUNDS = 80
CAPACITY = 3
STOCK_START = 4
STOCK_CAP = 6
REGEN_EVERY = 4
CRAFT_ROUNDS = 3
WORKSHOP_COST = (2, 1)      # timber, fibre from the warehouse at the site
CRAFT_COST = (2, 1)
BOAT_COST = (4, 2)          # from the home warehouse
HOME_START = (5, 3, 0)
START_BOATS = 2
MAX_BOATS = 3               # see RULES.md (build_boat never offered with 3 boats)

ACT_WAIT = (WAIT, -1, 0, 0)
ACT_BUILD_BOAT = (BUILD_BOAT, -1, 0, 0)


def to_dict(a):
    op = a[0]
    if op == WAIT:
        return {'op': 'wait'}
    if op == BUILD_BOAT:
        return {'op': 'build_boat'}
    if op == SAIL:
        return {'op': 'sail', 'boat': a[1], 'destination': a[2]}
    if op in (GATHER, LOAD, UNLOAD):
        return {'op': OPS[op], 'boat': a[1], 'good': a[2], 'quantity': a[3]}
    if op == DELIVER:
        return {'op': 'deliver', 'boat': a[1], 'contract': a[2]}
    return {'op': OPS[op], 'boat': a[1]}


def from_dict(d):
    op = OPCODE[d['op']]
    if op == SAIL:
        return (op, d['boat'], d['destination'], 0)
    if op in (GATHER, LOAD, UNLOAD):
        return (op, d['boat'], d['good'], d['quantity'])
    if op == DELIVER:
        return (op, d['boat'], d['contract'], 0)
    if op in (BUILD_WORKSHOP, CRAFT):
        return (op, d['boat'], 0, 0)
    return (op, -1, 0, 0)


class State(object):
    """Full game state. Boats are lists [position, destination, eta, cargo0, cargo1, cargo2]."""
    __slots__ = ('roles', 'routes', 'adj', 'homes', 'contracts', 'topology', 'round',
                 'stocks', 'claims', 'boats', 'wh', 'ws', 'jobs', 'score', 'crafted')

    def __init__(self, roles, routes, homes, contracts, topology=-1):
        self.roles = list(roles)
        self.routes = [list(r) for r in routes]
        self.adj = [[j for j in range(len(roles)) if routes[i][j]] for i in range(len(roles))]
        self.homes = list(homes)
        # contracts as tuples (destination, good, quantity, points, deadline)
        self.contracts = [(c['destination'], c['good'], c['quantity'], c['points'], c['deadline'])
                          if isinstance(c, dict) else tuple(c) for c in contracts]
        self.topology = topology
        self.round = 0
        n = len(roles)
        self.stocks = [STOCK_START if r in (0, 1) else 0 for r in roles]
        self.claims = [-1] * len(self.contracts)
        self.boats = [[[homes[s], -1, 0, 0, 0, 0] for _ in range(START_BOATS)] for s in (0, 1)]
        self.wh = [[[0, 0, 0] for _ in range(n)] for s in (0, 1)]
        for s in (0, 1):
            self.wh[s][homes[s]] = list(HOME_START)
        self.ws = [[False] * n for s in (0, 1)]
        self.jobs = [[0] * n for s in (0, 1)]
        self.score = [0, 0]
        self.crafted = [0, 0]

    @classmethod
    def from_map(cls, m):
        return cls(m['roles'], m['routes'], m['homes'], m['contracts'], m.get('topology', -1))

    @classmethod
    def from_observation(cls, obs):
        """Initial state from a round-0 observation (either seat)."""
        return cls.from_map(obs['map'])

    def copy(self):
        c = State.__new__(State)
        c.roles = self.roles; c.routes = self.routes; c.adj = self.adj
        c.homes = self.homes; c.contracts = self.contracts; c.topology = self.topology
        c.round = self.round
        c.stocks = self.stocks[:]
        c.claims = self.claims[:]
        c.boats = [[b[:] for b in self.boats[0]], [b[:] for b in self.boats[1]]]
        c.wh = [[w[:] for w in self.wh[0]], [w[:] for w in self.wh[1]]]
        c.ws = [self.ws[0][:], self.ws[1][:]]
        c.jobs = [self.jobs[0][:], self.jobs[1][:]]
        c.score = self.score[:]
        c.crafted = self.crafted[:]
        return c

    def done(self):
        return self.round >= ROUNDS


# ---------------------------------------------------------------------------------------------
# Legal actions (engine order)
# ---------------------------------------------------------------------------------------------

def legal_actions(st, seat):
    """List of action tuples in exactly the engine's order."""
    out = [ACT_WAIT]
    roles = st.roles; wh = st.wh[seat]; ws = st.ws[seat]; jobs = st.jobs[seat]
    rnd = st.round
    for b, boat in enumerate(st.boats[seat]):
        if boat[1] != -1:
            continue                                   # sailing boats take no orders
        p = boat[0]
        for d in st.adj[p]:
            out.append((SAIL, b, d, 0))
        free = CAPACITY - boat[3] - boat[4] - boat[5]
        role = roles[p]
        if (role == 0 or role == 1) and free > 0:
            n = st.stocks[p]
            if n > free:
                n = free
            for q in range(1, n + 1):
                out.append((GATHER, b, role, q))
        w = wh[p]
        for g in range(3):
            n = w[g]
            if n > free:
                n = free
            for q in range(1, n + 1):
                out.append((LOAD, b, g, q))
            for q in range(1, boat[3 + g] + 1):
                out.append((UNLOAD, b, g, q))
        if role == 2:
            if not ws[p]:
                if w[0] >= WORKSHOP_COST[0] and w[1] >= WORKSHOP_COST[1]:
                    out.append((BUILD_WORKSHOP, b, 0, 0))
            elif jobs[p] == 0 and w[0] >= CRAFT_COST[0] and w[1] >= CRAFT_COST[1]:
                out.append((CRAFT, b, 0, 0))
        for c, (dest, good, qty, pts, deadline) in enumerate(st.contracts):
            if dest == p and st.claims[c] == -1 and rnd < deadline and boat[3 + good] >= qty:
                out.append((DELIVER, b, c, 0))
    h = wh[st.homes[seat]]
    if len(st.boats[seat]) < MAX_BOATS and h[0] >= BOAT_COST[0] and h[1] >= BOAT_COST[1]:
        out.append(ACT_BUILD_BOAT)
    return out


def is_legal(st, seat, a):
    """Cheap legality test for one action (same conditions as legal_actions)."""
    op = a[0]
    if op == WAIT:
        return True
    if op == BUILD_BOAT:
        h = st.wh[seat][st.homes[seat]]
        return len(st.boats[seat]) < MAX_BOATS and h[0] >= BOAT_COST[0] and h[1] >= BOAT_COST[1]
    b = a[1]
    boats = st.boats[seat]
    if b < 0 or b >= len(boats):
        return False
    boat = boats[b]
    if boat[1] != -1:
        return False
    p = boat[0]
    free = CAPACITY - boat[3] - boat[4] - boat[5]
    if op == SAIL:
        return 0 <= a[2] < len(st.roles) and st.routes[p][a[2]] > 0
    if op == GATHER:
        role = st.roles[p]
        return (role == 0 or role == 1) and a[2] == role and 1 <= a[3] <= min(free, st.stocks[p])
    if op == LOAD:
        return 0 <= a[2] < 3 and 1 <= a[3] <= min(free, st.wh[seat][p][a[2]])
    if op == UNLOAD:
        return 0 <= a[2] < 3 and 1 <= a[3] <= boat[3 + a[2]]
    if op == BUILD_WORKSHOP:
        w = st.wh[seat][p]
        return st.roles[p] == 2 and not st.ws[seat][p] and w[0] >= 2 and w[1] >= 1
    if op == CRAFT:
        w = st.wh[seat][p]
        return st.roles[p] == 2 and st.ws[seat][p] and st.jobs[seat][p] == 0 and w[0] >= 2 and w[1] >= 1
    if op == DELIVER:
        c = a[2]
        if c < 0 or c >= len(st.contracts):
            return False
        dest, good, qty, pts, deadline = st.contracts[c]
        return dest == p and st.claims[c] == -1 and st.round < deadline and boat[3 + good] >= qty
    return False


# ---------------------------------------------------------------------------------------------
# Round resolution
# ---------------------------------------------------------------------------------------------

def _apply(st, seat, a, departed):
    """Apply one side's action if it is (still) legal. Returns True if it took effect."""
    op = a[0]
    if op == WAIT:
        return True
    if not is_legal(st, seat, a):
        return False
    if op == BUILD_BOAT:
        h = st.wh[seat][st.homes[seat]]
        h[0] -= BOAT_COST[0]; h[1] -= BOAT_COST[1]
        st.boats[seat].append([st.homes[seat], -1, 0, 0, 0, 0])
        return True
    boat = st.boats[seat][a[1]]
    p = boat[0]
    if op == SAIL:
        key = (p, a[2]) if p < a[2] else (a[2], p)     # the route (undirected edge)
        if key in departed:                            # route-departure conflict: lost
            return False
        departed.add(key)
        boat[1] = a[2]
        boat[2] = st.routes[p][a[2]]
        return True
    if op == GATHER:
        st.stocks[p] -= a[3]
        boat[3 + a[2]] += a[3]
        return True
    if op == LOAD:
        st.wh[seat][p][a[2]] -= a[3]
        boat[3 + a[2]] += a[3]
        return True
    if op == UNLOAD:
        st.wh[seat][p][a[2]] += a[3]
        boat[3 + a[2]] -= a[3]
        return True
    if op == BUILD_WORKSHOP:
        w = st.wh[seat][p]
        w[0] -= WORKSHOP_COST[0]; w[1] -= WORKSHOP_COST[1]
        st.ws[seat][p] = True
        return True
    if op == CRAFT:
        w = st.wh[seat][p]
        w[0] -= CRAFT_COST[0]; w[1] -= CRAFT_COST[1]
        st.jobs[seat][p] = CRAFT_ROUNDS
        return True
    if op == DELIVER:
        c = a[2]
        dest, good, qty, pts, deadline = st.contracts[c]
        boat[3 + good] -= qty
        st.claims[c] = seat
        st.score[seat] += pts
        if good == 2:
            st.crafted[seat] += 1
        return True
    return False


def step(st, a0, a1):
    """Resolve one simultaneous round. a0/a1 are the action tuples of seat 0/1.
    Returns (ok0, ok1): whether each side's action took effect."""
    first = st.round & 1                               # seat 0 has priority on even rounds
    acts = (a0, a1)
    ok = [True, True]
    departed = set()
    for seat in (first, 1 - first):
        ok[seat] = _apply(st, seat, acts[seat], departed)
    # end of round: movement, production, regeneration
    for s in (0, 1):
        for boat in st.boats[s]:
            if boat[1] != -1:
                boat[2] -= 1
                if boat[2] <= 0:
                    boat[0] = boat[1]; boat[1] = -1; boat[2] = 0
        jobs = st.jobs[s]
        for i in range(len(jobs)):
            if jobs[i]:
                jobs[i] -= 1
                if jobs[i] == 0:
                    st.wh[s][i][2] += 1
    st.round += 1
    if st.round % REGEN_EVERY == 0:
        stocks = st.stocks
        for i, r in enumerate(st.roles):
            if (r == 0 or r == 1) and stocks[i] < STOCK_CAP:
                stocks[i] += 1
    return ok[0], ok[1]


# ---------------------------------------------------------------------------------------------
# Observation builder
# ---------------------------------------------------------------------------------------------

def visible_sites(st, seat):
    vis = [False] * len(st.roles)
    vis[st.homes[seat]] = True
    for boat in st.boats[seat]:
        if boat[1] == -1:
            vis[boat[0]] = True
    for i, w in enumerate(st.ws[seat]):
        if w:
            vis[i] = True
    return vis


def observation(st, seat, map_dict=None):
    """Engine-format observation dict for `seat` (map_dict: reuse the engine's map dict)."""
    vis = visible_sites(st, seat)
    other = 1 - seat
    enemy = []
    for b, boat in enumerate(st.boats[other]):
        if vis[boat[0]] or (boat[1] != -1 and vis[boat[1]]):
            enemy.append({'boat': b, 'destination': boat[1], 'eta': boat[2], 'position': boat[0]})
    if map_dict is None:
        map_dict = {
            'contracts': [{'deadline': c[4], 'destination': c[0], 'good': c[1], 'points': c[3],
                           'quantity': c[2]} for c in st.contracts],
            'homes': list(st.homes), 'roles': list(st.roles),
            'routes': [list(r) for r in st.routes], 'topology': st.topology}
    return {
        'claims': list(st.claims),
        'enemy_boats': enemy,
        'legal_actions': [to_dict(a) for a in legal_actions(st, seat)],
        'map': map_dict,
        'opponent_score': st.score[other],
        'own': {
            'boats': [{'cargo': [boat[3], boat[4], boat[5]], 'destination': boat[1], 'eta': boat[2],
                       'position': boat[0]} for boat in st.boats[seat]],
            'crafted_deliveries': st.crafted[seat],
            'home': st.homes[seat],
            'jobs': list(st.jobs[seat]),
            'score': st.score[seat],
            'warehouses': [list(w) for w in st.wh[seat]],
            'workshops': list(st.ws[seat]),
        },
        'round': st.round,
        'seat': seat,
        'stocks': [st.stocks[i] if vis[i] else None for i in range(len(vis))],
        'visible': vis,
    }


def state_from_observation(obs, stock_guess=None):
    """Best-effort State from one seat's mid-game observation.
    Exact: our boats/cargo/warehouses/workshops/jobs/score/crafted, claims, both scores, the
    opponent's crafted count (its M claims), stocks at visible sites, round.
    Guessed (the engine hides them): stocks at unseen sites (stock_guess[i] if given, else the
    regeneration-only value from the start, i.e. an upper bound), the opponent's boats (listed
    enemy boats as shown with empty cargo; unlisted ones docked at the enemy home; count = max(2,
    highest listed index + 1)), and the opponent's warehouses/workshops/jobs (start values)."""
    st = State.from_map(obs['map'])
    seat = obs['seat']
    other = 1 - seat
    st.round = obs['round']
    st.claims = list(obs['claims'])
    own = obs['own']
    st.boats[seat] = [[b['position'], b['destination'], b['eta'], b['cargo'][0], b['cargo'][1], b['cargo'][2]]
                      for b in own['boats']]
    st.wh[seat] = [list(w) for w in own['warehouses']]
    st.ws[seat] = list(own['workshops'])
    st.jobs[seat] = list(own['jobs'])
    st.score[seat] = own['score']
    st.crafted[seat] = own['crafted_deliveries']
    st.score[other] = obs['opponent_score']
    st.crafted[other] = sum(1 for c, cl in enumerate(obs['claims']) if cl == other and st.contracts[c][1] == 2)
    regen_only = min(STOCK_CAP, STOCK_START + st.round // REGEN_EVERY)
    for i, r in enumerate(st.roles):
        if obs['stocks'][i] is not None:
            st.stocks[i] = obs['stocks'][i]
        elif r in (0, 1):
            st.stocks[i] = stock_guess[i] if stock_guess is not None and stock_guess[i] is not None else regen_only
    listed = {e['boat']: e for e in obs['enemy_boats']}
    n = max([2] + [b + 1 for b in listed])
    home = st.homes[other]
    st.boats[other] = []
    for b in range(n):
        e = listed.get(b)
        if e is None:
            st.boats[other].append([home, -1, 0, 0, 0, 0])
        else:
            st.boats[other].append([e['position'], e['destination'], e['eta'], 0, 0, 0])
    return st


def result(st):
    """Final result in the engine's format, from seat-0's perspective is NOT assumed:
    returns scores [seat0, seat1] and the winner (-1 draw). See RULES.md for the tie-break."""
    s0, s1 = st.score
    if s0 != s1:
        return {'scores': [s0, s1], 'winner': 0 if s0 > s1 else 1}
    return {'scores': [s0, s1], 'winner': -1}
