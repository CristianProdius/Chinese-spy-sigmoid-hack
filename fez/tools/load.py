import csv, glob, os
from solver import parse
S = os.path.dirname(os.path.abspath(__file__))
_DIRS = [S, os.path.join(S, '..', 'data'), os.path.join(S, '..', 'task')]
def datafile(name):
    """Find a data file next to this script, in ../data or in ../task."""
    for d in _DIRS:
        if os.path.exists(os.path.join(d, name)):
            return os.path.join(d, name)
    return os.path.join(S, name)
def rd(f): return list(csv.DictReader(open(f, encoding='utf-8')))
def load_synth():
    """rows: dict(id, prompt, fam, d, c_ok, e_ok (None if missing), cheap, exp)"""
    prompts = {}
    for f in ['synth1.csv', 'synth2.csv']:
        for r in rd(datafile(f)): prompts[r['request_id']] = r['prompt']
    cheap = {}
    for f in ['synth1-cheap-gpu.csv', 'synth2-cheap-gpu.csv']:
        if os.path.exists(datafile(f)):
            for r in rd(datafile(f)): cheap[r['request_id']] = r['cheap_answer']
    exp = {}
    for f in [g for d in _DIRS for g in glob.glob(os.path.join(d, 'synth*_s*-exp.csv'))]:
        for r in rd(f):
            if r.get('expensive_raw'): exp[r['request_id']] = r['expensive_answer']
    out = []
    for k, p in prompts.items():
        fam, d = parse(p)
        a = d['answer']
        out.append(dict(id=k, prompt=p, fam=fam, d=d, src='synth',
                        cheap=cheap.get(k), exp=exp.get(k),
                        c_ok=(cheap[k] == a) if k in cheap else None,
                        e_ok=(exp[k] == a) if k in exp else None))
    return out
def load_train():
    inp = {r['request_id']: r['prompt'] for r in rd(datafile('train-input.csv'))}
    ans = {r['request_id']: r for r in rd(datafile('train-answers.csv'))}
    out = []
    for k, p in inp.items():
        fam, d = parse(p); a = ans[k]
        out.append(dict(id=k, prompt=p, fam=fam, d=d, src='train', cheap=a['cheap_answer'], exp=a['expensive_answer'],
                        c_ok=a['cheap_answer'] == d['answer'], e_ok=a['expensive_answer'] == d['answer']))
    return out
