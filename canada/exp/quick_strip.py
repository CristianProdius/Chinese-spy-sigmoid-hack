"""Quick test: strip header + generic sentences, language-balanced weights."""
import collections, re, sys, numpy as np
sys.path.insert(0, '.')
from lib import *

rows = load_corpus()
shape = lambda s: re.sub(r'\d[\d ,.]*', '0', s)
cnt = collections.defaultdict(collections.Counter)
for r in rows:
    for s in sentences(r['text']):
        cnt[shape(s)][r['label']] += 1
generic = {s for s, c in cnt.items() if len(c) >= 6}
YEAR_END = re.compile(r'\b1[89]\d\d\.$|\b20\d\d\.$')

texts, labels, langs = [], [], []
for r in rows:
    ss = sentences(r['text'])
    keep = []
    for i, s in enumerate(ss):
        if shape(s) in generic: continue
        if i == 0 and YEAR_END.search(s): continue
        keep.append(s)
    if not keep: continue
    texts.append(' '.join(keep)); labels.append(CLASSES.index(r['label'])); langs.append(text_lang(r['text']))
y = np.array(labels); langs = np.array(langs)
print('kept docs', len(texts))
X = featurize(texts)
cell = collections.Counter(zip(y, langs))
w = np.array([len(y) / (18 * cell[(a, l)]) for a, l in zip(y, langs)])
Xs = load_sealed()
for C in (1.0, 10.0):
    for wt in (None, w):
        W, b = train_lr(X, y, C=C, sample_weight=wt)
        tag = f"C={C} balanced={wt is not None}"
        pred, tv = sealed_report(W, b, Xs, tag)
        print(tag, 'vault ->', vault(W, b, Xs))
        save_model(f"exp/quick_strip_C{C}_{'bal' if wt is not None else 'raw'}.npz", W, b)
