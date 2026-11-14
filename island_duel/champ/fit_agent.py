"""Island Duel agent: alpha-beta search with a fitted evaluation, built against a
clone of the champion.

How it was built (details in island_duel/EXPLANATION.md):
  * The champion's decision procedure was reverse-engineered from the engine
    binary and re-implemented in C (champ.c): iterative-deepening negamax
    alpha-beta, <=4 plies, 2,048-node budget, transposition table, and a
    per-profile evaluation. The clone reproduces the engine's moves exactly.
  * A C simulator (sim.c) plays games against the clone at native speed, on
    maps from the real generator, under the same fog rules.
  * Our agent reuses the search machinery from its own seat, on its own fogged
    memory of the board, with a larger node budget and an evaluation fitted by
    phase-bucketed logistic regression of game outcomes on board features
    (fit_eval.py, Texel-style tuning) over ~1.5M simulated positions.

The agent only reads the observation it is given. Env: ID_THETA (theta json),
ID_BUDGET (131072), ID_DEPTH (16).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from simlib import search_decide_fit  # noqa: E402

THETA_PATH = os.environ.get("ID_THETA", os.path.join(HERE, "theta.json"))
BUDGET = int(os.environ.get("ID_BUDGET", "131072"))
DEPTH = int(os.environ.get("ID_DEPTH", "16"))
PRIOR_W, PRIOR_C = 6, 3  # memory prior for never-seen tiles
_cfg = json.load(open(THETA_PATH))
_mem = None


def reset_agent():
    global _mem
    _mem = None


def choose_action(state):
    global _mem
    seat = state["seat"]
    if _mem is None:
        own, w, c = [-3] * 225, [PRIOR_W] * 225, [PRIOR_C] * 225
        own[0], own[224] = 0, 1
        w[0] = w[224] = c[0] = c[224] = 0
        _mem = (own, w, c)
    owners = state["owners"]
    t = {
        "blocked": [1 if o == -2 else 0 for o in owners],
        "owner": [o if o in (0, 1) else -1 for o in owners],
        "w": [x if x is not None else 0 for x in state["weights"]],
        "c": [x if x is not None else 0 for x in state["costs"]],
        "energy": list(state["energy"]), "score": list(state["scores"]),
        "remaining": state["actions_remaining"],
    }
    a = search_decide_fit(t, seat, _cfg["theta"], _cfg.get("ha", 3), _cfg.get("hb", 4), BUDGET, DEPTH, _mem)
    a = None if a < 0 else a
    if a not in state["legal_actions"]:  # never expected; stay legal regardless
        a = None
    return a
