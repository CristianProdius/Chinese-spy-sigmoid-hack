import sys, time, random
sys.path.insert(0, ".")
from wp import load_vocab, encode
from tokenizers import Tokenizer
vocab = load_vocab("vocab.txt"); tk = Tokenizer.from_file("tokenizer.json")
lines = [l.strip() for l in open("../beir/beir.txt", encoding="utf-8") if l.strip()]
lines += ["the part where the Spaniards first saw people smoking rolled leaves", "the sugar figures for Matanzas in the 1890s", "the traveller who described the tobacco fields of Vuelta Abajo", "Güines, Señor Céspedes – “Habana” 1,234.5 tons; café/azúcar", "tobaeco plantat1ons of tlie Vuelta-Abajo ﬁelds"]
bad = 0
for l in lines:
    a = encode(l, vocab); b = tk.encode(l, add_special_tokens=False).ids
    if a != b:
        bad += 1
        if bad < 4: print("MISMATCH", repr(l[:80]), a[:12], b[:12])
print("lines", len(lines), "mismatches", bad)
q = "the traveller who described the tobacco fields of Vuelta Abajo and the slaves on the sugar estates"
ts=[]
for _ in range(2000):
    t0=time.perf_counter(); encode(q, vocab); ts.append((time.perf_counter()-t0)*1000)
ts.sort(); print("pure-python wordpiece ms: median %.3f p95 %.3f" % (ts[1000], ts[1900]))
t0=time.perf_counter(); load_vocab("vocab.txt"); print("vocab load ms %.1f" % ((time.perf_counter()-t0)*1000))
print([tk.id_to_token(i) for i in encode("tobaeco plantat1ons of tlie Vuelta-Abajo", vocab)])
