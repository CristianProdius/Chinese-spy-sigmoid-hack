import time, re, sys, random, statistics
import snowballstemmer, inspect
st = snowballstemmer.stemmer("english")
print("stemmer class:", type(st), inspect.getsourcefile(type(st)) if hasattr(type(st), '__module__') else '')
src = open(inspect.getsourcefile(snowballstemmer.basestemmer)).read() if hasattr(snowballstemmer, 'basestemmer') else ''
print("has cache in basestemmer:", '_cache' in src or 'cache' in src.lower())
# distinct English-ish words from python stdlib docstrings
import pydoc, os
txt = open(os.path.join(os.path.dirname(os.__file__), 'argparse.py')).read() + open(os.path.join(os.path.dirname(os.__file__), 'typing.py')).read() + open(os.path.join(os.path.dirname(os.__file__), 'inspect.py')).read()
words = sorted(set(re.findall(r"[a-z]{3,}", txt.lower())))
random.seed(0); random.shuffle(words)
print("distinct words:", len(words))
clk = time.thread_time
a = clk(); out = [st.stemWord(w) for w in words]; b = clk()
print(f"snowball (pure python) first pass: {(b-a)*1e6/len(words):.1f} us/word")
a = clk(); out = [st.stemWord(w) for w in words]; b = clk()
print(f"snowball (pure python) second pass (cache?): {(b-a)*1e6/len(words):.1f} us/word")
st2 = snowballstemmer.stemmer("english")
q = words[:12]
xs=[]
for i in range(200):
    st2 = snowballstemmer.stemmer("english")  # fresh => no cache
    a = clk(); [st2.stemWord(w) for w in q]; xs.append(clk()-a)
print(f"12-word query, fresh stemmer each time: median {statistics.median(xs)*1e6:.1f} us, p95 {sorted(xs)[189]*1e6:.1f} us")
a = clk(); import importlib; b = clk()
