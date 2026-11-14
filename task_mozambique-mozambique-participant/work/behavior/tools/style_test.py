"""Is game index a consistent Professor style? Within-map permutation test: shuffle the 5 game
labels inside each map and compare the spread of per-index means with the observed spread."""
import json, glob, os, random, statistics as st
from collections import defaultdict
D = os.path.join(os.path.dirname(__file__), '..', 'data')
bm = defaultdict(dict)
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); bm[(r['group'], r['seed'])][r['game']] = r
maps = [v for v in bm.values() if len(v) == 5]
print('maps', len(maps))
def feats(r):
    cr = r['claim_round']
    f = {'score': r['result']['scores'][1],
         'n_raw': sum(x is not None for x in cr[:4]), 'n_man': sum(x is not None for x in cr[4:]),
         'first_man': min([x for x in cr[4:] if x is not None], default=80),
         'first_claim': min([x for x in cr if x is not None], default=80),
         'last_claim': max([x for x in cr if x is not None], default=0)}
    for c in range(8):
        f['took_c%d' % c] = int(cr[c] is not None)
        f['round_c%d' % c] = cr[c] if cr[c] is not None else 80
    return f
import sys; sys.path.insert(0, os.path.dirname(__file__))
from styles import style_permutation
LABEL = sys.argv[1] if len(sys.argv) > 1 else 'game'
def order(m):
    if LABEL == 'game': return [m[g] for g in range(5)]
    perm = style_permutation(m[0]['seed'])      # perm[game] = style
    inv = {perm[g]: g for g in range(5)}
    return [m[inv[s]] for s in range(5)]        # index = style id
print('label:', LABEL)
F = [[feats(r) for r in order(m)] for m in maps]
rng = random.Random(1)
print(f'| feature | mean by {LABEL} 0..4 | spread | permutation p-value |')
print('|---|---|---|---|')
for name in F[0][0]:
    def spread(perm_maps):
        means = [st.mean(fm[g][name] for fm in perm_maps) for g in range(5)]
        return max(means) - min(means), means
    obs, means = spread(F)
    cnt = 0; N = 400
    for _ in range(N):
        P = []
        for fm in F:
            idx = list(range(5)); rng.shuffle(idx); P.append([fm[i] for i in idx])
        if spread(P)[0] >= obs: cnt += 1
    print(f"| {name} | {' / '.join(f'{x:.2f}' for x in means)} | {obs:.2f} | {cnt/N:.3f} |")
