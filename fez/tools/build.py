"""Build the probability tables the router embeds.

p_cheap and p_expensive per (family, cell): pooled counts from GPU-labelled synthetic + grid prompts and
the 400 training rows (recorded CPU answers, weight W_TRAIN), shrunk toward a parent bucket.
Cheap picks on souk questions use a name+position conditional logit.
"""
import json
import math
import sys
from collections import defaultdict

from load2 import load_all

W_TRAIN = 10.0     # one training row (true generator, reference CPU build) counts as 10 synthetic rows
M_CELL = 4.0       # prior strength pulling a cell toward its parent
M_PARENT = 10.0    # prior strength pulling a parent toward the family rate
SOUKS = ['attarine', 'boujloud', 'cherabliyine', 'chouara', 'henna', 'nejjarine', 'rcif', 'sagha', 'seffarine', 'talaa']


def walk_parts(d):
    s, t, E = d['src'], d['dst'], d['edges']
    nodes = set()
    for a, b, _ in E:
        nodes.update([a, b])
    via = [x for x in nodes if x not in (s, t) and any({a, b} == {s, x} for a, b, _ in E)
           and any({a, b} == {x, t} for a, b, _ in E)]
    if d['direct'] is None or not via:
        return None
    v = via[0]
    a = [w for x, y, w in E if {x, y} == {s, v}][0]
    b = [w for x, y, w in E if {x, y} == {v, t}][0]
    return a, b, d['direct'], max(w for _, _, w in E)


def walk_keys(fam, d):
    """(kind, cheap cell, exp cell) for a walk."""
    wp = walk_parts(d)
    if wp is None:
        return 'odd', 'odd', 'odd'
    a, b, dd, mx = wp
    if dd > a + b:
        return 'det', 'det', 'det_d%d' % min(dd // 4, 6)
    slack = a + b - dd
    sb = 0 if slack <= 2 else 1 if slack <= 5 else 2 if slack <= 9 else 3
    rank = ('lt_min' if dd < min(a, b) else 'eq_min' if dd == min(a, b) else 'mid' if dd < max(a, b)
            else 'eq_max' if dd == max(a, b) else 'gt_max')
    return 'dir', 'dir_max%d_s%d' % (dd == mx, sb), 'dir_%s' % rank


def cells(fam, d):
    """(cheap parent, cheap cell, exp parent, exp cell) for one request; None means 'use a model'."""
    if fam == 'price':
        return 'all', 'all', 'all', 'all'
    if fam == 'price_ind':
        return d['item'], '%s|%d' % (d['item'], d['pos']), 'all', 'all'
    if fam == 'toll1':
        return 'b%d' % d['base'], 'b%d|n%d' % (d['base'], d['n']), 'all', 'all'
    if fam == 'toll2':
        return 'all', 'all', 'all', 'k1' if d['k'] == 1 else 'k2+'
    if fam == 'stall1':
        return 'h%d' % d['h1'], 'h%d|o%d' % (d['h1'], d['open']), 'all', 'm45' if d['open'] % 60 >= 45 else 'm<45'
    if fam == 'stall2':
        return 'all', 'all', 'all', 'p%d' % d['pause']
    if fam in ('walk3', 'walk4'):
        kind, ck, ek = walk_keys(fam, d)
        return kind, ck, kind, ek
    if fam in ('take_most', 'take_least'):
        return None, None, 'all', 'all'
    if fam in ('fee_most', 'fee_least'):
        net = sorted(v for _, v in d['net'])
        gap = net[-1] - net[-2] if d['most'] else net[1] - net[0]
        return None, None, 'all', 'g%d' % min(gap // 10, 2)
    if fam == 'crate1':
        return 'c%d' % d['c'], 'c%d|b%d' % (d['c'], d['b']), 'all', 'all'
    if fam == 'crate2':
        return 'all', 'all', 'all', 'all'
    raise KeyError(fam)


def shrink(k, n, prior, m):
    return (k + m * prior) / (n + m)


def build_tables(rows, w_train=W_TRAIN):
    cnt = {g: defaultdict(lambda: [0.0, 0.0]) for g in ('c', 'e')}   # (fam, level, key) -> [k, n]
    for r in rows:
        try:
            cp, cc, ep, ec = cells(r['fam'], r['d'])
        except Exception:
            continue
        w = w_train if r['src'] == 'train' else 1.0
        for g, ok, par, cel in (('c', r['c_ok'], cp, cc), ('e', r['e_ok'], ep, ec)):
            if ok is None or par is None:
                continue
            for key in ((r['fam'], 'F', ''), (r['fam'], 'P', par), (r['fam'], 'C', par + '#' + cel)):
                cnt[g][key][0] += w * ok
                cnt[g][key][1] += w
    tables = {}
    for g in ('c', 'e'):
        fam_rate = {f: k / n for (f, lv, _), (k, n) in cnt[g].items() if lv == 'F' for _ in [0]}
        par = {}
        for (f, lv, key), (k, n) in cnt[g].items():
            if lv == 'P':
                par[(f, key)] = shrink(k, n, fam_rate[f], M_PARENT)
        cel = {}
        for (f, lv, key), (k, n) in cnt[g].items():
            if lv == 'C':
                p = key.split('#', 1)[0]
                cel[f + '#' + key] = round(shrink(k, n, par[(f, p)], M_CELL), 4)
        tables[g] = {'fam': {f: round(v, 4) for f, v in fam_rate.items()},
                     'par': {f + '#' + k: round(v, 4) for (f, k), v in par.items()},
                     'cell': cel}
    tables['logit'] = {grp: fit_logit(rows, fams, w_train) for grp, fams in
                       (('take', ('take_most', 'take_least')), ('fee', ('fee_most', 'fee_least')))}
    return tables


def fit_logit(rows, fams, w_train, iters=400, lr=0.5, l2=0.01):
    data = []
    for r in rows:
        if r['fam'] not in fams or r['cheap'] is None:
            continue
        names = [s.lower() for s, _ in r['d']['takings']]
        if r['cheap'] in names:
            data.append((names, names.index(r['cheap']), w_train if r['src'] == 'train' else 1.0))
    w = {}
    tot = sum(x[2] for x in data)
    for _ in range(iters):
        g = defaultdict(float)
        for names, j, wt in data:
            sc = [w.get('n_' + n, 0.0) + w.get('p%d' % i, 0.0) for i, n in enumerate(names)]
            m = max(sc)
            ex = [math.exp(s - m) for s in sc]
            z = sum(ex)
            for i, n in enumerate(names):
                resid = wt * ((1.0 if i == j else 0.0) - ex[i] / z)
                g['n_' + n] += resid
                g['p%d' % i] += resid
        for k in set(g) | set(w):
            w[k] = w.get(k, 0.0) + lr * (g.get(k, 0.0) / tot - l2 * w.get(k, 0.0))
    return {k: round(v, 4) for k, v in w.items()}


if __name__ == '__main__':
    t = build_tables(load_all())
    json.dump(t, open(sys.argv[1] if len(sys.argv) > 1 else 'tables.json', 'w'), indent=0, sort_keys=True)
    print('cells c=%d e=%d' % (len(t['c']['cell']), len(t['e']['cell'])))
