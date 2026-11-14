"""Stand-in reef simulator + strategy benchmark (real reef.py not available yet).

Scenario families mirror the storyline: ~9 steady reef spots (1-2 kg mean, noisy),
1 walu spot that pays ~20 kg with some probability p, else ~0.
"""
import sys, numpy as np, importlib, time

def make_day(rng, scen):
    n = 10
    kind = scen["kind"]
    walu_p = rng.uniform(*scen["walu_p"])
    walu_kg = 20.0
    steady_mu = rng.uniform(scen["steady_lo"], scen["steady_hi"], size=n)
    walu = rng.integers(n)
    def pull(arm):
        if arm == walu:
            if kind == "bern":
                return walu_kg if rng.random() < walu_p else 0.0
            else:  # bernoulli + small background
                return (walu_kg if rng.random() < walu_p else 0.0) + max(0.0, rng.normal(0.3, 0.3))
        mu = steady_mu[arm]
        return max(0.0, rng.normal(mu, scen["steady_sd"]))
    best_ev = max(walu_p * walu_kg + (0.0 if kind == "bern" else 0.3), steady_mu.max())
    return pull, best_ev

SCENARIOS = {
    "easy":   dict(kind="bern", walu_p=(0.30, 0.40), steady_lo=1.0, steady_hi=2.0, steady_sd=0.7),
    "mid":    dict(kind="bern", walu_p=(0.27, 0.33), steady_lo=1.0, steady_hi=2.0, steady_sd=1.0),
    "hard":   dict(kind="mix",  walu_p=(0.25, 0.30), steady_lo=1.0, steady_hi=2.5, steady_sd=1.5),
    "vhard":  dict(kind="mix",  walu_p=(0.20, 0.28), steady_lo=1.0, steady_hi=2.5, steady_sd=1.5),
}

def run(strategy_cls, scen, n_days=100, n_casts=1000, seed=0):
    rng = np.random.default_rng(seed)
    totals, oracles = [], []
    for d in range(n_days):
        pull, best_ev = make_day(rng, scen)
        s = strategy_cls(10, n_casts, seed=d)
        tot = 0.0
        for t in range(n_casts):
            a = s.choose()
            r = pull(a)
            s.update(a, r)
            tot += r
        totals.append(tot); oracles.append(best_ev * n_casts)
    return float(np.mean(totals)), float(np.std(totals)), float(np.mean(oracles))

if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "strategies")
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else mod.ALL
    for sc, scen in SCENARIOS.items():
        for nm in names:
            t0 = time.time()
            m, sd, orc = run(getattr(mod, nm), scen)
            print(f"{sc:6s} {nm:18s} mean={m:7.1f} sd={sd:6.1f} oracle={orc:7.1f} ratio={m/orc:.3f} ({time.time()-t0:.1f}s)", flush=True)
