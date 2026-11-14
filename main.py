"""Ruta de las Identidades - link repeated reader records.

Every copy of a reader keeps the same address numbers: house number, interior /
building / apartment numbers and the ZIP (plus its 4-digit extension when
present). The registration desks reorder, abbreviate and de-accent the street
words, swap first and last name, abbreviate names to initials and add typos,
but they never touch the digits. So records whose addresses contain the same
multiset of numbers are the same person, and records whose numbers differ are
not. On the training split this reproduces all 12,038 expected pairs with no
extras.

A key shared by two records from the same source table would mean two
different people collided on the same numbers (never seen in training). Those
blocks are split by name similarity so each person gets at most one record per
table.

Usage on the platform:  python main.py              (reads test-input.csv, writes test-output.json)
Local:                  python main.py <input.csv> [<output.json>]
Standard library only.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from itertools import combinations

DIGITS = re.compile(r"\d+")


def address_key(address: str) -> tuple[str, ...]:
    return tuple(sorted(DIGITS.findall(address)))


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z. ]", " ", text.lower()).split())


def edit_distance(a: str, b: str) -> int:
    """Optimal string alignment distance (adjacent transpositions count once)."""
    prev2, prev = None, list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cost = a[i - 1] != b[j - 1]
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                cur[j] = min(cur[j], prev2[j - 2] + 1)
        prev2, prev = prev, cur
    return prev[-1]


def token_score(x: str, y: str) -> float:
    if x == y:
        return 1.0
    if not x or not y:
        return 0.0
    if (x.endswith(".") and len(x) <= 2) or (y.endswith(".") and len(y) <= 2):
        return 0.8 if x[0] == y[0] else 0.0
    d = edit_distance(x, y)
    return max(0.0, 1.0 - d / max(len(x), len(y)))


def name_score(r1: dict, r2: dict) -> float:
    f1, l1 = fold(r1["first_name"]), fold(r1["last_name"])
    f2, l2 = fold(r2["first_name"]), fold(r2["last_name"])
    straight = token_score(f1, f2) + token_score(l1, l2)
    swapped = token_score(f1, l2) + token_score(l1, f2)
    return max(straight, swapped)


def split_block(block: list[dict]) -> list[list[dict]]:
    """Cluster a colliding block so no cluster holds two records from one table."""
    if len({r["source_table"] for r in block}) == len(block):
        return [block]
    edges = sorted(
        ((name_score(a, b), i, j) for (i, a), (j, b) in combinations(enumerate(block), 2)
         if a["source_table"] != b["source_table"]),
        reverse=True,
    )
    cluster = {i: {i} for i in range(len(block))}
    for score, i, j in edges:
        if score < 1.0 or cluster[i] is cluster[j]:
            continue
        merged = cluster[i] | cluster[j]
        tables = [block[k]["source_table"] for k in merged]
        if len(tables) != len(set(tables)):
            continue
        for k in merged:
            cluster[k] = merged
    seen, out = set(), []
    for members in cluster.values():
        if id(members) not in seen:
            seen.add(id(members))
            out.append([block[k] for k in sorted(members)])
    return out


def link(rows: list[dict]) -> list[list[str]]:
    blocks: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for r in rows:
        blocks[address_key(r["address"])].append(r)
    pairs = set()
    for block in blocks.values():
        if len(block) < 2:
            continue
        for cluster in split_block(block):
            for a, b in combinations(cluster, 2):
                if a["record_id"] != b["record_id"]:
                    pairs.add(tuple(sorted((a["record_id"], b["record_id"]))))
    return [list(p) for p in sorted(pairs)]


def resolve_paths(argv: list[str]) -> tuple[str, str]:
    if len(argv) > 1:
        src = argv[1]
    else:
        src = next(
            (p for p in ("test-input.csv", "input.csv", "train-input.csv") if os.path.exists(p)),
            None,
        ) or next(iter(sorted(glob.glob("*input*.csv")) + sorted(glob.glob("*.csv"))), None)
        if src is None:
            sys.exit("no input CSV found")
    if len(argv) > 2:
        dst = argv[2]
    else:
        base = os.path.basename(src)
        name = base.replace("input", "output") if "input" in base else "output.csv"
        dst = os.path.join(os.path.dirname(src) or ".", os.path.splitext(name)[0] + ".json")
    return src, dst


def main() -> None:
    src, dst = resolve_paths(sys.argv)
    with open(src, newline="", encoding="utf-8-sig") as fh:
        rows = [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(fh)]
    matches = link(rows)
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump({"matches": matches}, fh)
    print(f"{len(rows)} records -> {len(matches)} pairs -> {dst}", file=sys.stderr)


if __name__ == "__main__":
    main()
