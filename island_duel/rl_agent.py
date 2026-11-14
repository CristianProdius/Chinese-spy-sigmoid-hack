"""Island Duel agent: PPO policy network (warm-started from the search agent).

choose_action(state) featurises the observation (with a per-game memory of
terrain and last-seen owners), runs the network and plays the most likely
legal action. Model path: ID_MODEL env var, default ./model.pt next to this
file. ID_SAMPLE=1 samples from the policy instead of taking the argmax.
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "rl"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from features import Memory, featurize, to_engine_action  # noqa: E402
from model import Net  # noqa: E402

torch.set_num_threads(int(os.environ.get("ID_THREADS", "1")))
_DEV = torch.device(os.environ.get("ID_DEVICE", "cpu"))
_SAMPLE = os.environ.get("ID_SAMPLE") == "1"
_ck = torch.load(os.environ.get("ID_MODEL", os.path.join(HERE, "model.pt")), map_location=_DEV)
_args = _ck.get("args", {})
_net = Net(_args.get("ch", 96), _args.get("blocks", 8)).to(_DEV)
_net.load_state_dict(_ck["model"])
_net.eval()
_mem = Memory()


def reset_agent():
    global _mem
    _mem = Memory()


@torch.no_grad()
def choose_action(state):
    x, m = featurize(state, _mem)
    logits, _ = _net(torch.from_numpy(x[None]).to(_DEV), torch.from_numpy(m[None]).to(_DEV))
    if _SAMPLE:
        a = int(torch.distributions.Categorical(logits=logits[0]).sample())
    else:
        a = int(logits[0].argmax())
    act = to_engine_action(a, state["seat"])
    if act not in state["legal_actions"]:  # should never happen: illegal logits are masked
        act = None
    return act
