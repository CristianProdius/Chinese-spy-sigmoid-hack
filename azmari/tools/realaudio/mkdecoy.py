"""Real-audio robustness set "decoy" built from task_ethiopia/train-input.wav.
Usage: python mkdecoy.py [out_dir]   (default: azmari/tools/data/decoy; writes WAVs + labels.csv)
Score with: python ../eval.py ../../main.py --data <out_dir> --no-train --keep-names
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, '..', '..', '..', 'task_ethiopia', 'train-input.wav')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data', 'decoy')
os.makedirs(OUT, exist_ok=True)
import numpy as np, csv
from scipy.io import wavfile
from scipy import signal
sr,x=wavfile.read(TRAIN); x=x.astype(float); S,E=14.960,20.965
rng=np.random.default_rng(11)
def xfade(a,b,n):
    r=np.linspace(0,1,n); return np.concatenate([a[:-n],a[-n:]*(1-r)+b[:n]*r,b[n:]])
host=xfade(x[int(21.0*sr):], x[:int(14.9*sr)], int(0.03*sr))   # 49.7 s genuine host
src=x[int(S*sr):int(E*sr)]
def hp(v,fc): sos=signal.butter(4,fc,'high',fs=sr,output='sos'); return signal.sosfiltfilt(sos,v)
def ramp(n,f=0.3):
    k=int(f*sr); w=np.ones(n); w[:k]=np.linspace(0,1,k); w[-k:]=np.linspace(1,0,k); return w
def pink(n):
    w=rng.normal(0,1,n); b,a=[0.049922035,-0.095993537,0.050612699,-0.004408786],[1,-2.494956002,2.017265875,-0.522189400]
    p=signal.lfilter(b,a,w); return p/np.std(p)
rms=np.sqrt((host**2).mean())
def decoy(y,kind,p,L):
    n=int(L*sr); seg=y[p:p+n].copy(); w=ramp(n)
    if kind=='loud': y[p:p+n]=seg*(1+(10**(8/20)-1)*w)
    elif kind=='crowd': y[p:p+n]=seg+w*pink(n)*rms*0.5
    elif kind=='claps':
        c=np.zeros(n); 
        for t in np.arange(0.1,L-0.1,0.45): i=int(t*sr); c[i:i+300]+=rng.normal(0,1,300)*np.exp(-np.arange(300)/60)
        y[p:p+n]=seg+c*rms*3
    elif kind=='pause': y[p:p+n]=seg*(1-w*0.97)
    elif kind=='upreg':
        sh=signal.resample_poly(y[p:p+int(n*1.335)+10],3,4)[:n]; y[p:p+n]=seg*(1-w)+sh*w
    return y
def insert(y,mat,p,L):
    n=int(L*sr); m=mat[:n]; m=m*np.sqrt((y[p:p+n]**2).mean()/max((m**2).mean(),1e-9))
    nf=int(0.03*sr); r=np.linspace(0,1,nf); z=y.copy(); z[p:p+n]=m
    z[p:p+nf]=y[p:p+nf]*(1-r)+m[:nf]*r; z[p+n-nf:p+n]=m[-nf:]*(1-r)+y[p+n-nf:p+n]*r; return z
mats={'real':src,'noLF':hp(src,200)+2.0}
rows=[]
for kind in ['loud','crowd','claps','pause','upreg']:
    for mname,mat in mats.items():
        for k,(dp,sp,L) in enumerate([(5.0,30.0,6.0),(36.0,12.0,4.0)]):
            y=decoy(host.copy(),kind,int(dp*sr),7.0 if kind!='pause' else 3.0)
            y=insert(y,mat,int(sp*sr),L)
            fn=f'{kind}_{mname}_{k}.wav'; wavfile.write(f'{OUT}/'+fn,sr,np.clip(np.round(y),-32768,32767).astype(np.int16))
            rows.append((fn,f'{kind}_{mname}',f'{sp:.3f}',f'{sp+L:.3f}'))
with open(f'{OUT}/labels.csv','w',newline='') as fh:
    c=csv.writer(fh); c.writerow(['file','group','start_s','end_s']); c.writerows(rows)
print(len(rows))
