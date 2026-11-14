"""Sequential mini-eval in one process with per-game stats (debug on).
    pypy3 mini.py AGENT.py [--maps N] [--seed S] [--styles 0,1,2,3,4] [--first-map K]
"""
import sys, os, json, time, random, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import professor as P
import fasteval as F
ap = argparse.ArgumentParser()
ap.add_argument('agent'); ap.add_argument('--maps', type=int, default=4); ap.add_argument('--seed', type=int, default=20261114)
ap.add_argument('--styles', default='0,1,2,3,4'); ap.add_argument('--first-map', type=int, default=0)
a = ap.parse_args()
mod = F.load_agent(os.path.abspath(a.agent))
mod.PARAMS['debug'] = True
rng = random.Random(a.seed)
seeds = [rng.randrange(2 ** 32) for _ in range(a.first_map + a.maps)]
tot = 0; wins = 0
for m in range(a.first_map, a.first_map + a.maps):
    g = F.GROUPS[m % 8]
    for st in [int(x) for x in a.styles.split(',')]:
        r = F.play(mod, g, seeds[m], st)
        G = getattr(mod, '_LASTG', [None])[0]
        tot += 1; wins += r['hp'] == 2
        print('map %d g%d style %d: %d-%d hp %d cpu %.2f %s %s %s' % (m, g, st, r['us'], r['them'], r['hp'], r['cpu'], r['claims'],
              (' '.join('%s=%s' % (k, ('%.2f' % v) if isinstance(v, float) else v) for k, v in G.stats.items()), 'nrep', G.nrep, 'hyps', [h.style for h in G.hyps]) if G else '', r['error'] or ''), flush=True)
print('wins %d/%d' % (wins, tot))
