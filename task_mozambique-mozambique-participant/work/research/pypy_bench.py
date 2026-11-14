"""Micro-benchmarks for state representations in PyPy 3.10 (search-loop style)."""
import json, time, copy, sys

obs_text = open('sample_obs.json').read()

def bench(name, fn, n):
    fn(1000)                       # warm the JIT
    t = time.perf_counter(); fn(n); dt = time.perf_counter() - t
    print('%-38s %8.0f ns/op' % (name, dt / n * 1e9))

def j_loads(n):
    for _ in range(n): json.loads(obs_text)

flat = list(range(64))             # flat int list state (stocks, cargo, warehouses...)
def list_copy(n):
    s = flat
    for _ in range(n):
        t = s[:]; t[5] += 1; s = t

tup = tuple(range(64))
def tuple_replace(n):
    s = tup
    for _ in range(n):
        s = s[:5] + (s[5] + 1,) + s[6:]

nested = [[0, 0, 0] for _ in range(10)] + [[1, 2, 3, 4] for _ in range(4)]
def nested_copy(n):
    s = nested
    for _ in range(n):
        t = [x[:] for x in s]; t[3][1] += 1; s = t

def deep_copy(n):
    s = nested
    for _ in range(n):
        t = copy.deepcopy(s); s = t

dstate = {'stocks': list(range(10)), 'wh': [[0, 0, 0] for _ in range(10)], 'score': 0, 'round': 0}
def dict_copy(n):
    s = dstate
    for _ in range(n):
        t = dict(s); t['stocks'] = s['stocks'][:]; t['score'] = s['score'] + 1; s = t

class S:
    __slots__ = ('stocks', 'wh', 'score', 'round')
    def __init__(self, a, b, c, d): self.stocks = a; self.wh = b; self.score = c; self.round = d
sobj = S(list(range(10)), [0] * 30, 0, 0)
def slots_copy(n):
    s = sobj
    for _ in range(n):
        t = S(s.stocks[:], s.wh[:], s.score + 1, s.round + 1); s = t

def clock_cost(n):
    pc = time.perf_counter
    for _ in range(n): pc()

def proc_cost(n):
    pc = time.process_time
    for _ in range(n): pc()

N = 200000
print(sys.version.split()[0], sys.implementation.name)
bench('json.loads(observation ~2.6KB)', j_loads, 20000)
bench('flat list[64] copy+edit', list_copy, N)
bench('tuple[64] rebuild with one change', tuple_replace, N)
bench('nested 14 small lists copy', nested_copy, N)
bench('copy.deepcopy(nested)', deep_copy, 20000)
bench('dict state shallow+1 list copy', dict_copy, N)
bench('__slots__ object copy (2 lists)', slots_copy, N)
bench('time.perf_counter() call', clock_cost, N)
bench('time.process_time() call', proc_cost, N)
