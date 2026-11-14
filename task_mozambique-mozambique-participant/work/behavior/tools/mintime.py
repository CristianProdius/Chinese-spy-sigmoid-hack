"""Analytic single-contract earliest delivery round for a side starting at its home at round 0,
nobody else interfering, one action per round. Round = the round in which `deliver` is issued
(same convention as claim_round in the data files).
raw:  min over s in {home} U {natural sites of that good}: dist(h,s) + 1 + dist(s,d)
      (home: load at r0, sail from r1; stock site: gather on arrival, then sail)
man:  two boats each load 2T+1F (4 load actions), sail to manufacturing site m, A unloads+builds,
      B unloads+crafts, product usable 3 rounds after craft, load, sail, deliver:
      11 + dist(h,m) + dist(m,d), min over the two manufacturing sites.
"""
import heapq

def all_dist(routes):
    n = len(routes); out = []
    for src in range(n):
        dist = [10**9] * n; dist[src] = 0; pq = [(0, src)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: continue
            for v in range(n):
                w = routes[u][v]
                if w and d + w < dist[v]:
                    dist[v] = d + w; heapq.heappush(pq, (dist[v], v))
        out.append(dist)
    return out

def contract_times(m, home, D=None):
    D = D or all_dist(m['routes'])
    res = []
    for c in m['contracts']:
        d, g = c['destination'], c['good']
        if g != 2:
            cands = [D[home][s] + 1 + D[s][d] for s, r in enumerate(m['roles']) if r == g or s == home]
            res.append(min(cands))
        else:
            res.append(min(11 + D[home][s] + D[s][d] for s, r in enumerate(m['roles']) if r == 2))
    return res
