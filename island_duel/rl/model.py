"""Residual CNN policy/value network over the 15x15 board.

GroupNorm (not BatchNorm) so rollouts and PPO updates see the same function.
Cell logits come from a 1x1 conv (translation-equivariant); the rest logit and
the value come from pooled features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from features import C, CELLS


class Block(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.c1 = nn.Conv2d(ch, ch, 3, padding=1)
        self.c2 = nn.Conv2d(ch, ch, 3, padding=1)
        self.n1 = nn.GroupNorm(8, ch)
        self.n2 = nn.GroupNorm(8, ch)

    def forward(self, x):
        y = F.relu(self.n1(self.c1(x)))
        y = self.n2(self.c2(y))
        return F.relu(x + y)


class Net(nn.Module):
    def __init__(self, ch=96, blocks=8):
        super().__init__()
        self.stem = nn.Sequential(nn.Conv2d(C, ch, 3, padding=1), nn.GroupNorm(8, ch), nn.ReLU())
        self.blocks = nn.Sequential(*[Block(ch) for _ in range(blocks)])
        self.pol = nn.Conv2d(ch, 1, 1)
        self.rest = nn.Linear(2 * ch, 1)
        self.val = nn.Sequential(nn.Linear(2 * ch, 256), nn.ReLU(), nn.Linear(256, 1))

    def forward(self, x, mask):
        h = self.blocks(self.stem(x))
        g = torch.cat([h.mean(dim=(2, 3)), h.amax(dim=(2, 3))], 1)
        logits = torch.cat([self.pol(h).flatten(1), self.rest(g)], 1)
        logits = logits.masked_fill(~mask, -1e9)
        value = self.val(g).squeeze(1)
        return logits, value
