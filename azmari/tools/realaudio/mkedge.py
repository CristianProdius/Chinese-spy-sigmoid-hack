"""Real-audio robustness set "edge" built from task_ethiopia/train-input.wav.
Usage: python mkedge.py [out_dir]   (default: azmari/tools/data/edge; writes WAVs + labels.csv)
Score with: python ../eval.py ../../main.py --data <out_dir> --no-train --keep-names
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, '..', '..', '..', 'task_ethiopia', 'train-input.wav')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data', 'edge')
os.makedirs(OUT, exist_ok=True)
import numpy as np, csv
from scipy.io import wavfile
sr,x=wavfile.read(TRAIN); x=x.astype(float); S,E=14.960,20.965
rows=[]
def w(name,y,s,e):
    wavfile.write(f'{OUT}/{name}.wav',sr,np.clip(np.round(y),-32768,32767).astype(np.int16)); rows.append((name+'.wav','edge',f'{s:.3f}',f'{e:.3f}'))
def join(a,b,xf=0.03):
    n=int(xf*sr); r=np.linspace(0,1,n); return np.concatenate([a[:-n], a[-n:]*(1-r)+b[:n]*r, b[n:]])
A=x[int(21.5*sr):]
for g in [0.5,1,1.5,2,3,4]:
    B=x[:int((E+g)*sr)]; y=join(A,B); off=(len(A)-int(0.03*sr))/sr
    w(f'end_{g}',y,S+off,E+off)
for g in [0.5,1,1.5,2,3,4]:
    y=x[int((S-g)*sr):]; w(f'start_{g}',y,g,g+E-S)
with open(f'{OUT}/labels.csv','w',newline='') as f:
    c=csv.writer(f); c.writerow(['file','group','start_s','end_s']); c.writerows(rows)
for r in rows: print(r)
