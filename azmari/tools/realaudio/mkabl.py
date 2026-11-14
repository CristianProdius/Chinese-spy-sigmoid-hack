"""Real-audio robustness set "abl" built from task_ethiopia/train-input.wav.
Usage: python mkabl.py [out_dir]   (default: azmari/tools/data/abl; writes WAVs + labels.csv)
Score with: python ../eval.py ../../main.py --data <out_dir> --no-train --keep-names
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, '..', '..', '..', 'task_ethiopia', 'train-input.wav')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data', 'abl')
os.makedirs(OUT, exist_ok=True)
import numpy as np, csv
from scipy.io import wavfile
from scipy import signal
sr,x=wavfile.read(TRAIN); x=x.astype(float); S,E=14.960,20.965
rng=np.random.default_rng(7)
def xfade(a,b,n):
    r=np.linspace(0,1,n); return np.concatenate([a[:-n],a[-n:]*(1-r)+b[:n]*r,b[n:]])
# host: genuine material only (after the splice, then before it), one host-host seam at the join
host=xfade(x[int(21.0*sr):], x[:int(14.9*sr)], int(0.03*sr))
src=x[int(S*sr):int(E*sr)]
def hp(v,fc): sos=signal.butter(4,fc,'high',fs=sr,output='sos'); return signal.sosfiltfilt(sos,v)
def shift(v,semi):  # resample-based pitch shift (changes duration)
    up,down={-7:(3,2),-5:(4,3),-12:(2,1)}[semi]; return signal.resample_poly(v,up,down)
def reverb(v,rt=2.7,wet_db=-15):
    n=int(rt*sr); t=np.arange(n)/sr; ir=rng.normal(0,1,n)*np.exp(-6.9*t/rt); ir/=np.sqrt((ir**2).sum())
    wet=signal.fftconvolve(v,ir)[:len(v)]; return v+10**(wet_db/20)*wet*np.std(v)/max(np.std(wet),1e-9)
abl={
 'A0_none':lambda v:v,
 'A1_noLF':lambda v:hp(v,200)+2.0,
 'A2_noLF_down7':lambda v:hp(shift(v,-7),200)+2.0,
 'A3_noLF_down7_rev':lambda v:reverb(hp(shift(v,-7),200))+2.0,
 'A4_down7':lambda v:shift(v,-7),
 'A5_rev':lambda v:reverb(v),
 'A6_noLF_rev':lambda v:reverb(hp(v,200))+2.0,
}
rows=[]
for name,f in abl.items():
    mat=f(src.copy())
    for k,(L,pos) in enumerate([(6.0,8.0),(4.0,30.0),(3.0,40.0)]):
        n=int(L*sr); m=mat[:n] if len(mat)>=n else np.concatenate([mat,mat])[:n]
        p=int(pos*sr); seg=host[p:p+n]
        m=m*np.sqrt((seg**2).mean()/max((m**2).mean(),1e-9))
        nf=int(0.03*sr); r=np.linspace(0,1,nf)
        y=host.copy(); y[p:p+n]=m
        y[p:p+nf]=host[p:p+nf]*(1-r)+m[:nf]*r; y[p+n-nf:p+n]=m[-nf:]*(1-r)+host[p+n-nf:p+n]*r
        fn=f'{name}_{k}.wav'; wavfile.write(f'{OUT}/'+fn,sr,np.clip(np.round(y),-32768,32767).astype(np.int16))
        rows.append((fn,name,f'{pos:.3f}',f'{pos+L:.3f}'))
with open(f'{OUT}/labels.csv','w',newline='') as fh:
    c=csv.writer(fh); c.writerow(['file','group','start_s','end_s']); c.writerows(rows)
print(len(rows),'files; host seam at',round((len(x)/sr-21.0),2),'s')
