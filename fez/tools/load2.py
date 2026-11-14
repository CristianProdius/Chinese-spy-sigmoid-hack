from load import *
import csv, os
def load_grid():
    P = {r['request_id']: r['prompt'] for r in rd(datafile('grid.csv'))}
    C = {r['request_id']: r['cheap_answer'] for r in rd(datafile('grid-cheap-gpu.csv'))}
    out = []
    for k, p in P.items():
        fam, d = parse(p)
        out.append(dict(id=k, prompt=p, fam=fam, d=d, src='grid', cheap=C.get(k), exp=None,
                        c_ok=(C[k] == d['answer']) if k in C else None, e_ok=None))
    return out
def keep(r):
    """drop synthetic rows whose structure never occurs in train"""
    if r['src'] == 'train': return True
    f, d = r['fam'], r['d']
    if f == 'stall2' and d['pause'] == 30: return False
    if f.startswith('walk') and r['id'].startswith('syn1_'): return False  # random edge orientation
    if f == 'price_ind' and d['pos'] == 0: return False
    return True
def load_all():
    return [r for r in load_synth() + load_grid() + load_train() if keep(r)]
