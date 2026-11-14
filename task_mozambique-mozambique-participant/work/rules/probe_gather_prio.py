"""Gather race where WE have priority: does the Professor's later gather fail entirely or get a partial amount?"""
import json, sys, glob
from eng import Arena
files=sorted(glob.glob('_scratch/w*.jsonl'))+['_scratch/r1.jsonl']
events=[]
for fn in files:
    for line in open(fn):
        try: d=json.loads(line)
        except: continue
        obs=d['obs']; acts=d['acts']
        for r in range(len(obs)-1):
            o,o2=obs[r],obs[r+1]
            if r%2!=o['seat']: continue
            a=acts[r]
            for x in range(10):
                if o['map']['roles'][x] not in (0,1) or not o['visible'][x] or not o2['visible'][x]: continue
                if not any(e['position']==x and e['destination']==-1 for e in o['enemy_boats']): continue
                if a['op']=='gather': continue
                regen=(r+1)%4==0
                s=o['stocks'][x]; after=o2['stocks'][x]
                qopp = s - (after - (1 if regen else 0))
                if qopp<=0: continue
                # our docked boats at x with free capacity
                for bi,b in enumerate(o['own']['boats']):
                    if b['position']==x and b['destination']==-1:
                        free=3-sum(b['cargo'])
                        q=min(free,s)
                        if q>=1 and s-q<qopp:
                            events.append((d['group'],d['seed'],d['game'],r,x,bi,q,s,qopp,acts[:r]))
                            break
print('candidates',len(events))
out=[]
with Arena() as A:
    for (g,seed,game,r,x,bi,q,s,qopp,prefix) in events[:8]:
        st=A.reset(g,seed,game)
        for a in prefix: st=A.step(a)
        o=st['observation']
        assert o['stocks'][x]==s, (o['stocks'][x], s)
        act={'op':'gather','boat':bi,'good':o['map']['roles'][x],'quantity':q}
        assert act in o['legal_actions']
        st=A.step(act); o2=st['observation']
        regen=(r+1)%4==0
        after=o2['stocks'][x]
        print(dict(key=(g,seed,game),round=r,site=x,stock=s,our_q=q,opp_q_in_base=qopp,stock_after=after,regen=regen,
                   our_cargo=o2['own']['boats'][bi]['cargo'], verdict=('opp FAILED (no partial)' if after-(1 if regen else 0)==s-q else 'opp took %d'%(s-q-(after-(1 if regen else 0))))))
