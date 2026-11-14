"""Island Duel agent: alpha-beta search with an evaluation tuned against the champion.

The champion's decision procedure was reverse-engineered from the engine and
cloned in C (champ.c, exact on every move tested). Our agent runs the same
search machinery from our seat, on our own fogged memory of the board, with a
different evaluation whose weights were tuned by playing thousands of games
against the clone in the C simulator (sim.c, tune.py).

Env: ID_PARAMS (JSON file with "prm", "pw", "pc", optional "budget", "depth").
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simlib import DEFAULT_PRM, search_decide_ext  # noqa: E402

_cfg = {"prm": DEFAULT_PRM, "pw": 5, "pc": 3, "budget": 2048, "depth": 4}
_path = os.environ.get("ID_PARAMS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "params.json"))
if os.path.exists(_path):
    _cfg.update(json.load(open(_path)))
_mem = None


def reset_agent():
    global _mem
    _mem = None


def choose_action(state):
    global _mem
    seat = state["seat"]
    if _mem is None:
        own, w, c = [-3] * 225, [int(round(_cfg["pw"]))] * 225, [int(round(_cfg["pc"]))] * 225
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
    a = search_decide_ext(t, seat, _cfg["prm"], _cfg["budget"], _cfg["depth"], _mem)
    a = None if a < 0 else a
    if a not in state["legal_actions"]:
        a = None
    return a
