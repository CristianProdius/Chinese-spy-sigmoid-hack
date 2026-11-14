import traceback, os
out = open("/app/run_proven.out", "w")
def P(*a):
    print(*a, file=out); out.flush()
try:
    import numpy as np
    from lab import fitness as F, level as L, engine as E, brain as B, evolution as V
    P("_spread(COIN_SITES) =", F._spread(L.COIN_SITES))
    P("_terms(COIN_SITES) =", F._terms(L.COIN_SITES))
    P("_SIGN =", F._SIGN)
    d = [x for x in os.listdir("/tmp") if x.startswith("onefile_")][0]
    g = np.load(f"/tmp/{d}/lab/proven.npy")
    b = B.Brain.from_genome(g)
    env = E.MarathonEnv(reward_fn=F.reward)
    env.reset()
    steps = 0; total = 0.0; first = None
    while not (env.dead or env.won) and steps < env.max_steps:
        a = b.act(env)
        res = env.step(a)
        if first is None: first = res; P("step() returns:", type(res), repr(res)[:300])
        try: total += float(res[0]) if isinstance(res, tuple) else float(res)
        except Exception: pass
        steps += 1
    P("steps", steps, "x", env.x, "max_x", env.max_x, "won", env.won, "dead", env.dead, "coins", env.coins, "stomps", env.stomps, "score", total)
    P("taken", env.taken)
    taken_cols = sorted({int(t[0]) if isinstance(t, (tuple, list)) else int(t) for t in env.taken})
    P("taken_cols", taken_cols)
    bits = "".join("1" if c in taken_cols else "0" for c in L.COIN_SITES)
    P("taken bits  ", bits)
    P("_SIGN bits  ", "".join(str(F._SIGN[(c, L.COIN_ROW)]) for c in L.COIN_SITES))
    for name, bs in [("taken", bits), ("sign", "".join(str(F._SIGN[(c, L.COIN_ROW)]) for c in L.COIN_SITES))]:
        for a0 in (0, 1):
            P(name, "5-bit A=%d:" % a0, [chr(64 + a0 + int(bs[i:i+5], 2)) if 0 < a0 + int(bs[i:i+5], 2) <= 26 else "?" for i in range(0, 20, 5)])
except Exception:
    P(traceback.format_exc())
out.close()
