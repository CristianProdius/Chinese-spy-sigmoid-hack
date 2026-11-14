"""Unified prioritised job queue (resumable). usage: python3 sweep.py WORKER NWORKERS
Order: passive on experiment maps -> rush (2 maps/group) -> park (1 map/group) ->
passive round-robin over groups (30 rand maps/group) -> passive on train maps."""
import sys, json, os, glob
sys.path.insert(0, os.path.dirname(__file__))
from passive import maps, play, ROOT
from arena import Arena
from observe import observe
from runner import run_plan
from rush import rush_plan
D = os.path.join(os.path.dirname(__file__), '..', 'data')

def done_set(kind, keyf):
    s = set()
    for f in glob.glob(os.path.join(D, kind + '_*.jsonl')):
        for l in open(f):
            try: s.add(keyf(json.loads(l)))
            except Exception: pass
    return s

def jobs():
    ms = maps()
    rand = {g: [m for m in ms if m[0] == g and m[2] == 'rand'] for g in range(8)}
    train = [m for m in ms if m[2] == 'train']
    J = []
    exp2 = [m for g in range(8) for m in rand[g][:2]]
    J += [('passive', g, sd, src, game, None) for (g, sd, src) in exp2 for game in range(5)]
    J += [('rush', g, sd, src, game, c) for (g, sd, src) in exp2 for game in range(5) for c in range(8)]
    J += [('park', g, sd, src, game, site) for g in range(8) for (_, sd, src) in rand[g][:1] for game in range(5) for site in range(10)]
    for i in range(30):
        J += [('passive', g, rand[g][i][1], 'rand', game, None) for g in range(8) for game in range(5)]
    J += [('passive', g, sd, src, game, None) for (g, sd, src) in train for game in range(5)]
    seen = set(); out = []
    for j in J:
        if j not in seen: seen.add(j); out.append(j)
    return out

if __name__ == '__main__':
    w, n = int(sys.argv[1]), int(sys.argv[2])
    done = {'passive': done_set('passive', lambda d: (d['group'], d['seed'], d['game'])),
            'rush': done_set('rush', lambda d: (d['group'], d['seed'], d['game'], d['contract'])),
            'park': done_set('park', lambda d: (d['group'], d['seed'], d['game'], d['site']))}
    files = {k: open(os.path.join(D, '%s_w%d.jsonl' % (k, w)), 'a') for k in done}
    kf = lambda j: (j[1], j[2], j[4]) if j[0] == 'passive' else (j[1], j[2], j[4], j[5])
    todo = [j for j in jobs() if kf(j) not in done[j[0]]]
    with Arena() as a:
        for kind, g, sd, src, game, x in todo[w::n]:
            key = (g, sd, game) if kind == 'passive' else (g, sd, game, x)
            if kind == 'passive':
                rec = play(a, g, sd, game); rec['src'] = src
            elif kind == 'rush':
                o = a.reset(g, sd, game)['observation']
                plan, msite = rush_plan(o['map'], o['seat'], x)
                rec = run_plan(a, g, sd, game, plan)
                log = rec.pop('log')
                rec['contract'] = x; rec['msite'] = msite
                rec['sightings'] = [(L['r'], e['boat'], e['position'], e['destination'], e['eta']) for L in log for e in L['enemy']]
                rec['acts'] = [(L['r'], L['act']) for L in log if L['act']['op'] != 'wait']
            else:
                o = a.reset(g, sd, game)['observation']
                if o['map']['homes'][o['seat']] == x: continue
                rec = observe(a, g, sd, game, [x])
                log = rec.pop('log')
                rec['site'] = x
                rec['arrive'] = next((L['r'] for L in log if L['own'][0][0] == x and L['own'][0][1] == -1), None)
                rec['sightings'] = [(L['r'], e['boat'], e['position'], e['destination'], e['eta']) for L in log for e in L['enemy']]
                rec['site_stock'] = [L['stocks'][x] for L in log]
                rec.pop('targets', None); rec.pop('build', None)
            files[kind].write(json.dumps(rec) + '\n'); files[kind].flush()
