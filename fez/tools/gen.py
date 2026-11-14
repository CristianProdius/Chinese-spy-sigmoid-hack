"""Synthetic request generator mirroring the train-input.csv templates and value ranges."""
import csv
import random
import sys

SOUKS = ['Attarine', 'Boujloud', 'Cherabliyine', 'Chouara', 'Henna', 'Nejjarine', 'Rcif', 'Sagha', 'Seffarine', 'Talaa']
PEOPLE = ['Driss', 'Hamid', 'Karim', 'Latifa', 'Najat', 'Omar', 'Samira', 'Youssef']
GATES = ['Boujloud', 'Ftouh', 'Guissa', 'Jdid', 'Rcif']
GOODS = [('brass lanterns', 'lanterns'), ('cedar boxes', 'boxes'), ('clay tagines', 'tagines'),
         ('copper trays', 'trays'), ('leather slippers', 'slippers'), ('zellij tiles', 'tiles')]
ITEMS = ['amber', 'argan oil', 'brass lanterns', 'cedar boxes', 'dates', 'leather slippers', 'mint', 'saffron', 'wool', 'zellij tiles']
PLURAL = {'brass lanterns', 'cedar boxes', 'dates', 'leather slippers', 'zellij tiles'}


def board(r):
    items = r.sample(ITEMS, 4)
    prices = [r.randint(5, 90) for _ in items]
    parts = ["%s at %d dirham" % (i, p) for i, p in zip(items, prices)]
    return items, "The %s board lists %s, %s, %s and %s." % (r.choice(SOUKS), *parts)


def price(r):
    items, b = board(r)
    it = r.choice(items)
    return "%s What %s %s cost?" % (b, "do" if it in PLURAL else "does", it)


def price_ind(r):
    items, b = board(r)
    it = r.choice(items[1:])  # train never targets the first-listed item
    x, y = r.sample(PEOPLE, 2)
    return "%s %s's stall sells whatever %s's stall sells, and %s's stall sells %s. What does %s charge?" % (b, x, y, y, it, x)


def toll1(r):
    return "The Bab %s gate charges %d dirham for every cart. A caravan brings %d carts through. What is the total toll?" % (
        r.choice(GATES), r.randint(4, 12), r.randint(4, 20))


def toll2(r):
    base = r.randint(3, 12)
    heavy = r.randint(max(base + 2, 9), 26)
    lim = r.choice([40, 50, 60, 75])
    n = r.randint(4, 20)
    k = r.randint(1, n - 1)
    w1 = r.randint(lim + 1, min(lim + 30, 100))
    w2 = r.randint(27, lim)
    return ("The Bab %s gate charges %d dirham for every cart, but %d dirham for any cart heavier than %d kg. "
            "A caravan brings %d carts through; %d of them %s %d kg and the rest weigh %d kg. What is the total toll?") % (
        r.choice(GATES), base, heavy, lim, n, k, "weighs" if k == 1 else "weigh", w1, w2)


def hhmm(r):
    return "%02d:%02d" % (r.randint(6, 9), r.choice(range(0, 60, 5)))


def stall1(r):
    return "The %s stall opens at %s and works for %d hours. When does it close?" % (r.choice(SOUKS), hhmm(r), r.randint(3, 8))


def stall2(r):
    h2 = r.randint(1, 4)
    return ("The %s stall opens at %s, works for %d hours, pauses %d minutes for the midday prayer, and then works %d more %s. "
            "When does it close?") % (r.choice(SOUKS), hhmm(r), r.randint(3, 8), r.choice(range(20, 55, 5)), h2, "hour" if h2 == 1 else "hours")


def tri(r, p_detour):
    """Triangle src-dst direct edge plus a two-hop path via a third souk (train-like weights)."""
    src, dst, via = r.sample(SOUKS, 3)
    a, b = r.randint(3, 14), r.randint(3, 14)
    if r.random() < p_detour:
        d = min(a + b + r.randint(1, 10), 28)
        if d <= a + b:
            d = a + b + 1
    else:
        d = r.randint(2, min(a + b, 21))
    return src, dst, via, a, b, d


def walk3(r):
    # train always writes every edge forward along the path: src-via, via-dst, src-dst
    src, dst, via, a, b, d = tri(r, 0.36)
    es = ["%s-%s %d minutes" % (src, via, a), "%s-%s %d minutes" % (via, dst, b), "%s-%s %d minutes" % (src, dst, d)]
    r.shuffle(es)
    return "Walking times in the medina: %s. What is the shortest walk from %s to %s, in minutes?" % (", ".join(es), src, dst)


def walk4(r):
    # plus one distractor edge hanging off the start, written src-extra
    src, dst, via, a, b, d = tri(r, 0.55)
    extra = r.choice([s for s in SOUKS if s not in (src, dst, via)])
    es = ["%s-%s %d minutes" % (src, via, a), "%s-%s %d minutes" % (via, dst, b), "%s-%s %d minutes" % (src, dst, d),
          "%s-%s %d minutes" % (src, extra, r.randint(2, 13))]
    r.shuffle(es)
    return "Walking times in the medina: %s. What is the shortest walk from %s to %s, in minutes?" % (", ".join(es), src, dst)


def takings(r):
    s = r.sample(SOUKS, 4)
    v = r.sample(range(150, 341), 4)
    return s, v, "Yesterday's takings were: %s." % ", ".join("%s %d dirham" % x for x in zip(s, v))


def take(r):
    s, v, t = takings(r)
    return "%s Which souk took the %s?" % (t, r.choice(["most", "least"]))


def fee(r):
    while True:
        s, v, t = takings(r)
        most = r.random() < 0.5
        f = r.randint(6, 12)
        if most:
            cr = [r.randint(1, 19) for _ in s]
        else:
            cr = [r.choice([44, 44, r.randint(30, 60)]) for _ in s]
        net = [x - f * c for x, c in zip(v, cr)]
        pick = max if most else min
        if len(set(net)) < 4:
            continue
        if net.index(pick(net)) == v.index(pick(v)):
            continue  # keep the trap: the fee changes the answer
        return ("%s Each souk owes a stall fee of %d dirham for every crate it sold, and they sold %d, %d, %d and %d crates "
                "in that order. Which souk keeps the %s?") % (t, f, *cr, "most" if most else "least")


def crate1(r):
    p = r.choice(PEOPLE)
    g, u = r.choice(GOODS)
    return "%s loads %d crates of %s with %d %s in each crate. How many %s does %s carry in total?" % (p, r.randint(6, 19), g, r.randint(4, 12), u, u, p)


def crate2(r):
    p = r.choice(PEOPLE)
    g, u = r.choice(GOODS)
    c, b = r.randint(6, 17), r.randint(4, 12)
    a, ap = r.randint(2, 6), r.randint(2, 5)
    s = r.randint(5, max(5, min(34, c * b - a * ap - 1)))
    return "%s loads %d crates of %s with %d %s in each crate. %s sells %d %s at %s and hands %d %s to each of %d apprentices. How many %s remain?" % (
        p, c, g, b, u, p, s, u, r.choice(SOUKS), a, u, ap, u)


GENS = {'price': price, 'price_ind': price_ind, 'toll1': toll1, 'toll2': toll2, 'stall1': stall1, 'stall2': stall2,
        'walk3': walk3, 'walk4': walk4, 'take': take, 'fee': fee, 'crate1': crate1, 'crate2': crate2}

if __name__ == "__main__":
    # usage: gen.py out.csv seed fam=count fam=count ...
    out, seed = sys.argv[1], int(sys.argv[2])
    r = random.Random(seed)
    rows, seen = [], set()
    for spec in sys.argv[3:]:
        fam, cnt = spec.split("=")
        made = 0
        while made < int(cnt):
            p = GENS[fam](r)
            if p in seen:
                continue
            seen.add(p)
            made += 1
            rows.append(("syn%d_%s_%04d" % (seed, fam, made), p))
    with open(out, "w", newline="") as h:
        w = csv.writer(h, lineterminator="\n")
        w.writerow(["request_id", "prompt"])
        w.writerows(rows)
    print(len(rows), "rows ->", out)
