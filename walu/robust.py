"""Robustness sweep: random oceans in the same rule family as the practice reef."""
import sys, random, statistics, itertools, numpy as np
from multiprocessing import Pool
sys.path.insert(0, "task"); import reef
from strategies import Base

def random_ocean(seed):
    r = random.Random(seed)
    spots = []
    n_school = r.choice([1, 2, 3, 3])
    for i in range(10):
        if i < n_school:
            if i == 0:  # the real walu spot
                spots.append(reef.Spot("school", p=r.uniform(0.25, 0.45), big=r.uniform(16, 24), big_sd=r.uniform(3, 6), base=r.uniform(0.3, 0.9), base_sd=0.4))
            else:       # decoys
                spots.append(reef.Spot("school", p=r.uniform(0.03, 0.15), big=r.uniform(16, 24), big_sd=r.uniform(3, 6), base=r.uniform(0.3, 0.9), base_sd=0.4))
        else:
            m = r.uniform(0.6, 3.2)
            spots.append(reef.Spot("steady", mean=m, sd=r.uniform(0.5, 1.0) * m))
    r.shuffle(spots)
    return reef.Ocean(10, 1000, tuple(range(seed * 1000, seed * 1000 + 40)), tuple(spots), 5300.0)

OCEANS = [random_ocean(s) for s in range(1, 25)]

def make(c, b, init, floor):
    class U(Base):
        def choose(self):
            if self.t < init * self.n: return self.t % self.n
            n = self.cnt; lt = np.log(self.t + 1)
            v = np.maximum(self.var(), floor)
            return int(np.argmax(self.mean() + np.sqrt(c * v * lt / n) + b * lt / n))
    return U

def job(params):
    cls = make(*params)
    per = [statistics.mean(reef.play_all(cls, o)) for o in OCEANS]
    return params, statistics.mean(per), min(per), sum(x >= 5300 for x in per)

if __name__ == "__main__":
    grid = list(itertools.product([1.0, 2.0, 3.0, 4.0], [0.0, 1.0, 2.0, 4.0], [1, 2, 3], [0.5, 2.0, 8.0]))
    with Pool() as p:
        res = p.map(job, grid)
    res.sort(key=lambda r: -r[1])
    print("oracle per ocean:", [round(max(reef.expected_catch(s, 5000) for s in o.spots) * 1000) for o in OCEANS])
    for params, m, mn, npass in res[:20]:
        print(f"mean={m:7.1f} worst_ocean={mn:7.1f} oceans_pass={npass}/{len(OCEANS)} params={params}")
