import json, sys
fa, fb = sys.argv[1], sys.argv[2]
a={ (r['group'],r['seed'],r['style']): r for r in (json.loads(l) for l in open(fa) if l.startswith('{'))}
b={ (r['group'],r['seed'],r['style']): r for r in (json.loads(l) for l in open(fb) if l.startswith('{'))}
ks=[k for k in b if k in a]
print(len(ks),'A win',sum(a[k]['best']>0 for k in ks),'B win',sum(b[k]['best']>0 for k in ks),'A draw',sum(a[k]['best']==0 for k in ks),'B draw',sum(b[k]['best']==0 for k in ks))
print('mean best A %.1f B %.1f'%(sum(a[k]['best'] for k in ks)/max(1,len(ks)), sum(b[k]['best'] for k in ks)/max(1,len(ks))))
print('B better', sum(b[k]['best']>a[k]['best'] for k in ks), 'worse', sum(b[k]['best']<a[k]['best'] for k in ks))
def maps(d):
    m={}
    for k in ks: m.setdefault(k[:2],[]).append(d[k]['best'])
    full=[v for v in m.values() if len(v)==5]
    return len(full), sum(min(v)>0 for v in full), sum(min(v)==0 for v in full)
print('maps(full, allwin, worstdraw) A', maps(a), 'B', maps(b))
for k in ks[:int(sys.argv[3]) if len(sys.argv)>3 else 0]: print(k, a[k]['best'], b[k]['best'], b[k]['seq'], b[k]['B'], b[k]['ours'], b[k]['theirs'], b[k]['secs'])
