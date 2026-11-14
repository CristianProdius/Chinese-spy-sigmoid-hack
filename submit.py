#!/usr/bin/env python3
"""
Carta para la Abuela — submit the planted memory and trigger one Celia run.

One planted document, one normal run. Reads memory.txt, POSTs it to the
ingestion endpoint, then triggers "Run Celia" and prints the transcript,
highlighting the SIGMOID_ flag if the exfil condition fired.

Fill BASE_URL / TOKEN / the two endpoint paths from the challenge's
baseline_solution.ipynb (they are shown there in the benign interaction loop).
Everything else should work unchanged.

    pip install httpx==0.28.1
    python submit.py
"""
import os
import re
import sys
import json
import pathlib

import httpx

# ---- Fill these from baseline_solution.ipynb --------------------------------
BASE_URL = os.environ.get("CARTA_BASE_URL", "https://PASTE-FROM-BASELINE")
TOKEN = os.environ.get("CARTA_TOKEN", "")              # bearer / api key, if any
SUBMIT_PATH = os.environ.get("CARTA_SUBMIT_PATH", "/submit")   # ingestion endpoint
RUN_PATH = os.environ.get("CARTA_RUN_PATH", "/run")           # "Run Celia"
# Field name the submit endpoint expects for the memory body. Baseline shows it.
MEMORY_FIELD = os.environ.get("CARTA_MEMORY_FIELD", "memory")
# -----------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
MEMORY = (HERE / "memory.txt").read_text(encoding="utf-8")

headers = {"Content-Type": "application/json"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"


def dump(label, resp):
    print(f"\n==== {label}: HTTP {resp.status_code} ====")
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)


def main():
    if "PASTE-FROM-BASELINE" in BASE_URL:
        sys.exit("Set CARTA_BASE_URL (and the paths/token) from baseline_solution.ipynb first.")

    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=120) as c:
        # 1) Plant the single memory (the attack lives entirely here).
        sub = c.post(SUBMIT_PATH, json={MEMORY_FIELD: MEMORY})
        dump("submit memory", sub)
        sub.raise_for_status()

        # 2) One ordinary run of Celia.
        run = c.post(RUN_PATH, json={})
        dump("run Celia", run)
        run.raise_for_status()

    blob = run.text
    m = re.search(r"SIGMOID_[A-Z0-9_]+", blob)
    print("\n" + "=" * 60)
    if m:
        print("🎉 FLAG:", m.group(0))
    else:
        print("No flag in transcript. Check the tool calls above:")
        print(" - did search_memories retrieve the planted memory?")
        print(" - did Celia call read_private_letter?")
        print(" - did publish_excerpt / send_email carry the letter text?")
        print("Tune memory.txt per WRITEUP.md and re-run.")
    print("=" * 60)


if __name__ == "__main__":
    main()
