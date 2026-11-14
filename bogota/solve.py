"""Looks Good to Me! - Bogota Sound Check: find the altered reviews and recover the flag.

Two kinds of tampering hide in `samples`:
  1. invisible text edits (zero-width spaces, Cyrillic look-alike letters) in the first words;
  2. rating nudges of one star between 3 and 4, which read as perfectly normal.

Kind 1 is found with the trusted set alone (characters that never occur in trusted text).
Kind 2 is only exact when every review is matched back to its public source, the Amazon
"Musical Instruments 5-core" dump, and ratings are compared.  The union of both sets, hashed
as the archive note says, unmasks one seal in the trusted set.

usage: python solve.py [data/reviews.json]
"""
import gzip, hashlib, json, os, re, sys, urllib.request

DATA = sys.argv[1] if len(sys.argv) > 1 else "data/reviews.json"
SRC_URL = "https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Musical_Instruments_5.json.gz"
SRC = os.path.join(os.path.dirname(DATA) or ".", "reviews_Musical_Instruments_5.json.gz")

d = json.load(open(DATA, encoding="utf-8"))
T, S = d["trusted_reference"], d["samples"]

# ---- 1. characters that never appear in the trusted set ---------------------------------
trusted_chars = {c for r in T for c in r["review_text"] + r["summary"]}
text_edited = sorted(s["sample_index"] for s in S
                     if any(c not in trusted_chars for c in s["review_text"] + s["summary"]))
print("text-edited samples (chars absent from trusted):", text_edited)

# ---- 2. match every review to the public Amazon dump and compare ratings ----------------
if not os.path.exists(SRC):
    print("downloading", SRC_URL)
    urllib.request.urlretrieve(SRC_URL, SRC)
CYR = str.maketrans("аеос", "aeoc")
def norm(s):
    s = s.replace("’", "'").replace("–", "-").replace("​", "").translate(CYR)
    return re.sub(r"\s+", " ", s).strip().lower()
src = {}
for line in gzip.open(SRC, "rt", encoding="utf-8"):
    o = json.loads(line)
    src.setdefault(norm(o["reviewText"]), []).append(int(o["overall"]))
unmatched = [s["sample_index"] for s in S if norm(s["review_text"]) not in src]
assert not unmatched, f"unmatched samples: {unmatched}"
assert all(norm(t["review_text"]) in src for t in T)
assert all(t["rating"] in src[norm(t["review_text"])] for t in T), "trusted ratings should be untouched"
rating_edited = sorted(s["sample_index"] for s in S if s["rating"] not in src[norm(s["review_text"])])
print("rating-edited samples (differ from public source):", rating_edited)

# ---- 3. archive note: sha256 of the sorted, comma-joined indices is the XOR mask ---------
altered = sorted(set(text_edited) | set(rating_edited))
key = ",".join(map(str, altered))
mask = hashlib.sha256(key.encode("utf-8")).digest()
print(f"{len(altered)} altered records -> sha256({key!r})")
for kind, R in (("trusted_reference", T), ("samples", S)):
    for i, r in enumerate(R):
        msg = bytes(a ^ b for a, b in zip(bytes.fromhex(r["archive_tag"]), mask)).rstrip(b"\x00")
        if len(msg) > 3 and all(32 <= c < 127 for c in msg):
            print(f"seal {kind}[{r.get('sample_index', i)}] -> {msg.decode()}")
