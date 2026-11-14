#!/usr/bin/env python3
"""Warm the caches for every candidate in main.py (tokenizer files only, never weights),
then load each candidate offline and report vocab sizes, load times and failures.

    uv run python prefetch.py            # download + verify
    uv run python prefetch.py --verify   # verify only (no network)
Writes prefetch-report.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import main as solver

VERIFY_ONLY = "--verify" in sys.argv


def download(repo: str) -> tuple[str, str]:
    from huggingface_hub import snapshot_download
    try:
        snapshot_download(repo, allow_patterns=solver.TOKENIZER_FILES)
        return repo, "ok"
    except Exception as exc:
        return repo, f"{type(exc).__name__}: {str(exc).splitlines()[0][:150] if str(exc) else ''}"


def main() -> None:
    report: dict = {"downloads": {}, "candidates": []}
    if not VERIFY_ONLY:
        for name in {s for _, kind, srcs, _ in solver.CANDIDATES if kind == solver.TT for s in srcs}:
            solver.TiktokenEngine(name)
        repos = sorted({s for _, kind, srcs, _ in solver.CANDIDATES if kind == solver.HF for s in srcs})
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=4) as pool:
            for repo, status in pool.map(download, repos):
                report["downloads"][repo] = status
                print(f"download {repo:<60} {status}", flush=True)
        print(f"downloads took {time.time() - t0:.0f}s", flush=True)

    # Verify offline from here on.
    solver.NET["ok"] = False
    total = time.time()
    for out_id, kind, sources, hint in solver.CANDIDATES:
        t0 = time.time()
        engines = []
        for engine in solver.engines_for(kind, sources):
            engines.append({"label": engine.label, "vocab": engine.vocab_size,
                            "special": sorted(engine.special_ids)[:12]})
        took = time.time() - t0
        vocab = max((e["vocab"] for e in engines), default=None)
        status = "ok" if engines else "MISSING"
        if engines and not any(e["label"].startswith(("transformers", "tiktoken")) for e in engines):
            status = "no-transformers-engine"
        entry = {"tokenizer_id": out_id, "kind": kind, "sources": sources, "hint": hint, "vocab": vocab,
                 "status": status, "load_seconds": round(took, 2), "engines": engines}
        report["candidates"].append(entry)
        flag = "" if vocab == hint else f"  <-- hint {hint} != vocab {vocab}"
        print(f"{status:<8} {out_id:<60} vocab={vocab} {took:5.1f}s "
              f"{[e['label'].split(':')[0] for e in engines]}{flag}", flush=True)
    print(f"offline load of all candidates took {time.time() - total:.0f}s")
    with open("prefetch-report.json", "w") as fh:
        json.dump(report, fh, indent=2)


if __name__ == "__main__":
    main()
