import sys, traceback, json
out = open("/app/inject.out", "w")
def P(*a):
    print(*a, file=out); out.flush()
try:
    import numpy as np
    from lab import fitness, level, engine, brain, evolution
    for name, m in [("fitness", fitness), ("level", level), ("engine", engine), ("brain", brain), ("evolution", evolution)]:
        P("=" * 20, name)
        for k, v in sorted(vars(m).items()):
            if k.startswith("__"): continue
            r = repr(v)
            if len(r) > 1500: r = r[:1500] + "..."
            P(f"{k} = {r}")
    P("=" * 20, "run proven genome")
    g = np.load("/tmp/" + [d for d in __import__("os").listdir("/tmp") if d.startswith("onefile_")][0] + "/lab/proven.npy")
    P("genome", g.shape, g.dtype)
    b = brain.Brain.from_genome(g)
    env = engine.MarathonEnv(reward_fn=fitness.reward) if "reward_fn" in engine.MarathonEnv.__init__.__code__.co_varnames else engine.MarathonEnv()
    P("env attrs", [k for k in vars(env).keys()])
    obs = env.reset()
    total = 0.0; steps = 0
    log = []
    while not env.done() if callable(getattr(env, "done", None)) else not env.done:
        a = b.act(obs) if obs is not None else b.act(env.observe())
        res = env.step(a)
        steps += 1
        if steps > 20000: break
        obs = res[0] if isinstance(res, tuple) else env.observe()
    P("steps", steps, "x", getattr(env, "x", None), "won", getattr(env, "won", None), "dead", getattr(env, "dead", None))
    P("coins_got", getattr(env, "coins_got", None))
    P("coins taken", getattr(env, "taken", None), getattr(env, "coins", None))
    P("info", env.info() if callable(getattr(env, "info", None)) else None)
except Exception:
    P(traceback.format_exc())
out.close()
