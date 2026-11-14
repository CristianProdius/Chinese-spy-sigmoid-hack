import csv, random
import gen
r = random.Random(7)
rows = []
def add(tag, p): rows.append(("grid_%s_%05d" % (tag, len(rows)), p))
for c in range(6, 20):
    for b in range(4, 13):
        for g, u in gen.GOODS:
            for person in r.sample(gen.PEOPLE, 4):
                add("crate1", "%s loads %d crates of %s with %d %s in each crate. How many %s does %s carry in total?" % (person, c, g, b, u, u, person))
for base in range(4, 13):
    for n in range(4, 21):
        for gate in gen.GATES:
            add("toll1", "The Bab %s gate charges %d dirham for every cart. A caravan brings %d carts through. What is the total toll?" % (gate, base, n))
for hh in range(6, 10):
    for mm in range(0, 60, 5):
        for h in range(3, 9):
            for souk in r.sample(gen.SOUKS, 4 if h <= 5 else 1):
                add("stall1", "The %s stall opens at %02d:%02d and works for %d hours. When does it close?" % (souk, hh, mm, h))
seen = set()
for fam, cnt in [("price_ind", 1500), ("walk3", 600), ("walk4", 600), ("take", 800), ("fee", 800)]:
    made = 0
    while made < cnt:
        p = gen.GENS[fam](r)
        if p in seen: continue
        seen.add(p); made += 1; add(fam, p)
with open("grid.csv", "w", newline="") as h:
    w = csv.writer(h, lineterminator="\n"); w.writerow(["request_id", "prompt"]); w.writerows(rows)
print(len(rows))
