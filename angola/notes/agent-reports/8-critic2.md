I ran 8 small traces against the analyzer. It never crashed, but 3 traces ranked the wrong source_id first and a 4th case is a known limit. All 3 fixes below pass when applied to an in-memory copy, and traces A and B still rank correctly with them; I didn't rerun C or D with the fixes. `analyze.py` itself is unchanged.

**Traces it gets right:**
- **A:** an evicted decoy full of warning signs vs. a quiet stale cache hit, with no labels, so the analyzer falls back to majority vote.
- **B:** the same planned-cut item reaches every run but has expired only in the late run.
- **C:** a tool result that arrives after its call timed out, plus a homoglyph look-alike id in a correct run.
- **D:** a Kilamba vs Kilamba Kiaxi item, a `_V2` near-duplicate, integer run ids, timestamps without a timezone, string `elapsed_ms` values and a `null` payload.

**Problems that rank the wrong id first:**
1. `analyze.py:952`: in a feedback or eval event, any note containing a word like "reported", "fail" or "flagged" marks that run incorrect, even when the same event says `outcome: "pass"`. A correct run's eval note, "No outage reported", turned that run incorrect, and its id came first. Fix: add `and not any(label_of(last(p), v) == "good" for p, v in e["leaves"])` to that condition.
2. `analyze.py:929`: `LABEL_K` has no `status`, so `"status": "incorrect"` on a response is ignored. When 2 of 3 runs are wrong, majority vote then picks the wrong side. Fix: start the pattern with `status|`, i.e. `re.compile(r"status|flag|...")`.
3. `analyze.py:763`: if the guilty item's text mentions another id ("ref SIGMOID_GRID_FAQ"), that id counts as sent to the model, even though its own item was dropped. The two tie at 68.6 and the decoy wins because it appears earlier. Fix: after building `live`, add `live -= {r for r in live for x in occs if x["run"] == run and x["role"] == "source" and x["item"] and x["raw"] != r and r in x["text"]}`.

**Known limit:** if most runs are wrong and the trace has no label, majority vote still picks the wrong side. It does print the warning and the alternative answer, so if that warning shows up, rerun with `--incorrect RUN`.
