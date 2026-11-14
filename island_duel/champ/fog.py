"""Fog handling for planning against the champion clone.

Tracker: follows our observations, remembers seen terrain and owners, and logs
the champion's moves from public energy/score deltas (claims as (w, c) pairs,
captures of our tiles).
sample_world: builds one complete, consistent world (terrain for unseen tiles,
the champion's hidden territory, the champion's memory) for the C simulator.
"""
import random

N = 15
NT = 225
NB = [tuple((r + dr) * N + q + dq for dr, dq in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= r + dr < N and 0 <= q + dq < N) for r in range(N) for q in range(N)]
P_BLOCKED = 0.195


class Tracker:
    def __init__(self, seat):
        self.seat, self.opp = seat, 1 - seat
        self.seen = {}  # tile -> (blocked, w, c)
        self.owner = [-3] * NT  # last seen owner (-3 never seen)
        self.prev = None  # (energy, scores, owners) of previous observation
        self.my_action = None
        self.hidden = []  # champion claims (w, c) not yet located, oldest first
        self.cstart = 224 if seat == 0 else 0

    def _locate(self, i):
        key = (self.seen[i][1], self.seen[i][2])
        if key in self.hidden:
            self.hidden.remove(key)

    def update(self, obs):
        own, vis = obs["owners"], obs["visible"]
        e, s = obs["energy"], obs["scores"]
        newly_c = []
        for i in range(NT):
            if not vis[i] and self.owner[i] == self.seat:
                self.owner[i] = self.opp  # lost from view => captured
            if vis[i]:
                self.seen[i] = (own[i] == -2, obs["weights"][i] or 0, obs["costs"][i] or 0)
                if own[i] == self.opp and self.owner[i] != self.opp and i != self.cstart:
                    newly_c.append(i)
                self.owner[i] = own[i]
        # champion's last move from public deltas
        if self.prev is None:
            pe, ps, pown = [6, 6], [0, 0], None
            moved = self.seat == 1
            mine_w = mine_cap = 0
        else:
            pe, ps, pown = self.prev
            moved = True
            a = self.my_action
            mine_cap = 1 if (a is not None and pown[a] == self.opp) else 0
            mine_w = self.seen[a][1] if a is not None else 0
        captured_tiles = []
        if moved:
            dsc = s[self.opp] - (ps[self.opp] - (mine_w if mine_cap else 0))
            dec = e[self.opp] - pe[self.opp]
            if dsc > 0:
                lost = (ps[self.seat] + mine_w) - s[self.seat]
                if lost > 0:  # capture of one of our tiles: visible, located
                    captured_tiles = [i for i in newly_c if pown is not None and pown[i] == self.seat]
                else:
                    self.hidden.append((dsc, -dec))
        for i in newly_c:
            if i not in captured_tiles:
                self._locate(i)

    def remember(self, obs, action):
        self.prev = (list(obs["energy"]), list(obs["scores"]), list(obs["owners"]))
        self.my_action = action


def sample_world(tr, obs, rng, mean=False):
    """Return dict(blocked, w, c, owner, mo, mw, mc) for one sampled world.
    mean=True: deterministic world (no blocked unseen tiles, w=5, c=3; hidden
    champion tiles placed nearest its start first)."""
    blocked, w, c = [0] * NT, [0] * NT, [0] * NT
    unseen = []
    for i in range(NT):
        if i in tr.seen:
            b, wi, ci = tr.seen[i]
            blocked[i], w[i], c[i] = int(b), wi, ci
        elif i in (0, 224):
            pass
        else:
            if mean:
                w[i], c[i] = 5, 3
            else:
                blocked[i] = int(rng.random() < P_BLOCKED)
                w[i], c[i] = rng.randint(1, 9), rng.randint(1, 4)
            unseen.append(i)
    owner = [-1] * NT
    for i in range(NT):
        o = tr.owner[i]
        if o in (0, 1):
            owner[i] = o
    owner[0], owner[224] = 0, 1
    terr = {i for i in range(NT) if owner[i] == tr.opp}
    free = {i for i in unseen if not blocked[i]}
    front = {j for i in terr for j in NB[i] if j in free}
    for wi, ci in tr.hidden:
        if not front:
            break
        if mean:
            cs = tr.cstart
            j = min(front, key=lambda t: (abs(t // N - cs // N) + abs(t % N - cs % N), t))
        else:
            j = rng.choice(sorted(front))
        front.discard(j)
        free.discard(j)
        terr.add(j)
        owner[j], w[j], c[j] = tr.opp, wi, ci
        for k in NB[j]:
            if k in free:
                front.add(k)
    mo, mw, mc = [-3] * NT, [5] * NT, [3] * NT
    mo[0], mo[224] = 0, 1
    mw[0] = mw[224] = mc[0] = mc[224] = 0
    vis_c = set(terr)
    for i in terr:
        vis_c.update(NB[i])
    for i in vis_c:
        mo[i] = -2 if blocked[i] else owner[i]
        mw[i], mc[i] = w[i], c[i]
    return {"blocked": blocked, "w": w, "c": c, "owner": owner, "mo": mo, "mw": mw, "mc": mc}
