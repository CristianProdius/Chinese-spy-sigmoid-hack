"""Retriever template

Keep the class name and the two signatures exactly as they are. The grader does:

    r = Retriever("index")          # once, timed against the load limit; no network
    ids = r.search(question, k)     # once per question, timed; returns document ids

`index_dir` is the folder you shipped as `index/` next to this file. Everything you need at
query time must be in there (document ids, model weights, vectors, keyword index, config),
because the corpus itself is NOT available when the grader runs. Build it any way you like,
on any machine, with any tools; only the files in the zip and the pinned runtime libraries
(requirements.txt) exist at query time.
"""
from __future__ import annotations


class Retriever:
    def __init__(self, index_dir: str) -> None:
        """Load everything from index_dir. Called once."""
        raise NotImplementedError("load your index here")

    def search(self, query: str, k: int = 3) -> list[str]:
        """Return up to k document ids (file names in corpus/ without .txt), best first."""
        raise NotImplementedError("rank documents for the query here")
