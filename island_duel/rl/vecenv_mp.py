"""VecEnv split over worker processes so featurisation runs in parallel."""

from __future__ import annotations

import multiprocessing as mp

import numpy as np

from vecenv import VecEnv


def _worker(conn, n, engine_path, seed):
    env = VecEnv(n, engine_path, seed=seed)
    while True:
        cmd, payload = conn.recv()
        if cmd == "reset":
            conn.send(env.reset_all(payload))
        elif cmd == "step":
            conn.send(env.step(payload))
        elif cmd == "close":
            env.close()
            conn.close()
            return


class MPVecEnv:
    def __init__(self, n, engine_path, workers=16, seed=0):
        assert n % workers == 0
        self.k = n // workers
        ctx = mp.get_context("fork")
        self.conns, self.procs = [], []
        for w in range(workers):
            a, b = ctx.Pipe()
            p = ctx.Process(target=_worker, args=(b, self.k, engine_path, seed * 1000 + w), daemon=True)
            p.start()
            self.conns.append(a)
            self.procs.append(p)

    def reset_all(self, tasks=None):
        for i, c in enumerate(self.conns):
            c.send(("reset", None if tasks is None else tasks[i * self.k:(i + 1) * self.k]))
        xs, ms = zip(*(c.recv() for c in self.conns))
        return np.concatenate(xs), np.concatenate(ms)

    def step(self, actions):
        for i, c in enumerate(self.conns):
            c.send(("step", actions[i * self.k:(i + 1) * self.k]))
        outs = [c.recv() for c in self.conns]
        x = np.concatenate([o[0] for o in outs])
        m = np.concatenate([o[1] for o in outs])
        r = np.concatenate([o[2] for o in outs])
        d = np.concatenate([o[3] for o in outs])
        res = [{**x, "env": x["env"] + w * self.k} for w, o in enumerate(outs) for x in o[4]]
        return x, m, r, d, res

    def close(self):
        for c in self.conns:
            c.send(("close", None))
        for p in self.procs:
            p.join(timeout=5)
