"""Practice SDK (Python standard library only). Not part of your submission.

    from arena import Arena
    with Arena() as arena:
        state = arena.reset(group, seed, game)     # group 0-7, seed 0..2**32-1, game 0-4
        while not state['game_done']:
            state = arena.step(action)
        state['result']                            # {'scores': [you, professor], 'half_points': 0|1|2}

    python arena.py [main.py] [--maps 24] [--seed N] [--jobs 4]
runs your main.py exactly as the evaluator does (same stdin/stdout protocol, every
map played five times, a map counts by its worst game) on random practice maps
and prints the score.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

GROUPS = [2 * topology + seat for topology in range(4) for seat in range(2)]
GAMES_PER_MAP = 5
PYTHON = shutil.which('pypy3') or sys.executable   # the evaluator uses PyPy 3.10
GAME_BUDGET = 10.0   # seconds of main.py thinking per game, as in the evaluation
WARMUP = 10.0        # extra seconds for the first game of each main.py process


class Arena:
    def __init__(self):
        engine = Path(__file__).resolve().with_name('mozambique-engine')
        self.process = subprocess.Popen([str(engine)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        text=True, encoding='utf-8', bufsize=1)

    def request(self, command, **data):
        self.process.stdin.write(json.dumps(dict(command=command, **data)) + '\n')
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError('engine stopped')
        result = json.loads(line)
        if 'error' in result:
            raise RuntimeError(result['error'])
        return result

    def reset(self, group, seed, game=0):
        return self.request('reset', group=group, seed=seed, game=game)

    def step(self, action):
        return self.request('step', action=action)

    def close(self):
        if self.process.poll() is None:
            try:
                self.process.stdin.write('{"command":"quit"}\n')
                self.process.stdin.flush()
                self.process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                self.process.kill()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def _play(script, games):
    path = Path(script).resolve()
    agent = subprocess.Popen([PYTHON, path.name], cwd=path.parent,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    results = []
    first = True
    try:
        with Arena() as arena:
            for index, group, seed, game in games:
                state = arena.reset(group, seed, game)
                thinking = 0.0
                while not state['game_done']:
                    asked = time.monotonic()
                    agent.stdin.write(json.dumps({'observation': state['observation']}) + '\n')
                    agent.stdin.flush()
                    action = json.loads(agent.stdout.readline())
                    thinking += time.monotonic() - asked
                    state = arena.step(action)
                results.append((index, game, state['result']['half_points'], thinking - (WARMUP if first else 0)))
                first = False
    finally:
        agent.stdin.close()
        agent.wait(timeout=5)
    return results


def local_evaluation(script='main.py', maps=24, seed=None, jobs=4):
    rng = random.Random(seed)
    games = [(m, GROUPS[m % 8], s, p) for m, s in enumerate(rng.randrange(2 ** 32) for _ in range(maps))
             for p in range(GAMES_PER_MAP)]
    start = time.monotonic()
    with ThreadPoolExecutor(jobs) as pool:
        parts = pool.map(lambda part: _play(script, part), [games[i::jobs] for i in range(jobs)])
    by_map = {}
    slowest = 0.0
    for index, game, points, thinking in (r for part in parts for r in part):
        by_map.setdefault(index, {})[game] = points
        slowest = max(slowest, thinking)
    worst = [min(v.values()) for v in by_map.values()]
    return dict(maps=maps, map_wins=sum(w == 2 for w in worst), map_draws=sum(w == 1 for w in worst),
                match_score=round(sum(worst) / (2 * maps), 4),
                games_won=sum(p == 2 for v in by_map.values() for p in v.values()),
                slowest_game_seconds=round(slowest, 2),
                within_time_limit=slowest <= GAME_BUDGET,
                seconds=round(time.monotonic() - start, 1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Local practice evaluation of main.py')
    parser.add_argument('script', nargs='?', default='main.py')
    parser.add_argument('--maps', type=int, default=24)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    result = local_evaluation(args.script, args.maps, args.seed, args.jobs)
    print(json.dumps(result))
    if 'pypy' not in Path(PYTHON).name:
        print('note: pypy3 not found; timings are from CPython (the evaluator uses PyPy 3.10, usually faster)',
              file=sys.stderr)
    if not result['within_time_limit']:
        print(f'WARNING: a game used {result["slowest_game_seconds"]} s of thinking; the evaluator allows '
              f'{GAME_BUDGET:.0f} s per game (+{WARMUP:.0f} s for the first) and would stop with 0 points. Run with --jobs <= your free cores.',
              file=sys.stderr)
