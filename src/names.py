"""Self-distillation data: clean the base model's own answers, then class their names with the teacher.

  python names.py clean    data/prompts_base.jsonl data/clean.jsonl
  python names.py classify data/clean.jsonl data/names_map.json
  python names.py apply    data/clean.jsonl data/names_map.json data/fixed.jsonl

clean: keep the first 1-3 complete sentences (<= 16 words each) of the base answer, no lists.
classify: every distinct capitalised phrase gets a class letter (or N = not a name) from qwen, in batches.
apply: rows in the shape build_sft.py reads (answer + names).
"""
from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from register import FUNC, I_FORMS, STRIP, normalize_plain, split_sentences

CONNECT = {"of", "da", "de", "del", "the", "von", "van", "al", "el", "bin", "ibn", "du", "des", "la", "le", "di"}
TWO = re.compile(r"\b(two|2) sentences\b", re.I)
ONE = re.compile(r"\b(one|1) sentence\b", re.I)


def clean_answer(prompt: str, base: str, kind: str) -> str | None:
    t = base.strip()
    if not t:
        return None
    t = t.split("\n")[0].strip()
    if t.endswith(":") or re.match(r"^(\d+\.|-|\*)\s", t):
        return None
    if re.search(r"\b(\d+\.\d+|[A-Z]\.[A-Z]\.|e\.g\.|i\.e\.|etc\.|Mr\.|Dr\.|St\.)", t):
        return None
    t = normalize_plain(t)
    sents = split_sentences(t)
    maxk = 2 if kind == "fact" else 3
    if TWO.search(prompt):
        maxk = 2
    if ONE.search(prompt):
        maxk = 1
    keep = []
    for s in sents:
        if not s.endswith((".", "?")) or s.endswith(":"):
            break
        if len(s.split()) > 16:
            break
        keep.append(s)
        if len(keep) >= maxk:
            break
    if not keep:
        return None
    if TWO.search(prompt) and len(keep) < 2:
        return None
    return " ".join(keep)


LOWER: set = set()


def build_lower(texts) -> None:
    """Words seen in lowercase somewhere: a capitalised sentence opener among them is not a name."""
    from collections import Counter
    c = Counter(w.strip(STRIP) for t in texts for w in t.split() if w.strip(STRIP)[:1].islower())
    LOWER.update(w for w, k in c.items() if k >= 3)


def phrases(text: str) -> list[tuple[str, str]]:
    """Capitalised name phrases with the sentence they come from. A phrase ends at any punctuation."""
    out = []
    for s in split_sentences(text):
        raw = s.split(" ")
        toks = [t.strip(STRIP) for t in raw]
        stops = [r.rstrip() != r.rstrip().rstrip(".,;:!?)\"'") or r.endswith("'s") for r in raw]
        toks = [t[:-2] if t.endswith("'s") else t for t in toks]
        i = 1 if toks and toks[0].lower() in LOWER else 0
        while i < len(toks):
            t = toks[i]
            if t and t[0].isupper() and t not in I_FORMS and not any(c.isdigit() for c in t):
                j = i + 1
                while j < len(toks) and not stops[j - 1]:
                    u = toks[j]
                    if u and u[0].isupper() and u not in I_FORMS:
                        j += 1
                    elif u.lower() in CONNECT and j + 1 < len(toks) and toks[j + 1][:1].isupper() and not stops[j]:
                        j += 1
                    else:
                        break
                ph = " ".join(toks[i:j])
                # a lone function word ('The', 'In') opening a sentence is never a name
                if not (j == i + 1 and t.lower() in FUNC):
                    out.append((ph, s))
                i = j
            else:
                i += 1
    return out


SYSTEM = """You label names for a constructed register. For each numbered phrase (shown with the sentence it comes from), give ONE letter:
A land: countries, regions, continents, deserts, mountains, ranges, rivers, seas, oceans, lakes, islands, planets, the sun, stars, natural places, weather; adjectives made from a country or region (Algerian, European, French as in French army).
B living: people, roles and titles, peoples and nationalities as groups of people (the Tuareg, the Romans), gods, animals, plants, sports teams and clubs.
C built: cities, towns, villages, buildings, monuments, streets, bridges, ships, vehicles, tools, machines, companies, organisations, institutions, museums, universities, parks.
D time: years, months, days, centuries, eras, ages, periods, wars, battles, revolutions, games, tournaments, Olympics, festivals, holidays, events, prizes and awards.
E speech: languages (Arabic, English, French as a language), writing systems, words, books, plays, poems, stories, songs, films, paintings, artworks, laws, religions and holy books, sciences, music styles, colours, theories.
F goods: food, dishes, drinks, fruits, spices, cloth, goods, coins, currencies, product brands.
N: not a name, an ordinary word capitalised only because it starts the sentence (The, It, Many, People, Yes, This, When, ...).
An adjective made from a name takes the class of that name (Roman from the Romans = B, Arabic = E, Algerian = A).
Answer JSON only: {"1": "C", "2": "N", ...} with one entry per number."""


EVASIVE = re.compile(r"\b(as an ai|i'm sorry|i am sorry|i don't have|i do not have|i'd be happy|i would be happy|"
                     r"i can't|i cannot|i'm not able|i am not able|sure,|certainly|of course|here is|here are|"
                     r"real-time|language model)\b", re.I)
JUDGE_SYSTEM = """For each numbered question with an answer, say Y if the answer is factually correct and actually answers the question, N otherwise (wrong fact, wrong number, evasive, or off-topic). Answer JSON only: {"1": "Y", "2": "N", ...}"""
KEY_SYSTEM = SYSTEM.split("N: not a name")[0] + """Give the correct short answer to the user's question as the shortest string: a name, a number in digits, or one word (e.g. "Madrid", "1962", "oxygen"), and its class letter by the rules above (a plain number or year is D; an ordinary lowercase noun like oxygen still gets the class of what it names).
Answer JSON only: {"key": "Madrid", "key_class": "C"}"""


def classify_batch(batch):
    from gen import chat
    lines = "\n".join(f"{k + 1}. {ph}  || {ctx}" for k, (ph, ctx) in enumerate(batch))
    out = chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": lines}],
               temperature=0.0, max_tokens=12 * len(batch) + 20)
    res = {}
    if isinstance(out, dict):
        for k, (ph, _) in enumerate(batch):
            v = str(out.get(str(k + 1), "")).strip().upper()[:1]
            if v in "ABCDEFN" and v:
                res[ph] = v
    return res


def main():
    mode = sys.argv[1]
    if mode == "clean":
        n = 0
        with open(sys.argv[3], "w") as fh:
            for l in open(sys.argv[2]):
                r = json.loads(l)
                a = clean_answer(r["prompt"], r["base"], r.get("kind", "fact"))
                if a:
                    fh.write(json.dumps({**r, "answer": a}, ensure_ascii=False) + "\n")
                    n += 1
        print("kept", n)
    elif mode == "classify":
        ctx = {}
        build_lower(json.loads(l)["answer"] for l in open(sys.argv[2]))
        for l in open(sys.argv[2]):
            r = json.loads(l)
            for ph, s in phrases(r["answer"]):
                ctx.setdefault(ph, s)
        cache = {}
        for f in sys.argv[4:]:
            cache.update(json.load(open(f)))
        items = sorted((k, v) for k, v in ctx.items() if k not in cache)
        print(len(ctx), "distinct phrases,", len(items), "new", flush=True)
        batches = [items[i:i + 40] for i in range(0, len(items), 40)]
        result = {k: v for k, v in cache.items() if k in ctx}
        with ThreadPoolExecutor(32) as ex:
            for k, res in enumerate(ex.map(classify_batch, batches)):
                result.update(res)
                if k % 20 == 0:
                    print(f"{k}/{len(batches)} batches, {len(result)} labelled", flush=True)
        json.dump(result, open(sys.argv[3], "w"), indent=0, ensure_ascii=False)
        print("labelled", len(result), "of", len(ctx))
    elif mode == "verify_calls":
        # independent second label for each call answer; keep calls where it agrees with the generation class
        rows = [json.loads(l) for f in sys.argv[2:-1] for l in open(f)]
        items = [(r["answer"].strip(), r["prompt"].strip()) for r in rows]
        batches = [items[i:i + 40] for i in range(0, len(items), 40)]
        labels = {}
        with ThreadPoolExecutor(32) as ex:
            for k, res in enumerate(ex.map(classify_batch, batches)):
                labels.update({(ph, b[1]): v for b in batches[k] for ph, v in res.items() if ph == b[0]})
        n = 0
        with open(sys.argv[-1], "w") as fh:
            for r in rows:
                v = labels.get((r["answer"].strip(), r["prompt"].strip()))
                if v == r["class"]:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n += 1
        print("kept", n, "of", len(rows))
    elif mode == "keys":
        # held-out fact prompts: the teacher's short answer + its class, for a grader-format val set
        rows = [json.loads(l) for l in open(sys.argv[2])]
        n = int(sys.argv[4])
        facts = [r for r in rows if r.get("kind") == "fact"][:n]
        from gen import chat

        def key_job(r):
            out = chat([{"role": "system", "content": KEY_SYSTEM}, {"role": "user", "content": r["prompt"]}],
                       temperature=0.0, max_tokens=60)
            if isinstance(out, dict) and out.get("key"):
                return {**r, "key": str(out["key"]).strip(), "key_class": str(out.get("key_class", "")).strip()[:1]}
            return None
        with ThreadPoolExecutor(32) as ex, open(sys.argv[3], "w") as fh:
            k = 0
            for res in ex.map(key_job, facts):
                if res:
                    fh.write(json.dumps(res, ensure_ascii=False) + "\n")
                    k += 1
        print("keys", k)
    elif mode == "judge":
        # batch correctness check of the base model's fact answers; drop evasive replies too
        from gen import chat
        rows = [json.loads(l) for l in open(sys.argv[2])]
        rows = [r for r in rows if not EVASIVE.search(r["answer"])]
        facts = [r for r in rows if r.get("kind") == "fact"]
        batches = [facts[i:i + 20] for i in range(0, len(facts), 20)]

        def judge(b):
            lines = "\n".join(f"{k + 1}. Q: {r['prompt']}  A: {r['answer']}" for k, r in enumerate(b))
            out = chat([{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": lines}],
                       temperature=0.0, max_tokens=10 * len(b) + 20)
            return {k: str(out.get(str(k + 1), "")).upper().startswith("Y") for k in range(len(b))} if isinstance(out, dict) else {}
        ok = set()
        with ThreadPoolExecutor(32) as ex:
            for b, res in zip(batches, ex.map(judge, batches)):
                ok |= {id(b[k]) for k, v in res.items() if v}
        n = 0
        with open(sys.argv[3], "w") as fh:
            for r in rows:
                if r.get("kind") != "fact" or id(r) in ok:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n += 1
        print("kept", n, "of", len(rows), "facts ok", len(ok), "of", len(facts))
    elif mode == "apply":
        nm = json.load(open(sys.argv[3]))
        build_lower(json.loads(l)["answer"] for l in open(sys.argv[2]))
        n = 0
        with open(sys.argv[4], "w") as fh:
            for l in open(sys.argv[2]):
                r = json.loads(l)
                names, ok = [], True
                for ph, _ in phrases(r["answer"]):
                    c = nm.get(ph)
                    if c is None:
                        ok = False
                        break
                    if c != "N":
                        names.append({"name": ph, "class": c})
                if ok:
                    fh.write(json.dumps({**r, "names": names}, ensure_ascii=False) + "\n")
                    n += 1
        print("rows", n)


if __name__ == "__main__":
    main()
