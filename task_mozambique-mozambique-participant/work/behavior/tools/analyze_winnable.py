"""Item 4: per map and contract, our single-contract earliest delivery vs the Professor's claim in
each style (passive play). Our 'realistic' time = analytic bound for raw (hit 95% in engine rushes),
bound + 2 for manufactured (engine-measured with the best simple plan v3, median +1..2).
Writes data/winnable.csv and prints markdown tables."""
import json, glob, os, sys, csv, statistics as st
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from mintime import contract_times, all_dist
from styles import style_of
D = os.path.join(os.path.dirname(__file__), '..', 'data')
bymap = defaultdict(dict)
for f in glob.glob(os.path.join(D, 'passive_*.jsonl')):
    for l in open(f):
        r = json.loads(l); bymap[(r['group'], r['seed'])][style_of(r['seed'], r['game'])] = r
def we_win_tie(seat, rnd): return (rnd % 2 == 0) == (seat == 0)
def we_beat(seat, ours, prof):  # prof None = it never claims it in passive play
    return prof is None or ours < prof or (ours == prof and we_win_tie(seat, ours))
rows = []
for (grp, seed), gs in sorted(bymap.items()):
    if len(gs) < 5: continue
    r0 = gs[0]; m = r0['map']; seat = r0['seat']
    dist = all_dist(m['routes'])
    ours = contract_times(m, m['homes'][seat], dist)
    theirs = contract_times(m, m['homes'][1 - seat], dist)
    for c in range(8):
        dl = m['contracts'][c]['deadline']
        real = ours[c] + (2 if c >= 4 else 0)
        P = [gs[s]['claim_round'][c] for s in range(5)]
        row = dict(group=grp, seed=seed, seat=seat, topology=m['topology'], contract=c, deadline=dl,
                   dest=m['contracts'][c]['destination'], our_bound=ours[c], our_realistic=real,
                   prof_bound=theirs[c], **{f'prof_style{s}': P[s] for s in range(5)})
        row['guaranteed'] = real < dl and we_beat(seat, real, theirs[c])
        for s in range(5): row[f'beat_style{s}'] = real < dl and we_beat(seat, real, P[s])
        row['beat_all_styles'] = all(row[f'beat_style{s}'] for s in range(5))
        rows.append(row)
with open(os.path.join(D, 'winnable.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
n = len(rows) // 8
print('maps', n)
print('| contract | our bound (med) | our realistic (med) | Prof bound (med) | Prof claim median, style 0/1/2/3/4 (claim rate) | we beat its fastest possible trip | we beat style 0/1/2/3/4 | we beat all 5 |')
print('|---|---|---|---|---|---|---|---|')
for c in range(8):
    R = [x for x in rows if x['contract'] == c]
    cl = []
    for s in range(5):
        got = [x[f'prof_style{s}'] for x in R if x[f'prof_style{s}'] is not None]
        cl.append(f"{st.median(got):g} ({100*len(got)/len(R):.0f}%)")
    bs = '/'.join(f"{100*sum(x[f'beat_style{s}'] for x in R)/len(R):.0f}" for s in range(5))
    print(f"| {c} {'TFTFMMMM'[c]}<{R[0]['deadline']} | {st.median(x['our_bound'] for x in R):g} | {st.median(x['our_realistic'] for x in R):g} | {st.median(x['prof_bound'] for x in R):g} | "
          f"{' / '.join(cl)} | {100*sum(x['guaranteed'] for x in R)/len(R):.0f}% | {bs} % | {100*sum(x['beat_all_styles'] for x in R)/len(R):.0f}% |")
# by seat: raw contracts are a coin flip on geometry; manufactured are mostly ours if we go first
print('\nby seat (share of contracts we win single-handed against all 5 styles):')
for seat in (0, 1):
    R = [x for x in rows if x['seat'] == seat]
    print(f"seat {seat}: raw {100*sum(x['beat_all_styles'] for x in R if x['contract']<4)/max(1,sum(1 for x in R if x['contract']<4)):.0f}%, "
          f"manufactured {100*sum(x['beat_all_styles'] for x in R if x['contract']>=4)/max(1,sum(1 for x in R if x['contract']>=4)):.0f}%")
# slack: how many rounds before the Professor's claim we arrive (manufactured, fastest style)
print('\nmanufactured contracts: Professor fastest claim over styles minus our realistic time (rounds of slack):')
for c in range(4, 8):
    R = [x for x in rows if x['contract'] == c]
    sl = [min([x[f'prof_style{s}'] for s in range(5) if x[f'prof_style{s}'] is not None] or [x['deadline']]) - x['our_realistic'] for x in R]
    sl.sort()
    print(f"  contract {c}: median {st.median(sl):g}, p10 {sl[len(sl)//10]}, min {sl[0]}")
