"""Walu Season submission.

Protocol (matches the official starter): read test-input.json (n_spots, n_casts, n_days); for every
cast print a spot number to stdout, flush, then read the catch (kg) from stdin.
"""
import json
import sys

import numpy as np


class Strategy:
    """Variance-aware UCB (UCB-V / UCB-Tuned style).

    Why: catches are heavy-tailed (the walu spot pays ~20 kg rarely, 0 otherwise),
    so a mean-only bonus (UCB1) or a Gaussian Thompson sampler collapses the
    walu arm after a few empty casts. Scaling the bonus by the empirical variance
    keeps a high-variance arm alive until its mean is pinned down, while cheap
    low-variance reef spots are abandoned quickly.
    """

    C = 3.0        # multiplier on the variance term
    B = 0.0        # log(t)/n range term; the variance floor already covers heavy tails
    INIT = 2       # round-robin casts per spot before the bonus kicks in
    VAR_FLOOR = 8.0  # keeps zero-variance arms (all 0s or all ~1.5s) explorable; tuned on 24 random reefs

    def __init__(self, n_spots: int, n_casts: int, seed: int = 0):
        self.n = n_spots
        self.T = n_casts
        self.rng = np.random.default_rng(seed)
        self.t = 0
        self.cnt = np.zeros(n_spots)
        self.sum = np.zeros(n_spots)
        self.sq = np.zeros(n_spots)

    def choose(self) -> int:
        if self.t < self.INIT * self.n:
            return self.t % self.n
        n = self.cnt
        mean = self.sum / n
        var = np.maximum(self.sq / n - mean * mean, self.VAR_FLOOR)
        lt = np.log(self.t + 1.0)
        score = mean + np.sqrt(self.C * var * lt / n) + self.B * lt / n
        return int(np.argmax(score))

    def update(self, spot: int, catch: float) -> None:
        self.t += 1
        self.cnt[spot] += 1
        self.sum[spot] += catch
        self.sq[spot] += catch * catch


def main() -> None:
    with open("test-input.json") as f:
        cfg = json.load(f)
    n_spots = int(cfg["n_spots"])
    n_casts = int(cfg["n_casts"])
    n_days = int(cfg["n_days"])

    out = sys.stdout
    inp = sys.stdin
    for day in range(n_days):
        strat = Strategy(n_spots, n_casts, seed=day)
        for _ in range(n_casts):
            spot = strat.choose()
            out.write(f"{spot}\n")
            out.flush()
            line = inp.readline()
            if not line:
                return
            strat.update(spot, float(line.strip()))


if __name__ == "__main__":
    main()
