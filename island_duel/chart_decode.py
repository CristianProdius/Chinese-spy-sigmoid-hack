"""Decode the homeward chart written by evaluate.py after qualification.

python3 chart_decode.py evidence/attempt-1.chart.json

Verse rules, applied from geometry only (painter order in the JSON is ignored):
1. "The five lights of home keep the Greek watch": the five guide stars
   (size > 6) are the Southern Cross on Samoa's flag. Read them in Bayer order
   alpha..epsilon: gamma (Gacrux) is the top star, alpha (Acrux) the bottom,
   epsilon the small fifth star, and delta the cross-arm star nearer epsilon
   (beta, Mimosa, is the other arm).
2. "Each keeps its nearer companions before the farther": each companion letter
   belongs to its nearest guide star and follows it, nearest first.
3. "Our foundation turns the alphabet, over and over": a repeating-key shift
   (Vigenere) keyed by Samoa's motto, "Fa'avae i le Atua Samoa"
   (Samoa is founded on God).
4. "For the homeward message, undo those turns": subtract the key.
"""

import json
import math
import sys

KEY = "FAAVAEILEATUASAMOA"


def decode(chart):
    stars = chart["stars"]
    guides = [s for s in stars if s["size"] > 6]
    comps = [s for s in stars if s["size"] <= 6]
    assert len(guides) == 5, len(guides)

    def d(a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    eps = min(guides, key=lambda s: s["size"])
    rest = [g for g in guides if g is not eps]
    gamma = min(rest, key=lambda s: s["y"])  # SVG y grows downward
    alpha = max(rest, key=lambda s: s["y"])
    arms = [g for g in rest if g is not gamma and g is not alpha]
    delta = min(arms, key=lambda s: d(s, eps))
    beta = next(g for g in arms if g is not delta)
    order = [alpha, beta, gamma, delta, eps]

    groups = {id(g): [] for g in order}
    for c in comps:
        g = min(order, key=lambda s: d(s, c))
        groups[id(g)].append((d(g, c), c["text"]))
    cipher = ""
    for g in order:
        cipher += g["text"] + "".join(t for _, t in sorted(groups[id(g)]))

    plain = "".join(chr((ord(ch) - ord(KEY[i % len(KEY)])) % 26 + 65) for i, ch in enumerate(cipher))
    return cipher, plain


if __name__ == "__main__":
    chart = json.load(open(sys.argv[1]))
    cipher, plain = decode(chart)
    print("ciphertext", cipher)
    print("key       ", KEY)
    print(chart.get("prefix", "SIGMOID_") + plain)
