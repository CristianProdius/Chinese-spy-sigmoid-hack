"""Dev runner: play a few games in-process with exceptions raised.
   pypy3 devrun.py AGENT.py [--maps 4] [--seed 20261114] [--styles 0,1,2,3,4] [--first-map 0] [--trace]"""
import argparse, json, os, random, sys, time, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import professor as P
import fasteval as FE

ap = argparse.ArgumentParser()
ap.add_argument('agent'); ap.add_argument('--maps', type=int, default=4); ap.add_argument('--first-map', type=int, default=0)
ap.add_argument('--seed', type=int, default=20261114); ap.add_argument('--styles', default='0,1,2,3,4')
ap.add_argument('--trace', action='store_true')
a = ap.parse_args()
spec = importlib.util.spec_from_file_location('ag', os.path.abspath(a.agent)); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rng = random.Random(a.seed)
seeds = [rng.randrange(2 ** 32) for _ in range(a.first_map + a.maps)]
styles = [int(x) for x in a.styles.split(',')]
orig_agent = mod.agent
def dbg_agent(obs, memory):
    memory["debug"] = True; mod.PARAMS["debug"] = True
    act = orig_agent(obs, memory)
    g = memory.get('g')
    if a.trace and g is not None:
        print('  r%2d %-50s hyps=%s tag=%s P=%s' % (obs['round'], json.dumps(act), sorted(g.hyps), g.plan_tag, g.P))
    return act
mod.agent = dbg_agent
tot = 0
for m in range(a.first_map, a.first_map + a.maps):
    grp = FE.GROUPS[m % 8]
    res = []
    for st in styles:
        r = FE.play(mod, grp, seeds[m], st)
        res.append(r)
        if r['error']: print('ERROR', r['error'])
    print('map %d g%d seed %d: %s' % (m, grp, seeds[m], ' '.join('s%d:%d-%d(%s,%.1fs)' % (r['style'], r['us'], r['them'], r['claims'], r['cpu']) for r in res)), flush=True)
