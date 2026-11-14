import json, sys, glob
from collections import Counter
files=['_scratch/r1.jsonl']+sorted(glob.glob('_scratch/w*.jsonl'))
c=Counter(); ex={}
for fn in files:
    for line in open(fn):
        try: d=json.loads(line)
        except: continue
        k=(d['group'],d['seed'],d['game'])
        obs=d['obs']; acts=d['acts']; R=obs[0]['map']['routes']
        for r in range(len(obs)-1):
            a=acts[r]; o=obs[r]; o2=obs[r+1]
            if a['op']!='sail': continue
            b=o['own']['boats'][a['boat']]; P=b['position']; Q=a['destination']
            b2=o2['own']['boats'][a['boat']]
            ok = not (b2['position']==P and b2['destination']==-1)
            prio = 'us' if r%2==o['seat'] else 'them'
            # enemy in transit on same edge at o (departed earlier)
            for e in o['enemy_boats']:
                if e['destination']!=-1 and {e['position'],e['destination']}=={P,Q}:
                    c[('transit_same_edge', prio, ok)]+=1; ex.setdefault(('transit',ok),(k,r))
            # enemy departing same round to same destination from another origin (seen at o2 sailing with eta L-1)
            for e2 in o2['enemy_boats']:
                if e2['destination']==Q and e2['position']!=P and e2['eta']==R[e2['position']][Q]-1:
                    c[('same_dest_other_origin', prio, ok)]+=1; ex.setdefault(('samedest',prio,ok),(k,r))
                if e2['destination']!=-1 and e2['position']==P and e2['destination']!=Q and e2['eta']==R[P][e2['destination']]-1:
                    c[('same_origin_other_dest', prio, ok)]+=1
print(c); print(ex)
