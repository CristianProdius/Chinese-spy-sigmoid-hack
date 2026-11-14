"""Markdown tables for passive play (item 1). Also writes data/passive_summary.csv (one row per game)."""
import json, glob, os, sys, csv, statistics as st
from collections import defaultdict, Counter
sys.path.insert(0, os.path.dirname(__file__))
from mintime import contract_times
from styles import style_of, STYLES
D = os.path.join(os.path.dirname(__file__), '..', 'data')
recs = {}
for f in sorted(glob.glob(os.path.join(D, 'passive_*.jsonl'))):
    for l in open(f):
        r = json.loads(l); recs[(r['group'], r['seed'], r['game'])] = r
recs = list(recs.values())
bymap = defaultdict(dict)
for r in recs: bymap[(r['group'], r['seed'])][r['game']] = r
full = {k: v for k, v in bymap.items() if len(v) == 5}
recs = [g for v in full.values() for g in v.values()]
print(f"complete maps: {len(full)} ({dict(sorted(Counter(k[0] for k in full).items()))} per group), games: {len(recs)}")
rows = []
for r in recs:
    cr = r['claim_round']
    order = sorted((x, c) for c, x in enumerate(cr) if x is not None)
    m = r['map']; t = contract_times(m, m['homes'][1 - r['seat']])
    rows.append(dict(group=r['group'], seed=r['seed'], game=r['game'], style=style_of(r['seed'], r['game']), seat=r['seat'], topology=m['topology'], src=r['src'],
                     score=r['result']['scores'][1], n_raw=sum(1 for c in range(4) if cr[c] is not None),
                     n_man=sum(1 for c in range(4, 8) if cr[c] is not None),
                     first=order[0][0] if order else None, first_c=order[0][1] if order else None,
                     first_man=min([x for x in cr[4:] if x is not None], default=None),
                     last=order[-1][0] if order else None, seq=''.join('RM'[c >= 4] for x, c in order),
                     at_min=sum(1 for c in range(8) if cr[c] is not None and cr[c] == t[c]),
                     claims='/'.join('-' if x is None else str(x) for x in cr)))
with open(os.path.join(D, 'passive_summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def s(xs):
    xs = [x for x in xs if x is not None]
    return f"{st.mean(xs):.1f} (med {st.median(xs):g}, {min(xs)}-{max(xs)})" if xs else '-'
def table(keyname, keyf, keys):
    print(f"\n| {keyname} | games | Prof score | raw claimed | manufactured claimed | first claim rnd | first manuf. rnd | last claim rnd | starts raw | all 8 claimed |")
    print('|---|---|---|---|---|---|---|---|---|---|')
    for k in keys:
        R = [x for x in rows if keyf(x) == k]
        if not R: continue
        print(f"| {k} | {len(R)} | {s([x['score'] for x in R])} | {st.mean(x['n_raw'] for x in R):.2f} | {st.mean(x['n_man'] for x in R):.2f} | "
              f"{s([x['first'] for x in R])} | {s([x['first_man'] for x in R])} | {s([x['last'] for x in R])} | "
              f"{100*sum(1 for x in R if x['seq'][:1]=='R')/len(R):.0f}% | {100*sum(1 for x in R if x['n_raw']+x['n_man']==8)/len(R):.0f}% |")
table('style (B, A, W)', lambda x: x['style'], range(5))
table('game index', lambda x: x['game'], range(5))
table('seat (Prof is the other seat)', lambda x: x['seat'], range(2))
table('topology', lambda x: x['topology'], range(4))
table('group', lambda x: x['group'], range(8))
print('\nper-contract claim rate and median claim round by STYLE:')
print('| contract | ' + ' | '.join(f'style {g} {STYLES[g]}' for g in range(5)) + ' |')
print('|---|' + '---|' * 5)
for c in range(8):
    cells = []
    for g in range(5):
        R = [r for r in recs if style_of(r['seed'], r['game']) == g]
        got = [r['claim_round'][c] for r in R if r['claim_round'][c] is not None]
        cells.append(f"{100*len(got)/len(R):.0f}% @ {st.median(got):g}")
    print(f"| {c} | " + ' | '.join(cells) + ' |')
print('\nper-contract claim rate and median claim round by game index:')
print('| contract | ' + ' | '.join(f'game {g}' for g in range(5)) + ' |')
print('|---|' + '---|' * 5)
for c in range(8):
    cells = []
    for g in range(5):
        R = [r for r in recs if r['game'] == g]
        got = [r['claim_round'][c] for r in R if r['claim_round'][c] is not None]
        cells.append(f"{100*len(got)/len(R):.0f}% @ {st.median(got):g}")
    print(f"| {c} | " + ' | '.join(cells) + ' |')
# score distribution
print('\nProfessor passive score histogram:', sorted(Counter(x['score'] for x in rows).items()))
print('order patterns (top):', Counter(x['seq'] for x in rows).most_common(10))
for g in range(5):
    print(f'style {g} top order patterns:', Counter(x['seq'] for x in rows if x['style'] == g).most_common(5))
# style identity across games of a map
pat = Counter(); pairs = Counter()
for k, gs in full.items():
    lab = {}; out = []
    for g in range(5):
        v = tuple(gs[g]['claim_round'])
        lab.setdefault(v, len(lab)); out.append(lab[v])
    pat[len(lab)] += 1
    for a in range(5):
        for b in range(a + 1, 5):
            if gs[a]['claim_round'] == gs[b]['claim_round']: pairs[(a, b)] += 1
print('\ndistinct claim vectors among the 5 games of a map:', sorted(pat.items()))
print('identical pairs by game-index pair:', sorted(pairs.items()))
sc = Counter()
for k, gs in full.items():
    v = [gs[g]['result']['scores'][1] for g in range(5)]
    for g in range(5):
        if v[g] == max(v): sc[('max', g)] += 1
        if v[g] == min(v): sc[('min', g)] += 1
print('game index holding the map max / min Prof score:', {k: sc[k] for k in sorted(sc)})
