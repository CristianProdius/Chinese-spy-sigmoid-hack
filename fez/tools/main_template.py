#!/usr/bin/env python3
"""The Dispatch Desk of Fez: route each request to the cheap or the expensive guide.

Reads test-input.csv (request_id,prompt) from the working folder and writes
routing_log.csv (request_id,model). Python 3.10-3.12, standard library only, offline.

How it decides:
1. Every request kind is a fixed template, so the router parses the prompt and
   solves it exactly (the solver reproduces all 400 training answers).
2. It estimates p_cheap and p_expensive, the chance each guide answers this
   request correctly, from the numbers, the wording and the true answer. The
   tables below were measured by running both guide models (same GGUF files,
   prompts and greedy settings as run_guides.py) on ~13,000 synthetic requests
   built from the same templates, pooled with the 400 recorded training answers.
3. It sends to the expensive guide the requests with the largest expected gain
   p_expensive - p_cheap, as many as the budget allows: cost = N + 24 * E must
   stay within 20 * N, so E <= 19N/24 (395 of 500). Because the router counts its
   own picks, the cost gate holds whatever the mix of request kinds.
"""

import csv
import math
import re
import sys

INPUT = "test-input.csv"
OUTPUT = "routing_log.csv"
BUDGET_PER_REQUEST = 20
CHEAP_COST, EXPENSIVE_COST = 1, 25


# ---------------------------------------------------------------- parsing ----

def _ints(pattern, text):
    m = re.search(pattern, text)
    if not m:
        raise ValueError(pattern)
    return [int(g) for g in m.groups()]


def parse(p):
    """Return (family, info). info['answer'] is the exact answer as a string."""
    d = {}
    if "board lists" in p:
        head = p.split(" lists ", 1)[1].split(". ", 1)[0]
        prices = [(n.strip(), int(v)) for n, v in re.findall(r"(?:^|, |and )([a-z][a-z ]*?) at (\d+) dirham", head)]
        if len(prices) < 2:
            raise ValueError("board")
        m = re.search(r"What do(?:es)? (.+?) cost\?", p)
        if m:
            fam, item = "price", m.group(1).strip()
        else:
            m = re.search(r"stall sells ([a-z][a-z ]*?)\. What does", p)
            if not m:
                raise ValueError("price item")
            fam, item = "price_ind", m.group(1).strip()
        names = [n for n, _ in prices]
        d.update(prices=prices, item=item, pos=names.index(item))
        d["answer"] = str(dict(prices)[item])
        return fam, d
    if "gate charges" in p:
        base, = _ints(r"charges (\d+) dirham for every cart", p)
        n, = _ints(r"brings (\d+) carts?", p)
        d.update(base=base, n=n)
        if "heavier" in p:
            heavy, lim = _ints(r"but (\d+) dirham for any cart heavier than (\d+) kg", p)
            k, w1, w2 = _ints(r"(\d+) of them weighs? (\d+) kg and the rest weigh (\d+) kg", p)
            tot = k * (heavy if w1 > lim else base) + (n - k) * (heavy if w2 > lim else base)
            d.update(heavy=heavy, lim=lim, k=k, w1=w1, w2=w2, answer=str(tot))
            return "toll2", d
        d["answer"] = str(base * n)
        return "toll1", d
    if "stall opens" in p:
        hh, mm = _ints(r"opens at (\d+):(\d+)", p)
        h1, = _ints(r"works for (\d+) hours?", p)
        t = hh * 60 + mm + h1 * 60
        d.update(open=hh * 60 + mm, h1=h1)
        fam = "stall1"
        if "pauses" in p:
            pause, = _ints(r"pauses (\d+) minutes?", p)
            h2, = _ints(r"works (\d+) more hours?", p)
            t += pause + h2 * 60
            d.update(pause=pause, h2=h2)
            fam = "stall2"
        t %= 24 * 60
        d["answer"] = "%02d:%02d" % (t // 60, t % 60)
        return fam, d
    if "Walking times" in p or "shortest walk" in p:
        edges = [(a, b, int(w)) for a, b, w in re.findall(r"([A-Z][a-z]+)-([A-Z][a-z]+) (\d+) minutes?", p)]
        src, dst = re.search(r"shortest walk from ([A-Z][a-z]+) to ([A-Z][a-z]+)", p).groups()
        g = {}
        for a, b, w in edges:
            g.setdefault(a, {})[b] = min(w, g.get(a, {}).get(b, 10 ** 9))
            g.setdefault(b, {})[a] = min(w, g.get(b, {}).get(a, 10 ** 9))
        dist, todo = {src: 0}, set(g)
        while todo:
            reach = [x for x in todo if x in dist]
            if not reach:
                break
            u = min(reach, key=lambda x: dist[x])
            todo.discard(u)
            for v, w in g[u].items():
                if dist[u] + w < dist.get(v, 10 ** 9):
                    dist[v] = dist[u] + w
        d.update(edges=edges, src=src, dst=dst, direct=g.get(src, {}).get(dst), answer=str(dist[dst]))
        return "walk%d" % len(edges), d
    if "takings" in p:
        head = p.split(": ", 1)[1].split(". ", 1)[0]
        tk = [(s, int(v)) for s, v in re.findall(r"([A-Z][a-z]+) (\d+) dirham", head)]
        most = bool(re.search(r"\bmost\b", p.rsplit(". ", 1)[-1]))
        d.update(takings=tk, most=most)
        vals, fam = tk, "take"
        if "stall fee" in p:
            fee, = _ints(r"stall fee of (\d+) dirham", p)
            crates = [int(x) for x in re.findall(r"\d+", p.split("they sold", 1)[1].split("crates", 1)[0])]
            if len(crates) != len(tk):
                raise ValueError("crates")
            vals = [(s, v - fee * c) for (s, v), c in zip(tk, crates)]
            d.update(fee=fee, crates=crates, net=vals)
            fam = "fee"
        pick = max if most else min
        d["answer"] = pick(vals, key=lambda x: x[1])[0].lower()
        return fam + ("_most" if most else "_least"), d
    if " loads " in p:
        c, b = _ints(r"loads (\d+) crates? of .+? with (\d+) \w+ in each crate", p)
        d.update(c=c, b=b)
        if "sells" in p:
            s, = _ints(r"sells (\d+) ", p)
            a, ap = _ints(r"hands (\d+) \w+ to each of (\d+) apprentices?", p)
            d.update(s=s, a=a, ap=ap, answer=str(c * b - s - a * ap))
            return "crate2", d
        d["answer"] = str(c * b)
        return "crate1", d
    raise ValueError("unknown template")


def family_by_keywords(p):
    """Best-effort family when exact parsing fails (wording not seen in training)."""
    if "board lists" in p:
        return "price_ind" if "whatever" in p else "price"
    if "gate charges" in p:
        return "toll2" if "heavier" in p else "toll1"
    if "stall opens" in p:
        return "stall2" if "pause" in p else "stall1"
    if "Walking times" in p or "shortest walk" in p:
        return "walk4" if p.count(" minutes,") >= 3 else "walk3"
    if "takings" in p:
        return ("fee" if "fee" in p else "take") + ("_most" if "most" in p else "_least")
    if " loads " in p:
        return "crate2" if "sells" in p else "crate1"
    return "unknown"


# ----------------------------------------------------------- table lookup ----

__CELLS__


TABLES = __TABLES__

# Used only when a prompt cannot be parsed at all: no family, so a mid-range gain.
UNKNOWN = (0.34, 0.85)


def _lookup(g, fam, par, cel):
    t = TABLES[g]
    if par is not None:
        v = t["cell"].get("%s#%s#%s" % (fam, par, cel))
        if v is None:
            v = t["par"].get("%s#%s" % (fam, par))
        if v is not None:
            return v
    return t["fam"].get(fam)


def _souk_pick_prob(fam, d):
    """Chance the cheap guide names the right souk: it picks by name and list position, not by the values."""
    w = TABLES["logit"]["fee" if fam.startswith("fee") else "take"]
    names = [s.lower() for s, _ in d["takings"]]
    sc = [w.get("n_" + n, 0.0) + w.get("p%d" % i, 0.0) for i, n in enumerate(names)]
    m = max(sc)
    ex = [math.exp(s - m) for s in sc]
    return ex[names.index(d["answer"])] / sum(ex) if d["answer"] in names else 0.0


def estimate(fam, d):
    """(p_cheap_right, p_expensive_right) for one parsed request."""
    cp, cc, ep, ec = cells(fam, d)
    pc = _souk_pick_prob(fam, d) if cp is None else _lookup("c", fam, cp, cc)
    pe = _lookup("e", fam, ep, ec)
    if pc is None or pe is None:
        raise KeyError(fam)
    return pc, pe


def estimate_family(fam):
    pc, pe = TABLES["c"]["fam"].get(fam), TABLES["e"]["fam"].get(fam)
    if pc is None and fam.startswith(("take", "fee")):
        pc = 0.25
    return (pc, pe) if pc is not None and pe is not None else UNKNOWN


# ---------------------------------------------------------------- routing ----

def score(prompt):
    try:
        fam, d = parse(prompt)
        return estimate(fam, d)
    except Exception:
        return estimate_family(family_by_keywords(prompt))


def route(rows):
    """rows: list of (request_id, prompt) -> list of 'cheap'/'expensive' in the same order."""
    n = len(rows)
    max_expensive = (BUDGET_PER_REQUEST * n - CHEAP_COST * n) // (EXPENSIVE_COST - CHEAP_COST)
    gains = []
    for i, (_, prompt) in enumerate(rows):
        pc, pe = score(prompt)
        gains.append((pe - pc, i))
    choice = ["cheap"] * n
    picked = 0
    for gain, i in sorted(gains, key=lambda x: (-x[0], x[1])):
        if picked >= max_expensive or gain <= 0:
            break
        choice[i] = "expensive"
        picked += 1
    return choice


def read_requests(path):
    """(request_id, prompt) pairs. Tolerates a BOM, CRLF, header case, extra or reordered columns, no header."""
    try:
        csv.field_size_limit(2 ** 31 - 1)
    except OverflowError:
        pass
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        table = [row for row in csv.reader(handle) if any(cell.strip() for cell in row)]
    if not table:
        return []
    header = [cell.strip().lower() for cell in table[0]]
    if "request_id" in header:
        i_id = header.index("request_id")
        i_p = header.index("prompt") if "prompt" in header else (1 if i_id == 0 else 0)
        table = table[1:]
    else:
        i_id, i_p = 0, 1
    rows = []
    for row in table:
        rid = row[i_id].strip() if i_id < len(row) else ""
        if rid:
            rows.append((rid, row[i_p] if i_p < len(row) else ""))
    return rows


def main():
    rows = read_requests(INPUT)
    choice = route(rows)
    with open(OUTPUT, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["request_id", "model"])
        for (rid, _), model in zip(rows, choice):
            writer.writerow([rid, model])
    n_exp = choice.count("expensive")
    print("routed %d requests: %d expensive, %d cheap, cost %d (budget %d)" % (
        len(rows), n_exp, len(rows) - n_exp, len(rows) - n_exp + EXPENSIVE_COST * n_exp,
        BUDGET_PER_REQUEST * len(rows)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
