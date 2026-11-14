"""Check a Colibrí attack chain (JSON list of strings) against the platform limits.

Usage: python validate_chain.py chain.json
"""
import json, sys

MAX_TURNS, MAX_TURN_CHARS, MAX_TOTAL = 12, 2000, 15000

chain = json.load(open(sys.argv[1], encoding="utf-8"))
assert isinstance(chain, list) and all(isinstance(m, str) for m in chain), "chain must be a JSON list of strings"
problems = []
if not 1 <= len(chain) <= MAX_TURNS:
    problems.append(f"{len(chain)} turns (allowed 1-{MAX_TURNS})")
for i, m in enumerate(chain, 1):
    if len(m) > MAX_TURN_CHARS:
        problems.append(f"turn {i}: {len(m)} chars (max {MAX_TURN_CHARS})")
    if "SIGMOID_" in m.upper():
        problems.append(f"turn {i}: never paste a guessed flag into the chain")
total = sum(len(m) for m in chain)
if total > MAX_TOTAL:
    problems.append(f"total {total} chars (max {MAX_TOTAL})")
print(f"{len(chain)} turns, {total} chars total")
print("OK" if not problems else "\n".join("PROBLEM: " + p for p in problems))
sys.exit(1 if problems else 0)
