import sys, os, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binary')); sys.path.insert(0, os.path.join(HERE, '..', 'fast'))
import professor as P, fastcore as F
rng = random.Random(3)
games = [(rng.randrange(4), rng.randrange(2**32), rng.randrange(5), rng.randrange(2)) for _ in range(40)]
def run(M, use_clone):
    t0 = time.process_time()
    for topo, seed, style, seat in games:
        md = M.generate_map(topo, seed); mp = M.Map(md)
        e = M.Engine(mp); p = M.Professor(style, 1 - seat)
        while e.round < 80:
            po = p.choose(e.view(1 - seat)); o = [None, None]; o[seat] = M.WAIT; o[1 - seat] = po; e.step(o)
    return time.process_time() - t0
for rep in range(2):
    print('ref  %.2fs' % run(P, False), flush=True)
    print('fast %.2fs' % run(F, True), flush=True)
