"""RL policy + energy-reserve rule.

The champion searches 4 plies: it does not capture a tile when it can see us
capture it straight back. Keeping enough energy to recapture therefore deters
its captures. If the policy's move would leave us below RESERVE energy, rest
instead (unless resting would be wasted at the cap, the move is a capture of
at least CAPTURE_OK value, or the game is in its last ENDGAME decisions).

Env: ID_RESERVE (default 5), ID_CAPTURE_OK (default 99), ID_ENDGAME (default 6),
plus rl_agent's ID_MODEL / ID_DEVICE.
"""

import os

import rl_agent

RESERVE = int(os.environ.get("ID_RESERVE", "5"))
CAPTURE_OK = int(os.environ.get("ID_CAPTURE_OK", "99"))
ENDGAME = int(os.environ.get("ID_ENDGAME", "6"))


def reset_agent():
    rl_agent.reset_agent()


def choose_action(state):
    a = rl_agent.choose_action(state)
    if a is None:
        return None
    seat = state["seat"]
    e = state["energy"][seat]
    capture = state["owners"][a] == 1 - seat
    cost = state["costs"][a] + (2 if capture else 0)
    decisions_left = (state["actions_remaining"] + 1) // 2
    if decisions_left <= ENDGAME or e >= 7:
        return a
    if capture and state["weights"][a] >= CAPTURE_OK:
        return a
    if e - cost < RESERVE:
        return None
    return a
