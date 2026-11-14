"""Island Duel agent: determinized rollout planning against a model of the champion.

The champion's decision procedure was rebuilt from the engine binary (champ.c)
and reproduces its moves exactly given its inputs. At each decision we:
  1. update a fog tracker (seen terrain, the champion's claims from public
     energy/score deltas);
  2. sample M complete worlds consistent with what we know (unseen terrain
     from the i.i.d. prior, the champion's hidden territory grown from its
     start using its logged claims, its memory = its territory + neighbours);
  3. pick candidate moves (opponent-model search in one world, plus the
     negamax choice in every world);
  4. play each candidate to the end of the game in every world (us: negamax,
     champion: the exact clone) and choose the best average result.

Env: ID_K (2), ID_M (3), ID_RB (512), ID_WORKERS (16), ID_SEED (12345).
"""
import multiprocessing as mp
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fog import Tracker, sample_world  # noqa: E402
from simlib import Game  # noqa: E402

K = int(os.environ.get("ID_K", "2"))
M = int(os.environ.get("ID_M", "3"))
RB = int(os.environ.get("ID_RB", "512"))
WORKERS = int(os.environ.get("ID_WORKERS", "16"))
SEED = int(os.environ.get("ID_SEED", "12345"))
E, F = 160.0, 9.0

_pool = None
_tr = None
_rng = None
_games = 0


def _rollout(job):
    wd, pub, a = job
    return Game.from_world(wd, pub).rollout(a, E, F, RB, 4)


def _get_pool():
    global _pool
    if _pool is None and WORKERS > 1:
        _pool = mp.get_context("fork").Pool(WORKERS)
    return _pool


def reset_agent():
    global _tr, _rng, _games
    _tr = None
    _games += 1
    _rng = random.Random(SEED * 7919 + _games)


def choose_action(state):
    global _tr, _rng
    if _rng is None:
        reset_agent()
    if _tr is None:
        _tr = Tracker(state["seat"])
    _tr.update(state)
    legal = state["legal_actions"]
    if len(legal) == 1:
        a = legal[0]
    else:
        pub = {k: state[k] for k in ("energy", "scores", "actions_remaining", "seat", "opponent_profile")}
        wds = [sample_world(_tr, state, _rng) for _ in range(M)]
        worlds = [Game.from_world(wd, pub) for wd in wds]
        _, mv, vals = worlds[0].om_nm(E, F, 1000000, 2)
        cands = [x for _, x in sorted(zip(vals, mv), reverse=True)[:K]]
        for g in worlds:
            x = g.negamax(E, F)
            if x not in cands:
                cands.append(x)
        if len(cands) == 1:
            best = cands[0]
        else:
            jobs = [(wd, pub, x) for x in cands for wd in wds]
            pool = _get_pool()
            res = pool.map(_rollout, jobs) if pool else [_rollout(j) for j in jobs]
            score = {}
            for i, x in enumerate(cands):
                ms = res[i * M:(i + 1) * M]
                score[x] = sum((m > 0) - (m < 0) for m in ms) / M + sum(ms) / M / 200
            best = max(cands, key=lambda x: score[x])
        a = None if best < 0 else best
    _tr.remember(state, a)
    return a
