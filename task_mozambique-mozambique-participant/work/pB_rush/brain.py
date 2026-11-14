# ==== pB_rush brain (appended after the engine/Professor core by build.py) ====
import time
from core import *  # noqa: F401,F403  (BUILD-STRIP)

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
