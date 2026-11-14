"""Observation -> network input, shared by training and the submitted agent.

The board is canonicalised so the agent's start tile is always cell 0: seat 1
boards are rotated 180 degrees (cell i <-> 224 - i). A per-game Memory keeps
terrain and last-seen owners of cells that have dropped back into fog.
"""

from __future__ import annotations

import numpy as np

N = 15
CELLS = N * N
NUM_ACTIONS = CELLS + 1  # index CELLS = rest
C = 24  # input planes


class Memory:
    __slots__ = ("w", "c", "owner")

    def __init__(self):
        self.w = np.zeros(CELLS, np.float32)        # known weight (0 if unknown)
        self.c = np.zeros(CELLS, np.float32)        # known cost
        self.owner = np.full(CELLS, -3, np.int8)    # last seen owner (raw seats)


def _adj(m: np.ndarray) -> np.ndarray:
    out = np.zeros_like(m)
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def featurize(obs: dict, mem: Memory):
    """Returns (planes [C,15,15] float32, legal mask [226] bool)."""
    seat = obs["seat"]
    opp = 1 - seat
    vis = np.fromiter(obs["visible"], bool, CELLS)
    own = np.fromiter(obs["owners"], np.int8, CELLS)
    w = np.array([x if x is not None else 0 for x in obs["weights"]], np.float32)
    cst = np.array([x if x is not None else 0 for x in obs["costs"]], np.float32)
    mem.w[vis] = w[vis]
    mem.c[vis] = cst[vis]
    mem.owner[vis] = own[vis]

    o = mem.owner
    mine = (o == seat) & vis
    enemy_vis = (o == opp) & vis
    enemy_mem = (o == opp) & ~vis
    neutral_vis = (o == -1) & vis
    neutral_mem = (o == -1) & ~vis
    blocked = o == -2
    unknown = o == -3

    legal = np.zeros(NUM_ACTIONS, bool)
    for a in obs["legal_actions"]:
        legal[CELLS if a is None else a] = True
    claim = legal[:CELLS] & (o == -1)
    capture = legal[:CELLS] & (o == opp)

    e_me, e_op = obs["energy"][seat], obs["energy"][opp]
    starts = np.zeros(CELLS, bool)
    starts[0] = starts[CELLS - 1] = True
    grid = lambda x: x.reshape(N, N)  # noqa: E731
    near_enemy = _adj(grid(enemy_vis)).ravel()
    threatened = mine & near_enemy & ~starts & (mem.c + 2 <= e_op)
    exposed = mine & near_enemy & ~starts

    planes = np.zeros((C, CELLS), np.float32)
    planes[0] = mine
    planes[1] = enemy_vis
    planes[2] = enemy_mem
    planes[3] = neutral_vis
    planes[4] = neutral_mem
    planes[5] = blocked
    planes[6] = unknown
    planes[7] = mem.w / 9.0
    planes[8] = mem.c / 4.0
    planes[9] = claim
    planes[10] = capture
    planes[11] = threatened * (mem.w / 9.0)
    planes[12] = exposed
    planes[13] = vis
    planes[14] = e_me / 9.0
    planes[15] = e_op / 9.0
    planes[16] = obs["actions_remaining"] / 256.0
    planes[17] = (obs["scores"][seat] - obs["scores"][opp]) / 100.0
    planes[18 + obs["opponent_profile"]] = 1.0
    planes[21] = seat
    planes[22] = (mem.c + 2 <= e_me) & enemy_vis   # affordable captures (any adjacency)
    planes[23] = starts

    if seat == 1:  # rotate so our start is cell 0
        planes = planes[:, ::-1]
        legal = np.concatenate([legal[:CELLS][::-1], legal[CELLS:]])
    return np.ascontiguousarray(planes.reshape(C, N, N)), legal


def to_engine_action(a: int, seat: int):
    """Canonical action index -> engine action (cell or None)."""
    if a == CELLS:
        return None
    return CELLS - 1 - a if seat == 1 else a
