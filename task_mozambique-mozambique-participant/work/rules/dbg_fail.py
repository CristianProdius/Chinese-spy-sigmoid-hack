import json, sys
sys.argv=['x']
import validate_sim as V, sim
evs=[]
orig=V.note
def note(kind, detail):
    if kind=='own.boats': evs.append(detail)
    orig(kind, detail)
V.note=note
files=['_scratch/r1.jsonl','_scratch/w1.jsonl','_scratch/w2.jsonl','_scratch/w3.jsonl','_scratch/w4.jsonl']
games={}
for fn in files:
    for line in open(fn):
        try: d=json.loads(line)
        except: continue
        games[(d['group'],d['seed'],d['game'])]=d
V.offline(files)
seen=set()
for (key,act,ob,pb) in evs:
    g=key[:3]; r=key[3]-1
    if (g,r) in seen: continue
    seen.add((g,r))
    d=games[g]; o=d['obs'][r]; o2=d['obs'][r+1]
    R=o['map']['routes']
    b=o['own']['boats'][act['boat']] if 'boat' in act else None
    print(g, 'round', r, 'parity', r%2, 'seat', o['seat'], 'act', act, 'route L', R[b['position']][act['destination']] if act['op']=='sail' else None)
    print('   en before', o['enemy_boats'], 'vis', [i for i,v in enumerate(o['visible']) if v])
    print('   en after ', o2['enemy_boats'], 'vis', [i for i,v in enumerate(o2['visible']) if v])
    print('   our boat after', o2['own']['boats'][act['boat']] if b else None)
