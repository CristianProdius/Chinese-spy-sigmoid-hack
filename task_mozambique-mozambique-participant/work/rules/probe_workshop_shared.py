"""After the Professor's first manufactured delivery (so it owns a workshop at one of the two mfg
sites), bring 2T+1F to BOTH mfg sites and check build_workshop is legal and works at both."""
import sys, json, random
from eng import Arena
from nav import next_hop, pick
def play(a, g, seed, game):
    s=a.reset(g,seed,game); o=s['observation']; mp=o['map']; R=mp['routes']; seat=o['seat']
    mfg=[i for i,r in enumerate(mp['roles']) if r==2]
    plan=[('load',0,0,2),('load',0,1,1),('load',1,0,2),('load',1,1,1)]
    first_m=None; built={}; log=[]
    while not s['game_done']:
        o=s['observation']; la=o['legal_actions']; r=o['round']; act=la[0]
        if first_m is None:
            for c in range(4,8):
                if o['claims'][c]==1-seat: first_m=r
        if plan:
            op,b,gd,q=plan[0]; x=pick(la,op=op,boat=b,good=gd,quantity=q)
            if x: act=x; plan.pop(0)
        elif first_m is not None:
            for bi,tgt in ((0,mfg[0]),(1,mfg[1])):
                bt=o['own']['boats'][bi]
                if bt['destination']!=-1: continue
                if bt['position']!=tgt:
                    act=pick(la,op='sail',boat=bi,destination=next_hop(R,bt['position'],tgt)); break
                if bt['cargo'][0]: act=pick(la,op='unload',boat=bi,good=0,quantity=bt['cargo'][0]); break
                if bt['cargo'][1]: act=pick(la,op='unload',boat=bi,good=1,quantity=bt['cargo'][1]); break
                if not o['own']['workshops'][tgt]:
                    x=pick(la,op='build_workshop',boat=bi)
                    log.append((r,tgt,'legal' if x else 'NOT LEGAL', o['own']['warehouses'][tgt]))
                    if x: act=x; break
        s=a.step(act)
        if not s['game_done']:
            o2=s['observation']
    fo=o2
    return dict(key=(g,seed,game), first_professor_M_round=first_m, mfg=mfg, workshops_built=[i for i,v in enumerate(fo['own']['workshops']) if v], log=log[:4], result=s['result'])
rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 3)
with Arena() as a:
    for i in range(int(sys.argv[2]) if len(sys.argv)>2 else 4):
        g=rng.randrange(8); seed=rng.randrange(2**32); game=rng.randrange(5)
        print(json.dumps(play(a,g,seed,game))); sys.stdout.flush()
