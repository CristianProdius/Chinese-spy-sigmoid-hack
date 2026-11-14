"""Practice only: replay real engine games in the C simulator and compare outcomes."""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser("~/island-duel/bundle"))
sys.path.insert(0, os.path.expanduser("~/island-duel/agent"))
from client import ArenaClient  # noqa: E402
from style_agent import choose_action  # noqa: E402
from simlib import Game  # noqa: E402

trace = "/tmp/simcheck.trace"
os.environ["CHAMP_TRACE"] = trace
here = os.path.dirname(os.path.abspath(__file__))
ok = 0
games = int(sys.argv[1])
with ArenaClient(os.path.join(here, "samoa-gdb")) as env:
    for k in range(games):
        arena, seed = k % 32, 9000 + k
        open(trace, "w").close()
        r = env.reset(arena, seed)
        ours = []
        while not r["done"]:
            a = choose_action(r["observation"])
            ours.append(a)
            r = env.step(a)
        recs = [json.loads(l) for l in open(trace)]
        st = next(x for x in recs if x["t"] == "state")
        champ_actions = [x["a"] for x in recs if x["t"] == "action"]
        seat = arena % 2
        g = Game(st, 1 - seat, st["profile"])
        sim_champ = []
        it = iter(ours)
        while g.get("remaining") > 0:
            if g.get("cur") == seat:
                g.apply(next(it))
            else:
                a = g.champ()
                sim_champ.append(a)
                g.apply(a)
        same = sim_champ == champ_actions and g.get("score", 2) == r["scores"]
        ok += same
        if not same:
            print("MISMATCH game", k, "engine", r["scores"], "sim", g.get("score", 2),
                  "first diff", next((i for i, (x, y) in enumerate(zip(sim_champ, champ_actions)) if x != y), None))
print(f"{ok}/{games} games reproduced exactly")
