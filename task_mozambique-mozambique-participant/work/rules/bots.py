"""Simple scripted policies used to generate validation traces that reach every mechanic
(workshops, crafting, manufactured deliveries, boat building, races with the Professor).
Not a strategy: just goal-directed noise. policy(obs, mem, rng) -> one legal action dict."""
import heapq


def _sp(routes):
    n = len(routes)
    D = [[10 ** 9] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = 0
        for j in range(n):
            if routes[i][j]:
                D[i][j] = routes[i][j]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
    return D


def _hop(routes, D, src, dst):
    best = None
    for v in range(len(routes)):
        L = routes[src][v]
        if L and L + D[v][dst] == D[src][dst]:
            if best is None or v < best:
                best = v
    return best


def _find(la, **kw):
    for x in la:
        if all(x.get(k) == v for k, v in kw.items()):
            return x
    return None


def econ(o, mem, rng, eps=0.08):
    la = o['legal_actions']
    if rng.random() < eps:
        return rng.choice(la)
    mp = o['map']
    R = mp['routes']
    if 'D' not in mem:
        mem['D'] = _sp(R)
        mfg = [i for i, r in enumerate(mp['roles']) if r == 2]
        mem['M'] = rng.choice(mfg)
        mem['order'] = rng.random() < 0.5
    D = mem['D']
    M = mem['M']
    roles = mp['roles']
    own = o['own']
    rnd = o['round']
    claims = o['claims']
    cts = mp['contracts']
    ops = {}
    for x in la:
        ops.setdefault(x['op'], []).append(x)
    if 'deliver' in ops:
        return max(ops['deliver'], key=lambda x: cts[x['contract']]['points'])
    if 'craft' in ops:
        return ops['craft'][0]
    if 'build_workshop' in ops and rng.random() < 0.9:
        return ops['build_workshop'][0]
    if 'build_boat' in ops and rng.random() < 0.3:
        return ops['build_boat'][0]
    boats = list(enumerate(own['boats']))
    if mem['order']:
        boats.reverse()
    wh = own['warehouses']
    for i, b in boats:
        if b['destination'] != -1:
            continue
        p = b['position']
        cg = b['cargo']
        free = 3 - sum(cg)
        # unload raw at the workshop site
        if p == M and (cg[0] or cg[1]):
            g = 0 if cg[0] else 1
            x = _find(la, op='unload', boat=i, good=g, quantity=cg[g])
            if x:
                return x
        # pick up manufactured goods
        if free and wh[p][2]:
            x = _find(la, op='load', boat=i, good=2, quantity=min(free, wh[p][2]))
            if x:
                return x
        # carry goods to a contract
        target = None
        for c, ct in enumerate(cts):
            if claims[c] == -1 and cg[ct['good']] >= ct['quantity'] and rnd + D[p][ct['destination']] < ct['deadline']:
                if target is None or D[p][ct['destination']] < D[p][target]:
                    target = ct['destination']
        if target is not None and target != p:
            return _find(la, op='sail', boat=i, destination=_hop(R, D, p, target)) or la[0]
        # at home: load raw
        if p == own['home'] and free:
            for g in (0, 1):
                if wh[p][g]:
                    x = _find(la, op='load', boat=i, good=g, quantity=min(free, wh[p][g]))
                    if x:
                        return x
        # gather
        if free and roles[p] in (0, 1) and o['stocks'][p]:
            x = _find(la, op='gather', boat=i, good=roles[p], quantity=min(free, o['stocks'][p]))
            if x:
                return x
        # full enough: go to the workshop
        if (cg[0] + cg[1] >= 2 or free == 0) and p != M:
            return _find(la, op='sail', boat=i, destination=_hop(R, D, p, M)) or la[0]
        # otherwise go gather the scarcer good
        need = 0 if wh[M][0] <= 2 * wh[M][1] else 1
        if free:
            sites = [s for s in range(len(roles)) if roles[s] == need and s != p]
            if sites:
                s = min(sites, key=lambda s: D[p][s] + rng.random())
                return _find(la, op='sail', boat=i, destination=_hop(R, D, p, s)) or la[0]
    return rng.choice(la) if rng.random() < 0.3 else la[0]
