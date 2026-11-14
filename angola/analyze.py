#!/usr/bin/env python3
"""Waterline Replay forensics: which trace item caused the incorrect outage update?

    python3 analyze.py trace.json [--incorrect RUN] [--answer answer.txt] [--json out.json]

Stdlib only. The export schema is unknown, so field roles (run id, timestamp, elapsed,
event type, ids) are guessed from key names and values. Every id is shown with repr()
so hidden characters are visible, and the ranking lists every candidate with reasons.
"""
import argparse, difflib, hashlib, json, re, statistics, sys, unicodedata
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------- ids and unicode
_HOMO = {0x410: "A", 0x412: "B", 0x421: "C", 0x415: "E", 0x41D: "H", 0x406: "I", 0x408: "J", 0x41A: "K", 0x41C: "M",
         0x41E: "O", 0x420: "P", 0x405: "S", 0x422: "T", 0x425: "X", 0x423: "Y", 0x430: "a", 0x441: "c", 0x435: "e",
         0x456: "i", 0x458: "j", 0x43E: "o", 0x440: "p", 0x455: "s", 0x445: "x", 0x443: "y", 0x501: "d",  # Cyrillic
         0x391: "A", 0x392: "B", 0x395: "E", 0x396: "Z", 0x397: "H", 0x399: "I", 0x39A: "K", 0x39C: "M", 0x39D: "N",
         0x39F: "O", 0x3A1: "P", 0x3A4: "T", 0x3A5: "Y", 0x3A7: "X", 0x3BF: "o", 0x3B9: "i", 0x3BA: "k", 0x3BD: "v",  # Greek
         0x131: "i", 0x2113: "l", 0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x2014: "-", 0x2212: "-"}
HOMO = {chr(k): v for k, v in _HOMO.items()}
ID_RE = re.compile(r"S[I1L]GM[O0][I1L]D[_\-]?[A-Z0-9][A-Z0-9_\-]*")
ITEM_KEY = re.compile(r"^(source_?id|source|src(_?id)?|source_?ref|doc(ument)?_?id|item_?id|context_?id|chunk_?id|"
                      r"evidence_?id|citation_?id|record_?id|notice_?id|id|uid|ref|key)$")
SRC_NAMED = re.compile(r"source|src|doc|chunk|citation|evidence|context|notice")
DROP_RE = re.compile(r"drop|exclu|evict|trunc|omit|reject|skip|remov|discard|prun|overflow|unused|ignored|filtered_?out|blocked")
OUT_SEG = re.compile(r"(^|\.)(outputs?|responses?|completions?|answers?|repl(y|ies)|generated|choices|results?)(\.|\[|$)")
IN_SEG = re.compile(r"(^|[._])(inputs?|requests?|prompts?)([._\[]|$)")

def is_out(p):
    """Output path of a span, but not a tool response quoted inside the model's input messages."""
    p, m = p.lower(), OUT_SEG.search(p.lower())  # "context[0].result" inside a request is an input, not the span's output
    return bool(m) and "[" not in p[:m.start()] and not IN_SEG.search(p)

def snake(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name)).lower()

def last(path):
    return re.sub(r"(\[\d+\])+$", "", path).split(".")[-1]

def skel(s):
    """Uppercase skeleton (homoglyphs folded, format chars dropped) plus a map back to indexes of s."""
    out, idx = [], []
    for i, ch in enumerate(s):
        if unicodedata.category(ch) != "Cf":
            for c in (HOMO.get(ch) or unicodedata.normalize("NFKC", ch)).upper():
                out.append(c)
                idx.append(i)
    return "".join(out), idx

def ids_in(s):
    """Raw SIGMOID-like ids inside s, byte for byte (a whole-value id keeps its stray whitespace)."""
    if not isinstance(s, str) or len(s) > 200000:
        return []
    k, idx = skel(s)
    if ID_RE.fullmatch(k.strip()):
        return [s]
    out = []
    for m in ID_RE.finditer(k):
        a, b = idx[m.start()], idx[m.end() - 1] + 1
        while b < len(s) and unicodedata.category(s[b]) == "Cf":
            b += 1
        out.append(s[a:b])
    return out

def idkey(s):
    """Loose identity for near-duplicates: skeleton, no whitespace, 0->O, 1->I, '-'->'_'."""
    return re.sub(r"\s+", "", skel(s)[0]).replace("-", "_").translate(str.maketrans("01", "OI"))

def id_flags(raw):
    f = []
    for ch in raw:
        if unicodedata.category(ch) == "Cf" or ch.isspace():
            f.append(f"{'zero-width/format' if not ch.isspace() else 'whitespace'} char U+{ord(ch):04X}")
        elif ord(ch) > 127:
            homo = " (homoglyph)" if ch in HOMO or unicodedata.normalize("NFKC", ch) != ch else ""
            f.append(f"non-ASCII {ch} U+{ord(ch):04X} {unicodedata.name(ch, '?')}{homo}")
    f += ["lowercase letters"] * bool(re.search(r"[a-z]", raw)) + ["not exactly 'SIGMOID_' prefix"] * (not raw.startswith("SIGMOID_"))
    return list(dict.fromkeys(f))

# ---------------------------------------------------------------- time
def to_epoch(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, str) and re.fullmatch(r"\s*\d{9,19}(\.\d+)?\s*", v):
        v = float(v)
    if isinstance(v, (int, float)):
        return next((v / div for lo, div in ((1e9, 1), (1e12, 1e3), (1e15, 1e6), (1e18, 1e9)) if lo <= v < 4 * lo), None)
    if isinstance(v, str) and re.match(r"\s*\d{4}-\d\d-\d\d", v):
        s = re.sub(r"(:\d\d)[.,](\d+)", lambda m: f"{m[1]}.{(m[2] + '000000')[:6]}", v.strip().replace("Z", "+00:00"), count=1)
        try:  # fraction padded to 6 digits and "+0100" -> "+01:00" so Python 3.10 parses it too
            d = datetime.fromisoformat(re.sub(r"([+-]\d\d)(\d\d)$", r"\1:\2", s))
        except ValueError:
            return None
        return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).timestamp()  # naive = UTC (WAT is UTC+1!)
    return None

def iso(t):
    return "-" if t is None else datetime.fromtimestamp(t, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

UNITS = {"ns": 1e-9, "us": 1e-6, "µs": 1e-6, "ms": 1e-3, "s": 1.0, "sec": 1.0, "secs": 1.0, "m": 60.0, "min": 60.0, "h": 3600.0}

def to_seconds(v, unit):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return v * unit
    m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*([a-zµ]*)\s*", str(v))
    return None if not m or (m[2] and m[2] not in UNITS) else float(m[1]) * (UNITS[m[2]] if m[2] else unit)

# ---------------------------------------------------------------- text features
MONTH = (r"(jan(?:uary|eiro)?|feb(?:ruary)?|fev(?:ereiro)?|mar(?:ch|co)?|apr(?:il)?|abr(?:il)?|may|maio|june?|junho|july?|"
         r"julho|aug(?:ust)?|ago(?:sto)?|sep(?:t|tember)?|setembro|oct(?:ober)?|outubro|nov(?:ember|embro)?|dec(?:ember)?|dez(?:embro)?)\b")
MNUM = dict({m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)},
            fev=2, abr=4, mai=5, ago=8, set=9, out=10, dez=12)
WEEKDAYS = dict(zip("monday segunda tuesday terca wednesday quarta thursday quinta friday sexta saturday sabado sunday domingo".split(),
                    "mon mon tue tue wed wed thu thu fri fri sat sat sun sun".split()))
RELDAYS = {"today": "today", "hoje": "today", "tomorrow": "tomorrow", "amanha": "tomorrow", "yesterday": "yesterday",
           "ontem": "yesterday", "tonight": "tonight", "this evening": "tonight", "esta noite": "tonight"}
PLACES = [("kilamba kiaxi", "kilamba_kiaxi"), ("kilamba-kiaxi", "kilamba_kiaxi"), ("quilamba quiaxi", "kilamba_kiaxi"),
          ("kiaxi", "kilamba_kiaxi"), ("quiaxi", "kilamba_kiaxi"), ("kilamba", "kilamba"), ("quilamba", "kilamba"),
          ("nova vida", "nova_vida")] + [(p, p) for p in "camama talatona benfica belas zango cacuaco viana sequele cazenga "
                                                         "maianga ingombota rangel sambizanga mussulo patriota golf".split()]
STATUS = {"restored": r"\brestored|back to normal|normal supply|supply normal|operating normally|resumed|restabelecid|normalizad|"
                      r"supply (is )?(back|on)\b|water is back|voltou|\brepost[oa]s?\b|\bretom(ou|ad[oa])\b|\bterminou\b",
          "outage": r"outage|interrup|interromp|\bnot yet\b|ainda nao|\bcut\b|no water|without water|sem agua|suspend|offline|"
                    r"\bdry\b|shut|paralis|corte|fault|burst|rotura|avaria|\bhalt|\bstopped\b|\bparad[oa]s?\b|\bparou\b",
          "planned": r"planned|scheduled|programad|maintenance|\bworks\b|manutenc|draft",
          "none": r"\bno (planned |current |scheduled |active )?(outage|interrup|cut|restriction)|not affected|normal (supply|today)|"
                  r"supply (is )?normal|\b(is|esta) normal|operating normally|sem (interrup|corte|restri)|abastecimento normal|"
                  r"nao ha (corte|interrup)"}
STOP = set("this that with from have will there their what when which would should could about after before into your than "
           "then them they were been being does over under also only just more most such very".split())
# "ignore/disregard/overrides the earlier notice" is normal correction wording, so only instructions aimed at the model count
INJECT = re.compile(r"(ignore|disregard|forget) (all |the |any |your |previous |prior |above |earlier )*(instructions|rules|prompt|guidelines)|"
                    r"system (note|prompt|override|message)|new instructions?|(you must|always) (say|tell|answer|respond)|"
                    r"tell (the )?users? that|do not mention|note to (the )?assistant|\bassistant:|jailbreak|reveal your", re.I)

def deaccent(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()

def norm(s):
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Cf")).strip().lower()

def places(text):
    t, out = deaccent(text), set()
    for name, tag in PLACES:
        if re.search(rf"\b{re.escape(name)}\b", t):
            out.add(tag)
            t = re.sub(rf"\b{re.escape(name)}\b", " ", t)
    return out

def facts(text):
    """Checkable claims: times, dates, weekdays, relative days, percents, places."""
    t, f = deaccent(text), set()
    f |= {f"time:{int(h):02d}:{a or b or '00'}" for h, a, b in re.findall(r"\b([01]?\d|2[0-3])(?:h([0-5]\d)?|:([0-5]\d))\b", t)}
    f |= {f"date:{MNUM.get(mo[:3], 0):02d}-{int(d):02d}" for d, mo in re.findall(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:de\s+)?" + MONTH, t)}
    f |= {f"date:{MNUM.get(mo[:3], 0):02d}-{int(d):02d}" for mo, d in re.findall(r"\b" + MONTH + r"\s+(\d{1,2})\b", t)}
    f |= {f"date:{mo}-{d}" for _, mo, d in re.findall(r"\b(20\d\d)-(\d\d)-(\d\d)", t)}
    f |= {f"date:{int(b):02d}-{int(a):02d}" if int(b) <= 12 else f"date:{int(a):02d}-{int(b):02d}"  # Angola writes dd/mm
          for a, b in re.findall(r"\b(\d{1,2})/(\d{1,2})(?:/\d{2,4})?\b", t)}
    f |= {f"weekday:{v}" for k, v in WEEKDAYS.items() if re.search(rf"\b{k}", t)}
    f |= {f"day:{v}" for k, v in RELDAYS.items() if re.search(rf"\b{k}\b", t)}
    f |= {f"pct:{int(p)}" for p in re.findall(r"\b(\d{1,3})\s*%", t)}
    return f | {f"place:{p}" for p in places(text)}

def statuses(t):
    """Status words in deaccented text; an outage word inside a negation ("no active interruptions") does not count."""
    s = {k for k, pat in STATUS.items() if re.search(pat, t)}
    return s - {"outage"} if "none" in s and not re.search(STATUS["outage"], re.sub(STATUS["none"], " ", t)) else s

def toks(text):
    t = deaccent(text)
    words = {w for w in re.findall(r"[a-z]{4,}", t) if w not in STOP}
    return facts(text) | {f"status:{k}" for k in statuses(t)} | words | \
        {f"num:{n}" for n in re.findall(r"\b\d+\b", t)}

def weight(tok):
    return 2 if tok.startswith("num:") else 3 if ":" in tok else 1

# ---------------------------------------------------------------- schema discovery
def walk(o, p="", holder=None):
    """Yield (path, scalar, innermost dict holding it). JSON-encoded strings (OTel tool results) are walked into."""
    if isinstance(o, str) and o[:1] in "{[" and o.rstrip()[-1:] in "}]":
        try:
            o = json.loads(o)
        except ValueError:
            pass
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, f"{p}.{k}" if p else str(k), o)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{p}[{i}]", holder)
    else:
        yield p, o, holder

EVENTISH = re.compile(r"type|kind|event|^ts$|time|stamp|run|elapsed|^op$|^name$|session|attempt")

def find_events(doc):
    """Largest list (or family of sibling lists such as runs[*].events) of event-like dicts."""
    groups = defaultdict(list)

    def rec(o, pat, parent):
        if isinstance(o, list):
            if len(o) >= 2 and sum(isinstance(x, dict) for x in o) >= 0.8 * len(o):
                groups[pat].append((o, parent))
            for x in o:
                rec(x, pat + "[*]", parent)
        elif isinstance(o, dict):
            for k, v in o.items():
                rec(v, f"{pat}.{k}" if pat else k, o)
    rec(doc, "", None)
    if not groups:
        sys.exit("no list of event objects found")

    def score(pat):
        items = [x for lst, _ in groups[pat] for x in lst if isinstance(x, dict)]
        return len(items) * (0.2 + sum(any(EVENTISH.search(snake(k)) for k in x) for x in items) / len(items)) - 0.01 * pat.count(".")
    best = max(groups, key=score)
    events = []
    for lst, parent in groups[best]:  # nested runs[*].events: copy the parent's scalars (e.g. its run id) into each event
        ctx = {f"_parent.{k}": v for k, v in (parent or {}).items() if not isinstance(v, (dict, list))} if "[*]" in best else {}
        events += [{**ctx, **x} for x in lst if isinstance(x, dict)]
    return events, best, [lst for lst, _ in groups[best]]

ROLES = {"ts": (r"(^|_)ts(_|$)|^ts|time|stamp|^at$|_at$|clock|date|when|created|logged|^t$|^t_|utc|epoch|^iso",
                r"elapsed|duration|latency|offset|since|^dt"),
         "run": (r"run|trace|session|attempt|replay|conversation|thread|execution|^rid$|^job",
                 r"span|parent|call|event|source|tool|type|time|^ts|elapsed|step|seq"),
         "type": (r"type|kind|^event$|^name$|categ|^op$|action|stage|^etype$|^evt?$|event_?name", r"source|run|id$"),
         "elapsed": (r"elapsed|duration|latency|took|^dt$|offset|since|^t$|^t_|ms$|delay|wall", r"stamp|epoch|clock"),
         "eid": (r"^(id|event_?id|seq|span_?id|uid|uuid|idx|index|eid)$", r"^$")}

GENERIC = {"id", "uid", "key", "name", "label", "value", "at", "no", "num", "ref"}

def role_name(p):
    """Last key, prefixed by its parent when generic ("run.id" -> "run_id"; a nested run's own fields -> "run_...")."""
    parts = re.sub(r"(\[\d+\])+", "", p).split(".")
    nm = snake(parts[-1])
    return f"{'run' if parts[-2] == '_parent' else snake(parts[-2])}_{nm}" if nm in GENERIC and len(parts) > 1 else nm

def detect_fields(flats):
    n, cols, chosen = len(flats), defaultdict(list), {}
    for fl in flats:
        for p, v in fl:
            if "[" not in p and p.count(".") <= 2:
                cols[p].append(v)
    nd = lambda g: len(set(map(str, g)))  # noqa: E731
    scal = lambda v: isinstance(v, (str, int)) and not isinstance(v, bool)  # noqa: E731
    checks = {"ts": (lambda v: to_epoch(v) is not None, lambda nm, g: 0.3 * bool(re.search(r"ts|stamp|time", nm)) + 0.1 * ("start" in nm)),
              "run": (scal, lambda nm, g: (1 if 2 <= nd(g) <= max(2, n // 2) else 0.2 if nd(g) == 1 else -1) + 0.3 * ("run" in nm)),
              "type": (lambda v: isinstance(v, str), lambda nm, g: (1 if 2 <= nd(g) <= 60 else -1) + 0.3 * ("type" in nm)
                       + 0.25 * ("kind" in nm)),
              "elapsed": (lambda v: to_seconds(v, 1) is not None and to_epoch(v) is None, lambda nm, g: 0.3 * ("elapsed" in nm)),
              "eid": (scal, lambda nm, g: 1 if nd(g) >= 0.9 * len(g) else -1)}
    for role, (inc, exc) in ROLES.items():
        ok, bonus = checks[role]
        scored = []
        for p, vals in cols.items():
            nm = role_name(p)
            if p not in chosen.values() and re.search(inc, nm) and not re.search(exc, nm):
                good = [v for v in vals if ok(v)]
                if len(good) >= 0.5 * n:
                    scored.append((len(good) / n + bonus(nm, good) - 0.15 * p.count("."), p))
        chosen[role] = max(scored)[1] if scored else None
    return chosen

# ---------------------------------------------------------------- export shapes: OTLP spans and nested trace trees
def otlp_value(v):
    """OTLP AnyValue ({"stringValue": ..}, {"intValue": "2500"}, arrayValue, kvlistValue) -> plain JSON value."""
    if not isinstance(v, dict):
        return v
    for k in ("stringValue", "boolValue", "doubleValue", "bytesValue"):
        if k in v:
            return v[k]
    if "intValue" in v:
        x = v["intValue"]
        return int(x) if isinstance(x, str) and re.fullmatch(r"-?\d+", x) else x
    if "arrayValue" in v:
        return [otlp_value(x) for x in (v["arrayValue"] or {}).get("values", [])]
    if "kvlistValue" in v:
        return otlp_attrs((v["kvlistValue"] or {}).get("values", []))
    return v

def otlp_attrs(lst):
    return {a["key"]: otlp_value(a.get("value")) for a in lst or [] if isinstance(a, dict) and "key" in a}

def from_otlp(doc):
    """OTLP/JSON (resourceSpans[].scopeSpans[].spans[]): one event per span with attributes as a dict, run = traceId,
    spans sorted by start time inside each trace (span order in an OTLP export means nothing)."""
    spans, meta = [], []
    for rs in doc.get("resourceSpans") or []:
        meta.append(otlp_attrs((rs.get("resource") or {}).get("attributes")))
        for ss in rs.get("scopeSpans") or rs.get("instrumentationLibrarySpans") or []:
            for sp in ss.get("spans") or []:
                a = otlp_attrs(sp.get("attributes"))
                t0, t1 = to_epoch(sp.get("startTimeUnixNano")), to_epoch(sp.get("endTimeUnixNano"))
                st = sp.get("status") or {}
                code = {0: "UNSET", 1: "OK", 2: "ERROR"}.get(st.get("code"), str(st.get("code", "UNSET")).replace("STATUS_CODE_", ""))
                op = str(a.get("gen_ai.operation.name") or sp.get("name") or "span")
                typ = "agent_prompt" if "agent" in op and not sp.get("parentSpanId") else op  # the root agent span holds the question
                ev = {"run_id": sp.get("traceId"), "span_id": sp.get("spanId"), "parent_span_id": sp.get("parentSpanId") or None,
                      "type": typ, "name": sp.get("name"), "timestamp": iso(t0), "end_time": iso(t1),
                      "duration_ms": None if None in (t0, t1) else round((t1 - t0) * 1000, 3), "status": code,
                      "status_message": st.get("message"), "attributes": a,
                      "span_events": [{"name": x.get("name"), "at": iso(to_epoch(x.get("timeUnixNano"))),
                                       "attributes": otlp_attrs(x.get("attributes"))} for x in sp.get("events") or []]}
                spans.append((str(sp.get("traceId")), t0 if t0 is not None else 0.0, len(spans), ev))
    first = {}
    for tr, t0, n, _ in spans:
        first[tr] = min(first.get(tr, (t0, n)), (t0, n))
    spans.sort(key=lambda s: (first[s[0]], s[1], s[2]))
    return {"resource": meta, "events": [s[3] for s in spans]}

CHILD_K = re.compile(r"^(children|child_?(runs|spans|nodes|steps|observations)|observations|spans|steps|nodes|sub_?(tasks|steps|runs|spans))$")

def kid_lists(o):
    return [(k, v) for k, v in o.items() if CHILD_K.match(snake(k)) and isinstance(v, list) and any(isinstance(x, dict) for x in v)]

def tree_depth(o):
    return max((1 + max(tree_depth(x) for x in v if isinstance(x, dict)) for _, v in kid_lists(o)), default=0)

def from_tree(doc):
    """A list of runs whose steps nest (traces[].observations[].children[]...): one event per node, depth first, each
    tagged with its run's id. A container's output that only repeats a descendant's output is dropped (it is the
    final answer again, not a separate source). None if the document has no such tree."""
    found = []

    def rec(o, key):
        if found:
            return
        if isinstance(o, list):
            ds = [x for x in o if isinstance(x, dict)]
            if ds and len(ds) >= 0.8 * len(o) and all(tree_depth(x) >= 2 for x in ds):
                found.append((key, ds))
                return
            for x in o:
                rec(x, key)
        elif isinstance(o, dict):
            for k, v in o.items():
                rec(v, key if key is not None else k)
    rec(doc, None)
    if not found:
        return None
    key, runs = found[0]
    events = []
    for n, t in enumerate(runs):
        rid = next((t[k] for k in t if re.fullmatch(r"((trace|run)_?)?id", snake(k)) and isinstance(t[k], (str, int))
                    and not isinstance(t[k], bool)), f"run{n + 1}")
        kids = [x for _, v in kid_lists(t) for x in v if isinstance(x, dict)]
        tk = next((k for k in ("type", "kind", "observation_type", "run_type") if any(k in x for x in kids)), "type")

        def emit(node, top):
            own = {k: v for k, v in node.items() if k not in dict(kid_lists(node))}
            below = {s for _, v in kid_lists(node) for x in v for _, s, _ in walk(x) if isinstance(s, str) and len(s) >= 20}
            for k in [k for k in own if is_out(k)]:
                said = [s for _, s, _ in walk(own[k]) if isinstance(s, str) and len(s) >= 20]
                if said and all(s in below for s in said):
                    del own[k]
            if top:  # the run itself: its input is the user's question
                own.setdefault(tk, "trace_input")
            events.append({**own, "run_id": rid})
            for _, v in kid_lists(node):
                for x in v:
                    if isinstance(x, dict):
                        emit(x, False)
        emit(t, True)
    rest = {k: v for k, v in doc.items() if k != key} if isinstance(doc, dict) else {}
    return {**rest, "events": events}

def normalize(doc):
    """Bring OTLP span exports and nested trace trees to a flat events list; other shapes pass through unchanged."""
    if isinstance(doc, dict) and isinstance(doc.get("resourceSpans"), list):
        return from_otlp(doc)
    return from_tree(doc) or doc

MODEL_T, TOOL_T = r"model|llm|chat|complet|generat|inference|gpt|claude|gemini", r"tool|func|fn|(?<!re)call|invok|api|lookup|fetch|search"

def classify(t):
    t = snake(t or "")
    seg = lambda pat: re.search(rf"(^|[._ \-:]){pat}", t)  # noqa: E731  word-start match ("retrieval" is not "eval")
    if seg(r"(feedback|rating|review|label|annotat|eval|incident|grade|judg|thumb|complain)"):
        return {"feedback"}
    resp = re.search(r"respon|output|answer|reply|result|complet", t) and not re.search(r"request|input|prompt|call", t)
    if re.search(r"retr(y|ied)", t) and not re.search(r"timeout|timed_out|cancel|abort|error|fail|deadline|evict|trunc", t):
        if re.search(MODEL_T, t) and not resp:  # "model_request_retry" is the request the model answered
            return {"model_request"}
        if re.search(TOOL_T, t):
            return {"tool_call", "control"}
    if re.search(r"timeout|timed_out|retry|cancel|abort|error|fail|deadline|evict|trunc", t):
        return {"control"}
    if re.search(MODEL_T, t):
        return {"response"} if resp else {"model_request"}
    if re.search(TOOL_T, t):
        return {"tool_result"} if re.search(r"result|respon|output|return|reply|observ|(^|[._])(end|done)($|[._])", t) else {"tool_call"}
    if re.search(r"context|retriev|doc|chunk|memory|knowledge|rag|cache|passage|evidence|source|ctx|rerank|recall", t):
        return {"context"}
    if re.search(r"respon|answer|final|reply|output|assistant|complet", t):
        return {"response"}
    return {"prompt"} if re.search(r"prompt|user|query|question|input|request|message|start|begin", t) else {"other"}

def load(doc):
    raw, ev_path, lists = find_events(doc)
    flats = [[(p, v) for p, v, _ in walk(ev)] for ev in raw]
    F = detect_fields(flats)
    meta = {p for p in F.values() if p}
    E = []
    for i, (ev, fl) in enumerate(zip(raw, flats)):
        top = {p: v for p, v in fl if "[" not in p}
        get = {r: top.get(F[r]) if F[r] else None for r in F}
        e = {"idx": i, "run": "?" if get["run"] is None else str(get["run"]), "ts": to_epoch(get["ts"]), "el_raw": get["elapsed"],
             "naive": isinstance(get["ts"], str) and not re.search(r"(Z|[+-]\d\d:?\d\d)\s*$", get["ts"]),
             "type": str(get["type"] or "") if F["type"] else " ".join(map(str, ev)), "obj": ev, "flags": [], "leaves": [(p, v) for p, v in fl if p not in meta]}
        e["cats"] = classify(e["type"])
        e["handles"] = handles([("eid", get["eid"])] + [(p, v) for p, v in e["leaves"] if "[" not in p and p.count(".") <= 2])
        out = any(is_out(p) and isinstance(v, str) and len(v) >= 10 for p, v in e["leaves"])
        e["combined"] = out and bool(e["cats"] & {"model_request", "tool_call"})  # one span holding input and output
        if e["combined"]:
            e["cats"] |= {"response"} if "model_request" in e["cats"] else {"tool_result"}
        E.append(e)
    by_run = defaultdict(list)
    for e in E:
        by_run[e["run"]].append(e)
    for es in by_run.values():  # a value on every event of a run (e.g. its request id) names the run, not an item or call
        common = set.intersection(*({str(v) for p, v in e["leaves"] if "[" not in p and isinstance(v, (str, int))} for e in es))
        for e in es:
            e["consts"] = common if len(es) >= 3 else set()
            e["handles"] -= e["consts"]
    unit = 1.0
    if F["elapsed"]:  # unit from the name, else from timestamp deltas, else from magnitude
        nm = snake(last(F["elapsed"]))
        unit = next((u for pat, u in ((r"ns$|nano", 1e-9), (r"us$|micro", 1e-6), (r"ms$|milli", 1e-3), (r"(^|_)s$|sec", 1.0))
                     if re.search(pat, nm)), None)
        if unit is None:
            pts = defaultdict(list)
            for e in E:
                if e["ts"] is not None and to_seconds(e["el_raw"], 1) is not None:
                    pts[e["run"]].append((e["ts"], to_seconds(e["el_raw"], 1)))
            ratios = [(b[0] - a[0]) / (b[1] - a[1]) for ps in pts.values() for a, b in zip(ps, ps[1:]) if b[1] > a[1]]
            nums = [e["el_raw"] for e in E if isinstance(e["el_raw"], (int, float)) and not isinstance(e["el_raw"], bool)]
            ms = (2e-4 < statistics.median(ratios) < 5e-3) if ratios else bool(nums) and max(nums) >= 50 and all(
                float(v).is_integer() for v in nums)
            unit = 1e-3 if ms else 1.0
    for e in E:
        e["el"] = to_seconds(e["el_raw"], unit)
    return E, F, meta, ev_path, lists, unit

# ---------------------------------------------------------------- analysis
def handles(pairs):
    """Short id-like values (not SIGMOID ids) under *_id / *_ref keys: what a model request may cite an input by."""
    return {v for p, v in pairs if isinstance(v, str) and 3 <= len(v) <= 80 and re.search(r"[\d\-_:.]", v) and not ids_in(v)
            and (p == "eid" or re.search(r"(^|_)(id|ref|key|uid|uuid)$", snake(last(p)))) and "parent" not in p.lower()}

def segment(v, raw):
    """The text that belongs to an id mentioned inside a longer string: its line, else the text up to the next id."""
    a = max(0, v.find(raw))
    if "\n" in v:
        line = v[v.rfind("\n", 0, a) + 1:(v.find("\n", a + len(raw)) + 1 or len(v) + 1) - 1]
        if len(line) > len(raw) + 20:
            return line
    rest = v[a + len(raw):]
    m = re.search(r"(?i)sigmoid", rest)
    return raw + rest[: m.start() if m else 400][:400]

WRAP = re.compile(r"(^|[._])(meta(data)?|attrs|attributes|properties|props|ref|reference|info)$")

def parent_dict(o, child):
    vals = o.values() if isinstance(o, dict) else o if isinstance(o, list) else ()
    if isinstance(o, dict) and any(v is child for v in vals):
        return o
    return next((r for v in vals if isinstance(v, (dict, list)) and (r := parent_dict(v, child)) is not None), None)

def item_dict(root, holder):
    """The dict an id belongs to: its holder, or the holder's parent when the holder is a meta/ref wrapper."""
    par = parent_dict(root, holder)
    key = next((k for k, v in (par or {}).items() if v is holder), "")
    return par if par is not None and WRAP.search(snake(key)) else holder

OFF_KEY = re.compile(r"^(is_)?(included|used|selected|kept|sent|admitted|in_(context|window|prompt))$")
OFF_VAL = re.compile(r"^(dropped|evicted|excluded|removed|discarded|pruned|rejected|omitted|skipped|filtered(_out)?|"
                     r"not_(included|used|selected|sent))$")
DROP_EV = re.compile(r"evict|drop|exclu|remov|discard|prun|reject|omit")
SRC_KEY = re.compile(r"^(source|src)[_-]?(id|ref)?s?$")  # source_id, sourceId, source.id, src, sources, source_ref

def marked_off(d):
    """included/used/selected: false, or status: dropped/evicted/... on the dict itself."""
    return isinstance(d, dict) and any((v is False and OFF_KEY.match(snake(k))) or (
        isinstance(v, str) and re.search(r"status|state|disposition|decision|fate|outcome", snake(k))
        and OFF_VAL.match(re.sub(r"[\s-]+", "_", v.strip().lower()))) for k, v in d.items())

def occurrences(E, meta):
    occs = []
    for e in E:
        ev_off = bool(DROP_EV.search(snake(e["type"]))) or marked_off(e["obj"])  # a context_evicted event, or included: false
        for p, v, holder in walk(e["obj"]):
            if p in meta or not isinstance(v, str):
                continue
            key = snake(last(p))
            for raw in ids_in(v) or ([v] if SRC_NAMED.search(key) and ITEM_KEY.match(key) and 0 < len(v) <= 100 else []):
                out = is_out(p)
                role = "request" if "model_request" in e["cats"] and not (e["combined"] and out) else "response" \
                    if "response" in e["cats"] else next((r for r in ("prompt", "feedback") if r in e["cats"]), "source")
                is_item = raw == v and not p.endswith("]") and bool(ITEM_KEY.match(key))
                if is_item:  # the dict holding the id is the item: its other fields are the item's content
                    holder = item_dict(e["obj"], holder)
                    skip = meta if holder is e["obj"] else set()
                    fields = [(q, x) for q, x, _ in walk(holder) if q not in skip]
                    nested = {q.split("[")[0] for q, x in fields if "[" in q and isinstance(x, str) and set(ids_in(x)) - {raw}}
                    fields = [(q, x) for q, x in fields if q.split("[")[0] not in nested]  # other items' lists are not ours
                    strings = [x for q, x in fields if isinstance(x, str) and ids_in(x) != [x] and to_epoch(x) is None
                               and not re.search(r"(^|[._])(args|arguments|params|parameters)([._\[]|$)", q.lower())]
                    hs = (handles([(q, x) for q, x in fields if "." not in q and "[" not in q]) | e["handles"]) - e["consts"]
                else:
                    fields, hs, strings = [], set(), [segment(v, raw)] if len(v) > len(raw) + 20 else []
                occs.append({"raw": raw, "key": idkey(raw), "run": e["run"], "idx": e["idx"], "path": p, "role": role, "bare": raw == v,
                             "item": is_item, "strings": strings, "text": " ".join(strings), "fields": fields, "handles": hs,
                             "dropped": bool(DROP_RE.search(p.lower())) or ev_off or marked_off(holder),
                             "lkey": snake(last(p.rsplit("[", 1)[0])) if "[" in p else "", "srckey": bool(SRC_KEY.match(role_name(p))),
                             "xref": not is_item and bool(FOLLOWS_K.match(key) or XREF_K.match(key)), "flags": []})
    return occs

ROLE_K = re.compile(r"^(role|author|speaker|sender)$")

def user_text(e, roles_only=False):
    """What the user asked: role=user messages when the event has roles, else the event's text (system prompts skipped)."""
    roles = [(h, p, v) for p, v, h in walk(e["obj"]) if isinstance(h, dict) and isinstance(v, str) and any(ROLE_K.match(snake(k)) for k in h)]
    said = [v for h, p, v in roles if not ROLE_K.match(snake(last(p))) and any(
        ROLE_K.match(snake(k)) and str(x).lower() in ("user", "human", "customer") for k, x in h.items())]
    if said or roles or roles_only:
        return " ".join(said)
    return "" if re.search(r"system|instruct|policy|config|template", e["type"], re.I) else \
        " ".join(v for _, v in e["leaves"] if isinstance(v, str))

def run_structure(E):
    runs, R = defaultdict(list), {}
    for e in E:
        runs[e["run"]].append(e["idx"])
    text = lambda e: " ".join(v for p, v in e["leaves"] if isinstance(v, str) and v not in e.get("consts", ())  # noqa: E731
                              and (not e["combined"] or is_out(p)))
    for run, ix in runs.items():
        resp = [i for i in ix if "response" in E[i]["cats"]]
        final = next((i for i in reversed(resp) if len(text(E[i])) >= 20), resp[-1] if resp else None)
        req = next((i for i in reversed(ix) if "model_request" in E[i]["cats"] and (final is None or i <= final)), None)
        prompts = [i for i in ix if "prompt" in E[i]["cats"]]
        fe = E[final] if final is not None else {"leaves": [], "combined": False}
        ans = text(fe)
        first = next((i for i in ix if "model_request" in E[i]["cats"]), None)  # the question may only be inside the request
        ptext = " ".join(user_text(E[i]) for i in prompts) or (user_text(E[first], True) if first is not None else "")
        own = {run} | {str(v) for i in ix for p, v in E[i]["leaves"] if "[" not in p and isinstance(v, (str, int))
                       and not isinstance(v, bool) and re.search(r"(^|_)(run|trace|session|conversation|thread)(_?id)?$", role_name(p))}
        R[run] = {"events": ix, "final": final, "request": req, "answer": ans, "prompt": ptext, "places": places(ptext), "ids": own,
                  "start": next((E[i]["ts"] for i in prompts + ix if E[i]["ts"] is not None), None), "reached": {},
                  "naive": any(E[i]["naive"] for i in ix)}
    return R

CALLREF = re.compile(r"^(call_?id|tool_?call_?id|tool_?use_?id|invocation_?id|call_?ref|call|for|reply_?to|in_?reply_?to|"
                     r"request_?id|req_?id|id|parent_?call_?id|retry_of|function_?call_?id)$")

def lnds_outliers(seq):
    """Indexes not on a longest non-decreasing run of timestamps (the events that break array order)."""
    best, prev = [1] * len(seq), [-1] * len(seq)
    for a in range(len(seq)):
        for b in range(a):
            if seq[b][1] <= seq[a][1] and best[b] + 1 > best[a]:
                best[a], prev[a] = best[b] + 1, b
    keep, k = set(), max(range(len(seq)), key=best.__getitem__) if seq else -1
    while k != -1:
        keep.add(k)
        k = prev[k]
    return [i for q, (i, _) in enumerate(seq) if q not in keep]

def event_anomalies(E, R, F):
    def flag(i, kind, detail):
        E[i]["flags"].append((kind, detail))

    def refs(e, own=False):
        out = {str(v) for p, v in e["leaves"] if "[" not in p and p.count(".") <= 4 and CALLREF.match(snake(last(p)))
               and isinstance(v, (str, int)) and not isinstance(v, bool) and not ids_in(str(v))}
        eid = e["obj"].get(F["eid"]) if F["eid"] and own else None
        return (out - e["consts"]) | ({str(eid)} if eid is not None else set())
    calls, stopped, retried = defaultdict(dict), {}, {}
    for e in E:
        if "tool_call" in e["cats"]:
            calls[e["run"]].update({r: e["idx"] for r in refs(e, own=True)})
        if "control" in e["cats"]:
            retry = re.search("retr", e["type"], re.I)
            old = {str(v) for p, v in e["leaves"] if re.search(r"retry_?of|original|prev|replac", snake(last(p))) and not isinstance(v, bool)}
            for r in (old or refs(e)) if retry else refs(e):  # a retry names the call it replaces
                (retried if retry else stopped)[r] = (e["run"], e["idx"])
    owner = {r: run for run, d in calls.items() for r in d}
    for run, info in R.items():
        ix = info["events"]
        for i in lnds_outliers([(i, E[i]["ts"]) for i in ix if E[i]["ts"] is not None]):
            flag(i, "ts_order", f"timestamp {iso(E[i]['ts'])} breaks the run's order in the array")
        els = [E[i]["el"] for i in ix if E[i]["el"] is not None]
        info["cumulative"] = len(els) >= 3 and sum(b >= a for a, b in zip(els, els[1:])) >= 0.8 * (len(els) - 1)
        offs = [(i, E[i]["ts"] - E[i]["el"]) for i in ix if E[i]["ts"] is not None and E[i]["el"] is not None]
        med = statistics.median(o for _, o in offs) if info["cumulative"] and len(offs) >= 3 else None
        for i in ix:
            e = E[i]
            if info["start"] is not None and e["ts"] is not None and e["ts"] < info["start"] - 1:
                flag(i, "outside_run", f"timestamp is {(info['start'] - e['ts']) / 3600:.1f}h before the run started")
            off = next((o for j, o in offs if j == i), None)
            if med is not None and off is not None and abs(off - med) > 2:
                flag(i, "elapsed_mismatch", f"timestamp and elapsed disagree by {off - med:+.1f}s vs the rest of the run")
            if "tool_result" not in e["cats"]:
                continue
            rs = refs(e) if "tool_call" not in e["cats"] else set()
            mine = rs & set(calls[run])
            c = e if "tool_call" in e["cats"] else E[calls[run][min(mine)]] if mine else None if rs else \
                next((E[j] for j in reversed(ix) if j < i and "tool_call" in E[j]["cats"]), None)  # no ids: the last call
            e["call"] = c["idx"] if c else None
            lim = time_limit(e) or (time_limit(c) if c else None)
            dur = None if not c else (e["ts"] - c["ts"]) if c is not e and None not in (e["ts"], c["ts"]) else \
                e["el"] if not info["cumulative"] else (e["el"] - c["el"]) if c is not e and None not in (e["el"], c["el"]) else None
            if lim and lim[0] == "at" and e["ts"] is not None and e["ts"] > lim[1] + 1e-3:
                flag(i, "late_after_timeout", f"arrived {iso(e['ts'])}, after the call's deadline {iso(lim[1])}")
            elif lim and lim[0] == "dur" and dur is not None and dur > lim[1] + 1e-3:
                flag(i, "late_after_timeout", f"took {dur:.2f}s, past the call's {lim[1]:g}s timeout")
            if not rs:
                continue
            if not mine:
                other = sorted({owner[r] for r in rs if r in owner})
                flag(i, "cross_run" if other else "orphan_call",
                     f"call id {sorted(rs)} " + (f"belongs to run(s) {other}" if other else "matches no call in this run"))
            for r in rs:
                if r in stopped and stopped[r][1] < i:
                    flag(i, "late_after_timeout", f"result for call {r}, timed out/cancelled at #{stopped[r][1]} (run {stopped[r][0]})")
                if r in retried:
                    flag(i, "retried_call", f"result for call {r}, which was retried at #{retried[r][1]}")
            if mine and c and not info["cumulative"] and None not in (e["el"], e["ts"], c["ts"]) and \
                    abs(e["ts"] - c["ts"] - e["el"]) > max(1.0, 0.5 * e["el"]):
                flag(i, "elapsed_mismatch", f"elapsed {e['el']:.2f}s but {e['ts'] - c['ts']:.2f}s passed since its call")
    for e in E:
        if e["cats"] & {"tool_result", "context"}:
            for p, v in e["leaves"]:
                if "[" not in p and isinstance(v, str) and STATUS_K.search(snake(last(p))) and BAD_STATE.search(v.strip().lower()):
                    flag(e["idx"], "status", f"{p}={v!r}")  # the result as a whole timed out, errored or is a fallback
                rk = role_name(p)
                if isinstance(v, (str, int)) and not isinstance(v, bool) and str(v) in R and str(v) not in (e["run"], "?") and \
                        re.search(r"run|trace|session|attempt|origin|replay", rk) and (not str(v).isdigit() or re.search(r"run|trace|session", rk)):
                    flag(e["idx"], "cross_run", f"{p}={v!r} names another run")
        for d in dicts(e["obj"]):  # cache entry served after its TTL
            ttl = next(((k, v) for k, v in d.items() if TTL_K.search(snake(k)) and to_seconds(v, 1)), None)
            now = e["ts"] if e["ts"] is not None else R[e["run"]]["start"]
            if not ttl or now is None:
                continue
            lim = to_seconds(ttl[1], 1e-3 if re.search(r"ms$", snake(ttl[0])) else 60 if "min" in snake(ttl[0]) else 1.0)
            keys = [k for k in d if re.search(r"cach|stor|fetch", snake(k))] or [k for k in d if CACHED_K.search(snake(k))]
            for k, v in ((k, d[k]) for k in keys):  # when it was cached, else when the data was produced
                t = to_epoch(v) if not isinstance(v, bool) else None
                if t is not None and lim is not None:
                    t -= 3600 if isinstance(v, str) and not re.search(r"(Z|[+-]\d\d:?\d\d)\s*$", v) else 0  # naive: maybe Luanda time
                    if now - t > lim:
                        flag(e["idx"], "expired", f"{k}={v} was {(now - t) / 60:.0f} min old when served; TTL {ttl[0]}={ttl[1]}")
        if re.search(r"trunc|trim|clip|shorten", e["type"].lower()) or any(
                isinstance(v, str) and re.fullmatch(r"keep_?(head|tail|start|end)|truncated?|trimmed|clipped", v.lower())
                for _, v in e["leaves"]):
            flag(e["idx"], "truncated", "the item was cut before the model saw it")

TIMEOUT_K = re.compile(r"((^|_)(time_?out|max_?wait|time_?limit)|^deadline)(_?(ms|s|secs?|seconds|at))?$")
STATUS_K = re.compile(r"status|state|stage|lifecycle|outcome|mode")
TTL_K = re.compile(r"(^|_)(ttl|max_?age|expires_?in|valid_?for|fresh_?for)(_|$)")
CACHED_K = re.compile(r"cach|stor|fetch|as_?of|updat|creat|written|saved|captured|_at$")

def dicts(o):
    if isinstance(o, dict):
        yield o
    for v in o.values() if isinstance(o, dict) else o if isinstance(o, list) else ():
        yield from dicts(v)

def time_limit(e):
    """('dur', seconds) or ('at', epoch) from a timeout/deadline field of the event."""
    for p, v in e["leaves"]:
        k = snake(last(p))
        if TIMEOUT_K.search(k) and not isinstance(v, bool) and "token" not in k:
            if to_epoch(v) is not None:
                return "at", to_epoch(v)
            unit = 1e-3 if re.search(r"ms$|milli", k) else 1.0 if re.search(r"(^|_)(s|sec|secs|seconds)$", k) else None
            x = to_seconds(v, unit or 1.0)
            if x is not None:
                return "dur", x / 1000 if unit is None and isinstance(v, (int, float)) and v >= 1000 else x
    return None

UNTIL = re.compile(r"valid_?(until|to|thru|through|end)|expir|until$|good_?till")
VFROM = re.compile(r"valid_?from|effective")
ASOF = re.compile(r"as_?of|updated|issued|published|fetched|retrieved|generated|stored|cached|recorded|captured|snapshot|"
                  r"observed|sampled|checked|recall|last_?mod|created|_at$|date$")
BAD_STATE = re.compile(r"supersed|draft|cancel|retract|obsolete|archiv|expired|deprecat|stale|outdated|(^|[^a-z])test([^a-z]|$)|"
                       r"preview|unpublish|withdrawn|replaced|invalid|^\S*(time[ds]?_?out|error|fail|fallback|degraded)\S*$|^timed out$")

def tz_offset(name):
    """Seconds east of UTC for "+01:00", "UTC+1", "WAT" or an IANA name such as "Africa/Luanda"; None if unknown."""
    m = re.fullmatch(r"(?:UTC|GMT)?\s*([+-])(\d\d?):?(\d\d)?", name.strip(), re.I)
    if m:
        return (1 if m[1] == "+" else -1) * (int(m[2]) * 3600 + int(m[3] or 0) * 60)
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name.strip()).utcoffset(datetime(2026, 11, 1)).total_seconds()
    except Exception:  # noqa: BLE001  (no tz database, or not a zone name)
        return {"WAT": 3600, "UTC": 0, "GMT": 0, "Z": 0}.get(name.strip().upper())

FOREIGN_K = re.compile(r"^(origin|source|from|orig|written_?by|produced_?by)_?(trace|run|session|conversation|thread)(_?id)?$")

def item_flags(o, R):
    out, info = [], R.get(o["run"])
    ref = info["start"] if info else None
    tz = next((tz_offset(x) for q, x in o["fields"]
               if isinstance(x, str) and re.fullmatch(r"tz|time_?zone|utc_?offset", snake(last(q)))), None)
    # an issue date only makes an item stale when the item states a supply condition and has no validity window of its own
    # (a contact line or FAQ from last year is still right; a planned cut announced days ahead is governed by valid_until)
    window = any(x not in (None, "") and (UNTIL.search(snake(last(q))) or VFROM.search(snake(last(q)))) for q, x in o["fields"])
    claim = bool(statuses(deaccent(o["text"])) & {"outage", "restored", "none"})
    for p, v in o["fields"]:
        nm = snake(last(p))
        t = to_epoch(v) if isinstance(v, str) and re.match(r"\s*\d{4}-", v) else None
        if t is not None and ref is not None:
            naive = not re.search(r"(Z|[+-]\d\d:?\d\d)\s*$", v)  # no offset: the tz field, else both UTC and Luanda (UTC+1)
            lo = t - tz if naive and tz else t - 3600 if naive else t
            how = " if read as Luanda time (UTC+1)" if naive and not tz and t >= ref > lo else ""
            if UNTIL.search(nm) and lo < ref:
                out.append(("expired", f"{nm}={v} is before the request ({iso(ref)}){how}"))
            elif VFROM.search(nm) and lo > ref:
                out.append(("not_yet_valid", f"{nm}={v} is after the request"))
            elif ASOF.search(nm) and ref - lo > 12 * 3600 and claim and not window:
                out.append(("stale", f"{nm}={v} is {(ref - lo) / 3600:.0f}h older than the request"))
            elif ASOF.search(nm) and lo - ref > 3900:  # > 1h05: beyond a UTC-vs-WAT slip
                out.append(("future_dated", f"{nm}={v} is after the request"))
        if STATUS_K.search(nm) and isinstance(v, str) and BAD_STATE.search(v.strip().lower()):
            out.append(("status", f"{nm}={v!r}"))
        if re.search(r"supersed(ed|_?by)|replaced_?by|obsolete|deprecated|retracted", nm) and v not in (None, False, ""):
            out.append(("superseded", f"{nm}={v!r}"))
        if re.search(r"published|approved|verified|is_live", nm) and v is False:
            out.append(("unpublished", f"{nm}=False"))
        if info and FOREIGN_K.match(nm) and isinstance(v, (str, int)) and not isinstance(v, bool) and str(v) not in info["ids"]:
            out.append(("cross_run", f"{nm}={v!r}: written by another run/trace/session, not by run {o['run']}"))
    if INJECT.search(o["text"]):
        out.append(("injection", f"instruction-like text: {INJECT.search(o['text'])[0]!r}"))
    pl = places(o["text"])
    if info and info["places"] and pl and not pl & info["places"]:
        out.append(("wrong_place", f"item is about {sorted(pl)}, the question asks about {sorted(info['places'])}"))
    return out

REACH_PTS = {"id": 40, "content": 40, "ref": 36, "listed": 34, "id~variant": 32, "upstream": 30, "content-only": 25, "order": 18}

def content_sig(o):
    return norm(" ".join(s for s in o["strings"] if len(s) >= 20))

INCL_L = re.compile(r"includ|used|select|kept|final|sent|attach|context|ctx|input")
CAND_L = re.compile(r"candidat|retriev|consider|rank|pool|availab|search|shortlist|recall|fetched|seen|^all_|options")

def reach_req(E, R, occs, run, req, no_req):
    """Source items of `run` that reached model request `req`: {raw: (method, occurrence)}."""
    got = {}
    rq = [o for o in occs if o["idx"] == req and o["role"] == "request"]
    lk = {o["lkey"] for o in rq if o["lkey"] and not o["dropped"]}
    if any(INCL_L.search(k) and not CAND_L.search(k) for k in lk):  # candidates/retrieved lists next to an included list
        for o in rq:
            if o["lkey"] and CAND_L.search(o["lkey"]) and not re.search(r"includ|used|select|kept|final|sent|attach", o["lkey"]):
                o["dropped"] = True
    rq = [o for o in rq if not o["xref"]]  # "supersedes: X" inside a request names X; it does not hand X to the model
    live = {o["raw"] for o in rq if not o["dropped"]}
    bare = {o["raw"] for o in rq if o["bare"]}  # listed as a value of its own, not only named inside some text
    live -= {r for r in live - bare if any(x["run"] == run and x["role"] == "source" and x["item"] and x["raw"] != r
                                           and r in x["text"] for x in occs)}
    live_keys = {idkey(r) for r in live}
    blob = "" if no_req else norm(" ".join(str(v) for p, v in E[req]["leaves"] if not (E[req]["combined"] and is_out(p))))
    src = [o for o in occs if o["run"] == run and o["role"] == "source" and not o["xref"]]
    src_keys = {o["key"] for o in src}
    # evicted / excluded / included:false before the request, or dropped by the request itself: never reached
    off = {o["key"] for o in src if o["dropped"] and o["idx"] < req} | {o["key"] for o in rq if o["dropped"]}
    off -= live_keys
    refs = set() if no_req else {v for p, v in E[req]["leaves"] if isinstance(v, str) and v not in R and not DROP_RE.search(p.lower())
            and re.search(r"id|ref|key|item|context|input|source|doc|chunk|call|attach|cite", snake(last(p))) and "parent" not in p.lower()
            and not (E[req]["combined"] and is_out(p))}
    id_mode = bool(live_keys & src_keys) or any(o["handles"] & refs for o in src)  # the request lists its inputs

    def put(o, m):
        old = got.get(o["raw"], ("", {"text": ""}))  # same method: keep the occurrence that carries the item's text
        if (REACH_PTS.get(m, 0), len(o["text"])) > (REACH_PTS.get(old[0], 0), len(old[1]["text"])):
            got[o["raw"]] = (m, o)
    kept = norm(" ".join(x["text"] for x in src if x["key"] not in off and not x["dropped"]))
    for o in src:
        pieces = [x for s in o["strings"] for x in [s] + re.split(r"(?<=[.;!?])\s+|\n", s) if len(norm(x)) >= 25]
        if o["raw"] in live:
            put(o, "id")
        elif o["key"] in live_keys - {x["key"] for x in src if x["raw"] in live}:
            put(o, "id~variant")
            o["flags"].append(("id_mismatch", f"the model request spells it {ascii(next(r for r in live if idkey(r) == o['key']))}"))
        elif o["key"] in off or o["dropped"]:  # unless its own text is in the request and no kept item carries that text
            sent = [x for x in pieces if norm(x)[:80] in blob and norm(x)[:80] not in kept]
            put(o, "content" if sent else "dropped")
            if sent:
                o["flags"].append(("dropped_but_sent", f"marked dropped, yet the request holds {short(sent[0], 60)!r}"))
        elif any(norm(x)[:80] in blob for x in pieces):
            put(o, "content-only" if id_mode and not o["handles"] & refs else "content")
        elif o["handles"] & refs:
            put(o, "ref")
    if not any(m in REACH_PTS for m, _ in got.values()):  # request names nothing: use the nearest earlier id list
        lists = [o for o in src if o["idx"] < req and not o["item"] and o["path"].endswith("]") and not o["dropped"]]
        listed = {o["key"] for o in lists if o["idx"] == max(x["idx"] for x in lists)} if lists else set()  # (context window,
        for o in src:  # rerank, ...), else array order
            if o["idx"] < req and not o["dropped"] and o["key"] not in off and (not listed or o["key"] in listed):
                put(o, "listed" if listed else "order")
    for o in rq:
        if not o["dropped"] and o["key"] not in src_keys and o["raw"] not in got:
            seen = sorted({x["run"] for x in occs if x["key"] == o["key"] and x["role"] == "source"})
            o["flags"].append(("phantom", "in the model request, but no tool/context event of this run returned it"
                               + (f" (seen in runs {seen})" if seen else " nor any other event")))
            put(o, "id")
    return got

def reach_all(E, R, occs):
    """Per run: which source items reached its last model request, and how (id, id variant, content, order, upstream)."""
    reach = defaultdict(dict)  # raw -> run -> (method, content signature, occurrence)
    for run, info in R.items():
        req, got = info["request"], info["reached"]
        if req is None and info["final"] is None:
            continue
        no_req, req = req is None, info["final"] if req is None else req  # no model request: inputs before the answer
        got.update(reach_req(E, R, occs, run, req, no_req))
        blob = "" if no_req else norm(" ".join(str(v) for p, v in E[req]["leaves"] if not (E[req]["combined"] and is_out(p))))
        done = set()
        for j in info["events"]:  # a summary/rewrite: an earlier answer quoted in the last request passes on its own inputs
            prev = next((i for i in reversed(info["events"]) if i < j and "model_request" in E[i]["cats"]), None)
            if j >= req or j == info["final"] or "response" not in E[j]["cats"] or prev is None or prev in done:
                continue
            said = [x for p, v in E[j]["leaves"] if isinstance(v, str) and (not E[j]["combined"] or is_out(p))
                    for x in re.split(r"(?<=[.;!?])\s+|\n", v) if len(norm(x)) >= 25]
            if any(norm(x)[:80] in blob for x in said):
                done.add(prev)
                for raw, (m, o) in reach_req(E, R, occs, run, prev, False).items():
                    if m in ("id", "id~variant", "content", "ref", "listed") and got.get(raw, ("",))[0] not in REACH_PTS:
                        got[raw] = ("upstream", o)
        for raw, (m, o) in got.items():
            if m in REACH_PTS:
                reach[raw][run] = (m, content_sig(o), o)
    return reach

XREF_K = re.compile(r"^(superseded_?by|replaced_?by|previous_?(version|id|item)|prev_?(version|id)|next_?version|see_?also|"
                    r"related(_?(ids?|items?|sources?))?|duplicate_?of|copy_?of|mirror_?of|parent_?(item|source|doc)(_?id)?)$")
FOLLOWS_K = re.compile(r"^(supersedes|replaces|updates|corrects|amends|refers_?to|follow_?up_?(of|to)|closes|cancels|resolves|"
                       r"restores|ends)(_?(id|ids|source_?ids?|ref|refs))?$")

def supersede_flags(R, occs, reach):
    """Items that a newer item names in supersedes / replaces / refers_to (a revision, a restoration closing an outage).
    In a run whose model saw the old item without the newer one, while the newer one existed (the run retrieved it, or it
    was issued before the run began), the old item is 'superseded'. Where both reached the same request, the model had
    the follow-up: 'superseded_seen', which rank() reads as the old item's problems being answered in that run."""
    newer = defaultdict(dict)  # old idkey -> {newer raw: its issue time or None}
    for o in occs:
        if o["item"] and o["role"] in ("source", "request"):
            for q, x in o["fields"]:
                if isinstance(x, str) and FOLLOWS_K.match(snake(last(q))):
                    t = next((to_epoch(v) for p, v in o["fields"] if isinstance(v, str) and ASOF.search(snake(last(p)))
                              and to_epoch(v) is not None), None)
                    for old in ids_in(x):
                        if idkey(old) != o["key"]:
                            newer[idkey(old)].setdefault(o["raw"], t)
    for raw, per_run in reach.items():
        new = newer.get(idkey(raw))
        for r, (_, _, o) in per_run.items() if new else ():
            seen = [n for n in new if r in reach.get(n, {})]
            if seen:
                o["flags"].append(("superseded_seen", f"{ascii(seen[0])} supersedes/answers it and reached the same request"))
                continue
            got = [n for n in new if any(x["raw"] == n and x["run"] == r and x["role"] == "source" for x in occs)]
            start = R[r]["start"]
            older = [n for n, t in new.items() if t is not None and start is not None and t <= start]
            if got or older:
                o["flags"].append(("superseded", f"{ascii((got or older)[0])} supersedes it, but " + (
                    "this run did not send it to the model" if got else "this run never retrieved it (issued before the run)")))

NEG = re.compile(r"incorrect|wrong|inaccurate|thumbs?[_ -]?down|negative|complain|mislead|\bbad\b|fail|reported|flagged", re.I)
GOOD_KEY = re.compile(r"(?<!in)correct|accura|helpful|\bgood|\bok\b", re.I)
BAD_KEY = re.compile(r"flag|incorrect|wrong|bad|fail|complain|report|incident|culprit|faulty|verdict|label", re.I)

HARD = ("time", "date", "pct", "weekday")
LOCAL = timedelta(hours=1)  # Luanda (WAT) wall clock, no DST
DEADLINE = re.compile(r"\b(until|till|by|ate|previst[oa]s? para|(?:expected|estimated|due) (?:at|by)|"
                      r"previsao de (?:reposicao|restabelecimento|normalizacao)(?: e|:)?)\s+"
                      r"(about |around |approximately |as |cerca das )?([01]?\d|2[0-3])(?::|h)([0-5]\d)?\b")
RANGE = re.compile(r"\b(?:das?|from|between)\s+(?:[01]?\d|2[0-3])(?::|h)(?:[0-5]\d)?\s*(?:as|a|ate|to|and|e|-)\s*"
                   r"([01]?\d|2[0-3])(?::|h)([0-5]\d)?\b")
# "restoration expected at 16h00" says the supply is still off, even with no outage word in the clause
PENDING = re.compile(r"\b(reposicao|restabelecimento|normalizacao|restoration|resumption)\b[^.;]{0,30}\b(previst|expected|estimated|due)|"
                     r"\bprevisao de (reposicao|restabelecimento|normalizacao)")

def answer_sig(text):
    return {t for t in toks(text) if t.split(":")[0] in HARD + ("place", "status")}

def agree(a, b):
    """Same claim: no hard fact kind with disjoint values, not water-on vs water-off, and the smaller claim mostly shared."""
    core = lambda s: {t for t in s if not t.startswith("place:")}  # noqa: E731  a shared place alone is no agreement
    if not core(a) or not core(b):
        return a == b
    kind = lambda s, k: {t for t in s if t.startswith(k + ":")}  # noqa: E731
    w = lambda s: sum(3 if t.split(":")[0] in HARD or t == "status:none" else 1 for t in s)  # noqa: E731  negation flips
    pol = lambda s: "up" if s & {"status:none", "status:restored"} else "down" if "status:outage" in s else None  # noqa: E731
    return not any(kind(a, k) and kind(b, k) and not kind(a, k) & kind(b, k) for k in HARD) and \
        not (pol(a) and pol(b) and pol(a) != pol(b)) and w(core(a & b)) >= 0.5 * min(w(core(a)), w(core(b)))

def end_times(text):
    t = deaccent(text)
    return {f"{int(m[3]):02d}:{m[4] or '00'}" for m in DEADLINE.finditer(t)} | {f"{int(m[1]):02d}:{m[2] or '00'}" for m in RANGE.finditer(t)}

RESTORED_NOW = re.compile(r"\b(now|already|ja)\b[^.;]{0,30}\b(restored|back|normal|resumed|running)|\b(has|have|had|was|were) (now )?"
                          r"(been )?(fully )?(restored|resumed)|\b(is|are|esta) (now )?(back|normal|restored)|restabelecid|voltou")

def passed_deadlines(answer, start, naive):
    """Outage end times the answer still promises ("interrupted until 18:00") that had passed, Luanda time, when the run began."""
    if start is None:
        return []
    now, out = datetime.fromtimestamp(start, timezone.utc) + LOCAL, []
    for sent in re.split(r"(?<=[.!?;])\s+", deaccent(answer)):
        if ("outage" not in statuses(sent) and not PENDING.search(sent)) or re.search(r"tomorrow|amanha", sent) or RESTORED_NOW.search(sent):
            continue
        dates = sorted(t[5:] for t in facts(sent) if t.startswith("date:"))
        for m in DEADLINE.finditer(sent):
            if re.search(r"\b(was|were|had|foi|esteve|estava)\b", " ".join(sent[:m.start()].split()[-5:])):
                continue  # "was interrupted until 08:00" reports the past
            try:
                d = now.replace(hour=int(m[3]), minute=int(m[4] or 0), second=0, microsecond=0)
                d = d.replace(month=int(dates[0][:2]), day=int(dates[0][3:])) if dates else d
            except ValueError:
                continue
            if d < now - timedelta(minutes=65 if naive else 5):  # naive timestamps may already be local time
                out.append(m[0])
    return out

LABEL_K = re.compile(r"(^|_)status$|flag|correct|accura|wrong|outcome|verdict|label|rating|grade|judg|assess|review|thumb|feedback|culprit|faulty")
LABEL_STATUS_K = re.compile(r"(^|_)status$")
VERDICT_V = re.compile(r"\s*(in)?(correct|accurate)\s*|\s*wrong\s*", re.I)
POS = re.compile(r"\s*(correct|accurate|ok|good|pass(ed)?|right|valid|thumbs?[_ -]?up|positive)\s*", re.I)

def label_of(k, v, any_str=False):
    """'bad', 'good' or None for one key/value of a label dict."""
    k = snake(k)
    if LABEL_STATUS_K.search(k):  # status: "incorrect" labels a run; status: "reported", "ok", "timeout" describe other things
        return None if not (isinstance(v, str) and VERDICT_V.fullmatch(v)) else "bad" if re.search(r"in|wrong", v, re.I) else "good"
    if isinstance(v, bool):
        return ("good" if v else "bad") if GOOD_KEY.search(k) else "bad" if v and BAD_KEY.search(k) else None
    if isinstance(v, str) and (any_str or LABEL_K.search(k)):
        return "bad" if NEG.search(v) else "good" if POS.fullmatch(v) else None
    return None

def verdict(E, R, occs, reach, meta_leaves, doc, in_events, F, forced=()):
    ids, answered = {r for r in R if r != "?"}, [r for r in R if R[r]["answer"]]
    inc, cor = set(), set()
    if forced:
        if set(forced) - set(R):
            sys.exit(f"--incorrect {sorted(set(forced) - set(R))}: no such run; runs are {sorted(R)}")
        return set(forced), set(answered) - set(forced), "set by --incorrect", None
    # a value names a run only under a run-like key, or when it is not a bare number ("severity": 2 is not run 2)
    names_run = lambda p, v: str(v) in ids and (re.search(r"run|trace|session|attempt|replay|(^|_)id$", snake(last(p)))  # noqa: E731
                                               or (not str(v).isdigit() and len(str(v)) > 2))
    for e in E:
        if "feedback" in e["cats"] and any((isinstance(v, str) and NEG.search(v)) or (v is False and GOOD_KEY.search(p))
                                           or (v is True and BAD_KEY.search(p)) for p, v in e["leaves"]) \
                and not any(label_of(last(p), v) == "good" for p, v in e["leaves"]):
            inc |= ({str(v) for p, v in e["leaves"] if names_run(p, v)} or {e["run"]}) & ids
    def scan(o, ctx, pk, strict, skip=None):
        """Each dict read as a whole: run ids in it (else the enclosing run) plus a label such as outcome/flagged/is_correct."""
        if isinstance(o, list):
            for v in o:
                scan(v, ctx, pk, strict)
        elif isinstance(o, dict) and (strict or id(o) not in in_events):
            own = {str(v) for k, v in o.items() if isinstance(v, (str, int)) and not isinstance(v, bool) and k != skip
                   and names_run(k, v)}
            rs = own or ctx
            for k, v in o.items():
                if str(k) in ids:  # {"r2": "incorrect"} or {"correct": {"r1": true}}
                    lab = label_of(pk, v, True)
                    (inc if lab == "bad" else cor).update({str(k)} if lab else set())
                    scan(v, {str(k)}, snake(k), strict)
                elif isinstance(v, (dict, list)):
                    scan(v, rs if len(rs) == 1 else set(), snake(k), strict)
                elif rs and (not strict or LABEL_K.search(snake(k))) and label_of(k, v):
                    (inc if label_of(k, v) == "bad" else cor).update(rs)
    scan(doc, set(), "", False)
    for e in E:  # flagged: true on a response, an evaluation event, a run summary event
        if e["cats"] & {"response", "feedback", "other"}:
            scan(e["obj"], {e["run"]} & ids, "", True, F["run"])  # the event's own run field is not a label target
    for p, v in meta_leaves:
        if names_run(p, v) and (BAD_KEY.search(p) or GOOD_KEY.search(p)):
            (cor if GOOD_KEY.search(p) and not BAD_KEY.search(p) else inc).add(str(v))
        elif isinstance(v, str) and NEG.search(v):  # prose such as "run-3 sent the incorrect update", clause by clause
            pre = lambda r: r"run\W{0,3}" if len(r) <= 2 else ""  # noqa: E731  short ids need "run" in front
            inc |= {r for c in re.split(r"[.;,\n]", v) if NEG.search(c) for r in ids
                    if re.search(pre(r) + rf"(?<![\w-]){re.escape(r)}(?![\w-])", c, re.I)}
    if inc:
        return inc, (cor or set(answered)) - inc, "explicit label/feedback in the trace", None
    if not answered:
        return set(R), set(), "no run has a final answer: every run treated as suspect", None
    late = {r: passed_deadlines(R[r]["answer"], R[r]["start"], R[r]["naive"]) for r in answered}
    if any(late.values()) and not all(late.values()):
        inc = {r for r in answered if late[r]}
        return inc, set(answered) - inc, "the answer promises an outage end time that had already passed (Luanda time) when " \
            f"the run started: {', '.join(f'{r}: {late[r]}' for r in sorted(inc))}", None
    heat = {r: sum(len({k for k, _ in v[2]["flags"] + E[v[2]["idx"]]["flags"]}) for v in
                   (reach[raw][r] for raw in reach if r in reach[raw])) for r in answered}
    sigs = {r: answer_sig(R[r]["answer"]) for r in answered}
    clusters = []  # greedy: a run joins the first cluster whose first member says the same thing
    for r in answered:
        home = next((c for c in clusters if agree(sigs[r], sigs[c[0]])), None)
        home.append(r) if home else clusters.append([r])
    clusters.sort(key=len, reverse=True)
    if len(clusters) == 1:
        return set(answered), set(), "all answers agree on their facts: every run treated as suspect", None
    if len(clusters[0]) > len(clusters[1]):
        cor, inc = set(clusters[0]), set(answered) - set(clusters[0])
        why = f"majority vote on answer facts ({len(cor)} of {len(answered)} runs agree)"
        mean = lambda rs: sum(heat[r] for r in rs) / len(rs)  # noqa: E731
        if mean(cor) > mean(inc):
            why += "; WARNING: the majority's model inputs carry MORE anomalies, so the majority may be the wrong side"
        return inc, cor, why, (cor, inc)
    hi = max(heat.values())
    if list(heat.values()).count(hi) == len(heat):
        return set(answered), set(), "no majority and no anomaly difference: every run treated as suspect", None
    inc = {r for r in answered if heat[r] == hi}
    return inc, set(answered) - inc, "no majority; picked the run(s) whose model inputs carry the most anomaly flags", \
        (set(answered) - inc, inc)

VALIDITY = {"expired", "not_yet_valid", "stale", "superseded", "status", "unpublished", "truncated", "cross_run",
            "late_after_timeout", "orphan_call"}
STRONG = VALIDITY | {"injection", "wrong_place", "id_mismatch", "arg_diff", "dropped_but_sent"}  # vs timing jitter, cache hits, retries
ARGS_P = re.compile(r"(^|[._])(args|arguments|params|parameters|input|query|kwargs)([._\[]|$)")
NAME_K = re.compile(r"^(tool|tool_?name|fn|function|function_?name|name|method)$")

def arg_flags(E, R, occs, inc, cor):
    """Flag results of tool calls whose arguments differ from what every correct run sent, or name a place not asked about."""
    sent, seen = {}, defaultdict(lambda: defaultdict(set))  # call idx -> {(tool, arg, value)}; (tool, arg) -> run -> values
    for e in E:
        if "tool_call" in e["cats"]:
            lv = [(p, v) for p, v in e["leaves"] if isinstance(v, (str, int, float)) and not isinstance(v, bool)]
            name = next((str(v) for p, v in lv if NAME_K.match(snake(last(p)))), "")
            args = [(p, v) for p, v in lv if ARGS_P.search(p.lower())] or \
                [(p, v) for p, v in lv if not NAME_K.match(snake(last(p))) and not CALLREF.match(snake(last(p)))]
            sent[e["idx"]] = {(name, snake(last(p)), norm(deaccent(str(v)))) for p, v in args
                              if str(v) not in e["consts"] and not ids_in(str(v))}
            for t, k, v in sent[e["idx"]]:
                seen[t, k][e["run"]].add(v)
    for e in E:
        notes = []
        for t, k, v in sent.get(e.get("call"), ()):
            cv = set().union(*(seen[t, k][x] for x in cor if x in seen[t, k]))
            if e["run"] in inc and len(cv) == 1 and v not in cv and (len(cor) > 1 or not re.search(r"\d", v)):
                notes.append(("arg_diff", f"its call sent {k}={v!r}; every correct run sent {next(iter(cv))!r}"))
        pl, ask = places(" ".join(v for _, _, v in sent.get(e.get("call"), ()))), R[e["run"]]["places"]
        if ask and pl and not pl & ask:
            notes.append(("wrong_place", f"its call asked about {sorted(pl)}, the question about {sorted(ask)}"))
        for o in occs:
            if notes and o["idx"] == e["idx"] and o["role"] == "source":
                o["flags"] += notes

def rank(R, occs, reach, inc, cor):
    def base(r):  # correct runs that say something else (a run saying the same thing at another time is no contrast)
        other = [c for c in cor if not agree(answer_sig(R[r]["answer"]), answer_sig(R[c]["answer"]))] or sorted(cor)
        return set().union(*(toks(R[c]["answer"]) for c in other)) if other else toks(R[r]["prompt"])
    dist = {r: toks(R[r]["answer"]) - base(r) for r in inc}
    late = {r: end_times(" ".join(passed_deadlines(R[r]["answer"], R[r]["start"], R[r]["naive"]))) for r in inc}
    cands = {}
    for o in occs:
        c = cands.setdefault(o["raw"], {"source_id": o["raw"], "repr": ascii(o["raw"]), "json": json.dumps(o["raw"]), "score": 0.0,
                                        "reasons": [], "flags": set(), "occurrences": [], "id_flags": id_flags(o["raw"]), "first": o["idx"]})
        c["occurrences"].append(f"run {o['run']} #{o['idx']} {o['role']} {o['path']}")
        c["flags"] |= {(o["run"], k, d) for k, d in o["flags"]}
    got = lambda r: {raw for raw in reach if r in reach[raw]}  # noqa: E731
    good = set().union(*map(got, cor)) if cor else set()
    subset = {r for r in inc if cor and got(r) <= good}  # nothing new reached the wrong run: an input was MISSING there
    elig = {o["raw"] for o in occs if o["srckey"]}  # the flag is a source_id: when such keys exist, nothing else qualifies
    for raw, c in cands.items():
        s, rs, mine = 0.0, c["reasons"], reach.get(raw, {})
        rin = {r: mine[r] for r in inc if r in mine}
        if rin:
            r, (m, sig, _) = max(rin.items(), key=lambda kv: REACH_PTS[kv[1][0]])
            s += REACH_PTS[m]
            rs.append(f"reached the last model request of {'incorrect' if cor else 'suspect'} run {r} via {m}")
            def valid(x):  # validity problems in run x; none that matter where a follow-up item answered it
                ks = {k for y, k, _ in c["flags"] if y == x}
                return {"answered"} if "superseded_seen" in ks else ks & VALIDITY
            same = [x for x in cor if x in mine and mine[x][1] == sig and valid(x) == valid(r)]
            diff = [x for x in cor if x in mine and x not in same]
            if same and r in subset:
                rs.append(f"also reached correct runs {sorted(same)}, but run {r} saw nothing they did not (an input was "
                          "missing there, see DIFF): ranked by the wrong claims it supplies")
            elif same:
                s -= 30 * len(same) / len(cor)
                rs.append(f"the same item also reached correct runs {sorted(same)}")
            elif diff and valid(r) - {"answered"} and all(valid(r) - valid(x) for x in diff):
                s += 10  # the time-dependent failure: same item, but expired/superseded/stale only where the answer went wrong
                rs.append(f"also reached correct runs {sorted(diff)}, but only in run {r} was it "
                          f"{'/'.join(sorted(valid(r) - {'answered'}))} with nothing newer to answer it")
            elif diff:
                s -= 3
                rs.append(f"same id but DIFFERENT content or validity in correct runs {sorted(diff)}")
            elif cor:
                rs.append("absent from every correct run's model request")
            sup = max((sum(map(weight, dist[x] & toks(mine[x][2]["text"]))) / max(1, sum(map(weight, dist[x])))
                       for x in rin if dist.get(x)), default=0)
            if any(late[x] & end_times(mine[x][2]["text"]) for x in rin):
                s += 15
                rs.append("states the outage end time the answer repeated after it had passed")
            if sup:
                s += 35 * sup
                rs.append(f"supplies {sup:.0%} of the claims only the wrong answer makes")
            elif r in subset:
                s -= 15
                rs.append("supplies none of the claims only the wrong answer makes")
        elif inc:
            s -= 15
            rs.append("did not reach the last model request of any incorrect run")
        hot = {k for r, k, _ in c["flags"] if r in inc}
        cold = {k for _, k, _ in c["flags"]} - hot
        s += min(30, sum(10 if k in STRONG else 6 for k in hot)) + min(4, len(cold))
        rs += [f"anomalies in incorrect runs: {', '.join(sorted(hot))}"] * bool(hot) + \
              [f"anomalies elsewhere: {', '.join(sorted(cold))}"] * bool(cold)
        if not ID_RE.fullmatch(skel(raw)[0].strip()):
            s -= 25
            rs.append("not a SIGMOID_ id")
        c["eligible"] = not elig or raw in elig
        rs += ["never appears under a source_id key, so it cannot be the answer"] * (not c["eligible"])
        c["score"], c["flags"] = round(s, 1), sorted(c["flags"])
    return sorted(cands.values(), key=lambda c: (not c["eligible"], -c["score"], c["first"])), dist

def analyze(doc, forced=()):
    doc = normalize(doc)
    E, F, meta, ev_path, lists, unit = load(doc)
    R = run_structure(E)
    occs = occurrences(E, meta)
    in_events = {id(x) for lst in lists for x in lst}
    meta_leaves = []

    def meta_walk(o, p=""):  # everything outside the events lists
        if isinstance(o, dict) and id(o) not in in_events:
            for k, v in o.items():
                meta_walk(v, f"{p}.{k}" if p else str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                meta_walk(v, f"{p}[{i}]")
        elif not isinstance(o, dict):
            meta_leaves.append((p, o))
    meta_walk(doc)
    occs += [{"raw": raw, "key": idkey(raw), "run": "-", "idx": -1, "path": "(metadata) " + p, "role": "meta", "item": False, "bare": raw == v,
              "strings": [], "text": "", "fields": [], "handles": set(), "dropped": False, "lkey": "",
              "srckey": bool(SRC_KEY.match(role_name(p))), "xref": False, "flags": []} for p, v in meta_leaves for raw in ids_in(v)]
    event_anomalies(E, R, F)
    for o in occs:
        if o["role"] == "source" or (o["role"] == "request" and o["item"]):
            o["flags"] = item_flags(o, R) + (E[o["idx"]]["flags"] if o["role"] == "source" else [])
    reach = reach_all(E, R, occs)
    supersede_flags(R, occs, reach)
    inc, cor, why, alt = verdict(E, R, occs, reach, meta_leaves, doc, in_events, F, forced)
    arg_flags(E, R, occs, inc, cor)
    ranking, dist = rank(R, occs, reach, inc, cor)
    alt_rank = rank(R, occs, reach, *alt)[0][:3] if alt else []
    for info in R.values():
        texts = " ".join(o["text"] for m, o in info["reached"].values() if m in REACH_PTS)
        info["unsupported"] = sorted(f for f in facts(info["answer"]) - facts(texts) if not f.startswith("day:"))
    keys = defaultdict(set)
    for c in ranking:
        keys[idkey(c["source_id"])].add(c["source_id"])
    ks = sorted(keys)
    near = [sorted(g, key=repr) for g in keys.values() if len(g) > 1] + [
        sorted(keys[a] | keys[b], key=repr) for i, a in enumerate(ks) for b in ks[i + 1:]
        if difflib.SequenceMatcher(None, a, b).ratio() >= 0.9 or b.startswith(a + "_") or a.startswith(b + "_")]
    return {"events_path": ev_path, "fields": F, "elapsed_unit_s": unit, "events": E, "runs": R, "occurrences": occs,
            "verdict": {"incorrect": sorted(inc), "correct": sorted(cor), "why": why,
                        "distinguishing": {r: sorted(d) for r, d in dist.items()}},
            "near_duplicates": near, "ranking": ranking, "answer": ranking[0]["source_id"] if ranking else None,
            "alternative": {"incorrect": sorted(alt[0]), "top": [(c["source_id"], c["score"]) for c in alt_rank]} if alt else None}

# ---------------------------------------------------------------- report
def short(s, n=90):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[: n - 3] + "..."

def report(res):
    E, R, V = res["events"], res["runs"], res["verdict"]
    print(f"== events at '{res['events_path']}' ({len(E)}); fields {res['fields']}; elapsed unit {res['elapsed_unit_s']}s")
    ids_at = defaultdict(set)
    for o in res["occurrences"]:
        ids_at[o["idx"]].add(ascii(o["raw"]))
    for run, info in R.items():
        tag = "INCORRECT" if run in V["incorrect"] and V["correct"] else "correct" if run in V["correct"] else "suspect"
        print(f"\n== run {run!r} [{tag}]: {len(info['events'])} events, last model request #{info['request']}, final #{info['final']}")
        for i in info["events"]:
            e = E[i]
            text = next((v for _, v in e["leaves"] if isinstance(v, str) and len(v) > 25 and ids_in(v) != [v]), "")
            el = "-" if e["el"] is None else f"{e['el']:.3f}s"
            print(f"  #{i:<4} {iso(e['ts'])} el={el:<9} {short(e['type'], 20):<20} {'/'.join(sorted(e['cats'])):<20}"
                  f" ids={','.join(sorted(ids_at[i])) or '-'} | {short(text, 70)}")
            for k, d in e["flags"]:
                print(f"         ! {k}: {d}")
        print(f"  FINAL: {short(info['answer'], 300)!r}")
        print(f"  answer facts not backed by this run's model inputs: {info['unsupported'] or 'none'}")
        for raw, (m, o) in sorted(info["reached"].items(), key=lambda kv: kv[1][1]["idx"]):
            print(f"  -> {m:<13} {ascii(raw)} (from #{o['idx']} {o['path']})")
    print(f"\n== verdict: incorrect {V['incorrect']}, correct {V['correct']} ({V['why']})")
    for r, d in V["distinguishing"].items():
        print(f"  claims only run {r}'s answer makes: {d}")
    reached = {r: {raw for raw, (m, _) in R[r]["reached"].items() if m in REACH_PTS} for r in R}
    good = set().union(*(reached[c] for c in V["correct"])) if V["correct"] else set()
    for r in V["incorrect"]:
        print(f"  DIFF {r!r} vs correct runs: only here {sorted(map(ascii, reached[r] - good))}; missing here "
              f"{sorted(map(ascii, good - reached[r]))}; shared {sorted(map(ascii, reached[r] & good))}")
    print("\n== id inventory (ascii() repr: hidden and non-ASCII characters escaped)")
    for c in sorted(res["ranking"], key=lambda c: c["repr"]):
        print(f"  {c['repr']}" + (f"   FLAGS: {'; '.join(c['id_flags'])}" if c["id_flags"] else ""))
        for occ in c["occurrences"][:10]:
            print(f"      {occ}")
        print(f"      ... {len(c['occurrences']) - 10} more" if len(c["occurrences"]) > 10 else "", end="")
    print("\n== near-duplicate id groups")
    for g in res["near_duplicates"]:
        print("  " + "  ~  ".join(map(ascii, g)))
    print("\n== item anomalies by id")
    for c in res["ranking"]:
        for run, k, d in c["flags"]:
            print(f"  {c['repr']:<42} run {run}: {k}: {d}")
    print("\n== ranking (every candidate)")
    for n, c in enumerate(res["ranking"], 1):
        print(f"  {n:>2}. {c['score']:6.1f}  {c['repr']}\n" + "".join(f"          - {r}\n" for r in c["reasons"]), end="")
    if res["alternative"]:
        print(f"\n== if instead runs {res['alternative']['incorrect']} were the incorrect ones, the top candidates would be: "
              + ", ".join(f"{ascii(r)} ({s})" for r, s in res["alternative"]["top"]))
    if res["ranking"]:
        top, rk, alt = res["ranking"][0], res["ranking"], res["alternative"]
        print(f"\nANSWER: {top['source_id']}\n  repr: {top['source_id']!r}\n  ascii: {top['repr']}\n  json: {top['json']}")
        warn = [f"lead over #2 is only {top['score'] - rk[1]['score']:.1f}"] * (len(rk) > 1 and top["score"] - rk[1]["score"] < 10)
        warn += ["no run is known to be correct"] * (not V["correct"]) + ["the top id is not under a source_id key"] * (not top["eligible"])
        print(f"  CHECK: {'LOW CONFIDENCE: ' + '; '.join(warn) if warn else 'clear lead'}. Verdict: {V['why']}.")
        if alt and alt["top"] and alt["top"][0][0] != top["source_id"]:
            print(f"  If runs {alt['incorrect']} were the wrong ones instead, the answer would be {ascii(alt['top'][0][0])}: "
                  "rerun with --incorrect RUN if you know which run gave the incorrect update.")
        print(f"  Read the final model request of run(s) {V['incorrect']} by hand before submitting.")

def load_file(path):
    """(document, sha256 of the file). utf-8-sig: a BOM must not break the load."""
    with open(path, "rb") as f:
        raw = f.read()
    return json.loads(raw.decode("utf-8-sig")), hashlib.sha256(raw).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trace")
    ap.add_argument("--json", dest="out")
    ap.add_argument("--incorrect", action="append", default=[], metavar="RUN",
                    help="run id known to be wrong (repeat or comma-separate); overrides the verdict")
    ap.add_argument("--answer", metavar="FILE", help="write the top source_id plus a newline to FILE")
    a = ap.parse_args()
    doc, sha = load_file(a.trace)
    print(f"== input {a.trace}: sha256 {sha} (compare with the laptop copy)")
    res = analyze(doc, [r.strip() for x in a.incorrect for r in x.split(",") if r.strip()])
    report(res)
    if a.answer and res["answer"] is not None:
        with open(a.answer, "w", encoding="utf-8", newline="") as f:
            f.write(res["answer"] + "\n")
        with open(a.answer, "rb") as f:
            print(f"\nwrote {a.answer} ({ascii(res['answer'])} + newline), bytes: {f.read().hex(' ')}")
    if a.out:
        drop = {"obj", "leaves", "fields", "handles"}
        clean = lambda d: {k: (sorted(v) if isinstance(v, set) else v) for k, v in d.items() if k not in drop}  # noqa: E731
        res = dict(res, events=[clean(e) for e in res["events"]], occurrences=[clean(o) for o in res["occurrences"]],
                   runs={r: clean(dict(i, reached={k: [m, o["idx"]] for k, (m, o) in i["reached"].items()}))
                         for r, i in res["runs"].items()})
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1, default=str)

if __name__ == "__main__":
    main()
