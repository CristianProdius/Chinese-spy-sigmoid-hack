"""CPU per game in one warm process: pypy3 warm.py AGENT.py [n_games] [seed]"""
import sys, os, json, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import fasteval as F
A = F.load_agent(os.path.abspath(sys.argv[1]))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 7)
for i in range(n):
    g = rng.randrange(8); sd = rng.randrange(2 ** 32); st = rng.randrange(5)
    r = F.play(A, g, sd, st)
    tm = getattr(A, 'LAST_TM', None)
    print('game', i, 'g', g, 'seed', sd, 'style', st, 'score %d-%d' % (r['us'], r['them']), 'cpu %.2f wall %.2f' % (r['cpu'], r['wall']), r['error'] or '', tm, flush=True)
