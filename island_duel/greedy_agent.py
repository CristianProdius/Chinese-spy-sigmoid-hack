"""Greedy energy-efficiency agent: claim the tile with the best value per decision.

A claim of value v and cost c uses 1 decision plus c/3 decisions of resting,
so its rate is 3v/(3+c). A capture swings 2v for cost c+2. Rest when the best
tile is not affordable yet.
"""


def _rate(state, i, seat):
    v, c = state["weights"][i], state["costs"][i]
    if state["owners"][i] == 1 - seat:
        return 6 * v / (5 + c), c + 2
    return 3 * v / (3 + c), c


def choose_action(state):
    seat = state["seat"]
    owners, n = state["owners"], state["size"]
    energy = state["energy"][seat]
    best, best_rate, best_cost = None, -1.0, 0
    for i in range(n * n):
        if owners[i] not in (-1, 1 - seat) or not state["visible"][i]:
            continue
        if state["weights"][i] == 0:  # enemy start tile, cannot be captured
            continue
        r, c = i // n, i % n
        if not any(0 <= r + dr < n and 0 <= c + dc < n and owners[(r + dr) * n + c + dc] == seat
                   for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        rate, cost = _rate(state, i, seat)
        if rate > best_rate:
            best, best_rate, best_cost = i, rate, cost
    if best is not None and best_cost <= energy and best in state["legal_actions"]:
        return best
    return None
