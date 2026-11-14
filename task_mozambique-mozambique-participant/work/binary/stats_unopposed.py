"""Unopposed Professor profile per style (pure Python model, opponent always waits).
Usage: pypy3 stats_unopposed.py [maps]   -> prints per-style and per-topology aggregates."""
import json, random, sys, time
import professor as P
n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
rng = random.Random(5)
agg = {}
cpu = 0.0; replans = 0; slowest = 0.0
for m in range(n):
    topo = m % 4; seed = rng.randrange(2 ** 32); prof_seat = rng.randrange(2)
    mp = P.Map(P.generate_map(topo, seed))
    for style in range(5):
        eng = P.Engine(mp); prof = P.Professor(style, prof_seat)
        first_claim = None; claim_round = {}
        while eng.round < 80:
            t0 = time.process_time()
            o = prof.choose(eng.view(prof_seat))
            dt = time.process_time() - t0; cpu += dt; slowest = max(slowest, dt)
            orders = [P.WAIT, P.WAIT]; orders[prof_seat] = o
            before = list(eng.claims)
            eng.step(orders)
            for c in range(8):
                if before[c] == -1 and eng.claims[c] != -1:
                    claim_round[c] = eng.round - 1
        replans += prof.replans
        side = eng.sides[prof_seat]
        for key in (('style', style), ('topology', topo), ('all', 0)):
            a = agg.setdefault(key, dict(games=0, score=0, min_score=999, max_score=0, raw=0, crafted=0,
                                        first=0, first_crafted=0, n_first_crafted=0, last=0, workshops=0))
            a['games'] += 1; a['score'] += side.score
            a['min_score'] = min(a['min_score'], side.score); a['max_score'] = max(a['max_score'], side.score)
            a['crafted'] += side.crafted; a['raw'] += sum(1 for c in claim_round if c < 4)
            a['first'] += min(claim_round.values()) if claim_round else 80
            a['last'] += max(claim_round.values()) if claim_round else 80
            fc = [r for c, r in claim_round.items() if c >= 4]
            if fc: a['first_crafted'] += min(fc); a['n_first_crafted'] += 1
            a['workshops'] += sum(side.ws)
for key in sorted(agg):
    a = agg[key]; g = a['games']
    print('%-12s games %3d  score avg %.1f min %d max %d | raw %.2f crafted %.2f | first claim r%.1f, first crafted r%.1f (%d/%d games), last claim r%.1f | workshops %.2f' % (
        '%s=%s' % key, g, a['score'] / g, a['min_score'], a['max_score'], a['raw'] / g, a['crafted'] / g, a['first'] / g,
        a['first_crafted'] / max(1, a['n_first_crafted']), a['n_first_crafted'], g, a['last'] / g, a['workshops'] / g))
print(json.dumps(dict(cpu_seconds=round(cpu, 2), replans=replans, ms_per_replan=round(1000 * cpu / max(1, replans), 1),
                      slowest_choose_ms=round(1000 * slowest, 1), cpu_per_game=round(cpu / (5 * n), 3))))
