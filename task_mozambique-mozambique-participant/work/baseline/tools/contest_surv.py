"""Survival of Professor claim time minus its LB in contested games (eval JSON with claim_round).
python3 contest_surv.py results/48_x.json [more.json ...]"""
import sys, json, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
spec = importlib.util.spec_from_file_location('ag', str(Path(__file__).resolve().parents[1] / 'agent_v1.py'))
ag = importlib.util.module_from_spec(spec); spec.loader.exec_module(ag)
games = []
for f in sys.argv[1:]:
    games += [g for g in json.load(open(f))['games'] if g.get('claim_round')]
lbs = {}
diffs = {c: [] for c in range(8)}
won = {c: [0, 0] for c in range(8)}
with Arena() as a:
    for g in games:
        key = (g['group'], g['seed'])
        if key not in lbs:
            o = a.reset(g['group'], g['seed'], 0)['observation']
            mp = o['map']
            lbs[key] = (ag.single_lb(mp, mp['homes'][1 - o['seat']]), ag.single_lb(mp, o['own']['home']))
        lbp, lbu = lbs[key]
        for c in range(8):
            r, who = g['claim_round'][c], g['claim_by'][c]
            if who == 'P':
                diffs[c].append(r - lbp[c])
            elif who == 'U':
                diffs[c].append(None)   # censored: we took it
                won[c][0] += 1
            else:
                diffs[c].append(999)
            won[c][1] += 1
xs = [0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 80]
for c in range(8):
    v = diffs[c]
    # Kaplan-Meier style: censored at our claim (unknown later time) -> skip from risk set after our claim
    print('c%d we took %d/%d' % (c, won[c][0], won[c][1]), ' '.join('%d:%.2f' % (x, sum(1 for y in v if y is not None and y > x) / max(1, sum(1 for y in v if y is not None))) for x in xs))
