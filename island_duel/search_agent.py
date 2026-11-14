"""Island Duel search agent.

Keeps a memory of everything seen this game (terrain is static), rebuilds the
board from the latest observation, and runs an alpha-beta search over single
actions (ours, the champion's, ours, ...) on the visible board. The champion's
expansion into fog is modelled as one abstract move worth EXP_GAIN for
EXP_COST energy. Leaves are scored by score margin plus the value of energy
still usable before the game ends, with a one-move capture quiescence.

Parameters can be overridden with the ID_PARAMS environment variable (JSON).
"""

from __future__ import annotations

import json
import os

N = 15
CELLS = N * N
NB = [tuple((r + dr) * N + c + dc for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= r + dr < N and 0 <= c + dc < N) for r in range(N) for c in range(N)]
STARTS = (0, CELLS - 1)
REST, EXPAND = -1, -2

P = {
    "depth": 4,           # plies searched (one action each)
    "k_energy": 1.6,      # points per unit of energy that can still be spent
    "energy_horizon": 12,  # energy value fades over the last N decisions
    "exp_gain": 3.0,      # champion's fog expansion: points
    "exp_cost": 2,        # ... and energy
    "q_capture": 1.0,     # weight of the side-to-move's best capture at a leaf
    "width": 10,          # moves searched per node (best by ordering)
    "exposure": 0.0,      # penalty per point of our value adjacent to enemy tiles
}
P.update(json.loads(os.environ.get("ID_PARAMS", "{}")))

_mem = {}


def reset_agent():
    _mem.clear()


class Board:
    __slots__ = ("owner", "w", "c", "energy", "score", "tiles", "rem")

    def __init__(self, owner, w, c, energy, score, rem):
        self.owner, self.w, self.c = owner, w, c
        self.energy, self.score, self.rem = energy, score, rem
        self.tiles = ({i for i in range(CELLS) if owner[i] == 0},
                      {i for i in range(CELLS) if owner[i] == 1})


def moves(b: Board, p: int):
    """(cell, cost, gain_for_p, swing) for every affordable claim/capture of p."""
    e, own, w, c = b.energy[p], b.owner, b.w, b.c
    out, seen = [], set()
    q = 1 - p
    for i in b.tiles[p]:
        for j in NB[i]:
            if j in seen:
                continue
            seen.add(j)
            o = own[j]
            if o == -1:
                cost = c[j]
                if cost <= e:
                    out.append((j, cost, w[j], w[j]))
            elif o == q and j not in STARTS:
                cost = c[j] + 2
                if cost <= e:
                    out.append((j, cost, w[j], 2 * w[j]))
    return out


def energy_value(b: Board, p: int, rem_p: int) -> float:
    # Energy is worth k per unit while it can still be spent.
    if rem_p <= 0:
        return 0.0
    f = min(1.0, rem_p / P["energy_horizon"])
    return P["k_energy"] * f * b.energy[p]


def evaluate(b: Board, me: int, to_move: int) -> float:
    opp = 1 - me
    rem_me = (b.rem + (1 if to_move == me else 0)) // 2
    rem_op = (b.rem + (1 if to_move == opp else 0)) // 2
    v = b.score[me] - b.score[opp]
    v += energy_value(b, me, rem_me) - energy_value(b, opp, rem_op)
    if b.rem > 0 and P["q_capture"]:
        best = 0.0
        k = P["k_energy"]
        for (j, cost, gain, swing) in moves(b, to_move):
            if swing != gain:  # capture
                val = swing - k * cost
                if val > best:
                    best = val
        v += P["q_capture"] * (best if to_move == me else -best)
    if P["exposure"]:
        exp = 0
        for i in b.tiles[me]:
            if b.w[i] and any(b.owner[j] == opp for j in NB[i]):
                exp += b.w[i]
        v -= P["exposure"] * exp
    return v


def ordered(b: Board, p: int):
    ms = moves(b, p)
    ms.sort(key=lambda m: -(m[3] - 0.8 * m[1]))
    acts = [m[0] for m in ms[: P["width"]]]
    acts.append(REST)
    return acts


def apply(b: Board, p: int, a: int):
    """Apply action; return undo record."""
    q = 1 - p
    e0 = b.energy[p]
    if a == REST:
        b.energy[p] = min(9, e0 + 3)
        b.rem -= 1
        return (a, e0, None)
    if a == EXPAND:
        b.energy[p] = e0 - P["exp_cost"]
        b.score[p] += P["exp_gain"]
        b.rem -= 1
        return (a, e0, None)
    prev = b.owner[a]
    if prev == -1:
        b.energy[p] = e0 - b.c[a]
    else:
        b.energy[p] = e0 - b.c[a] - 2
        b.score[q] -= b.w[a]
        b.tiles[q].discard(a)
    b.owner[a] = p
    b.tiles[p].add(a)
    b.score[p] += b.w[a]
    b.rem -= 1
    return (a, e0, prev)


def undo(b: Board, p: int, rec):
    a, e0, prev = rec
    b.energy[p] = e0
    b.rem += 1
    if a == REST:
        return
    if a == EXPAND:
        b.score[p] -= P["exp_gain"]
        return
    b.owner[a] = prev
    b.tiles[p].discard(a)
    b.score[p] -= b.w[a]
    if prev != -1:
        b.tiles[prev].add(a)
        b.score[prev] += b.w[a]


def search(b: Board, me: int, p: int, depth: int, alpha: float, beta: float) -> float:
    if depth == 0 or b.rem == 0:
        return evaluate(b, me, p)
    acts = ordered(b, p)
    if p != me and b.energy[p] >= P["exp_cost"]:
        acts.append(EXPAND)
    maximizing = p == me
    best = -1e18 if maximizing else 1e18
    for a in acts:
        rec = apply(b, p, a)
        v = search(b, me, 1 - p, depth - 1, alpha, beta)
        undo(b, p, rec)
        if maximizing:
            if v > best:
                best = v
            if best > alpha:
                alpha = best
        else:
            if v < best:
                best = v
            if best < beta:
                beta = best
        if alpha >= beta:
            break
    return best


def _board_from(state) -> Board:
    seat = state["seat"]
    mem = _mem.setdefault("terrain", {})
    seen_owner = _mem.setdefault("owner", {})
    for i in range(CELLS):
        if state["visible"][i]:
            mem[i] = (state["weights"][i], state["costs"][i])
            seen_owner[i] = state["owners"][i]
    owner = [-3] * CELLS
    w = [0] * CELLS
    c = [0] * CELLS
    for i, (wi, ci) in mem.items():
        w[i], c[i] = wi or 0, ci or 0
        o = state["owners"][i] if state["visible"][i] else seen_owner.get(i, -3)
        # A remembered tile of ours that is now hidden cannot exist (ours are visible);
        # a remembered neutral/enemy tile may have changed hands, keep the last view.
        if o == seat and not state["visible"][i]:
            o = 1 - seat
        owner[i] = o
    return Board(owner, w, c, list(state["energy"]), list(state["scores"]),
                 state["actions_remaining"])


def choose_action(state):
    me = state["seat"]
    legal = state["legal_actions"]
    if len(legal) == 1:
        return legal[0]
    b = _board_from(state)
    depth = min(P["depth"], b.rem)
    best_a, best_v = None, -1e18
    alpha = -1e18
    for a in ordered(b, me):
        rec = apply(b, me, a)
        v = search(b, me, 1 - me, depth - 1, alpha, 1e18)
        undo(b, me, rec)
        if v > best_v:
            best_a, best_v = a, v
            alpha = v
    act = None if best_a == REST else best_a
    if act not in legal:
        act = None
    return act
