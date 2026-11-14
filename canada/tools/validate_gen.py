"""Validate generated JSONL files: python tools/validate_gen.py data/gen/<prefix>*.jsonl

Each line: {"text": str, "label": one of CLASSES or "none", "lang": "en"|"fr"}.
Prints counts per label x lang, length stats, duplicate texts, and bad lines.
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import CLASSES, tokens, text_lang

ok = collections.Counter(); bad = 0; lens = []; seen = set(); dups = 0; mism = 0
for p in sys.argv[1:]:
    for i, line in enumerate(Path(p).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            o = json.loads(line)
            assert isinstance(o["text"], str) and o["text"].strip()
            assert o["label"] in CLASSES + ["none"], o["label"]
            assert o["lang"] in ("en", "fr"), o["lang"]
        except Exception as e:
            bad += 1; print(f"BAD {p}:{i}: {e}"); continue
        ok[(o["label"], o["lang"])] += 1
        lens.append(len(tokens(o["text"])))
        key = o["text"].strip().lower()
        dups += key in seen; seen.add(key)
        if len(tokens(o["text"])) >= 8 and text_lang(o["text"]) != o["lang"]:
            mism += 1
print("label        en   fr")
for c in CLASSES + ["none"]:
    if ok[(c, "en")] or ok[(c, "fr")]:
        print(f"{c:11s} {ok[(c,'en')]:4d} {ok[(c,'fr')]:4d}")
print(f"total {sum(ok.values())}  bad {bad}  duplicates {dups}  lang-mismatch {mism}")
if lens:
    s = sorted(lens); n = len(s)
    print(f"tokens: min {s[0]} p25 {s[n//4]} median {s[n//2]} p75 {s[3*n//4]} max {s[-1]}")
