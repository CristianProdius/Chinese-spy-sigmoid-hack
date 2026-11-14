import traceback
out = open("/app/verify.out", "w")
def P(*a):
    print(*a, file=out); out.flush()
try:
    from lab import fitness as F, level as L, engine as E
    env = E.MarathonEnv(reward_fn=F.reward); env.reset()
    env.step(2)
    info = env.step(2)[3]
    base = dict(info); base["coins_got"] = []
    P("keys", list(info.keys()))
    P("reward no coin      ", F.reward(dict(base)))
    for c in L.COIN_SITES:
        i = dict(base); i["coins_got"] = [(c, L.COIN_ROW)]
        P("reward coin", c, "sign", F._SIGN[(c, L.COIN_ROW)], "->", round(F.reward(i) - F.reward(dict(base)), 3))
except Exception:
    P(traceback.format_exc())
out.close()
