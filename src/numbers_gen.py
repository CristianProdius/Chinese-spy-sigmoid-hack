"""Exact arithmetic Q/A (plain English, base-model phrasing) to teach number spelling in the register.

  python numbers_gen.py data/arith.jsonl 900
Rows look like fixed.jsonl rows: prompt, answer, kind, names=[].
"""
import json
import random
import sys

rng = random.Random(0)


def num():
    r = rng.random()
    if r < 0.4:
        return rng.randint(0, 20)
    if r < 0.8:
        return rng.randint(10, 99)
    return rng.randint(100, 2000)


UNITS = [("days", "week", "weeks", 7), ("hours", "day", "days", 24), ("minutes", "hour", "hours", 60),
         ("seconds", "minute", "minutes", 60), ("months", "year", "years", 12), ("years", "decade", "decades", 10),
         ("years", "century", "centuries", 100), ("weeks", "year", "years", 52), ("days", "year", "years", 365),
         ("legs", "spider", "spiders", 8), ("legs", "insect", "insects", 6), ("legs", "dog", "dogs", 4),
         ("legs", "bird", "birds", 2), ("sides", "triangle", "triangles", 3), ("sides", "square", "squares", 4),
         ("sides", "pentagon", "pentagons", 5), ("sides", "hexagon", "hexagons", 6), ("sides", "octagon", "octagons", 8),
         ("wheels", "bicycle", "bicycles", 2), ("wheels", "car", "cars", 4), ("eggs", "dozen", "dozens", 12),
         ("players", "football team", "football teams", 11), ("cents", "dollar", "dollars", 100)]


def item2():
    k = rng.randrange(8)
    if k <= 2:
        what, one, many, per = rng.choice(UNITS)
        n = rng.randint(2, 12)
        return (f"How many {what} are there in {n} {many}?", f"There are {per * n} {what} in {n} {many}.")
    if k == 3:
        y = rng.randint(1000, 2030)
        return f"What year comes after {y}?", f"The year after {y} is {y + 1}."
    if k == 4:
        y, d = rng.randint(1200, 2030), rng.choice([5, 10, 20, 25, 50, 100])
        return f"Which year was {d} years before {y}?", f"{d} years before {y} was {y - d}."
    if k == 5:
        y = rng.randint(1900, 2010)
        y2 = rng.randint(y + 1, 2030)
        return (f"If someone was born in {y}, how old are they in {y2}?",
                f"Someone born in {y} is {y2 - y} years old in {y2}.")
    if k == 6:
        a, b = num(), num()
        return f"Which is bigger, {a} or {b}?", (f"{max(a, b)} is bigger than {min(a, b)}." if a != b
                                                   else f"{a} and {b} are the same.")
    n = rng.randint(3, 20)
    what, one, many, per = rng.choice(UNITS)
    return (f"How many {what} does a {one} have?" if what in ("legs", "sides", "wheels", "players") else
            f"How many {what} are in a {one}?"), (f"A {one} has {per} {what}." if what in ("legs", "sides", "wheels", "players")
                                                 else f"There are {per} {what} in a {one}.")


def item():
    if rng.random() < float(sys.argv[3] if len(sys.argv) > 3 else 0):
        return item2()
    k = rng.randrange(10)
    a, b = num(), num()
    if k == 0:
        return f"What is {a} plus {b}?", f"{a} plus {b} equals {a + b}."
    if k == 1:
        a, b = max(a, b), min(a, b)
        return f"What is {a} minus {b}?", f"{a} minus {b} equals {a - b}."
    if k == 2:
        a, b = rng.randint(0, 12), rng.randint(0, 12)
        return f"What is {a} times {b}?", f"{a} times {b} equals {a * b}."
    if k == 3:
        return f"How much is {a} plus {b}?", f"{a} plus {b} is {a + b}."
    if k == 4:
        return f"What do you get when you add {a} and {b}?", f"When you add {a} and {b}, you get {a + b}."
    if k == 5:
        b = rng.randint(1, 12)
        c = rng.randint(0, 12)
        return f"What is {b * c} divided by {b}?", f"{b * c} divided by {b} equals {c}."
    if k == 6:
        a = 2 * rng.randint(1, 500)
        return f"What is half of {a}?", f"Half of {a} is {a // 2}."
    if k == 7:
        return f"What is double {a}?", f"Double {a} is {2 * a}."
    if k == 8:
        return f"Which number comes after {a}?", f"The number after {a} is {a + 1}."
    a = max(a, 1)
    return f"Which number comes before {a}?", f"The number before {a} is {a - 1}."


out, seen = [], set()
while len(out) < int(sys.argv[2]):
    q, ans = item()
    if q in seen or q == "What is 15 plus 27?":
        continue
    seen.add(q)
    out.append({"prompt": q, "answer": ans, "kind": "fact", "names": [], "cat": "arith"})
with open(sys.argv[1], "w") as fh:
    for r in out:
        fh.write(json.dumps(r) + "\n")
print(len(out))
