"""Plain English -> the Call of the Square register, deterministic.

Content words come from the caller; this module only applies the register's surface rules
(opening, table words, numerals, name suffixes, seals). Every output is checked with the
task's own style_checker; to_register() returns None when the result is not 100% clean.

Names (capitalised words) need a class A-F from outside (the teacher model labels them).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

TASK = Path(os.environ.get("ALG_TASK", Path(__file__).resolve().parent.parent / "task_algeria"))
sys.path.insert(0, str(TASK))
from style_checker import vocab, check_reply, deregister, split_sentences, MAX_WORDS  # noqa: E402

V = vocab()
SUFFIX = {k: c["suffix"] for k, c in V["classes"].items()}
SEAL = {k: c["seal"] for k, c in V["classes"].items()}
NEUTRAL = V["neutral_seal"]
DIGITS = V["digits"]
FORM2BASE = {k.lower(): b for k, b in V["forbidden_english"].items()}
WORDS = V["words"]
STRIP = ".,;:!?\"'()[]{}«»“”‘’"
I_FORMS = {"I", "I'm", "I've", "I'd", "I'll"}

UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * (i + 2) for i, w in enumerate("twenty thirty forty fifty sixty seventy eighty ninety".split())}
SCALES = {"thousand": 1000, "million": 1_000_000, "billion": 1_000_000_000}
NUMWORDS = set(UNITS) | set(TENS) | set(SCALES) | {"hundred"}
ORD_UNITS = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth",
             "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth",
             "seventeenth", "eighteenth", "nineteenth"]
ORD_TENS = {20: "twentieth", 30: "thirtieth", 40: "fortieth", 50: "fiftieth", 60: "sixtieth", 70: "seventieth",
            80: "eightieth", 90: "ninetieth"}
TENS_WORD = {v: k for k, v in TENS.items()}
# lowercase these when capitalised inside a sentence (title words, name particles)
FUNC = {"the", "of", "and", "a", "an", "in", "on", "at", "for", "to", "with", "de", "da", "del", "la", "le",
        "von", "van", "al", "el", "du", "des", "di", "or", "from", "by"}
# 'one' stays a pronoun in these spots
ONE_PREV = {"no", "the", "this", "that", "any", "every", "each", "which", "someone", "anyone"}
ONE_NEXT = {"of", "another", "can", "must", "should", "may", "might", "will", "would", "who", "that", "which"}
BUILTIN_CLASS = {"BC": "D", "AD": "D", "BCE": "D", "CE": "D", "Celsius": "D", "Fahrenheit": "D"}
for _d in "Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July " \
          "August September October November December".split():
    BUILTIN_CLASS[_d] = "D"


class Fail(Exception):
    pass


def numeral(n: int) -> str:
    return "-".join(DIGITS[int(c)] for c in str(n)) + "-eth"


def ordinal_words(n: int) -> str:
    if n < 20:
        return ORD_UNITS[n]
    if n < 100:
        t, u = divmod(n, 10)
        return ORD_TENS[n] if u == 0 else f"{TENS_WORD[t * 10]}-{ORD_UNITS[u]}"
    raise Fail(f"ordinal {n}")


def words_to_int(ws: list[str]) -> int | None:
    total, cur, any_num = 0, 0, False
    for w in ws:
        if w in UNITS:
            cur += UNITS[w]
        elif w in TENS:
            cur += TENS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        elif w in SCALES:
            total += (cur or 1) * SCALES[w]
            cur = 0
        elif w == "and" and any_num:
            continue
        else:
            return None
        any_num = True
    return total + cur if any_num else None


def _split_tok(raw: str) -> tuple[str, str, str]:
    core = raw.strip(STRIP)
    if not core:
        return raw, "", ""
    i = raw.index(core[0]) if core else 0
    lead = raw[:i]
    trail = raw[i + len(core):]
    return lead, core, trail


def normalize_plain(text: str) -> str:
    t = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = t.replace("—", ", ").replace("–", "-").replace("…", ".")
    t = re.sub(r"[\"()\[\]{}*_#`]", "", t)
    t = t.replace("!", ".").replace(";", ",")
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)
    t = re.sub(r"(\d),(\d{3})", r"\1\2", t)
    t = re.sub(r"(\d+)\s*%", r"\1 percent", t)
    t = re.sub(r"(\d+)\s*°\s*C\b", r"\1 degrees Celsius", t)
    t = re.sub(r"(\d+)\s*°\s*F\b", r"\1 degrees Fahrenheit", t)
    t = re.sub(r"(\d+)(st|nd|rd|th)\b", lambda m: ordinal_words(int(m.group(1))), t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _name_classes(names) -> dict[str, str]:
    out = dict(BUILTIN_CLASS)
    items = names.items() if isinstance(names, dict) else [(n["name"], n["class"]) for n in names]
    for phrase, cls in items:
        cls = str(cls).strip().upper()[:1]
        if cls not in SUFFIX:
            continue
        phrase = phrase.strip()
        out[phrase] = cls  # whole hyphenated / single token
        for w in phrase.split():
            w = w.strip(STRIP)
            if w.endswith("'s"):
                w = w[:-2]
            if w and w[0].isupper() and w.lower() not in FUNC and w not in I_FORMS:
                out.setdefault(w, cls)
    return out


def convert_sentence(sent: str, cls_of: dict[str, str], first_of_reply: bool) -> str:
    raw_toks = sent.split(" ")
    # terminal punctuation
    end = "?" if sent.rstrip().endswith("?") else "."
    out: list[str] = []
    last_cls = None
    i = 0
    n = len(raw_toks)
    while i < n:
        raw = raw_toks[i]
        lead, core, trail = _split_tok(raw)
        if i == n - 1:
            trail = trail.rstrip(".?!")
        if not core:
            if raw.strip(STRIP + "-"):
                raise Fail(f"odd token {raw!r}")
            i += 1
            continue
        poss = ""
        if len(core) > 2 and core[-2:] == "'s":
            poss, core = "'s", core[:-2]
        low = core.lower()
        first = i == 0
        # ---- numbers in words (possibly several tokens: "two hundred and five") ----
        if low.split("-")[0] in NUMWORDS and all(p in NUMWORDS for p in low.split("-")):
            is_pronoun = low == "one" and (
                (i > 0 and raw_toks[i - 1].lower().strip(STRIP) in ONE_PREV)
                or (i + 1 < n and raw_toks[i + 1].lower().strip(STRIP) in ONE_NEXT))
            if not is_pronoun:
                ws = low.split("-")
                j = i + 1
                cur_trail = trail
                while j < n and not cur_trail and not poss:
                    l2, c2, t2 = _split_tok(raw_toks[j])
                    c2l = c2.lower()
                    parts = c2l.split("-")
                    if c2l == "and" and j + 1 < n and raw_toks[j + 1].lower().strip(STRIP).split("-")[0] in NUMWORDS \
                            and ws[-1] in ("hundred", "thousand", "million", "billion"):
                        ws.append("and")
                        j += 1
                        continue
                    if c2 and all(p in NUMWORDS for p in parts) and not l2:
                        ws.extend(parts)
                        cur_trail = t2 if j < n - 1 else t2.rstrip(".?!")
                        j += 1
                    else:
                        break
                val = words_to_int(ws)
                if val is None:
                    raise Fail(f"number words {ws}")
                out.append(lead + numeral(val) + poss + cur_trail)
                last_cls = "D"
                i = j
                continue
        # ---- digits ----
        if any(ch.isdigit() for ch in core):
            m = re.fullmatch(r"(\d+)(?:\.(\d+))?", core)
            if not m:
                raise Fail(f"digit token {core!r}")
            tok = numeral(int(m.group(1)))
            if m.group(2):
                tok += " point " + numeral(int(m.group(2)))
            out.append(lead + tok + poss + trail)
            last_cls = "D"
            i += 1
            continue
        # ---- table words ----
        if low in FORM2BASE:
            info = WORDS[FORM2BASE[low]]
            stem = info["stem"]
            if first:
                stem = stem[0].upper() + stem[1:]
            out.append(lead + f"{stem}-{SUFFIX[info['class']]}" + poss + trail)
            last_cls = info["class"]
            i += 1
            continue
        if "-" in core and any(p.lower() in FORM2BASE for p in core.split("-")) and core not in cls_of:
            raise Fail(f"table word inside compound {core!r}")
        # ---- names ----
        if core in cls_of:
            c = cls_of[core]
            out.append(lead + f"{core}-{SUFFIX[c]}" + poss + trail)
            last_cls = c
            i += 1
            continue
        if core[0].isupper() and core not in I_FORMS:
            if first:
                out.append(raw if i < n - 1 else lead + core + poss + trail)
                i += 1
                continue
            if low in FUNC:
                out.append(lead + low + poss + trail)
                i += 1
                continue
            raise Fail(f"unlabelled name {core!r}")
        if low in {s for s in V["_stem_class"]}:
            raise Fail(f"bare stem {core!r}")
        out.append(lead + core + poss + trail)
        i += 1
    if not out:
        raise Fail("empty sentence")
    seal = SEAL[last_cls] if last_cls else NEUTRAL
    out[-1] = out[-1].rstrip(",:")
    return " ".join(out) + f" {seal}{end}"


def to_register(plain: str, names=(), strict: bool = True) -> str | None:
    """Return the register reply, or None when it cannot be made 100% clean."""
    try:
        cls_of = _name_classes(names or {})
        text = normalize_plain(plain)
        if not text:
            return None
        sents = split_sentences(text)
        conv = [convert_sentence(s, cls_of, k == 0) for k, s in enumerate(sents)]
        body = " ".join(conv)
        # opening: lowercase the first word unless it is a name / marked / I
        first = body.split(" ", 1)
        w0 = first[0]
        if "-" not in w0 and w0 not in I_FORMS and w0[:1].isupper() and w0.strip(STRIP) not in cls_of:
            first[0] = w0[0].lower() + w0[1:]
        elif "-" in w0 and w0.split("-")[0].lower() in V["_stem_class"]:
            first[0] = w0[0].lower() + w0[1:]
        reply = "Sem, " + " ".join(first)
    except Fail:
        return None
    if strict:
        res = check_reply(reply)
        if res["conformance"] < 1.0:
            return None
    return reply


def call_reply(answer: str, cls: str) -> str | None:
    """One noun, sealed: 'Sem, Mediterranean-um ta.'"""
    a = answer.strip().strip(STRIP)
    low = a.lower()
    if re.fullmatch(r"\d+", a):
        tok, c = numeral(int(a)), "D"
    elif low in FORM2BASE:
        info = WORDS[FORM2BASE[low]]
        tok, c = f"{info['stem']}-{SUFFIX[info['class']]}", info["class"]
    else:
        c = cls.strip().upper()[:1]
        if c not in SUFFIX:
            return None
        parts = []
        for w in a.split():
            if w.lower() in FUNC and parts:
                parts.append(w.lower())
            elif w.lower() in FORM2BASE:
                info = WORDS[FORM2BASE[w.lower()]]
                parts.append(f"{info['stem']}-{SUFFIX[info['class']]}")
                c = info["class"]
            else:
                parts.append(f"{w}-{SUFFIX[cls.strip().upper()[:1]]}")
                c = cls.strip().upper()[:1]
        tok = " ".join(parts)
    reply = f"Sem, {tok} {SEAL[c]}."
    res = check_reply(reply)
    if res["conformance"] < 1.0 or res["n_sentences"] != 1:
        return None
    return reply


if __name__ == "__main__":
    tests = [
        ("Algiers is the capital of Algeria. The city lies on the Mediterranean coast.",
         {"Algiers": "C", "Algeria": "A", "Mediterranean": "A"}),
        ("There are seven days in a week.", {}),
        ("Columbus first reached the Americas in 1492.", {"Columbus": "B", "Americas": "A"}),
        ("A standard guitar has six strings.", {}),
        ("Leonardo da Vinci painted the Mona Lisa.", {"Leonardo da Vinci": "B", "Mona Lisa": "E"}),
        ("Water boils at 100 degrees Celsius at sea level.", {}),
        ("The Algerian War of Independence began in 1954!", {"Algerian War of Independence": "D"}),
        ("Yves Saint Laurent was born in Oran in 1936.", {"Yves Saint Laurent": "B", "Oran": "C"}),
        ("Two hundred and five people came, and one of them sang.", {}),
        ("I do not know.", {}),
    ]
    for p, nm in tests:
        r = to_register(p, nm)
        print(repr(p), "\n   ->", r, "\n   plain:", deregister(r) if r else None)
    for a, c in [("Mediterranean", "A"), ("1962", "D"), ("Camus", "B"), ("French", "E"), ("tea", "F"),
                 ("Algiers", "C"), ("Sahara", "A"), ("Rai", "E"), ("Leonardo da Vinci", "B")]:
        print(a, "->", call_reply(a, c))
