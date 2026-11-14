import importlib.util, random, sys, collections
import build
from load2 import load_all
spec = importlib.util.spec_from_file_location('router', sys.argv[1] if len(sys.argv) > 1 else __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'main.py'))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
ALL = load_all()
train = [r for r in ALL if r['src'] == 'train']
other = [r for r in ALL if r['src'] != 'train']
K = 5
rng = random.Random(1)
idx = list(range(len(train))); rng.shuffle(idx)
scored = []
for k in range(K):
    hold = set(idx[k::K])
    R.TABLES = build.build_tables(other + [r for i, r in enumerate(train) if i not in hold])
    for i in hold:
        r = train[i]
        pc, pe = R.score(r['prompt'])
        scored.append(dict(fam=r['fam'], pc=pc, pe=pe, c=bool(r['c_ok']), e=bool(r['e_ok'])))
def allocate(rows):
    n = len(rows); E = (19 * n) // 24
    order = sorted(range(n), key=lambda i: -(rows[i]['pe'] - rows[i]['pc']))
    exp = set()
    for i in order:
        if len(exp) >= E or rows[i]['pe'] - rows[i]['pc'] <= 0: break
        exp.add(i)
    q = sum((rows[i]['e'] if i in exp else rows[i]['c']) for i in range(n)) / n
    return q, len(exp)
q, e = allocate(scored)
print('honest 5-fold on train: quality %.4f with %d expensive (cap %d)' % (q, e, 19 * 400 // 24))
byfam = collections.defaultdict(list)
for r in scored: byfam[r['fam']].append(r)
fams = sorted(byfam); mix = [len(byfam[f]) / len(scored) for f in fams]
def gamma_dirichlet(alpha):
    xs = [rng.gammavariate(a, 1) for a in alpha]; s = sum(xs); return [x / s for x in xs]
for alpha_scale in (400, 100, 40):
    qs = []
    for _ in range(3000):
        w = gamma_dirichlet([alpha_scale * m for m in mix])
        counts = [0] * len(fams)
        for _ in range(500):
            u = rng.random(); acc = 0
            for j, wj in enumerate(w):
                acc += wj
                if u <= acc: counts[j] += 1; break
            else: counts[-1] += 1
        rows = []
        for f, c in zip(fams, counts): rows += [rng.choice(byfam[f]) for _ in range(c)]
        qs.append(allocate(rows)[0])
    qs.sort()
    print('mix concentration %4d: mean %.4f  p5 %.4f  p1 %.4f  P(q<0.80) %.4f' % (alpha_scale, sum(qs) / len(qs), qs[150], qs[30], sum(x < 0.80 for x in qs) / len(qs)))
# adversarial shifts: +50% weight on one family at a time
worst = []
for f in fams:
    w = [m * (1.5 if g == f else 1.0) for g, m in zip(fams, mix)]; s = sum(w); w = [x / s for x in w]
    qs = []
    for _ in range(400):
        rows = []
        for g, wj in zip(fams, w): rows += [rng.choice(byfam[g]) for _ in range(round(500 * wj))]
        qs.append(allocate(rows)[0])
    worst.append((sum(qs) / len(qs), f))
print('mean quality with one family up-weighted 1.5x, worst five:', ['%s %.4f' % (f, q) for q, f in sorted(worst)[:5]])

def alloc_cap(rows, E):
    order = sorted(range(len(rows)), key=lambda i: -(rows[i]['pe'] - rows[i]['pc']))
    exp = set()
    for i in order:
        if len(exp) >= E or rows[i]['pe'] - rows[i]['pc'] <= 0: break
        exp.add(i)
    return sum((rows[i]['e'] if i in exp else rows[i]['c']) for i in range(len(rows))) / len(rows), len(exp)
print('uncapped:', alloc_cap(scored, 10**9), ' capped:', alloc_cap(scored, 316), ' all-exp:', sum(r['e'] for r in scored) / 400,
      ' oracle:', sum(r['e'] or r['c'] for r in scored) / 400)
order = sorted(scored, key=lambda r: -(r['pe'] - r['pc']))
print('rows ranked 290-345 (fam, gain, cheapOK, expOK):')
print([(r['fam'], round(r['pe'] - r['pc'], 2), int(r['c']), int(r['e'])) for r in order[290:345]])
