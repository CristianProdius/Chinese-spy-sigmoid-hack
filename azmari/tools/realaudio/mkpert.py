"""Real-audio robustness set "pert" built from task_ethiopia/train-input.wav.
Usage: python mkpert.py [out_dir]   (default: azmari/tools/data/pert; writes WAVs + labels.csv)
Score with: python ../eval.py ../../main.py --data <out_dir> --no-train --keep-names
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, '..', '..', '..', 'task_ethiopia', 'train-input.wav')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'data', 'pert')
os.makedirs(OUT, exist_ok=True)
import numpy as np, csv
from scipy.io import wavfile
from scipy.signal import resample_poly
sr,x=wavfile.read(TRAIN); S,E=14.960,20.965
rows=[]
def w(name,y,s,e,rate=sr):
    y=np.clip(np.round(y),-32768,32767).astype(np.int16); wavfile.write(f'{OUT}/{name}.wav',rate,y); rows.append((name+'.wav','pert',f'{s:.3f}',f'{e:.3f}'))
xf=x.astype(float)
w('orig',xf,S,E)
for r,(u,d) in {'44k':(2,1),'16k':(320,441),'48k':(160,73),'11k':(1,2)}.items():
    rate=int(round(sr*u/d)); w('sr_'+r,resample_poly(xf,u,d),S,E,rate)
for cut in [10,12,13.5]:   # splice near start
    w(f'cutstart_{cut}',xf[int(cut*sr):],S-cut,E-cut)
for keep in [24,23,22]:    # splice near end
    w(f'cutend_{keep}',xf[:int(keep*sr)],S,E)
w('loop2x',np.concatenate([xf, xf[int(E*sr)+sr:]]),S,E)   # longer file (host appended)
w('short30',xf[int(5*sr):int(35*sr)],S-5,E-5)
w('gain_x3',xf*3,S,E)
w('noise_add',xf+np.random.default_rng(0).normal(0,20,len(xf)),S,E)
w('dc_shift',xf+50,S,E)
w('reversed',xf[::-1],len(xf)/sr-E,len(xf)/sr-S)
st=np.stack([xf,xf*0.9],1); y=np.clip(np.round(st),-32768,32767).astype(np.int16); wavfile.write(f'{OUT}/stereo.wav',sr,y); rows.append(('stereo.wav','pert',f'{S:.3f}',f'{E:.3f}'))
with open(f'{OUT}/labels.csv','w',newline='') as f:
    c=csv.writer(f); c.writerow(['file','group','start_s','end_s']); c.writerows(rows)
print(len(rows))
