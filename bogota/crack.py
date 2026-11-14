"""Brute-force candidate altered-record sets against the archive seals.
Usage: crack.py scores.json  -> ranks label-flip suspects by LLM disagreement, then searches
subsets of (unicode set) x (top-K flip suspects) for a mask that decodes a seal to text containing SIGMOID."""
import json, hashlib, itertools, sys, string
d=json.load(open('data/reviews.json'))
T=d['trusted_reference']; S=d['samples']
tags=[bytes.fromhex(r['archive_tag']) for r in T+S]
UNI=[36,119,216,273,357,367,462,478,513,685,752,1199]
sc=json.load(open(sys.argv[1]))
tr=sc['trusted']; sm=sc['samples']
import statistics
err=[abs(e-r) for _,r,e,_ in tr]; print("trusted LLM |E-r| mean", round(statistics.mean(err),3), "p95", sorted(err)[int(.95*len(err))])
sus=sorted(sm,key=lambda x:-abs(x[2]-x[1]))
print("top flip suspects (idx, rating, E[pred]):"); 
for i,r,e,p in sus[:30]: print(" ",i,r,round(e,2), [round(x,2) for x in p])
K=int(sys.argv[2]) if len(sys.argv)>2 else 18
top=[x[0] for x in sus[:K]]
def mask_for(idxs): return hashlib.sha256(",".join(map(str,sorted(idxs))).encode()).digest()
want={}
for ti,t in enumerate(tags):
    for o in range(0,25): want[(o,bytes(a^b for a,b in zip(t[o:o+8],b"SIGMOID_")))]=ti
def check(sub):
    m=mask_for(sub)
    for o in range(25):
        if (o,m[o:o+8]) in want:
            t=tags[want[(o,m[o:o+8])]]; return bytes(a^b for a,b in zip(t,m)).rstrip(b'\x00')
n=0
for base in (UNI, []):
    for k in range(0,K+1):
        for sub in itertools.combinations(top,k):
            n+=1; r=check(base+list(sub))
            if r: print("HIT", sorted(base+list(sub)), r); sys.exit()
print("no hit after", n, "subsets")
