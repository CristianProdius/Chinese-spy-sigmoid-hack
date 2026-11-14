"""Assume altered set = UNI block (optionally minus up to `drop` of them) + up to `k` extra sample indices.
Detect via trailing-zero padding: seal tail == mask tail and decoded bytes printable."""
import json, hashlib, itertools, sys, time
from multiprocessing import Pool
d=json.load(open('reviews.json' if len(sys.argv)>3 else 'data/reviews.json'))
tags=[bytes.fromhex(r['archive_tag']) for r in d['trusted_reference']+d['samples']]
UNI=[36,119,216,273,357,367,462,478,513,685,752,1199]
ALL=[i for i in range(1200) if i not in UNI]
tails={}
for ti,t in enumerate(tags): tails.setdefault(t[-3:],[]).append(ti)
def check(idxs):
    m=hashlib.sha256(",".join(map(str,sorted(idxs))).encode()).digest()
    for ti in tails.get(m[-3:],[]):
        dec=bytes(a^b for a,b in zip(tags[ti],m)).rstrip(b'\x00')
        if len(dec)>=4 and all(32<=c<127 for c in dec): return ti,dec
K=int(sys.argv[1]); DROP=int(sys.argv[2])
bases=[]
for dr in range(DROP+1):
    for drop in itertools.combinations(UNI,dr): bases.append([u for u in UNI if u not in drop])
def work(first):
    hits=[]
    for base in bases:
        for k in range(0,K+1):
            if k==0:
                if first==ALL[0]:
                    r=check(base); 
                    if r: hits.append((base,r))
                continue
            for rest in itertools.combinations([a for a in ALL if a>first],k-1):
                s=base+[first]+list(rest); r=check(s)
                if r: hits.append((sorted(s),r))
    return hits
if __name__=='__main__':
    t0=time.time()
    with Pool() as p:
        for hs in p.imap_unordered(work, ALL, chunksize=4):
            for h in hs: print("HIT",h,flush=True)
    print("done",K,DROP,round(time.time()-t0),"s",flush=True)
