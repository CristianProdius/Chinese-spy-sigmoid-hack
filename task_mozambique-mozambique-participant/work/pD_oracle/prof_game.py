"""Profile the agent over N games in one process (first game warms the JIT).
   pypy3 prof_game.py AGENT.py N [seed]"""
import importlib.util, json, os, sys, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F
path = sys.argv[1]; n = int(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 5
A = F.load_agent(path)
rng = random.Random(seed)
for i in range(n):
    g = rng.randrange(8); s = rng.randrange(2**32); st = rng.randrange(5)
    t0 = time.process_time()
    r = F.play(A, g, s, st)
    stats = getattr(A, 'STATS', None)
    print('game %d g%d s%d style %d: %d-%d cpu %.2f %s' % (i, g, s, st, r['us'], r['them'], r['cpu'], json.dumps(stats) if stats else ''), flush=True)
    if stats: stats.clear()
