"""Passive sweep: we always wait. Records per game the Professor's claim rounds and score timeline.
usage: python3 passive.py OUT.jsonl WORKER NWORKERS
"""
import sys, json, random, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)
from arena import Arena

def maps():
    rng = random.Random(20261114)
    out = []
    for g in range(8):
        for _ in range(30):
            out.append((g, rng.randrange(2**32), 'rand'))
    for c in json.load(open(os.path.join(ROOT, 'train-input.json'))):
        out.append((c['group'], c['seed'], 'train'))
    return out

def play(a, group, seed, game):
    s = a.reset(group, seed, game)
    o = s['observation']
    m = o['map']
    rec = dict(group=group, seed=seed, game=game, seat=o['seat'], map=m)
    claim_round = [None] * 8
    claim_by = [None] * 8
    score_tl = []
    last = 0
    enemy_seen = []
    while not s['game_done']:
        s = a.step({'op': 'wait'})
        o = s.get('observation')
        if o is None:
            break
        r = o['round']  # observation after round r-1 was resolved
        for c, v in enumerate(o['claims']):
            if v != -1 and claim_round[c] is None:
                claim_round[c] = r - 1
                claim_by[c] = v
        if o['opponent_score'] != last:
            score_tl.append((r - 1, o['opponent_score']))
            last = o['opponent_score']
        for e in o['enemy_boats']:
            enemy_seen.append((r - 1, e['boat'], e['position'], e['destination'], e['eta']))
    rec.update(claim_round=claim_round, claim_by=claim_by, score_tl=score_tl,
               result=s['result'], enemy_at_home=enemy_seen)
    return rec

if __name__ == '__main__':
    out, w, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    jobs = [(g, sd, src, game) for (g, sd, src) in maps() for game in range(5)]
    jobs = jobs[w::n]
    done = set()
    if os.path.exists(out):
        for line in open(out):
            d = json.loads(line); done.add((d['group'], d['seed'], d['game']))
    with Arena() as a, open(out, 'a') as f:
        for g, sd, src, game in jobs:
            if (g, sd, game) in done: continue
            rec = play(a, g, sd, game)
            rec['src'] = src
            f.write(json.dumps(rec) + '\n'); f.flush()
