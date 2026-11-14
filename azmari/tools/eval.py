#!/usr/bin/env python3
"""Evaluate a splice detector (main.py) on a labelled benchmark (default: SIM2 in ./data) plus the real
training file. Copy of wf1/out/sim/eval.py with --data and group support.

Usage: eval2.py MAIN_PY [--data DIR] [--groups near,weak] [--files near_01,hard_03] [--jobs 4] [--python PY]
                [--timeout 600] [--no-train] [--keep-names] [--csv results.csv]

--data DIR holds the WAVs and labels.csv (columns file,start_s,end_s and group or scenario; extra columns
such as params are ignored). Works for SIM2 (sim2/data) and SIM1 (wf1/out/sim/data, --groups = scenarios).

Each WAV is copied alone, with a copy of MAIN_PY, into a fresh temp dir and the detector runs there
as `python main.py test-1-input.wav` (the grader's call; --keep-names keeps the original file name).
It must write detection.csv (header start_s,end_s, one row). A file passes when both
|start error| and |end error| are <= 1.5 s. Up to 4 files run at once, with BLAS threads capped at 1.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1.5


def read_det(path):
    with open(path, newline='') as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    if not rows or [c.strip() for c in rows[0]] != ['start_s', 'end_s']:
        raise ValueError(f'bad header {rows[:1]}')
    if len(rows) != 2:
        raise ValueError(f'expected exactly one data row, got {len(rows) - 1}')
    return float(rows[1][0]), float(rows[1][1])


def run_one(job, a):
    wav, scen, ts, te = job
    name = os.path.basename(wav) if a.keep_names else 'test-1-input.wav'
    res = dict(file=os.path.basename(wav), group=scen, true_s=ts, true_e=te, pred_s=None, pred_e=None,
               err_s=None, err_e=None, ok=False, secs=0.0, note='')
    with tempfile.TemporaryDirectory(prefix='azmari_eval_') as d:
        shutil.copy(a.main, os.path.join(d, 'main.py'))
        shutil.copy(wav, os.path.join(d, name))
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1',
                   NUMEXPR_NUM_THREADS='1')
        t0 = time.time()
        try:
            p = subprocess.run([a.python, 'main.py', name], cwd=d, env=env, capture_output=True, text=True,
                               timeout=a.timeout)
            res['secs'] = time.time() - t0
            if p.returncode != 0:
                res['note'] = f'exit {p.returncode}: ' + (p.stderr.strip().splitlines() or [''])[-1][:120]
        except subprocess.TimeoutExpired:
            res['secs'] = time.time() - t0
            res['note'] = f'timeout {a.timeout}s'
            return res
        det = os.path.join(d, 'detection.csv')
        extra = sorted(set(os.listdir(d)) - {'main.py', name, 'detection.csv', '__pycache__'})
        if extra:
            res['note'] += f' extra files: {extra[:4]}'
        if not os.path.exists(det):
            res['note'] += ' no detection.csv'
            return res
        try:
            ps, pe = read_det(det)
        except Exception as ex:  # malformed output counts as a fail
            res['note'] += f' bad detection.csv: {ex}'
            return res
    res.update(pred_s=ps, pred_e=pe, err_s=ps - ts, err_e=pe - te)
    res['ok'] = abs(ps - ts) <= TOL and abs(pe - te) <= TOL
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('main')
    ap.add_argument('--groups', '--scenarios', dest='scenarios', default='',
                    help='comma list of groups/scenarios, e.g. near,weak (default: all)')
    ap.add_argument('--files', default='', help='comma list of file stems, e.g. a_1,h_3')
    ap.add_argument('--data', default=os.path.join(HERE, 'data'), help='dir with the WAVs and labels.csv')
    ap.add_argument('--train', default=os.path.normpath(os.path.join(HERE, '..', '..', 'task_ethiopia', 'train-input.wav')))
    ap.add_argument('--no-train', action='store_true')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--python', default=sys.executable)
    ap.add_argument('--timeout', type=float, default=600)
    ap.add_argument('--keep-names', action='store_true')
    ap.add_argument('--csv', default='', help='also write per-file results here')
    a = ap.parse_args()
    a.main = os.path.abspath(a.main)
    a.data = os.path.abspath(a.data)

    scen_ok = set(s.strip() for s in a.scenarios.split(',') if s.strip())
    file_ok = set(s.strip() for s in a.files.split(',') if s.strip())
    jobs = []
    if not a.no_train and os.path.exists(a.train):
        lab = os.path.join(os.path.dirname(a.train), 'train-output.csv')
        ts, te = read_det(lab)
        jobs.append((a.train, 'train', ts, te))
    lp = os.path.join(a.data, 'labels.csv')
    if not os.path.exists(lp):
        print(f'warning: no {lp}; evaluating the training file only', file=sys.stderr)
    with open(lp if os.path.exists(lp) else os.devnull, newline='') as f:
        for r in csv.DictReader(f):
            stem = r['file'].rsplit('.', 1)[0]
            grp = r.get('group') or r.get('scenario') or '?'
            if (scen_ok and grp not in scen_ok) or (file_ok and stem not in file_ok):
                continue
            jobs.append((os.path.join(a.data, r['file']), grp, float(r['start_s']), float(r['end_s'])))

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, min(a.jobs, 4))) as ex:
        results = list(ex.map(lambda j: run_one(j, a), jobs))

    def f3(v):
        return '   -   ' if v is None else f'{v:7.2f}'
    print(f"{'file':16s} {'grp':5s} {'true':>15s} {'pred':>15s} {'err_s':>7s} {'err_e':>7s} res   secs  note")
    for r in results:
        print(f"{r['file'][:16]:16s} {r['group']:5s} {r['true_s']:7.2f}-{r['true_e']:<7.2f} "
              f"{f3(r['pred_s'])}-{f3(r['pred_e']).strip():7s} {f3(r['err_s'])} {f3(r['err_e'])} "
              f"{'PASS' if r['ok'] else 'FAIL'} {r['secs']:6.1f}  {r['note'].strip()}")

    print('\ngroup      pass   rate   median|err|')
    groups = {}
    for r in results:
        groups.setdefault(r['group'], []).append(r)
    synth = [r for r in results if r['group'] != 'train']
    for sc in sorted(groups, key=lambda s: (s != 'train', s)):
        g = groups[sc]
        errs = [max(abs(r['err_s']), abs(r['err_e'])) for r in g if r['err_s'] is not None]
        med = sorted(errs)[len(errs) // 2] if errs else float('nan')
        npass = sum(r['ok'] for r in g)
        print(f'{sc:8s} {npass:3d}/{len(g):<3d} {npass / len(g):6.1%}   {med:6.2f}')
    if synth:
        p = sum(r['ok'] for r in synth) / len(synth)
        print(f"{'synthetic':8s} {sum(r['ok'] for r in synth):3d}/{len(synth):<3d} {p:6.1%}"
              f"   (3 independent tests all passing at this rate: {p ** 3:.1%})")
    print(f'wall {time.time() - t0:.0f}s')
    if a.csv:
        with open(a.csv, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)


if __name__ == '__main__':
    main()
