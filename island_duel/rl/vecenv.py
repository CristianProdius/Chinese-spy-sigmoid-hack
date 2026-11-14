"""Many engine processes driven from one Python process.

Each env is its own native engine subprocess speaking the bundle's line
protocol (reset/step -> one JSON line). Commands are written to every engine
first and the replies read afterwards, so the engines think in parallel.
"""

from __future__ import annotations

import json
import random
import subprocess

import numpy as np

from features import CELLS, Memory, featurize, to_engine_action


class Engine:
    def __init__(self, path):
        self.p = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  text=True, bufsize=1)
        self.send("hello")
        meta = self.recv()
        assert meta.get("protocol") == 3, meta

    def send(self, line):
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()

    def recv(self):
        line = self.p.stdout.readline()
        if not line:
            raise RuntimeError("engine exited")
        r = json.loads(line)
        if "error" in r:
            raise ValueError(r["error"])
        return r

    def close(self):
        try:
            self.send("quit")
            self.p.wait(timeout=3)
        except Exception:
            self.p.kill()


class VecEnv:
    def __init__(self, n, engine_path, seed=0, arenas=range(32)):
        self.n = n
        self.engines = [Engine(engine_path) for _ in range(n)]
        self.rng = random.Random(seed)
        self.arenas = list(arenas)
        self.mem = [Memory() for _ in range(n)]
        self.obs = [None] * n
        self.info = [None] * n

    def reset_all(self, tasks=None):
        for i, e in enumerate(self.engines):
            if tasks is None:
                arena, seed = self.rng.choice(self.arenas), self.rng.getrandbits(32)
            else:
                arena, seed = tasks[i]
            self.info[i] = (arena, seed)
            e.send(f"reset {arena} {seed}")
        for i, e in enumerate(self.engines):
            r = e.recv()
            self.mem[i] = Memory()
            self.obs[i] = r["observation"]
        return self._features()

    def _features(self):
        xs, ms = zip(*(featurize(o, m) for o, m in zip(self.obs, self.mem)))
        return np.stack(xs), np.stack(ms)

    def step(self, actions):
        """actions: canonical indices. Returns (x, mask, reward, done, results)."""
        for i, e in enumerate(self.engines):
            a = to_engine_action(int(actions[i]), self.obs[i]["seat"])
            e.send(f"step {-1 if a is None else a}")
        rew = np.zeros(self.n, np.float32)
        done = np.zeros(self.n, bool)
        results = []
        for i, e in enumerate(self.engines):
            r = e.recv()
            rew[i] = r["reward"]
            done[i] = r["done"]
            self.obs[i] = r["observation"]
            if r["done"]:
                seat = self.obs[i]["seat"]
                results.append({
                    "env": i, "arena": self.info[i][0], "seat": seat,
                    "profile": self.obs[i]["opponent_profile"],
                    "win": r["winner"] == seat, "draw": r["winner"] is None,
                    "margin": r["scores"][seat] - r["scores"][1 - seat],
                })
        x, m = self._features()
        return x, m, rew, done, results

    def close(self):
        for e in self.engines:
            e.close()
