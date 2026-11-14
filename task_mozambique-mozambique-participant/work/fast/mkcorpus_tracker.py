"""Record the replan inputs of reference 5-hypothesis tracking on bench trajectories."""
import sys, os, pickle
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import bench
trajs = pickle.load(open(sys.argv[1], 'rb'))
recs = []
orig = P.Professor.replan
def rp(self, view):
    side = view.side
    st = (side.home, side.score, side.crafted, [b[:] for b in side.boats], side.wh[:], side.ws[:], side.jobs[:], list(view.claims), view.round, view.seat)
    est = self.est[:]
    best = orig(self, view)
    out = None if best is None else (best[0].actions(), list(best[1]), best[2])
    style = P.STYLES.index((self.B, self.A, self.W))
    recs.append((self._md, style, st, est, out))
    return best
P.Professor.replan = rp
orig_choose = P.Professor.choose
for t in trajs:
    md = t['obs'][0]['map']
    P.Professor._md = md
    bench.play_tracked('ref', t)
pickle.dump(recs, open(sys.argv[2], 'wb'))
print(len(recs), 'replans')
