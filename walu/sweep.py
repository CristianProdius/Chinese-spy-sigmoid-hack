import itertools, sys, numpy as np
from multiprocessing import Pool
import sim
from strategies import Base

def make_ucbv(c, b, init, floor):
    class U(Base):
        def choose(self):
            if self.t < init * self.n: return self.t % self.n
            n = self.cnt; lt = np.log(self.t + 1)
            v = np.maximum(self.var(), floor)
            return int(np.argmax(self.mean() + np.sqrt(c * v * lt / n) + b * lt / n))
    return U

def make_ts(prior_kg, prior_n, init, floor):
    class TS(Base):
        def choose(self):
            if self.t < init * self.n: return self.t % self.n
            n = self.cnt + prior_n
            m = (self.sum + prior_kg * prior_n) / n
            v = np.maximum(self.var(), floor)
            return int(np.argmax(self.rng.normal(m, np.sqrt(v / n))))
    return TS

def job(args):
    kind, params = args
    cls = make_ucbv(*params) if kind == "ucbv" else make_ts(*params)
    out = {}
    for sc, scen in sim.SCENARIOS.items():
        m, sd, orc = sim.run(cls, scen, n_days=200, seed=123)
        out[sc] = (m, orc)
    score = np.mean([m / o for m, o in out.values()])
    return kind, params, score, out

if __name__ == "__main__":
    grid = []
    for c in [0.5, 1.0, 2.0, 3.0]:
        for b in [0.0, 1.0, 2.0, 4.0, 8.0]:
            for init in [1, 2, 3]:
                for floor in [0.5, 2.0, 8.0]:
                    grid.append(("ucbv", (c, b, init, floor)))
    for pk in [5.0, 10.0, 20.0]:
        for pn in [0.5, 1.0, 2.0, 4.0]:
            for init in [1, 2]:
                for floor in [0.5, 2.0, 8.0]:
                    grid.append(("ts", (pk, pn, init, floor)))
    with Pool() as p:
        res = p.map(job, grid, chunksize=2)
    res.sort(key=lambda r: -r[2])
    for kind, params, score, out in res[:25]:
        print(f"{score:.4f} {kind} {params} " + " ".join(f"{sc}={m:.0f}/{o:.0f}" for sc, (m, o) in out.items()))
