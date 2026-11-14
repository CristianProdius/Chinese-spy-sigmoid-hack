import json, hashlib, itertools, sys, time
from multiprocessing import Pool
d=json.load(open('reviews.json'))
tags=[bytes.fromhex(r['archive_tag']) for r in d['trusted_reference']+d['samples']]
tails={}
for ti,t in enumerate(tags): tails.setdefault(t[-3:],[]).append(ti)
def check(idxs):
    m=hashlib.sha256(",".join(map(str,idxs)).encode()).digest()
    for ti in tails.get(m[-3:],[]):
        dec=bytes(a^b for a,b in zip(tags[ti],m)).rstrip(b'\x00')
        if len(dec)>=4 and all(32<=c<127 for c in dec): return ti,dec
def work(a):
    hits=[]
    r=check([a]); 
    if r: hits.append(([a],r))
    for b in range(a+1,1200):
        r=check([a,b])
        if r: hits.append(([a,b],r))
        for c in range(b+1,1200):
            r=check([a,b,c])
            if r: hits.append(([a,b,c],r))
    return hits
if __name__=='__main__':
    t0=time.time()
    with Pool() as p:
        for hs in p.imap_unordered(work, range(1200), chunksize=2):
            for h in hs: print("HIT",h,flush=True)
    print("done any<=3",round(time.time()-t0),"s",flush=True)
