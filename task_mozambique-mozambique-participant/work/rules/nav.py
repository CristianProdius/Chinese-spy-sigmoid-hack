"""Helpers for scripted probes: shortest paths and a goto-and-wait policy."""
import heapq
def dist_next(routes, src):
    n=len(routes); D=[10**9]*n; first=[-1]*n; D[src]=0; pq=[(0,src,-1)]
    while pq:
        d,u,f=heapq.heappop(pq)
        if d>D[u]: continue
        for v in range(n):
            L=routes[u][v]
            if L and d+L<D[v]:
                D[v]=d+L; first[v]=v if u==src else f; heapq.heappush(pq,(D[v],v,first[v]))
    return D, first
def next_hop(routes, src, dst):
    D, first = dist_next(routes, src)
    return first[dst]
def pick(la, **kw):
    for x in la:
        if all(x.get(k)==v for k,v in kw.items()): return x
    return None
