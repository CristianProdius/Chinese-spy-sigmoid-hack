# ---- sched: one-sided timetable scheduler for our side (one order per round slot) ----
try:
    from core import *          # noqa: F401,F403  (stripped by build.py)
except ImportError:
    pass

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
