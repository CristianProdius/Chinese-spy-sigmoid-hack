"""Evaluate fez/main.py on train: copy train-input as test-input in a scratch dir, run, score."""
import csv, os, shutil, subprocess, sys, tempfile
S = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.abspath(sys.argv[1])
inp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(S, '..', 'task', 'train-input.csv')
ansf = sys.argv[3] if len(sys.argv) > 3 else os.path.join(S, '..', 'task', 'train-answers.csv')
d = tempfile.mkdtemp()
shutil.copy(inp, d + '/test-input.csv')
r = subprocess.run([sys.executable, MAIN], cwd=d, capture_output=True, text=True)
print(r.stderr.strip())
log = {x['request_id']: x['model'] for x in csv.DictReader(open(d + '/routing_log.csv'))}
ans = {x['request_id']: x for x in csv.DictReader(open(ansf))}
ids = [x['request_id'] for x in csv.DictReader(open(inp))]
assert set(log) == set(ids) and all(v in ('cheap', 'expensive') for v in log.values())
ok = sum(ans[k]['%s_answer' % log[k]].strip().lower() == ans[k]['reference_answer'].strip().lower() for k in ids)
cost = sum(1 if log[k] == 'cheap' else 25 for k in ids)
print('N=%d quality=%.4f cost=%d (%.2f/req, cap %d)' % (len(ids), ok / len(ids), cost, cost / len(ids), 20 * len(ids)))
shutil.rmtree(d)
