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
    ga0=0.55,           # CPU seconds of GA at round 0
    front=2.0,          # front-loading factor of the per-round slice
    elites=8,
    delta_unverified=2.0,
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

def exact_rollout(G, hyp, plan, tlimit):
    """Exact game to the end against hypothesis `hyp`. Returns None when aborted on time, else
    (margin, us, them, tempo, pc, pg)."""
    eng = clone_engine(hyp.eng)
    prof = hyp.prof0.clone()
    seat = G.seat
    pseat = 1 - seat
    us = eng.sides[seat]
    them = eng.sides[pseat]
    pc = []
    pg = []
    tempo = 0
    plan = plan.copy() if plan is not None else None
    stocks = eng.stocks
    claims = eng.claims
    orders = [None, None]
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
        if us.score != s0:
            tempo += (us.score - s0) * (80 - r)
        if them.score != p0:
            pc.append((r, po[5]))
        elif po[0] == 'gather' and ok[pseat]:
            pg.append((r, them.boats[po[1]][0], po[4]))
    return (us.score - them.score, us.score, them.score, tempo, pc, pg)


def phantom_rollout(G, hyp, plan):
    """Cheap estimate: our side simulated exactly, the Professor replaced by its reference claim
    schedule (from the last exact rollout) with a simple redirect rule for goods we sniped."""
    eng = hyp.eng
    mp = G.mp
    seat = G.seat
    pseat = 1 - seat
    side = copy_side(eng.sides[seat])
    stocks = eng.stocks[:]
    claims = eng.claims[:]
    rnd = eng.round
    pscore = eng.sides[pseat].score
    pc = hyp.pc
    pg = hyp.pg
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
    tempo = 0
    for t in range(rnd, 80):
        o = plan_act(G, plan, side, stocks, claims, t)
        first = (t % 2 == seat)
        s0 = side.score
        if first and o[0] != 'wait':
            apply_order(mp, side, stocks, claims, seat, o, None)
        while ig < npg and pg[ig][0] == t:
            e = pg[ig]
            ig += 1
            if stocks[e[1]] >= e[2]:
                stocks[e[1]] -= e[2]
        while ic < npc and pc[ic][0] == t:
            c = pc[ic][1]
            ic += 1
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
                else:
                    i += 1
        if not first and o[0] != 'wait':
            if o[0] == 'gather':
                if stocks[side.boats[o[1]][0]] >= o[4]:
                    apply_order(mp, side, stocks, claims, seat, o, None)
            else:
                apply_order(mp, side, stocks, claims, seat, o, None)
        if side.score != s0:
            tempo += (side.score - s0) * (80 - t)
        advance_side(side)
        if (t + 1) % 4 == 0:
            for s in range(10):
                if (roles[s] == 0 or roles[s] == 1) and stocks[s] < 6:
                    stocks[s] += 1
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


def phantom_value(G, plan):
    return value_of([phantom_rollout(G, h, plan) for h in G.hyps])


def exact_value(G, plan, tlimit, store):
    """Exact value over all hypotheses, or None if time ran out. `store`: refresh the references."""
    res = []
    for h in G.hyps:
        r = exact_rollout(G, h, plan, tlimit)
        if r is None:
            return None
        res.append(r)
    if store:
        for h, r in zip(G.hyps, res):
            h.pc = r[4]
            h.pg = r[5]
    return value_of(res)


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
    G.elites = []            # list of (value, genome)
    G.used = 0.0             # CPU seconds used this game
    G.wused = 0.0            # wall seconds used this game
    G.rng = _random.Random(12345)
    G.fb = None
    G.log = []
    G.inc_exact = None
    G.first = (_PROCESS_GAMES[0] == 0)
    _PROCESS_GAMES[0] += 1
    G.total = (PARAMS['total'] + (PARAMS['first_extra'] if G.first else 0.0)) * PARAMS['scale']
    G.stats = dict(ph=0, ex=0, exab=0, sw=0, t0=0.0, ttrack=0.0, tex=0.0, tga=0.0)
    _LASTG[0] = G
    return G


def ga_search(G, side, stocks, claims, rnd, tend, base):
    """Evolve genomes on the phantom fitness until CPU time `tend`. Returns sorted [(value, genome, plan)]."""
    rng = G.rng
    seen = {}
    pool = []                # (value, genome, plan)

    def consider(genome):
        if genome in seen:
            return
        plan = decode(G, genome[0], genome[1], side, stocks, claims, rnd)
        v = phantom_value(G, plan)
        G.stats['ph'] += 1
        seen[genome] = v
        pool.append((v, genome, plan))

    for genome in base:
        if _clock() > tend:
            break
        consider(genome)
    nel = PARAMS['elites']
    it = 0
    while _clock() < tend:
        it += 1
        if not pool:
            break
        if it % 16 == 0 or len(pool) > 4 * nel:
            pool.sort(key=lambda x: -x[0])
            del pool[nel:]
        k = min(len(pool), nel)
        # bias towards the best
        top = sorted(range(len(pool)), key=lambda i: -pool[i][0])[:k]
        a = pool[top[min(int(rng.random() * rng.random() * k), k - 1)]][1]
        r = rng.random()
        if r < 0.15 and k >= 2:
            b = pool[top[rng.randrange(k)]][1]
            child = crossover(a, b, rng)
        else:
            child = mutate(G, a, rng, side, claims, rnd)
            if r > 0.7:
                child = mutate(G, child, rng, side, claims, rnd)
        consider(child)
    pool.sort(key=lambda x: -x[0])
    return pool


def brain(obs, memory):
    t_cpu0 = _clock()
    t_wall0 = _wall()
    rnd = obs['round']
    G = memory.get('G')
    if G is None or rnd == 0:
        G = new_game(obs)
        memory['G'] = G
    seat = G.seat
    mp = G.mp
    # ---- tracking -------------------------------------------------------------------------
    if G.hyps:
        alive = [h for h in G.hyps if obs_matches(obs, h.eng, seat)]
        if len(alive) != len(G.hyps):
            G.inc_exact = None
        G.hyps = alive
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
    budget_ok = (G.wused + (_wall() - t_wall0)) < PARAMS['wall_hard']
    used_now = G.used + (_clock() - t_cpu0)
    G.stats['ttrack'] += _clock() - t_cpu0
    rem = G.total - used_now

    if G.plan is None:
        # references: the Professor's future when we do nothing
        for h in G.hyps:
            r = exact_rollout(G, h, None, None)
            h.pc = r[4]
            h.pg = r[5]
        G.stats['t0'] = _clock() - t_cpu0
        tend = _clock() + PARAMS['ga0'] * PARAMS['scale']
        base = seed_genomes(G, side, claims, rnd)
        pool = ga_search(G, side, stocks, claims, rnd, tend, base)
        G.plan = pool[0][2]
        G.elites = [(v, g) for v, g, _ in pool[:PARAMS['elites']]]
        G.inc_exact = None
        if PARAMS.get('debug'):
            G.log.append((rnd, None, pool[0][0], pool[0][0], None))
    elif budget_ok and rem > 0.02 and left > 1:
        inc = G.plan
        if inc.pend is not None or inc.dirty:
            # normalise the incumbent on the real state before evaluating copies of it
            pass
        slice_ = rem / max(4.0, float(left)) * PARAMS['front']
        t0 = _clock()
        # 1. exact value of the incumbent (cheap when cached), refresh references
        v_inc = exact_value(G, inc, t0 + 0.4 * slice_, True)
        G.stats['ex'] += 1
        if v_inc is None:
            G.stats['exab'] += 1
        G.stats['tex'] += _clock() - t0
        t1 = _clock()
        # 2. GA on the phantom fitness
        base = [(live_genes(G, inc, claims, rnd, side), inc.mode)]
        for _, g in G.elites:
            pg = Plan.__new__(Plan)
            pg.genes = g[0]
            pg.done = frozenset()
            pg.bb = True
            base.append((live_genes(G, pg, claims, rnd, side), g[1]))
        v_inc_ph = phantom_value(G, inc)
        tend = t0 + 0.75 * slice_
        pool = ga_search(G, side, stocks, claims, rnd, tend, base)
        G.elites = [(v, g) for v, g, _ in pool[:PARAMS['elites']]]
        G.stats['tga'] += _clock() - t1
        t1 = _clock()
        # 3. challengers
        ref = v_inc if v_inc is not None else v_inc_ph
        best_plan = None
        best_v = ref
        tlim = t0 + slice_
        tried = 0
        for v, g, plan in pool[:3]:
            if v <= v_inc_ph + 1e-9 and v <= ref + 1e-9:
                break
            if _clock() >= tlim:
                break
            tried += 1
            ve = exact_value(G, plan, tlim, False)
            G.stats['ex'] += 1
            if ve is None:
                G.stats['exab'] += 1
                if tried == 1 and v > ref + PARAMS['delta_unverified'] and v > v_inc_ph + PARAMS['delta_unverified']:
                    best_plan = plan
                    best_v = v
                break
            if ve > best_v + 1e-9:
                best_v = ve
                best_plan = plan
        if PARAMS.get('debug'):
            G.log.append((rnd, v_inc, v_inc_ph, pool[0][0] if pool else None, best_v if best_plan is not None else None))
        if best_plan is not None:
            G.plan = best_plan
            G.stats['sw'] += 1
            # refresh references for the new incumbent when affordable
            exact_value(G, best_plan, _clock() + 0.25 * slice_, True)
        G.stats['tex'] += _clock() - t1
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
