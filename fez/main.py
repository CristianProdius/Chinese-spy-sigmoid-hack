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

def walk_parts(d):
    s, t, E = d['src'], d['dst'], d['edges']
    nodes = set()
    for a, b, _ in E:
        nodes.update([a, b])
    via = [x for x in nodes if x not in (s, t) and any({a, b} == {s, x} for a, b, _ in E)
           and any({a, b} == {x, t} for a, b, _ in E)]
    if d['direct'] is None or not via:
        return None
    v = via[0]
    a = [w for x, y, w in E if {x, y} == {s, v}][0]
    b = [w for x, y, w in E if {x, y} == {v, t}][0]
    return a, b, d['direct'], max(w for _, _, w in E)


def walk_keys(fam, d):
    """(kind, cheap cell, exp cell) for a walk."""
    wp = walk_parts(d)
    if wp is None:
        return 'odd', 'odd', 'odd'
    a, b, dd, mx = wp
    if dd > a + b:
        return 'det', 'det', 'det_d%d' % min(dd // 4, 6)
    slack = a + b - dd
    sb = 0 if slack <= 2 else 1 if slack <= 5 else 2 if slack <= 9 else 3
    rank = ('lt_min' if dd < min(a, b) else 'eq_min' if dd == min(a, b) else 'mid' if dd < max(a, b)
            else 'eq_max' if dd == max(a, b) else 'gt_max')
    return 'dir', 'dir_max%d_s%d' % (dd == mx, sb), 'dir_%s' % rank


def cells(fam, d):
    """(cheap parent, cheap cell, exp parent, exp cell) for one request; None means 'use a model'."""
    if fam == 'price':
        return 'all', 'all', 'all', 'all'
    if fam == 'price_ind':
        return d['item'], '%s|%d' % (d['item'], d['pos']), 'all', 'all'
    if fam == 'toll1':
        return 'b%d' % d['base'], 'b%d|n%d' % (d['base'], d['n']), 'all', 'all'
    if fam == 'toll2':
        return 'all', 'all', 'all', 'k1' if d['k'] == 1 else 'k2+'
    if fam == 'stall1':
        return 'h%d' % d['h1'], 'h%d|o%d' % (d['h1'], d['open']), 'all', 'm45' if d['open'] % 60 >= 45 else 'm<45'
    if fam == 'stall2':
        return 'all', 'all', 'all', 'p%d' % d['pause']
    if fam in ('walk3', 'walk4'):
        kind, ck, ek = walk_keys(fam, d)
        return kind, ck, kind, ek
    if fam in ('take_most', 'take_least'):
        return None, None, 'all', 'all'
    if fam in ('fee_most', 'fee_least'):
        net = sorted(v for _, v in d['net'])
        gap = net[-1] - net[-2] if d['most'] else net[1] - net[0]
        return None, None, 'all', 'g%d' % min(gap // 10, 2)
    if fam == 'crate1':
        return 'c%d' % d['c'], 'c%d|b%d' % (d['c'], d['b']), 'all', 'all'
    if fam == 'crate2':
        return 'all', 'all', 'all', 'all'
    raise KeyError(fam)



TABLES = {"c":{
"cell":{"crate1#c10#c10|b10":0.7287,"crate1#c10#c10|b11":0.9968,"crate1#c10#c10|b12":0.9968,"crate1#c10#c10|b4":0.9964,"crate1#c10#c10|b5":0.9966,"crate1#c10#c10|b6":0.9959,"crate1#c10#c10|b7":0.9954,"crate1#c10#c10|b8":0.9957,"crate1#c10#c10|b9":0.9973,"crate1#c11#c11|b10":0.9909,"crate1#c11#c11|b11":0.6186,"crate1#c11#c11|b12":0.9915,"crate1#c11#c11|b4":0.9936,"crate1#c11#c11|b5":0.992,"crate1#c11#c11|b6":0.9925,"crate1#c11#c11|b7":0.9917,"crate1#c11#c11|b8":0.992,"crate1#c11#c11|b9":0.9936,"crate1#c12#c12|b10":0.9593,"crate1#c12#c12|b11":0.9247,"crate1#c12#c12|b12":0.9785,"crate1#c12#c12|b4":0.9305,"crate1#c12#c12|b5":0.9065,"crate1#c12#c12|b6":0.848,"crate1#c12#c12|b7":0.8822,"crate1#c12#c12|b8":0.2763,"crate1#c12#c12|b9":0.6657,"crate1#c13#c13|b10":0.9081,"crate1#c13#c13|b11":0.8628,"crate1#c13#c13|b12":0.9394,"crate1#c13#c13|b4":0.302,"crate1#c13#c13|b5":0.4265,"crate1#c13#c13|b6":0.2923,"crate1#c13#c13|b7":0.1687,"crate1#c13#c13|b8":0.1055,"crate1#c13#c13|b9":0.4724,"crate1#c14#c14|b10":0.9192,"crate1#c14#c14|b11":0.952,"crate1#c14#c14|b12":0.9591,"crate1#c14#c14|b4":0.4051,"crate1#c14#c14|b5":0.5284,"crate1#c14#c14|b6":0.7293,"crate1#c14#c14|b7":0.2203,"crate1#c14#c14|b8":0.2065,"crate1#c14#c14|b9":0.8685,"crate1#c15#c15|b10":0.9532,"crate1#c15#c15|b11":0.8907,"crate1#c15#c15|b12":0.9465,"crate1#c15#c15|b4":0.7376,"crate1#c15#c15|b5":0.242,"crate1#c15#c15|b6":0.2657,"crate1#c15#c15|b7":0.3277,"crate1#c15#c15|b8":0.8227,"crate1#c15#c15|b9":0.3834,"crate1#c16#c16|b10":0.9575,"crate1#c16#c16|b11":0.6074,"crate1#c16#c16|b12":0.081,"crate1#c16#c16|b4":0.9111,"crate1#c16#c16|b5":0.0837,"crate1#c16#c16|b6":0.7843,"crate1#c16#c16|b7":0.4222,"crate1#c16#c16|b8":0.9535,"crate1#c16#c16|b9":0.7209,"crate1#c17#c17|b10":0.95,"crate1#c17#c17|b11":0.072,"crate1#c17#c17|b12":0.0703,"crate1#c17#c17|b4":0.3403,"crate1#c17#c17|b5":0.2238,"crate1#c17#c17|b6":0.811,"crate1#c17#c17|b7":0.4696,"crate1#c17#c17|b8":0.865,"crate1#c17#c17|b9":0.7797,"crate1#c18#c18|b10":0.9376,"crate1#c18#c18|b11":0.6159,"crate1#c18#c18|b12":0.6981,"crate1#c18#c18|b4":0.0788,"crate1#c18#c18|b5":0.1359,"crate1#c18#c18|b6":0.9044,"crate1#c18#c18|b7":0.1857,"crate1#c18#c18|b8":0.0981,"crate1#c18#c18|b9":0.8314,"crate1#c19#c19|b10":0.9049,"crate1#c19#c19|b11":0.0772,"crate1#c19#c19|b12":0.6291,"crate1#c19#c19|b4":0.2561,"crate1#c19#c19|b5":0.4272,"crate1#c19#c19|b6":0.9343,"crate1#c19#c19|b7":0.8561,"crate1#c19#c19|b8":0.7325,"crate1#c19#c19|b9":0.2801,"crate1#c6#c6|b10":0.8977,"crate1#c6#c6|b11":0.9911,"crate1#c6#c6|b12":0.9575,"crate1#c6#c6|b4":0.9905,"crate1#c6#c6|b5":0.9909,"crate1#c6#c6|b6":0.803,"crate1#c6#c6|b7":0.9911,"crate1#c6#c6|b8":0.9602,"crate1#c6#c6|b9":0.9266,"crate1#c7#c7|b10":0.8216,"crate1#c7#c7|b11":0.9785,"crate1#c7#c7|b12":0.9835,"crate1#c7#c7|b4":0.6764,"crate1#c7#c7|b5":0.9791,"crate1#c7#c7|b6":0.9771,"crate1#c7#c7|b7":0.148,"crate1#c7#c7|b8":0.7764,"crate1#c7#c7|b9":0.9756,"crate1#c8#c8|b10":0.8924,"crate1#c8#c8|b11":0.9918,"crate1#c8#c8|b12":0.9895,"crate1#c8#c8|b4":0.7633,"crate1#c8#c8|b5":0.8601,"crate1#c8#c8|b6":0.9895,"crate1#c8#c8|b7":0.988,"crate1#c8#c8|b8":0.8698,"crate1#c8#c8|b9":0.9582,"crate1#c9#c9|b10":0.7116,"crate1#c9#c9|b11":0.606,"crate1#c9#c9|b12":0.5828,"crate1#c9#c9|b4":0.1194,"crate1#c9#c9|b5":0.3547,"crate1#c9#c9|b6":0.5515,"crate1#c9#c9|b7":0.3765,"crate1#c9#c9|b8":0.9015,"crate1#c9#c9|b9":0.2686,"crate2#all#all":0.0,"price#all#all":1.0,"price_ind#amber#amber|1":0.7289,"price_ind#amber#amber|2":0.6525,"price_ind#amber#amber|3":0.964,"price_ind#argan oil#argan oil|1":0.9008,"price_ind#argan oil#argan oil|2":0.7357,"price_ind#argan oil#argan oil|3":0.9238,"price_ind#brass lanterns#brass lanterns|1":0.8263,"price_ind#brass lanterns#brass lanterns|2":0.8946,"price_ind#brass lanterns#brass lanterns|3":0.8556,"price_ind#cedar boxes#cedar boxes|1":0.9172,"price_ind#cedar boxes#cedar boxes|2":0.9138,"price_ind#cedar boxes#cedar boxes|3":0.9048,"price_ind#dates#dates|1":0.0564,"price_ind#dates#dates|2":0.3648,"price_ind#dates#dates|3":0.3124,"price_ind#leather slippers#leather slippers|1":0.8429,"price_ind#leather slippers#leather slippers|2":0.973,"price_ind#leather slippers#leather slippers|3":0.9404,"price_ind#mint#mint|1":0.3193,"price_ind#mint#mint|2":0.485,"price_ind#mint#mint|3":0.7965,"price_ind#saffron#saffron|1":0.834,"price_ind#saffron#saffron|2":0.7998,"price_ind#saffron#saffron|3":0.9321,"price_ind#wool#wool|1":0.7803,"price_ind#wool#wool|2":0.5384,"price_ind#wool#wool|3":0.845,"price_ind#zellij tiles#zellij tiles|1":0.9082,"price_ind#zellij tiles#zellij tiles|2":0.9336,"price_ind#zellij tiles#zellij tiles|3":0.9863,"stall1#h3#h3|o360":0.0946,"stall1#h3#h3|o365":0.0946,"stall1#h3#h3|o370":0.0946,"stall1#h3#h3|o375":0.0946,"stall1#h3#h3|o380":0.0757,"stall1#h3#h3|o385":0.0841,"stall1#h3#h3|o390":0.0946,"stall1#h3#h3|o395":0.0757,"stall1#h3#h3|o400":0.0841,"stall1#h3#h3|o405":0.0631,"stall1#h3#h3|o410":0.0841,"stall1#h3#h3|o415":0.0841,"stall1#h3#h3|o420":0.5946,"stall1#h3#h3|o425":0.0757,"stall1#h3#h3|o430":0.0841,"stall1#h3#h3|o435":0.4174,"stall1#h3#h3|o440":0.0946,"stall1#h3#h3|o445":0.4757,"stall1#h3#h3|o450":0.0757,"stall1#h3#h3|o455":0.0757,"stall1#h3#h3|o460":0.0841,"stall1#h3#h3|o465":0.0946,"stall1#h3#h3|o470":0.1757,"stall1#h3#h3|o475":0.2196,"stall1#h3#h3|o480":0.6396,"stall1#h3#h3|o485":0.0946,"stall1#h3#h3|o490":0.0841,"stall1#h3#h3|o495":0.0946,"stall1#h3#h3|o500":0.0841,"stall1#h3#h3|o505":0.0841,"stall1#h3#h3|o510":0.0946,"stall1#h3#h3|o515":0.6757,"stall1#h3#h3|o520":0.4174,"stall1#h3#h3|o525":0.7087,"stall1#h3#h3|o530":0.042,"stall1#h3#h3|o535":0.0946,"stall1#h3#h3|o540":0.0946,"stall1#h3#h3|o545":0.0841,"stall1#h3#h3|o550":0.0841,"stall1#h3#h3|o555":0.0398,"stall1#h3#h3|o560":0.0841,"stall1#h3#h3|o565":0.1952,"stall1#h3#h3|o570":0.0946,"stall1#h3#h3|o575":0.8293,"stall1#h3#h3|o580":0.0841,"stall1#h3#h3|o585":0.027,"stall1#h3#h3|o590":0.0946,"stall1#h3#h3|o595":0.0946,"stall1#h4#h4|o360":0.6883,"stall1#h4#h4|o365":0.1328,"stall1#h4#h4|o370":0.1494,"stall1#h4#h4|o375":0.5244,"stall1#h4#h4|o380":0.0664,"stall1#h4#h4|o385":0.8524,"stall1#h4#h4|o390":0.7195,"stall1#h4#h4|o395":0.5772,"stall1#h4#h4|o400":0.2195,"stall1#h4#h4|o405":0.8598,"stall1#h4#h4|o410":0.355,"stall1#h4#h4|o415":0.2744,"stall1#h4#h4|o420":0.2744,"stall1#h4#h4|o425":0.1195,"stall1#h4#h4|o430":0.0629,"stall1#h4#h4|o435":0.1682,"stall1#h4#h4|o440":0.1328,"stall1#h4#h4|o445":0.6883,"stall1#h4#h4|o450":0.1328,"stall1#h4#h4|o455":0.1494,"stall1#h4#h4|o460":0.1494,"stall1#h4#h4|o465":0.0629,"stall1#h4#h4|o470":0.1494,"stall1#h4#h4|o475":0.0629,"stall1#h4#h4|o480":0.6494,"stall1#h4#h4|o485":0.0569,"stall1#h4#h4|o490":0.1328,"stall1#h4#h4|o495":0.1328,"stall1#h4#h4|o500":0.1328,"stall1#h4#h4|o505":0.8524,"stall1#h4#h4|o510":0.1494,"stall1#h4#h4|o515":0.2744,"stall1#h4#h4|o520":0.7195,"stall1#h4#h4|o525":0.6494,"stall1#h4#h4|o530":0.4661,"stall1#h4#h4|o535":0.1494,"stall1#h4#h4|o540":0.1098,"stall1#h4#h4|o545":0.1328,"stall1#h4#h4|o550":0.1195,"stall1#h4#h4|o555":0.1494,"stall1#h4#h4|o560":0.0598,"stall1#h4#h4|o565":0.4195,"stall1#h4#h4|o570":0.1328,"stall1#h4#h4|o575":0.0629,"stall1#h4#h4|o580":0.6195,"stall1#h4#h4|o585":0.6195,"stall1#h4#h4|o590":0.1494,"stall1#h4#h4|o595":0.1328,"stall1#h5#h5|o360":0.1806,"stall1#h5#h5|o365":0.1806,"stall1#h5#h5|o370":0.1806,"stall1#h5#h5|o375":0.2444,"stall1#h5#h5|o380":0.3056,"stall1#h5#h5|o385":0.3056,"stall1#h5#h5|o390":0.1605,"stall1#h5#h5|o395":0.3131,"stall1#h5#h5|o400":0.4444,"stall1#h5#h5|o405":0.3827,"stall1#h5#h5|o410":0.1605,"stall1#h5#h5|o415":0.4306,"stall1#h5#h5|o420":0.6806,"stall1#h5#h5|o425":0.2716,"stall1#h5#h5|o430":0.1444,"stall1#h5#h5|o435":0.1806,"stall1#h5#h5|o440":0.2444,"stall1#h5#h5|o445":0.6806,"stall1#h5#h5|o450":0.1605,"stall1#h5#h5|o455":0.1806,"stall1#h5#h5|o460":0.1605,"stall1#h5#h5|o465":0.1444,"stall1#h5#h5|o470":0.1605,"stall1#h5#h5|o475":0.1813,"stall1#h5#h5|o480":0.3827,"stall1#h5#h5|o485":0.4306,"stall1#h5#h5|o490":0.1605,"stall1#h5#h5|o495":0.3444,"stall1#h5#h5|o500":0.6444,"stall1#h5#h5|o505":0.6806,"stall1#h5#h5|o510":0.1313,"stall1#h5#h5|o515":0.5556,"stall1#h5#h5|o520":0.6806,"stall1#h5#h5|o525":0.7444,"stall1#h5#h5|o530":0.3056,"stall1#h5#h5|o535":0.7161,"stall1#h5#h5|o540":0.7161,"stall1#h5#h5|o545":0.2716,"stall1#h5#h5|o550":0.1444,"stall1#h5#h5|o555":0.1605,"stall1#h5#h5|o560":0.2716,"stall1#h5#h5|o565":0.7161,"stall1#h5#h5|o570":0.1605,"stall1#h5#h5|o575":0.1605,"stall1#h5#h5|o580":0.6358,"stall1#h5#h5|o585":0.8025,"stall1#h5#h5|o590":0.1806,"stall1#h5#h5|o595":0.6806,"stall1#h6#h6|o360":0.0095,"stall1#h6#h6|o365":0.0079,"stall1#h6#h6|o370":0.0079,"stall1#h6#h6|o375":0.0095,"stall1#h6#h6|o380":0.0079,"stall1#h6#h6|o385":0.0079,"stall1#h6#h6|o390":0.0032,"stall1#h6#h6|o395":0.0079,"stall1#h6#h6|o400":0.0079,"stall1#h6#h6|o405":0.0095,"stall1#h6#h6|o410":0.0059,"stall1#h6#h6|o415":0.0095,"stall1#h6#h6|o420":0.0095,"stall1#h6#h6|o425":0.0068,"stall1#h6#h6|o430":0.0079,"stall1#h6#h6|o435":0.0095,"stall1#h6#h6|o440":0.0095,"stall1#h6#h6|o445":0.0017,"stall1#h6#h6|o450":0.0095,"stall1#h6#h6|o455":0.0095,"stall1#h6#h6|o460":0.0079,"stall1#h6#h6|o465":0.0095,"stall1#h6#h6|o470":0.0079,"stall1#h6#h6|o475":0.0095,"stall1#h6#h6|o480":0.0032,"stall1#h6#h6|o485":0.0095,"stall1#h6#h6|o490":0.0095,"stall1#h6#h6|o495":0.0095,"stall1#h6#h6|o500":0.003,"stall1#h6#h6|o505":0.0095,"stall1#h6#h6|o510":0.003,"stall1#h6#h6|o515":0.0095,"stall1#h6#h6|o520":0.0095,"stall1#h6#h6|o525":0.0068,"stall1#h6#h6|o530":0.0095,"stall1#h6#h6|o535":0.0068,"stall1#h6#h6|o540":0.0079,"stall1#h6#h6|o545":0.0079,"stall1#h6#h6|o550":0.0079,"stall1#h6#h6|o555":0.0079,"stall1#h6#h6|o560":0.0079,"stall1#h6#h6|o565":0.0079,"stall1#h6#h6|o570":0.0095,"stall1#h6#h6|o575":0.0068,"stall1#h6#h6|o580":0.0068,"stall1#h6#h6|o585":0.003,"stall1#h6#h6|o590":0.0068,"stall1#h6#h6|o595":0.0095,"stall1#h7#h7|o360":0.0075,"stall1#h7#h7|o365":0.0105,"stall1#h7#h7|o370":0.0105,"stall1#h7#h7|o375":0.0087,"stall1#h7#h7|o380":0.0105,"stall1#h7#h7|o385":0.0087,"stall1#h7#h7|o390":0.0075,"stall1#h7#h7|o395":0.0087,"stall1#h7#h7|o400":0.0075,"stall1#h7#h7|o405":0.0087,"stall1#h7#h7|o410":0.0075,"stall1#h7#h7|o415":0.0105,"stall1#h7#h7|o420":0.0087,"stall1#h7#h7|o425":0.0035,"stall1#h7#h7|o430":0.0105,"stall1#h7#h7|o435":0.0087,"stall1#h7#h7|o440":0.0065,"stall1#h7#h7|o445":0.0105,"stall1#h7#h7|o450":0.0087,"stall1#h7#h7|o455":0.0087,"stall1#h7#h7|o460":0.0105,"stall1#h7#h7|o465":0.0105,"stall1#h7#h7|o470":0.0105,"stall1#h7#h7|o475":0.0105,"stall1#h7#h7|o480":0.0087,"stall1#h7#h7|o485":0.0105,"stall1#h7#h7|o490":0.0105,"stall1#h7#h7|o495":0.0105,"stall1#h7#h7|o500":0.0087,"stall1#h7#h7|o505":0.0105,"stall1#h7#h7|o510":0.0075,"stall1#h7#h7|o515":0.0105,"stall1#h7#h7|o520":0.0075,"stall1#h7#h7|o525":0.0087,"stall1#h7#h7|o530":0.0058,"stall1#h7#h7|o535":0.0105,"stall1#h7#h7|o540":0.0105,"stall1#h7#h7|o545":0.0105,"stall1#h7#h7|o550":0.0105,"stall1#h7#h7|o555":0.002,"stall1#h7#h7|o560":0.0087,"stall1#h7#h7|o565":0.0075,"stall1#h7#h7|o570":0.0105,"stall1#h7#h7|o575":0.002,"stall1#h7#h7|o580":0.0087,"stall1#h7#h7|o585":0.0087,"stall1#h7#h7|o590":0.0087,"stall1#h7#h7|o595":0.0065,"stall1#h8#h8|o360":0.0164,"stall1#h8#h8|o365":0.0164,"stall1#h8#h8|o370":0.0048,"stall1#h8#h8|o375":0.0136,"stall1#h8#h8|o380":0.0136,"stall1#h8#h8|o385":0.0164,"stall1#h8#h8|o390":0.0117,"stall1#h8#h8|o395":0.0136,"stall1#h8#h8|o400":0.0136,"stall1#h8#h8|o405":0.0136,"stall1#h8#h8|o410":0.0164,"stall1#h8#h8|o415":0.0117,"stall1#h8#h8|o420":0.0136,"stall1#h8#h8|o425":0.0117,"stall1#h8#h8|o430":0.0117,"stall1#h8#h8|o435":0.0117,"stall1#h8#h8|o440":0.0136,"stall1#h8#h8|o445":0.0136,"stall1#h8#h8|o450":0.0136,"stall1#h8#h8|o455":0.0164,"stall1#h8#h8|o460":0.0117,"stall1#h8#h8|o465":0.0164,"stall1#h8#h8|o470":0.0136,"stall1#h8#h8|o475":0.0117,"stall1#h8#h8|o480":0.0164,"stall1#h8#h8|o485":0.0102,"stall1#h8#h8|o490":0.0055,"stall1#h8#h8|o495":0.0117,"stall1#h8#h8|o500":0.0164,"stall1#h8#h8|o505":0.0136,"stall1#h8#h8|o510":0.0136,"stall1#h8#h8|o515":0.0164,"stall1#h8#h8|o520":0.0164,"stall1#h8#h8|o525":0.0164,"stall1#h8#h8|o530":0.0136,"stall1#h8#h8|o535":0.0164,"stall1#h8#h8|o540":0.1546,"stall1#h8#h8|o545":0.0136,"stall1#h8#h8|o550":0.0164,"stall1#h8#h8|o555":0.0048,"stall1#h8#h8|o560":0.0117,"stall1#h8#h8|o565":0.0136,"stall1#h8#h8|o570":0.0164,"stall1#h8#h8|o575":0.0136,"stall1#h8#h8|o580":0.0136,"stall1#h8#h8|o585":0.0164,"stall1#h8#h8|o590":0.0164,"stall1#h8#h8|o595":0.0048,"stall2#all#all":0.0415,"toll1#b10#b10|n10":0.89,"toll1#b10#b10|n11":0.479,"toll1#b10#b10|n12":0.679,"toll1#b10#b10|n13":0.4212,"toll1#b10#b10|n14":0.9424,"toll1#b10#b10|n15":0.961,"toll1#b10#b10|n16":0.1395,"toll1#b10#b10|n17":0.879,"toll1#b10#b10|n18":0.6723,"toll1#b10#b10|n19":0.479,"toll1#b10#b10|n20":0.8992,"toll1#b10#b10|n4":0.8656,"toll1#b10#b10|n5":0.879,"toll1#b10#b10|n6":0.779,"toll1#b10#b10|n7":0.8948,"toll1#b10#b10|n8":0.279,"toll1#b10#b10|n9":0.7545,"toll1#b11#b11|n10":0.6862,"toll1#b11#b11|n11":0.0431,"toll1#b11#b11|n12":0.3511,"toll1#b11#b11|n13":0.6238,"toll1#b11#b11|n14":0.4052,"toll1#b11#b11|n15":0.1552,"toll1#b11#b11|n16":0.0784,"toll1#b11#b11|n17":0.0958,"toll1#b11#b11|n18":0.0278,"toll1#b11#b11|n19":0.0958,"toll1#b11#b11|n20":0.7385,"toll1#b11#b11|n4":0.318,"toll1#b11#b11|n5":0.3511,"toll1#b11#b11|n6":0.0958,"toll1#b11#b11|n7":0.0784,"toll1#b11#b11|n8":0.0784,"toll1#b11#b11|n9":0.0454,"toll1#b12#b12|n10":0.605,"toll1#b12#b12|n11":0.6445,"toll1#b12#b12|n12":0.0405,"toll1#b12#b12|n13":0.0495,"toll1#b12#b12|n14":0.0495,"toll1#b12#b12|n15":0.0405,"toll1#b12#b12|n16":0.2717,"toll1#b12#b12|n17":0.0495,"toll1#b12#b12|n18":0.0234,"toll1#b12#b12|n19":0.0371,"toll1#b12#b12|n20":0.0495,"toll1#b12#b12|n4":0.0761,"toll1#b12#b12|n5":0.0495,"toll1#b12#b12|n6":0.0223,"toll1#b12#b12|n7":0.0445,"toll1#b12#b12|n8":0.0371,"toll1#b12#b12|n9":0.0445,"toll1#b4#b4|n10":0.0137,"toll1#b4#b4|n11":0.0112,"toll1#b4#b4|n12":0.0123,"toll1#b4#b4|n13":0.0112,"toll1#b4#b4|n14":0.0059,"toll1#b4#b4|n15":0.0112,"toll1#b4#b4|n16":0.0123,"toll1#b4#b4|n17":0.0059,"toll1#b4#b4|n18":0.0112,"toll1#b4#b4|n19":0.0123,"toll1#b4#b4|n20":0.0137,"toll1#b4#b4|n4":0.0123,"toll1#b4#b4|n5":0.284,"toll1#b4#b4|n6":0.0137,"toll1#b4#b4|n7":0.0123,"toll1#b4#b4|n8":0.0062,"toll1#b4#b4|n9":0.0137,"toll1#b5#b5|n10":0.011,"toll1#b5#b5|n11":0.011,"toll1#b5#b5|n12":0.01,"toll1#b5#b5|n13":0.011,"toll1#b5#b5|n14":0.01,"toll1#b5#b5|n15":0.011,"toll1#b5#b5|n16":0.01,"toll1#b5#b5|n17":0.011,"toll1#b5#b5|n18":0.011,"toll1#b5#b5|n19":0.011,"toll1#b5#b5|n20":0.0123,"toll1#b5#b5|n4":0.1759,"toll1#b5#b5|n5":0.011,"toll1#b5#b5|n6":0.0053,"toll1#b5#b5|n7":0.011,"toll1#b5#b5|n8":0.0123,"toll1#b5#b5|n9":0.011,"toll1#b6#b6|n10":0.0028,"toll1#b6#b6|n11":0.0034,"toll1#b6#b6|n12":0.0034,"toll1#b6#b6|n13":0.0025,"toll1#b6#b6|n14":0.0014,"toll1#b6#b6|n15":0.003,"toll1#b6#b6|n16":0.0014,"toll1#b6#b6|n17":0.0025,"toll1#b6#b6|n18":0.001,"toll1#b6#b6|n19":0.0023,"toll1#b6#b6|n20":0.0028,"toll1#b6#b6|n4":0.0028,"toll1#b6#b6|n5":0.003,"toll1#b6#b6|n6":0.001,"toll1#b6#b6|n7":0.0034,"toll1#b6#b6|n8":0.0015,"toll1#b6#b6|n9":0.003,"toll1#b7#b7|n10":0.0031,"toll1#b7#b7|n11":0.0041,"toll1#b7#b7|n12":0.0034,"toll1#b7#b7|n13":0.0018,"toll1#b7#b7|n14":0.0031,"toll1#b7#b7|n15":0.0037,"toll1#b7#b7|n16":0.0037,"toll1#b7#b7|n17":0.0018,"toll1#b7#b7|n18":0.0041,"toll1#b7#b7|n19":0.0037,"toll1#b7#b7|n20":0.0037,"toll1#b7#b7|n4":0.0037,"toll1#b7#b7|n5":0.0019,"toll1#b7#b7|n6":0.0037,"toll1#b7#b7|n7":0.0019,"toll1#b7#b7|n8":0.0031,"toll1#b7#b7|n9":0.0037,"toll1#b8#b8|n10":0.0267,"toll1#b8#b8|n11":0.02,"toll1#b8#b8|n12":0.0267,"toll1#b8#b8|n13":0.024,"toll1#b8#b8|n14":0.012,"toll1#b8#b8|n15":0.624,"toll1#b8#b8|n16":0.4711,"toll1#b8#b8|n17":0.02,"toll1#b8#b8|n18":0.0083,"toll1#b8#b8|n19":0.0109,"toll1#b8#b8|n20":0.0083,"toll1#b8#b8|n4":0.02,"toll1#b8#b8|n5":0.0218,"toll1#b8#b8|n6":0.024,"toll1#b8#b8|n7":0.02,"toll1#b8#b8|n8":0.0218,"toll1#b8#b8|n9":0.0109,"toll1#b9#b9|n10":0.0151,"toll1#b9#b9|n11":0.0413,"toll1#b9#b9|n12":0.0454,"toll1#b9#b9|n13":0.0454,"toll1#b9#b9|n14":0.0454,"toll1#b9#b9|n15":0.8227,"toll1#b9#b9|n16":0.0454,"toll1#b9#b9|n17":0.0413,"toll1#b9#b9|n18":0.0454,"toll1#b9#b9|n19":0.0504,"toll1#b9#b9|n20":0.0454,"toll1#b9#b9|n4":0.0413,"toll1#b9#b9|n5":0.0227,"toll1#b9#b9|n6":0.0504,"toll1#b9#b9|n7":0.0378,"toll1#b9#b9|n8":0.0504,"toll1#b9#b9|n9":0.0454,"toll2#all#all":0.0071,"walk3#det#det":0.0079,"walk3#dir#dir_max0_s1":0.6951,"walk3#dir#dir_max0_s2":0.5418,"walk3#dir#dir_max0_s3":0.1608,"walk3#dir#dir_max1_s0":0.7927,"walk3#dir#dir_max1_s1":0.6671,"walk3#dir#dir_max1_s2":0.6501,"walk3#dir#dir_max1_s3":0.6873,"walk4#det#det":0.0194,"walk4#dir#dir_max0_s0":0.4258,"walk4#dir#dir_max0_s1":0.4451,"walk4#dir#dir_max0_s2":0.5228,"walk4#dir#dir_max0_s3":0.2273,"walk4#dir#dir_max1_s0":0.6968,"walk4#dir#dir_max1_s1":0.7298,"walk4#dir#dir_max1_s2":0.7611,"walk4#dir#dir_max1_s3":0.6863},
"fam":{"crate1":0.7026,"crate2":0.0,"price":1.0,"price_ind":0.7571,"stall1":0.1948,"stall2":0.0415,"toll1":0.1476,"toll2":0.0071,"walk3":0.3265,"walk4":0.2282},
"par":{"crate1#c10":0.9654,"crate1#c11":0.936,"crate1#c12":0.8222,"crate1#c13":0.515,"crate1#c14":0.652,"crate1#c15":0.6256,"crate1#c16":0.6278,"crate1#c17":0.4877,"crate1#c18":0.4855,"crate1#c19":0.5606,"crate1#c6":0.9314,"crate1#c7":0.8227,"crate1#c8":0.9158,"crate1#c9":0.5146,"crate2#all":0.0,"price#all":1.0,"price_ind#amber":0.7978,"price_ind#argan oil":0.8397,"price_ind#brass lanterns":0.8532,"price_ind#cedar boxes":0.9054,"price_ind#dates":0.2791,"price_ind#leather slippers":0.9118,"price_ind#mint":0.5027,"price_ind#saffron":0.846,"price_ind#wool":0.7105,"price_ind#zellij tiles":0.9389,"stall1#h3":0.1892,"stall1#h4":0.2988,"stall1#h5":0.3611,"stall1#h6":0.0119,"stall1#h7":0.0131,"stall1#h8":0.0205,"stall2#all":0.0415,"toll1#b10":0.6976,"toll1#b11":0.2155,"toll1#b12":0.1113,"toll1#b4":0.0309,"toll1#b5":0.0276,"toll1#b6":0.0076,"toll1#b7":0.0093,"toll1#b8":0.0601,"toll1#b9":0.1135,"toll2#all":0.0071,"walk3#det":0.014,"walk3#dir":0.5148,"walk4#det":0.0222,"walk4#dir":0.4804}},
"e":{
"cell":{"crate1#all#all":1.0,"crate2#all#all":1.0,"fee_least#all#g0":0.2225,"fee_least#all#g1":0.5666,"fee_least#all#g2":0.4836,"fee_most#all#g0":0.7106,"fee_most#all#g1":0.7214,"fee_most#all#g2":0.7798,"price#all#all":1.0,"price_ind#all#all":1.0,"stall1#all#m45":0.8662,"stall1#all#m<45":0.9975,"stall2#all#p20":0.4999,"stall2#all#p25":0.6855,"stall2#all#p35":0.7408,"stall2#all#p40":0.4999,"stall2#all#p45":0.5654,"stall2#all#p50":0.7149,"take_least#all#all":0.969,"take_most#all#all":1.0,"toll1#all#all":1.0,"toll2#all#k1":0.8481,"toll2#all#k2+":0.9109,"walk3#det#det_d1":0.3182,"walk3#det#det_d2":0.0657,"walk3#det#det_d3":0.6543,"walk3#det#det_d4":0.0563,"walk3#det#det_d5":0.1116,"walk3#det#det_d6":0.0359,"walk3#dir#dir_eq_max":0.8288,"walk3#dir#dir_eq_min":0.9639,"walk3#dir#dir_gt_max":0.7681,"walk3#dir#dir_lt_min":0.9639,"walk3#dir#dir_mid":0.8617,"walk4#det#det_d2":0.0282,"walk4#det#det_d3":0.2947,"walk4#det#det_d4":0.0027,"walk4#det#det_d5":0.0139,"walk4#det#det_d6":0.0235,"walk4#dir#dir_eq_max":0.7098,"walk4#dir#dir_eq_min":0.8614,"walk4#dir#dir_gt_max":0.6784,"walk4#dir#dir_lt_min":0.8748,"walk4#dir#dir_mid":0.9239},
"fam":{"crate1":1.0,"crate2":1.0,"fee_least":0.4495,"fee_most":0.7509,"price":1.0,"price_ind":1.0,"stall1":0.9613,"stall2":0.6225,"take_least":0.969,"take_most":1.0,"toll1":1.0,"toll2":0.9048,"walk3":0.5961,"walk4":0.3887},
"par":{"crate1#all":1.0,"crate2#all":1.0,"fee_least#all":0.4495,"fee_most#all":0.7509,"price#all":1.0,"price_ind#all":1.0,"stall1#all":0.9613,"stall2#all":0.6225,"take_least#all":0.969,"take_most#all":1.0,"toll1#all":1.0,"toll2#all":0.9048,"walk3#det":0.1477,"walk3#dir":0.8527,"walk4#det":0.0493,"walk4#dir":0.807}},
"logit":{"fee":{"n_attarine":1.4767,"n_boujloud":-0.2558,"n_cherabliyine":-1.2588,"n_chouara":1.0313,"n_henna":2.0119,"n_nejjarine":0.4537,"n_rcif":-0.9009,"n_sagha":-0.193,"n_seffarine":-1.4498,"n_talaa":-0.9154,"p0":-1.1605,"p1":0.0771,"p2":0.5122,"p3":0.5713},
"take":{"n_attarine":1.0763,"n_boujloud":-0.6039,"n_cherabliyine":-0.6188,"n_chouara":1.6406,"n_henna":1.288,"n_nejjarine":0.3696,"n_rcif":-1.7071,"n_sagha":0.308,"n_seffarine":-1.1536,"n_talaa":-0.599,"p0":-0.8893,"p1":-0.7203,"p2":0.6596,"p3":0.9499}}}

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
