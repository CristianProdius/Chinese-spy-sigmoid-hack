"""Record replan inputs from games played by the reference engine + Professor.
Usage: pypy3 mkcorpus.py OUT.pkl [--games N] [--seed S]
Each record: (map_dict, style, seat, view-state tuple, est, plan_out, contracts_out)."""
import os, sys, random, pickle, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--games', type=int, default=20)
    ap.add_argument('--seed', type=int, default=5)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    recs = []
    for g in range(a.games):
        topo = rng.randrange(4); seat = rng.randrange(2); seed = rng.randrange(2 ** 32)
        style = rng.randrange(5)
        md = P.generate_map(topo, seed); mp = P.Map(md)
        eng = P.Engine(mp)
        prof = P.Professor(style, 1 - seat)
        pol = g % 3
        mirror = P.Professor(rng.randrange(5), seat)
        orig = prof.replan
        def rp(view, prof=prof, orig=orig, md=md, style=style):
            side = view.side
            st = (side.home, side.score, side.crafted, [b[:] for b in side.boats], side.wh[:], side.ws[:],
                  side.jobs[:], list(view.claims), view.round, view.seat)
            est = prof.est[:]
            best = orig(view)
            out = None if best is None else (best[0].actions(), list(best[1]), best[2])
            recs.append((md, style, st, est, out))
            return best
        prof.replan = rp
        while eng.round < 80:
            if pol == 0:
                mine = P.WAIT
            elif pol == 1:
                legal = eng.legal(seat)
                pool = [o for o in legal if o[0] in ('deliver', 'build_workshop', 'craft')]
                mine = P.WAIT if rng.random() < 0.25 else rng.choice(pool if pool and rng.random() > 0.2 else legal)
            else:
                mine = mirror.choose(eng.view(seat))
            po = prof.choose(eng.view(1 - seat))
            o = [None, None]; o[seat] = mine; o[1 - seat] = po
            eng.step(o)
    with open(a.out, 'wb') as f:
        pickle.dump(recs, f)
    print(len(recs), 'replans')

main()
