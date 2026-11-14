"""Measure Professor replan cost by round / open contracts (passive opponent)."""
import sys, os, time, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'binary'))
import professor as P

rng = random.Random(5)
rows = []
tot_games = 0
t_all = time.process_time()
for g in range(12):
    topo = g % 4; seed = rng.randrange(2**32)
    md = P.generate_map(topo, seed); mp = P.Map(md)
    for style in range(5):
        eng = P.Engine(mp); prof = P.Professor(style, 1)
        tg = time.process_time()
        while eng.round < 80:
            n0 = prof.replans
            t0 = time.process_time()
            o = prof.choose(eng.view(1))
            dt = time.process_time() - t0
            if prof.replans != n0:
                rows.append((eng.round, sum(1 for c in range(8) if eng.claims[c] == -1 and mp.c_deadline[c] > eng.round), dt, g))
            eng.step([P.WAIT, o])
        tot_games += 1
        if g < 2:
            print('game', g, 'style', style, 'cpu %.3f' % (time.process_time() - tg), 'replans', prof.replans, 'score', eng.sides[1].score)
print('total cpu %.2f for %d games' % (time.process_time() - t_all, tot_games))
by = {}
for r, n, dt, g in rows:
    if g < 2: continue
    by.setdefault(n, []).append(dt)
for n in sorted(by):
    v = sorted(by[n])
    print('open %d: n=%d mean %.1f ms med %.1f max %.1f' % (n, len(v), 1000*sum(v)/len(v), 1000*v[len(v)//2], 1000*v[-1]))
byr = {}
for r, n, dt, g in rows:
    if g < 2: continue
    byr.setdefault(r // 10, []).append(dt)
for n in sorted(byr):
    v = sorted(byr[n])
    print('round %d0s: n=%d mean %.1f ms med %.1f max %.1f sum/game %.1f ms' % (n, len(v), 1000*sum(v)/len(v), 1000*v[len(v)//2], 1000*v[-1], 1000*sum(v)/50))
