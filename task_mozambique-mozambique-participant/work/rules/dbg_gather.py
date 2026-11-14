import json, sys, glob
sys.argv=['x']
import validate_sim as V, sim
files=sys.argv[1:] or ['_scratch/r1.jsonl']+sorted(glob.glob('_scratch/w*.jsonl'))
games={}
for fn in files:
    for line in open(fn):
        try: d=json.loads(line)
        except: continue
        games[(d['group'],d['seed'],d['game'])]=d
# scan directly: rounds where we gather and an enemy boat docked at same site at o
for k,d in games.items():
    obs=d['obs']; acts=d['acts']
    for r in range(len(obs)-1):
        a=acts[r]; o=obs[r]; o2=obs[r+1]
        if a['op']!='gather': continue
        b=o['own']['boats'][a['boat']]; p=b['position']
        en=[e for e in o['enemy_boats'] if e['position']==p and e['destination']==-1]
        if not en: continue
        b2=o2['own']['boats'][a['boat']]
        got=b2['cargo'][a['good']]-b['cargo'][a['good']]
        regen = 1 if (r+1)%4==0 else 0
        print(k,'r',r,'par',r%2,'seat',o['seat'],'prio', 'us' if r%2==o['seat'] else 'them', 'stock',o['stocks'][p],'want',a['quantity'],'got',got,'stock after',o2['stocks'][p],'regen',regen,'en',[(e['boat']) for e in en], 'en after', [(e['boat'],e['position'],e['destination']) for e in o2['enemy_boats']])
