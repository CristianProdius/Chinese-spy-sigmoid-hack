"""Replan micro-benchmark: reference vs fast on a recorded corpus (same process, warm JIT).
pypy3 benchreplan.py CORPUS [--passes 3] [--n N] [--which ref,fast]"""
import os, sys, pickle, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fastcore as F
ap = argparse.ArgumentParser(); ap.add_argument('corpus'); ap.add_argument('--passes', type=int, default=3)
ap.add_argument('--n', type=int, default=0); ap.add_argument('--which', default='ref,fast')
a = ap.parse_args()
recs = pickle.load(open(a.corpus, 'rb'))
if a.n: recs = recs[:a.n]

def prep(M):
    maps = {}
    jobs = []
    for md, style, st, est, out in recs:
        mp = maps.get(id(md)) or maps.setdefault(id(md), M.Map(md))
        side = M.Side(st[0]); side.score, side.crafted = st[1], st[2]
        side.boats = [b[:] for b in st[3]]; side.wh = st[4][:]; side.ws = st[5][:]; side.jobs = st[6][:]
        v = M.View(); v.mp = mp; v.side = side; v.claims = st[7]; v.round = st[8]; v.seat = st[9]
        jobs.append((v, style, est))
    return jobs

def run_ref(jobs):
    for v, style, est in jobs:
        pr = P.Professor(style, v.seat); pr.mp = v.mp; pr.est = est[:]
        pr.replan(v)

def run_fast(jobs):
    for v, style, est in jobs:
        pr = F.Professor(style, v.seat, use_cache=False); pr.mp = v.mp; pr.est = est[:]
        pr.replan(v)

res = {}
for w in a.which.split(','):
    jobs = prep(P if w == 'ref' else F)
    fn = run_ref if w == 'ref' else run_fast
    ts = []
    for p in range(a.passes):
        t0 = time.process_time(); fn(jobs); ts.append(time.process_time() - t0)
    res[w] = ts
    print('%-5s passes %s  -> %.2f ms/replan (best pass)' % (w, ' '.join('%.2f' % t for t in ts), 1000 * min(ts) / len(jobs)), flush=True)
if 'ref' in res and 'fast' in res:
    print('speedup best-pass %.2fx, first-pass %.2fx' % (min(res['ref']) / min(res['fast']), res['ref'][0] / res['fast'][0]))
