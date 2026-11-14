import traceback, inspect
out = open("/app/probe.out", "w")
def P(*a):
    print(*a, file=out); out.flush()
try:
    import numpy as np
    from lab import fitness as F, level as L, engine as E, brain as B, evolution as V
    for fn in [F._spread, F._terms, F.defined, F.reward, E.MarathonEnv.__init__, E.MarathonEnv.step, E.MarathonEnv.info, E.MarathonEnv.features, B.Brain.act, B.Brain.from_genome, V._proven, V.Lab.__init__, V.Lab.replay, V.Lab.finish, V.Lab.leader]:
        try: P(fn.__qualname__, inspect.signature(fn))
        except Exception as e: P(fn.__qualname__, "sig-err", e)
    for args in [(919247,), (131,), (7,), (20,)]:
        for fn in [F._spread, F._terms, F.defined]:
            try: P(fn.__name__, args, "->", fn(*args))
            except Exception as e: P(fn.__name__, args, "err", repr(e)[:200])
    try: P("defined()", F.defined())
    except Exception as e: P("defined() err", repr(e)[:200])
    try: P("_terms()", F._terms())
    except Exception as e: P("_terms() err", repr(e)[:200])
    env = E.MarathonEnv()
    P("env vars", {k: (v if not hasattr(v, "__len__") or len(repr(v)) < 200 else type(v)) for k, v in vars(env).items()})
    env.reset()
    P("info()", env.info())
    # probe reward with synthetic infos
    base = env.info()
    import copy
    P("reward(base)", F.reward(base) if not isinstance(base, dict) else F.reward(dict(base)))
    if isinstance(base, dict):
        for site in L.COIN_SITES:
            i = dict(base); i["coins_taken"] = [(site, L.COIN_ROW)] if "coins_taken" in i else i.get("coins_taken")
            try: P("reward coin", site, F.reward(i))
            except Exception as e: P("reward coin err", site, repr(e)[:200])
except Exception:
    P(traceback.format_exc())
out.close()
