"""A/B two fastcore versions on a corpus, alternating passes in one process (pypy3 ab.py A.py B.py CORPUS [rounds])."""
import importlib.util, pickle, sys, time
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
A = load(sys.argv[1], 'modA'); B = load(sys.argv[2], 'modB')
recs = pickle.load(open(sys.argv[3], 'rb'))
R = int(sys.argv[4]) if len(sys.argv) > 4 else 6
def prep(M):
    maps = {}; jobs = []
    for md, style, st, est, out in recs:
        mp = maps.get(id(md)) or maps.setdefault(id(md), M.Map(md))
        side = M.Side(st[0]); side.score, side.crafted = st[1], st[2]
        side.boats = [b[:] for b in st[3]]; side.wh = st[4][:]; side.ws = st[5][:]; side.jobs = st[6][:]
        v = M.View(); v.mp = mp; v.side = side; v.claims = st[7]; v.round = st[8]; v.seat = st[9]
        jobs.append((v, style, est))
    return jobs
def run(M, jobs):
    t0 = time.process_time()
    for v, style, est in jobs:
        pr = M.Professor(style, v.seat, use_cache=False); pr.mp = v.mp; pr.est = est[:]; pr.replan(v)
    return time.process_time() - t0
ja, jb = prep(A), prep(B)
ta, tb = [], []
for i in range(R):
    if i % 2 == 0: ta.append(run(A, ja)); tb.append(run(B, jb))
    else: tb.append(run(B, jb)); ta.append(run(A, ja))
print('A', ' '.join('%.2f' % x for x in ta)); print('B', ' '.join('%.2f' % x for x in tb))
sa = sorted(ta[1:]); sb = sorted(tb[1:])
print('median warm A %.3f B %.3f  B/A %.3f ; first A %.2f B %.2f' % (sa[len(sa)//2], sb[len(sb)//2], sb[len(sb)//2]/sa[len(sa)//2], ta[0], tb[0]))
