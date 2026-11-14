"""Replay park runs in the decoded model (work/binary/professor.py, read-only import) to see whether
the Professor's plan changes are explained by physical conflicts (failed sails/gathers)."""
import json, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'binary'))
import professor as PM
from styles import style_of
from observe import next_hop
D = os.path.join(HERE, '..', 'data')
P = {}
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        d = json.loads(l); P[(d['group'], d['seed'], d['game'])] = d
def replay(rec, site):
    m = rec['map']; seat = rec['seat']; ps = 1 - seat
    mp = PM.Map(m); eng = PM.Engine(mp); prof = PM.Professor(style_of(rec['seed'], rec['game']), ps)
    fails = []; claims = [None] * 8
    for r in range(80):
        # our order: observe() policy for boat 0 -> site
        b = eng.sides[seat].boats[0]
        our = {'op': 'wait'}
        if b[2] == 0 and b[0] != site and site is not None:
            our = {'op': 'sail', 'boat': 0, 'destination': next_hop(m['routes'], b[0], site)}
        po = prof.choose(eng.view(ps))
        orders = [None, None]; orders[seat] = PM.order_from_json(our); orders[ps] = po
        ok = eng.step(orders)
        if not ok[ps]: fails.append((r, po[0], 'prof'))
        if not ok[seat]: fails.append((r, our['op'], 'us'))
        for c in range(8):
            if eng.claims[c] != -1 and claims[c] is None: claims[c] = (r, eng.claims[c])
    return claims, fails, eng.sides[ps].score
if __name__ == '__main__':
    runs = [json.loads(l) for f in glob.glob(os.path.join(D, 'park_*.jsonl')) for l in open(f)]
    changed = [r for r in runs if [x[0] if x else None for x in r['claim_round']] != P[(r['group'], r['seed'], r['game'])]['claim_round']]
    sample_unchanged = [r for r in runs if r not in changed][:12]
    for tag, R in (('changed', changed), ('unchanged-sample', sample_unchanged)):
        match = 0
        for r in R:
            claims, fails, sc = replay(r, r['site'])
            ok = [x[0] if x else None for x in claims] == [x[0] if x else None for x in r['claim_round']] and sc == r['result']['scores'][1]
            match += ok
            print(tag, r['group'], r['seed'], r['game'], 'site', r['site'], 'model==engine', ok, 'failed orders', fails[:4])
        print(tag, 'model reproduces engine:', match, '/', len(R))
