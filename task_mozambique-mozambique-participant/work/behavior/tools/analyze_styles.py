import sys, json, glob, os
from collections import defaultdict, Counter
D = os.path.join(os.path.dirname(__file__), '..', 'data')
recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(D, 'passive_*.jsonl'))) for l in open(f)]
bymap = defaultdict(dict)
for r in recs: bymap[(r['group'], r['seed'])][r['game']] = r
pat = Counter(); pairsame = Counter(); n = 0
best = Counter(); worst = Counter()
for k, gs in bymap.items():
    if len(gs) < 5: continue
    n += 1
    vec = {g: tuple(gs[g]['claim_round']) for g in range(5)}
    # partition label: games with identical claim vectors share a label
    lab = {}; out = []
    for g in range(5):
        if vec[g] not in lab: lab[vec[g]] = len(lab)
        out.append(lab[vec[g]])
    pat[tuple(out)] += 1
    for a in range(5):
        for b in range(a+1, 5):
            if vec[a] == vec[b]: pairsame[(a, b)] += 1
    sc = [gs[g]['result']['scores'][1] for g in range(5)]
    mx = max(sc); mn = min(sc)
    for g in range(5):
        if sc[g] == mx: best[g] += 1
        if sc[g] == mn: worst[g] += 1
print('complete maps', n)
print('identical-claim partitions over games 0..4:')
for p, c in pat.most_common(): print(' ', p, c)
print('pairs identical:', sorted(pairsame.items()))
print('game with max prof score (ties counted):', sorted(best.items()))
print('game with min prof score:', sorted(worst.items()))
