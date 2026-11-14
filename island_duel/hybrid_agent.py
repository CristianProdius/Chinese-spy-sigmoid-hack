"""Island Duel hybrid agent: PPO policy/value network + 2-ply lookahead.

For our top-K moves by the policy, simulate the move, then every reply the
champion can make on the board we can see (each capture of our tiles it can
afford, each visible neutral claim next to its tiles, resting, and one
abstract "expand into fog" move). Each resulting position (our turn again)
is scored with the value network:

    Q(a) = min over replies [ margin change / 100 + V(position) ]

and we play argmax Q(a) + prior_weight * log pi(a). Terminal positions use
the exact result (+-1 plus margin / 100), matching the training reward scale.

Env vars: ID_MODEL (checkpoint), ID_DEVICE (cuda/cpu), ID_HPARAMS (JSON).
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "rl"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from features import CELLS, Memory, featurize, to_engine_action  # noqa: E402
from model import Net  # noqa: E402

N = 15
NB = [tuple((r + dr) * N + c + dc for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= r + dr < N and 0 <= c + dc < N) for r in range(N) for c in range(N)]
STARTS = {0, CELLS - 1}

H = {"top_k": 6, "prior": 0.02, "exp_gain": 4, "exp_cost": 2, "agg": "min"}
H.update(json.loads(os.environ.get("ID_HPARAMS", "{}")))

torch.set_num_threads(int(os.environ.get("ID_THREADS", "1")))
_DEV = torch.device(os.environ.get("ID_DEVICE", "cuda" if torch.cuda.is_available() else "cpu"))
_ck = torch.load(os.environ.get("ID_MODEL", os.path.join(HERE, "model.pt")), map_location=_DEV)
_a = _ck.get("args", {})
_net = Net(_a.get("ch", 96), _a.get("blocks", 8)).to(_DEV)
_net.load_state_dict(_ck["model"])
_net.eval()
_mem = Memory()


def reset_agent():
    global _mem
    _mem = Memory()


def _legal(owners, costs, energy, p, weights):
    e = energy[p]
    out = [None]
    seen = set()
    for i in range(CELLS):
        if owners[i] != p:
            continue
        for j in NB[i]:
            if j in seen:
                continue
            seen.add(j)
            o = owners[j]
            if o == -1 and costs[j] is not None and costs[j] <= e:
                out.append(j)
            elif o == 1 - p and j not in STARTS and costs[j] + 2 <= e:
                out.append(j)
    return out


def _apply(obs, p, a, exp=False):
    """Copy of obs after player p plays a (cell, None=rest, or expand)."""
    o = dict(obs)
    owners = list(obs["owners"])
    energy = list(obs["energy"])
    scores = list(obs["scores"])
    if exp:
        energy[p] -= H["exp_cost"]
        scores[p] += H["exp_gain"]
    elif a is None:
        energy[p] = min(9, energy[p] + 3)
    else:
        w, c = obs["weights"][a], obs["costs"][a]
        if owners[a] == 1 - p:
            energy[p] -= c + 2
            scores[1 - p] -= w
        else:
            energy[p] -= c
        scores[p] += w
        owners[a] = p
    o["owners"], o["energy"], o["scores"] = owners, energy, scores
    o["actions_remaining"] = obs["actions_remaining"] - 1
    return o


def _margin(o, seat):
    return o["scores"][seat] - o["scores"][1 - seat]


def _terminal_value(o, seat):
    m = _margin(o, seat)
    return (1.0 if m > 0 else -1.0 if m < 0 else 0.0)


@torch.no_grad()
def choose_action(state):
    seat = state["seat"]
    opp = 1 - seat
    legal = state["legal_actions"]
    x0, m0 = featurize(state, _mem)
    logits, _ = _net(torch.from_numpy(x0[None]).to(_DEV), torch.from_numpy(m0[None]).to(_DEV))
    logp = torch.log_softmax(logits[0], 0).cpu().numpy()
    if len(legal) == 1:
        return legal[0]
    order = np.argsort(-logp)
    cands = [int(i) for i in order[: H["top_k"]] if m0[i]]
    base = _margin(state, seat)

    # Build every (candidate, reply) position.
    leaves = []  # (cand_idx, delta_margin/100, obs or None, terminal_value or None)
    for ci, ca in enumerate(cands):
        a = to_engine_action(ca, seat)
        o1 = _apply(state, seat, a)
        if o1["actions_remaining"] == 0:
            leaves.append((ci, (_margin(o1, seat) - base) / 100, None, _terminal_value(o1, seat)))
            continue
        replies = [(None, False)]
        if o1["energy"][opp] >= H["exp_cost"]:
            replies.append((None, True))
        replies += [(j, False) for j in _legal(o1["owners"], o1["costs"], o1["energy"], opp,
                                                o1["weights"]) if j is not None]
        for (j, exp) in replies:
            o2 = _apply(o1, opp, j, exp)
            d = (_margin(o2, seat) - base) / 100
            if o2["actions_remaining"] == 0:
                leaves.append((ci, d, None, _terminal_value(o2, seat)))
                continue
            o2["current_player"] = seat
            o2["legal_actions"] = _legal(o2["owners"], o2["costs"], o2["energy"], seat, o2["weights"])
            leaves.append((ci, d, o2, None))

    need = [k for k, lf in enumerate(leaves) if lf[2] is not None]
    vals = {}
    if need:
        xs, ms = [], []
        for k in need:
            mem = Memory()
            mem.w[:], mem.c[:], mem.owner[:] = _mem.w, _mem.c, _mem.owner
            x, m = featurize(leaves[k][2], mem)
            xs.append(x)
            ms.append(m)
        _, v = _net(torch.from_numpy(np.stack(xs)).to(_DEV), torch.from_numpy(np.stack(ms)).to(_DEV))
        for k, vv in zip(need, v.cpu().numpy()):
            vals[k] = float(vv)
    q = [None] * len(cands)
    for k, (ci, d, o2, tv) in enumerate(leaves):
        val = d + (tv if tv is not None else vals[k])
        if q[ci] is None:
            q[ci] = [val]
        else:
            q[ci].append(val)
    best, best_s = None, -1e18
    for ci, ca in enumerate(cands):
        vs = q[ci]
        agg = min(vs) if H["agg"] == "min" else float(np.mean(vs))
        s = agg + H["prior"] * logp[ca]
        if s > best_s:
            best, best_s = ca, s
    act = to_engine_action(best, seat)
    if act not in legal:
        act = None
    return act
