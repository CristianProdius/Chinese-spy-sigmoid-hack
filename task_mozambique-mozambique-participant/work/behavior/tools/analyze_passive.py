import sys, json, glob, os, statistics as st
from collections import defaultdict, Counter
D = os.path.join(os.path.dirname(__file__), '..', 'data')
recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(D, 'passive_*.jsonl'))) for l in open(f)]
print('games', len(recs), 'maps', len({(r['group'], r['seed']) for r in recs}))
# contract structure
struct = Counter()
for r in recs:
    cs = r['map']['contracts']
    struct[tuple((c['good'], c['quantity'], c['points'], c['deadline']) for c in cs)] += 1
print('contract structures (good,qty,pts,deadline):')
for k, v in struct.most_common(10): print(' ', v, k)
roles = Counter(tuple(sorted(Counter(r['map']['roles']).items())) for r in recs)
print('role multisets', roles.most_common(5))
def q(xs):
    xs = sorted(xs)
    if not xs: return '-'
    return f"{st.mean(xs):.1f} [{xs[0]}..{xs[-1]}] med {st.median(xs)}"
by = defaultdict(list)
for r in recs: by[r['game']].append(r)
for g in range(5):
    R = by[g]
    sc = [r['result']['scores'][1] for r in R]
    nraw = [sum(1 for c in range(4) if r['claim_round'][c] is not None) for r in R]
    nman = [sum(1 for c in range(4, 8) if r['claim_round'][c] is not None) for r in R]
    first = [min(x for x in r['claim_round'] if x is not None) for r in R if any(x is not None for x in r['claim_round'])]
    firstman = [min(x for x in r['claim_round'][4:] if x is not None) for r in R if any(x is not None for x in r['claim_round'][4:])]
    last = [max(x for x in r['claim_round'] if x is not None) for r in R if any(x is not None for x in r['claim_round'])]
    print(f"game {g}: n={len(R)} score {q(sc)} raw {q(nraw)} man {q(nman)} first {q(first)} firstman {q(firstman)} last {q(last)}")
    for c in range(8):
        cr = [r['claim_round'][c] for r in R]
        got = [x for x in cr if x is not None]
        print(f"   contract {c}: claimed {len(got)}/{len(R)} round {q(got)}")
