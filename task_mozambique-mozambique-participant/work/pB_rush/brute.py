"""Brute-force builder sequences vs one known style at round 0 (offline experiment).
   pypy3 brute.py AGENT.py MAP STYLE [--maxlen 5]"""
import argparse, os, sys, random, time, importlib.util, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab')); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import fasteval as FE
ap = argparse.ArgumentParser(); ap.add_argument('agent'); ap.add_argument('m', type=int); ap.add_argument('style', type=int)
ap.add_argument('--maxlen', type=int, default=5); ap.add_argument('--seed', type=int, default=20261114)
a = ap.parse_args()
spec = importlib.util.spec_from_file_location('ag', os.path.abspath(a.agent)); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
rng = random.Random(a.seed); seeds = [rng.randrange(2 ** 32) for _ in range(a.m + 1)]
grp = FE.GROUPS[a.m % 8]; md = A.generate_map(grp // 2, seeds[a.m]); mp = A.Map(md); seat = grp % 2
eng = A.Engine(mp); ob = json.loads(json.dumps(FE.obs_dict(eng, seat, md)))
g = A.new_game(ob); side = A.obs_side(ob)
hyps = [(a.style, g.hyps[a.style])]
stocks = eng.stocks[:]
cx = A.CX
base = A.base_builder(side, stocks, 0); base.claims0 = [-1] * 8
roots = [base]
for W in cx.mfg:
    for v in (0, 1, 2, 3):
        r = base.copy()
        if r.kit(W, v):
            r.W = W; r.tag = 'k%d%d' % (W, v); roots.append(r)
for r in list(roots):
    r2 = r.copy(); r2.ret = True; r2.tag = r.tag + 'r'; roots.append(r2)
best = None; n = 0; t0 = time.process_time()
res = []
def dfs(node, depth):
    global best, n
    if node.cons:
        exe = node.finish()
        key, ths = A.evaluate_exact(g, exe, hyps)
        n += 1
        res.append((key[0], node.tag))
        if best is None or key > best[0]:
            best = (key, node.tag)
    if depth >= a.maxlen:
        return
    for c in range(8):
        if c in node.cons:
            continue
        ch = node.copy()
        if not ch.add(c):
            continue
        ch.tag = node.tag + '.%d' % c
        d = A.own_sim(ch.finish(), side, stocks, [-1] * 8, 0)
        if c not in d:
            continue
        dfs(ch, depth + 1)
for r in roots:
    dfs(r, 0)
res.sort(reverse=True)
print('evaluated %d plans in %.1fs; best %s' % (n, time.process_time() - t0, best))
print('top:', res[:12])
print('wins:', sum(1 for x in res if x[0] > 0), 'draws:', sum(1 for x in res if x[0] == 0))
