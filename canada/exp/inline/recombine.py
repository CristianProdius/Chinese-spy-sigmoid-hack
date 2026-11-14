"""Decorrelate the synthetic corpus.

The corpus ties labels to things that carry no hazard meaning: the place/date header, generic impact
lines ("Roads were closed"), and language. This rebuilds every row as:
    random header (same language)  +  the row's hazard-bearing sentences  +  0-3 random generic lines
and drops rows with no hazard-bearing sentence. Writes data/corpus_recombined.jsonl.

    .venv/bin/python exp/inline/recombine.py
"""
import collections
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lib import CLASSES, load_corpus, sentences, text_lang  # noqa: E402

YEAR_END = re.compile(r"\b(1[89]\d\d|20\d\d)\.$")
ON_DATE = re.compile(r"^(On|Le) [^,]+, (?:(?:in|near|près de|à) )?[^,]+?(?: \([^)]*\))?[,:] (.+)$")


def shape(s):
    return re.sub(r"\d[\d ,.]*", "0", s)


def split_rows(rows):
    """-> list of (label, lang, header or None, body sentences)."""
    out = []
    for r in rows:
        ss = sentences(r["text"])
        # re-join the "St." splits that the sentence splitter makes
        merged = []
        for s in ss:
            if merged and merged[-1].endswith(("St.", "Ste.", "Mt.")):
                merged[-1] += " " + s
            else:
                merged.append(s)
        header, body = None, merged
        if merged and YEAR_END.search(merged[0]):
            header, body = merged[0], merged[1:]
        elif merged:
            m = ON_DATE.match(merged[0])
            if m:
                rest = m.group(2)
                body = [rest[0].upper() + rest[1:]] + merged[1:]
        out.append((r["label"], text_lang(r["text"]), header, body))
    return out


def build(seed=0, min_classes_generic=6):
    rows = load_corpus()
    parts = split_rows(rows)
    cnt = collections.defaultdict(collections.Counter)
    for label, _, _, body in parts:
        for s in body:
            cnt[shape(s)][label] += 1
    generic = {s for s, c in cnt.items() if len(c) >= min_classes_generic}
    rng = random.Random(seed)
    headers = {"en": [], "fr": []}
    gen_pool = {"en": [], "fr": []}
    for label, lang, header, body in parts:
        if header:
            headers[lang].append(header)
        for s in body:
            if shape(s) in generic:
                gen_pool[lang].append(s)
    out = []
    for label, lang, header, body in parts:
        spec = [s for s in body if shape(s) not in generic]
        if not spec:
            continue
        doc = []
        if rng.random() < 0.8:
            doc.append(rng.choice(headers[lang]))
        doc += spec
        for _ in range(rng.randint(0, 3)):
            doc.insert(rng.randint(1 if doc and doc[0] in headers[lang] else 0, len(doc)), rng.choice(gen_pool[lang]))
        out.append({"text": " ".join(doc), "label": label, "lang": lang})
    return out


if __name__ == "__main__":
    docs = build()
    p = ROOT / "data/corpus_recombined.jsonl"
    p.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs), encoding="utf-8")
    c = collections.Counter((d["label"], d["lang"]) for d in docs)
    print(len(docs), "docs ->", p)
    for k in CLASSES:
        print(f"{k:11s} {c[(k,'en')]:4d} {c[(k,'fr')]:4d}")
    for d in docs[:5]:
        print(d)
