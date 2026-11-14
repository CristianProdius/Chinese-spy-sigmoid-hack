"""Parameterised scripted agent for testing play styles against the champion.

Score of a move = rate (value per decision) + adjustments; rest if nothing
beats the rest threshold. Params via ID_STYLE (JSON):
  contact_pen   penalty (x value) for claiming a neutral tile next to an enemy tile
  capture_mult  multiplier on capture rate
  reserve       keep at least this much energy after acting (unless e >= 7)
  exposure_pen  penalty (x value) when the claimed tile would be capturable by
                the champion right now (its energy >= cost + 2)
  min_rate      rest if the best move's score is below this
"""

import json
import os

N = 15
NB = [tuple((r + dr) * N + c + dc for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= r + dr < N and 0 <= c + dc < N) for r in range(N) for c in range(N)]
S = {"patient": 0, "contact_pen": 0.0, "capture_mult": 1.0, "reserve": 0, "exposure_pen": 0.0, "min_rate": 0.0}
S.update(json.loads(os.environ.get("ID_STYLE", "{}")))


def choose_action(state):
    seat = state["seat"]
    opp = 1 - seat
    own, w, c = state["owners"], state["weights"], state["costs"]
    e = state["energy"][seat]
    e_op = state["energy"][opp]
    endgame = state["actions_remaining"] <= 12
    best, best_s, best_cost = None, S["min_rate"], 0
    if S["patient"]:
        cands = set()
        for i in range(N * N):
            if own[i] == seat:
                for j in NB[i]:
                    if (own[j] == -1 or (own[j] == opp and w[j])) and state["visible"][j]:
                        cands.add(j)
    else:
        cands = [a for a in state["legal_actions"] if a is not None]
    for a in cands:
        near_enemy = any(own[j] == opp for j in NB[a])
        if own[a] == opp:
            cost = c[a] + 2
            s = S["capture_mult"] * 6 * w[a] / (5 + c[a])
        else:
            cost = c[a]
            s = 3 * w[a] / (3 + c[a])
            if near_enemy:
                s -= S["contact_pen"] * w[a] / 9
                if e_op >= c[a] + 2:
                    s -= S["exposure_pen"] * w[a] / 9
        if not S["patient"] and not endgame and e < 7 and e - cost < S["reserve"]:
            continue
        if s > best_s:
            best, best_s, best_cost = a, s, cost
    if best is None:
        return None
    if S["patient"]:
        # wait (rest) until the best tile is affordable and the reserve is kept
        need = best_cost + (0 if endgame else S["reserve"])
        if e < min(need, 9) and e < 9:
            return None
        if best not in state["legal_actions"]:
            return None
    return best
