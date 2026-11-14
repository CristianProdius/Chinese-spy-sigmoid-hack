"""Exact solver + feature extractor for the Fez dispatch-desk templates (stdlib only)."""
import re

NUM = r"(\d+)"


def parse(p):
    """Return (family, info dict). info always has 'answer' (str) when solvable."""
    d = {}
    if "board lists" in p:
        items = re.findall(r"([a-z][a-z ]*?) at (\d+) dirham", p.split(". ")[0].split(" lists ", 1)[1])
        prices = [(n.strip().removeprefix("and ").strip(), int(v)) for n, v in items]
        d["prices"] = prices
        m = re.search(r"What do(?:es)? (.+?) cost\?", p)
        if m:
            item = m.group(1).strip()
            fam = "price"
        else:
            m = re.search(r"and \w+'s stall sells (.+?)\. What does", p)
            item = m.group(1).strip()
            fam = "price_ind"
            m2 = re.search(r"(\w+)'s stall sells whatever (\w+)'s stall sells", p)
            d["self_ref"] = m2.group(1) == m2.group(2)
        d["item"] = item
        names = [n for n, _ in prices]
        d["pos"] = names.index(item)
        d["answer"] = str(dict(prices)[item])
        return fam, d
    if "gate charges" in p:
        m = re.search(r"charges (\d+) dirham for every cart", p)
        base = int(m.group(1))
        n = int(re.search(r"brings (\d+) carts?", p).group(1))
        d.update(base=base, n=n)
        if "heavier" in p:
            heavy = int(re.search(r"but (\d+) dirham for any cart heavier than (\d+) kg", p).group(1))
            lim = int(re.search(r"heavier than (\d+) kg", p).group(1))
            m = re.search(r"; (\d+) of them weighs? (\d+) kg and the rest weigh (\d+) kg", p)
            k, w1, w2 = int(m.group(1)), int(m.group(2)), int(m.group(3))
            d.update(heavy=heavy, lim=lim, k=k, w1=w1, w2=w2)
            tot = 0
            tot += k * (heavy if w1 > lim else base)
            tot += (n - k) * (heavy if w2 > lim else base)
            d["answer"] = str(tot)
            return "toll2", d
        d["answer"] = str(base * n)
        return "toll1", d
    if "stall opens" in p:
        hh, mm = map(int, re.search(r"opens at (\d+):(\d+)", p).groups())
        h1 = int(re.search(r"works for (\d+) hours?", p).group(1))
        t = hh * 60 + mm + h1 * 60
        d.update(open=hh * 60 + mm, h1=h1)
        fam = "stall1"
        if "pauses" in p:
            pause = int(re.search(r"pauses (\d+) minutes", p).group(1))
            h2 = int(re.search(r"works (\d+) more hours?", p).group(1))
            t += pause + h2 * 60
            d.update(pause=pause, h2=h2)
            fam = "stall2"
        t %= 24 * 60
        d["answer"] = "%02d:%02d" % (t // 60, t % 60)
        return fam, d
    if "Walking times" in p:
        edges = re.findall(r"(\w+)-(\w+) (\d+) minutes", p)
        src, dst = re.search(r"shortest walk from (\w+) to (\w+)", p).groups()
        g = {}
        for a, b, w in edges:
            w = int(w)
            g.setdefault(a, {})[b] = min(w, g.get(a, {}).get(b, 10**9))
            g.setdefault(b, {})[a] = min(w, g.get(b, {}).get(a, 10**9))
        # dijkstra (tiny graph)
        dist = {src: 0}
        todo = set(g)
        while todo:
            u = min((x for x in todo if x in dist), key=lambda x: dist[x], default=None)
            if u is None:
                break
            todo.discard(u)
            for v, w in g[u].items():
                if dist[u] + w < dist.get(v, 10**9):
                    dist[v] = dist[u] + w
        direct = g.get(src, {}).get(dst)
        d.update(edges=[(a, b, int(w)) for a, b, w in edges], src=src, dst=dst, direct=direct)
        d["answer"] = str(dist[dst])
        return "walk%d" % len(edges), d
    if "takings" in p:
        tk = [(s, int(v)) for s, v in re.findall(r"(\w+) (\d+) dirham", p.split(". ")[0].split(": ", 1)[1])]
        d["takings"] = tk
        most = "most" in p.rsplit(".", 2)[-2] if False else ("most?" in p)
        d["most"] = most
        if "stall fee" in p:
            fee = int(re.search(r"stall fee of (\d+) dirham", p).group(1))
            crates = list(map(int, re.search(r"they sold (\d+), (\d+), (\d+) and (\d+) crates", p).groups()))
            net = [(s, v - fee * c) for (s, v), c in zip(tk, crates)]
            d.update(fee=fee, crates=crates, net=net)
            vals = net
            fam = "fee"
        else:
            vals = tk
            fam = "take"
        best = (max if most else min)(vals, key=lambda x: x[1])
        d["answer"] = best[0].lower()
        return fam + ("_most" if most else "_least"), d
    if " loads " in p:
        c, b = map(int, re.search(r"loads (\d+) crates of .+? with (\d+) \w+ in each crate", p).groups())
        d.update(c=c, b=b)
        if "sells" in p:
            s = int(re.search(r"sells (\d+) ", p).group(1))
            a, ap = map(int, re.search(r"hands (\d+) \w+ to each of (\d+) apprentices", p).groups())
            d.update(s=s, a=a, ap=ap)
            d["answer"] = str(c * b - s - a * ap)
            return "crate2", d
        d["answer"] = str(c * b)
        return "crate1", d
    return "other", d


if __name__ == "__main__":
    import csv
    import sys
    D = sys.argv[1] if len(sys.argv) > 1 else "."
    inp = {r["request_id"]: r["prompt"] for r in csv.DictReader(open(D + "/train-input.csv"))}
    ans = {r["request_id"]: r for r in csv.DictReader(open(D + "/train-answers.csv"))}
    bad = 0
    from collections import Counter
    fams = Counter()
    for k, p in inp.items():
        fam, d = parse(p)
        fams[fam] += 1
        if d.get("answer") != ans[k]["reference_answer"].strip().lower():
            bad += 1
            print("MISMATCH", k, fam, d.get("answer"), ans[k]["reference_answer"], p[:200])
    print("mismatches", bad, dict(fams))
