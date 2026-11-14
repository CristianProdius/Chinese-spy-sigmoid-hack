import numpy as np

class Base:
    def __init__(self, n_spots, n_casts, seed=0):
        self.n, self.T = n_spots, n_casts
        self.rng = np.random.default_rng(seed)
        self.t = 0
        self.cnt = np.zeros(n_spots)
        self.sum = np.zeros(n_spots)
        self.sq = np.zeros(n_spots)
    def update(self, a, r):
        self.t += 1; self.cnt[a] += 1; self.sum[a] += r; self.sq[a] += r * r
    def mean(self):
        return self.sum / np.maximum(self.cnt, 1)
    def var(self):
        m = self.mean()
        return np.maximum(self.sq / np.maximum(self.cnt, 1) - m * m, 1e-6)

class Greedy(Base):
    def choose(self):
        if self.t < self.n: return self.t
        return int(np.argmax(self.mean()))

class Random(Base):
    def choose(self): return int(self.rng.integers(self.n))

class EpsGreedy(Base):
    eps = 0.05
    def choose(self):
        if self.t < 2 * self.n: return self.t % self.n
        if self.rng.random() < self.eps: return int(self.rng.integers(self.n))
        return int(np.argmax(self.mean()))

class UCB1(Base):
    c = 2.0
    def choose(self):
        if self.t < self.n: return self.t
        return int(np.argmax(self.mean() + np.sqrt(self.c * np.log(self.t + 1) / self.cnt)))

class UCBV(Base):
    """UCB-Tuned / UCB-V: variance-aware, good for heavy-tailed payoffs."""
    def choose(self):
        if self.t < 2 * self.n: return self.t % self.n
        n = self.cnt; lt = np.log(self.t + 1)
        b = np.sqrt(2 * self.var() * lt / n) + 3 * 20.0 * lt / n * 0.1
        return int(np.argmax(self.mean() + b))

class GaussTS(Base):
    """Thompson sampling with per-arm Gaussian posterior on the mean using empirical variance."""
    init = 2
    def choose(self):
        if self.t < self.init * self.n: return self.t % self.n
        m = self.mean(); v = self.var()
        # inflate variance for low counts (unknown variance -> t-like behaviour)
        sd = np.sqrt(v / self.cnt) * (1 + 2.0 / self.cnt)
        return int(np.argmax(self.rng.normal(m, sd)))

class BootstrapTS(Base):
    """Non-parametric TS: Bayesian bootstrap on observed rewards per arm."""
    init = 2
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.hist = [[] for _ in range(self.n)]
    def update(self, a, r):
        super().update(a, r); self.hist[a].append(r)
    def choose(self):
        if self.t < self.init * self.n: return self.t % self.n
        s = np.empty(self.n)
        for a in range(self.n):
            h = np.asarray(self.hist[a])
            w = self.rng.dirichlet(np.ones(len(h) + 1))
            # pseudo-observation = optimistic prior (20kg) to keep exploring sparse arms
            s[a] = w[:-1] @ h + w[-1] * 20.0
        return int(np.argmax(s))

class ExploreCommit(Base):
    k = 25
    def choose(self):
        if self.t < self.k * self.n: return self.t % self.n
        return int(np.argmax(self.mean()))

class SuccElim(Base):
    """Successive elimination with variance-aware confidence."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.alive = list(range(self.n)); self.i = 0
    def choose(self):
        if len(self.alive) == 1: return self.alive[0]
        a = self.alive[self.i % len(self.alive)]; self.i += 1; return a
    def update(self, a, r):
        super().update(a, r)
        if len(self.alive) > 1 and self.cnt[a] >= 3 and self.i % len(self.alive) == 0:
            al = np.array(self.alive); m = self.mean()[al]; n = self.cnt[al]
            ci = np.sqrt(2 * self.var()[al] * np.log(4 * self.T) / n) + 20.0 * np.log(4 * self.T) / (n * 1.0) * 0.1
            lo = m - ci; hi = m + ci
            keep = hi >= lo.max()
            self.alive = [int(x) for x in al[keep]]

ALL = ["Greedy", "EpsGreedy", "UCB1", "UCBV", "GaussTS", "BootstrapTS", "ExploreCommit", "SuccElim"]
