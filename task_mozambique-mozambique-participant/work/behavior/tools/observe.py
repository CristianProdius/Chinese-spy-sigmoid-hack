"""Parked observers: send our boats (optionally building a 3rd) to target sites and log what we see.
Library + CLI: python3 observe.py GROUP SEED GAME 'targets json list' [build]
"""
import sys, json, os, heapq
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)
from arena import Arena

def dijkstra(routes, src):
    n = len(routes)
    dist = [10**9] * n; prev = [-1] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for v in range(n):
            w = routes[u][v]
            if w and d + w < dist[v]:
                dist[v] = d + w; prev[v] = u; heapq.heappush(pq, (dist[v], v))
    return dist, prev

def next_hop(routes, src, dst):
    if src == dst: return None
    dist, prev = dijkstra(routes, src)
    v = dst
    while prev[v] != src:
        v = prev[v]
    return v

def observe(a, group, seed, game, targets, build=False, rounds=80, extra=None):
    """targets: list of sites, one per boat (boat i -> targets[i]). If len(targets)==3 and build, builds boat 2 at round 0."""
    s = a.reset(group, seed, game)
    o = s['observation']
    m = o['map']
    log = []
    claim_round = [None] * 8
    last = 0; score_tl = []
    built = False
    while not s['game_done']:
        o = s['observation']
        la = o['legal_actions']
        act = {'op': 'wait'}
        if build and not built and {'op': 'build_boat'} in la:
            act = {'op': 'build_boat'}; built = True
        else:
            for i, b in enumerate(o['own']['boats']):
                if i >= len(targets) or targets[i] is None: continue
                if b['destination'] != -1: continue
                if b['position'] != targets[i]:
                    h = next_hop(m['routes'], b['position'], targets[i])
                    cand = {'op': 'sail', 'boat': i, 'destination': h}
                    if cand in la:
                        act = cand; break
        if extra:
            act = extra(o, act) or act
        s = a.step(act)
        o2 = s.get('observation')
        if o2 is None: break
        r = o2['round'] - 1
        for c, v in enumerate(o2['claims']):
            if v != -1 and claim_round[c] is None: claim_round[c] = (r, v)
        if o2['opponent_score'] != last:
            score_tl.append((r, o2['opponent_score'])); last = o2['opponent_score']
        log.append(dict(r=r, act=act, vis=[i for i, v in enumerate(o2['visible']) if v],
                        stocks=o2['stocks'], enemy=o2['enemy_boats'],
                        own=[(b['position'], b['destination'], b['eta']) for b in o2['own']['boats']]))
    return dict(group=group, seed=seed, game=game, seat=o['seat'], map=m, targets=targets, build=build,
                claim_round=claim_round, score_tl=score_tl, result=s['result'], log=log)

if __name__ == '__main__':
    g, sd, gm = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    targets = json.loads(sys.argv[4]); build = len(sys.argv) > 5
    with Arena() as a:
        rec = observe(a, g, sd, gm, targets, build)
    m = rec['map']
    print('homes', m['homes'], 'roles', m['roles'], 'seat', rec['seat'])
    print('claims', rec['claim_round'], 'score', rec['score_tl'], rec['result'])
    for L in rec['log']:
        if L['enemy'] or L['act']['op'] != 'wait':
            print(L['r'], L['act'], 'own', L['own'], 'enemy', [(e['boat'], e['position'], e['destination'], e['eta']) for e in L['enemy']], 'stocks', [(i, L['stocks'][i]) for i in L['vis']])
