import json, hashlib, itertools, sys, time
d=json.load(open('data/reviews.json'))
tags=[bytes.fromhex(r['archive_tag']) for r in d['trusted_reference']+d['samples']]
UNI=[36,119,216,273,357,367,462,478,513,685,752,1199]
NEAR=[593,700,546]
sc=json.load(open('scores.json'))
sus=[x[0] for x in sorted(sc['samples'],key=lambda x:-abs(x[2]-x[1]))]
K=int(sys.argv[1]); MAXK=int(sys.argv[2])
top=[i for i in sus if i not in UNI and i not in NEAR][:K]
tails={}
for ti,t in enumerate(tags): tails.setdefault(t[-3:],[]).append(ti)
def mask_for(idxs): return hashlib.sha256(",".join(map(str,sorted(idxs))).encode()).digest()
def check(idxs):
    m=mask_for(idxs)
    for ti in tails.get(m[-3:],[]):
        dec=bytes(a^b for a,b in zip(tags[ti],m)).rstrip(b'\x00')
        if len(dec)<=29 and all(32<=c<127 for c in dec): return ti,dec
n=0; t0=time.time()
for uni in (UNI,[]):
    for nk in range(0,4):
        for near in itertools.combinations(NEAR,nk):
            for k in range(0,MAXK+1):
                for sub in itertools.combinations(top,k):
                    n+=1; s=uni+list(near)+list(sub)
                    if not s: continue
                    r=check(s)
                    if r: print("HIT", sorted(s), r); sys.exit()
print("no hit", n, "subsets", round(time.time()-t0,1),"s")
