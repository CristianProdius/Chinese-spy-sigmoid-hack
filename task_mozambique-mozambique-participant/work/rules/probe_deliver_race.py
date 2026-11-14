"""Find Professor raw-contract deliveries we can contest; test same-round delivery conflicts."""
import sys, json, random
from eng import Arena
from nav import next_hop, dist_next, pick
def policy_factory(c, deliver_at=None):
    state={}
    def pol(o):
        mp=o['map']; ct=mp['contracts'][c]; R=mp['routes']; home=o['own']['home']
        la=o['legal_actions']; b=o['own']['boats'][0]
        r=o['round']
        if r==0: return pick(la, op='load', boat=0, good=ct['good'], quantity=ct['quantity']) or la[0]
        if deliver_at is not None and r==deliver_at:
            return pick(la, op='deliver', boat=0, contract=c) or la[0]
        if b['destination']==-1 and b['position']!=ct['destination']:
            return pick(la, op='sail', boat=0, destination=next_hop(R,b['position'],ct['destination'])) or la[0]
        return la[0]
    return pol
def play(a, g, seed, game, pol):
    s=a.reset(g,seed,game); obs=[s['observation']]; acts=[]
    while not s['game_done']:
        act=pol(s['observation']); acts.append(act); s=a.step(act)
        obs.append(s['observation'] if not s['game_done'] else s)
    return obs, acts
rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 5)
res=[]
with Arena() as a:
    tries=0
    while len(res)<int(sys.argv[2] if len(sys.argv)>2 else 6) and tries<200:
        tries+=1
        g=rng.randrange(8); seed=rng.randrange(2**32); game=rng.randrange(5)
        o0=a.reset(g,seed,game)['observation']; mp=o0['map']; home=o0['own']['home']
        D,_=dist_next(mp['routes'],home)
        cands=[c for c in range(4) if D[mp['contracts'][c]['destination']]+2 < mp['contracts'][c]['deadline']]
        if not cands: continue
        c=rng.choice(cands)
        obs,acts=play(a,g,seed,game,policy_factory(c))
        # when did the professor claim c? and were we already there?
        tclaim=None
        for o in obs[1:]:
            if 'claims' in o and o['claims'][c]==1-o0['seat']:
                tclaim=o['round']-1; break
        if tclaim is None: continue
        o_at=obs[tclaim]
        b=o_at['own']['boats'][0]
        if not (b['position']==mp['contracts'][c]['destination'] and b['destination']==-1): continue
        if not pick(o_at['legal_actions'], op='deliver', boat=0, contract=c): continue
        obs2,acts2=play(a,g,seed,game,policy_factory(c, deliver_at=tclaim))
        o_after=obs2[tclaim+1]
        prio='us' if tclaim%2==o0['seat'] else 'them'
        r=dict(key=(g,seed,game), contract=c, round=tclaim, seat=o0['seat'], prio=prio,
               claims_after=o_after['claims'][c], our_score=o_after['own']['score'], opp_score=o_after['opponent_score'],
               opp_score_base=obs[tclaim+1]['opponent_score'], cargo_after=o_after['own']['boats'][0]['cargo'])
        print(json.dumps(r)); sys.stdout.flush()
        res.append(r)
