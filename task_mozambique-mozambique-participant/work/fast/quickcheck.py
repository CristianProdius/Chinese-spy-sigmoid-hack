"""Replay the corpus: fast replan (uncached) vs recorded reference output."""
import os, sys, pickle, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fastcore as F
recs = pickle.load(open(sys.argv[1], 'rb'))
n = int(sys.argv[2]) if len(sys.argv) > 2 else len(recs)
maps = {}
bad = 0
t0 = time.process_time()
for i, (md, style, st, est, out) in enumerate(recs[:n]):
    key = id(md)
    mp = maps.get(key) or maps.setdefault(key, F.Map(md))
    side = F.Side(st[0]); side.score, side.crafted = st[1], st[2]
    side.boats = [b[:] for b in st[3]]; side.wh = st[4][:]; side.ws = st[5][:]; side.jobs = st[6][:]
    v = F.View(); v.mp = mp; v.side = side; v.claims = st[7]; v.round = st[8]; v.seat = st[9]
    pr = F.Professor(style, st[9], use_cache=False); pr.mp = mp; pr.est = est[:]
    r = pr.replan(v)
    if (r is None) != (out is None) or (r is not None and (r[0] != out[0] or r[1] != out[1] or r[2] != out[2])):
        bad += 1
        if bad <= 3:
            print('MISMATCH rec', i, 'round', st[8], 'style', style)
            print(' ref ', out if out is None else (out[0][:12], out[1], out[2]))
            print(' fast', r if r is None else (r[0][:12], r[1], r[2]))
print('checked', n, 'bad', bad, 'cpu %.2fs' % (time.process_time() - t0))
