import json, sys, glob
from collections import Counter
files=sys.argv[1:] or ['_scratch/r1.jsonl']+sorted(glob.glob('_scratch/w*.jsonl'))
rows=[]
for fn in files:
    for line in open(fn):
        try: d=json.loads(line)
        except: continue
        k=(d['group'],d['seed'],d['game'])
        obs=d['obs']; acts=d['acts']
        for r in range(len(obs)-1):
            a=acts[r]; o=obs[r]; o2=obs[r+1]
            if a['op']!='gather': continue
            b=o['own']['boats'][a['boat']]; p=b['position']
            en=[e for e in o['enemy_boats'] if e['position']==p and e['destination']==-1]
            b2=o2['own']['boats'][a['boat']]
            got=b2['cargo'][a['good']]-b['cargo'][a['good']]
            s=o['stocks'][p]; after=o2['stocks'][p]
            if after is None: continue
            regen=(r+1)%4==0
            x = after - (1 if regen and after>0 else 0)  # value before regen (ambiguous if after==6? stock-before-regen<6 always since gathered)
            opp = s - got - x
            prio = 'us' if r%2==o['seat'] else 'them'
            rows.append((prio, s, a['quantity'], got, opp, len(en), k, r))
c=Counter()
for prio,s,w,g,opp,nen,k,r in rows:
    if nen==0 and opp==0 and g==w: continue
    c[(prio,s,w,g,opp,nen)]+=1
for key,v in sorted(c.items()): print(key, v)
