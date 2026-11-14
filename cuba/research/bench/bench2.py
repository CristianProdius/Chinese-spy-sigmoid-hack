"""Calibration, casting costs, vocab lookup, tokenizer and stemmer speed, mmap first-touch."""
import os, time, json, re, gc, statistics, subprocess, sys
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
I = "idx/"
clk = time.thread_time

def t(fn, n=7):
    xs = []
    for _ in range(n):
        a = clk(); fn(); xs.append(clk() - a)
    return statistics.median(xs) * 1e3

E32 = np.load(I + "emb32.npy"); E16 = np.load(I + "emb16.npy"); E8 = np.load(I + "emb8.npy")
print("=== CALIBRATION / CASTS (CPU ms) ===")
print(f"memcpy 46MB (E32.copy())            {t(lambda: E32.copy(), 5):8.2f}")
print(f"f16->f32 cast 11.5M elems           {t(lambda: E16.astype(np.float32), 5):8.2f}")
print(f"i8->f32 cast 11.5M elems            {t(lambda: E8.astype(np.float32), 5):8.2f}")
print(f"f32 sum 11.5M (bandwidth)           {t(lambda: E32.sum(), 5):8.2f}")

print("\n=== VOCAB LOOKUP for a 10-term query (us) ===")
words = open(I + "vocab.txt").read().split("\n")
d = {w: i for i, w in enumerate(words)}
U = np.load(I + "vocab_sorted_U.npy"); S = np.load(I + "vocab_sorted_S.npy"); order = np.load(I + "vocab_order.npy")
rng = np.random.default_rng(0)
q = [words[i] for i in rng.choice(len(words), 10)] + ["zzznotaword"]
qU = np.array(q); qS = np.array([x.encode() for x in q])
def ss_U():
    pos = np.searchsorted(U, qU); pos = np.minimum(pos, len(U) - 1)
    hit = U[pos] == qU
    return order[pos[hit]]
def ss_S():
    pos = np.searchsorted(S, qS); pos = np.minimum(pos, len(S) - 1)
    hit = S[pos] == qS
    return order[pos[hit]]
assert sorted(ss_U().tolist()) == sorted(d[x] for x in q if x in d)
print(f"python dict .get x11                {t(lambda: [d.get(x) for x in q], 101)*1e3:8.1f}")
print(f"np.searchsorted on sorted U array   {t(ss_U, 101)*1e3:8.1f}")
print(f"np.searchsorted on sorted S array   {t(ss_S, 101)*1e3:8.1f}")

print("\n=== TOKENIZER + STEMMERS ===")
text = ("the part where the Spaniards first saw people smoking rolled leaves and the sugar figures for "
        "Matanzas in the 1890s, the traveller who described the tobacco fields of Vuelta Abajo plantations "
        "negroes ingenios hacendados insurrection governorship captain-general")
tok_re = re.compile(r"[a-z0-9]+")
print(f"regex lower+findall on 40-word query {t(lambda: tok_re.findall(text.lower()), 201)*1e3:8.1f} us")
import unicodedata
print(f"NFKD strip accents on query          {t(lambda: unicodedata.normalize('NFKD', text).encode('ascii','ignore'), 201)*1e3:8.1f} us")
toks = tok_re.findall(text.lower())
import snowballstemmer
a = clk(); st = snowballstemmer.stemmer("english"); b = clk()
print(f"snowballstemmer construct            {(b-a)*1e3:8.2f} ms")
print(f"snowballstemmer(pure py) {len(toks)} words  {t(lambda: [st.stemWord(w) for w in toks], 51)*1e3:8.1f} us  ({t(lambda: [st.stemWord(w) for w in toks], 51)*1e6/len(toks):.1f} us/word)")
print(f"snowballstemmer stemWords batch      {t(lambda: st.stemWords(toks), 51)*1e3:8.1f} us")
try:
    import Stemmer
    cst = Stemmer.Stemmer("english")
    print(f"PyStemmer (C) {len(toks)} words           {t(lambda: cst.stemWords(toks), 201)*1e3:8.1f} us")
except Exception as e:
    print("PyStemmer n/a", e)
try:
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    print(f"nltk PorterStemmer {len(toks)} words      {t(lambda: [ps.stem(w) for w in toks], 51)*1e3:8.1f} us")
except Exception as e:
    print("nltk n/a")
# surface->stem lookup table (built offline)
stemmap = {w: st.stemWord(w) for w in toks}
print(f"precomputed surface->id dict lookup  {t(lambda: [stemmap.get(w) for w in toks], 201)*1e3:8.1f} us")

print("\n=== MMAP first touch vs np.load: scoring a query on mmap'd postings ===")
indptr = np.load(I + "indptr.npy")
def fresh_mmap_query():
    ind = np.load(I + "indices.npy", mmap_mode="r"); dat = np.load(I + "data32.npy", mmap_mode="r")
    s = np.zeros(30000, np.float32)
    for tid in (5, 50, 500, 5000, 20000):
        a_, b_ = int(indptr[tid]), int(indptr[tid + 1])
        s[ind[a_:b_]] += dat[a_:b_]
    return s
print(f"mmap open + 5-term query (warm cache) {t(fresh_mmap_query, 21):8.3f} ms")
