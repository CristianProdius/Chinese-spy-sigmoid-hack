"""Measure replan-cache memory per entry: fill caches from lookahead rollouts, compare RSS."""
import gc, os, pickle, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import fastcore as F
import bench

def rss():
    with open('/proc/self/status') as f:
        for line in f:
            if line.startswith('VmRSS'):
                return int(line.split()[1]) / 1024.0

trajs = pickle.load(open(sys.argv[1], 'rb'))
bases = []
for t in trajs:
    snaps = {}
    def on_round(rnd, tr, preds, style=t['style']):
        if rnd in (4, 12, 20, 28, 36, 44, 52):
            for h in tr.hyps:
                if h.style == style:
                    snaps[rnd] = h.clone()
    bench.play_tracked('fast', t, on_round)
    bases += [(t['seat'], h) for h in snaps.values()]
caches = {id(h.prof.cache): h.prof.cache for s, h in bases}
for c in caches.values():
    c.clear()
gc.collect(); r0 = rss()
rng = random.Random(1)
for seat, base in bases:
    for k in range(150):
        h = base.clone()
        for _ in range(16):
            if h.eng.round >= 80:
                break
            h.step(F.WAIT if rng.random() < 0.3 else rng.choice(h.eng.legal(seat)))
            h.order()
n = sum(len(c) for c in caches.values())
gc.collect(); r1 = rss()
for c in caches.values():
    c.clear()
gc.collect(); r2 = rss()
print('entries %d  rss before %.1f MB, filled %.1f MB, cleared %.1f MB  ->  %.2f KB/entry (filled-cleared), %.2f KB/entry (filled-before)' % (
    n, r0, r1, r2, 1024 * (r1 - r2) / max(1, n), 1024 * (r1 - r0) / max(1, n)))
