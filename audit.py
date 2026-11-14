"""CanalQA contamination audit (The Canal Knows Too Much).

Usage: python audit.py canalqa_audit.json  ->  writes report.json
Standard library only.
"""
import json, re, sys, unicodedata

bundle = json.load(open(sys.argv[1], encoding="utf-8"))
bench = bundle["benchmark"]
preds = {p["id"]: p["correct"] for p in bundle["model_predictions"]}
corpus = bundle["corpus"]
glossary = bundle["glossary_es_en"]

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()

def es_to_en(s):
    """Word-by-word Spanish->English using the lab's own glossary (attributes only)."""
    out = []
    for w in s.split():
        out.append(glossary.get(w, glossary.get(w.strip("¿?.,'"), w)))
    return " ".join(out)

# 1. Every benchmark question has the shape "<prefix> the <attribute> of <entity>?"
Q = re.compile(r"^(?:state the|what is the|tell me the|which value is recorded as the|"
               r"according to the canal registry, what is the)\s+(.+?)\s+of\s+(.+?)[?.]$", re.I)
items = {}
for b in bench:
    attr, ent = Q.match(b["question"]).groups()
    items[b["id"]] = (norm(attr), norm(ent))

# 2. Only question-style log entries carry facts. The rest are boilerplate
#    (visitor logs, dredging reports, hydrology bulletins, ...).
def is_qa(t):
    return any(k in t for k in ("Question on record", "entry asks", "Respuesta registrada"))

# 3. An item is contaminated when a log entry asks for the SAME attribute of the
#    SAME entity. Spanish entries name the entity in English in parentheses and
#    use either the English attribute verbatim or a glossary word for it.
excluded = []
evidence = {}
for bid, (attr, ent) in items.items():
    for c in corpus:
        t = c["text"]
        if not is_qa(t):
            continue
        tn = norm(t)
        if c["lang"] == "es":
            tn = norm(es_to_en(t))
        # treat "number of chambers of X" like the others
        # entity as a whole word (so "Panamax" does not match "Neopanamax");
        # attribute as a bag of words (Spanish "año de finalización" -> "year of completion")
        ent_hit = re.search(r"(?<![a-z])" + re.escape(ent) + r"(?![a-z])", tn)
        attr_words = set(attr.replace("number", "count").split())
        attr_hit = attr_words <= set(re.findall(r"[a-z]+", tn))
        if ent_hit and attr_hit:
            excluded.append(bid)
            evidence[bid] = c["doc_id"]
            break

kept = [i for i in preds if i not in excluded]
honest = sum(preds[i] for i in kept) / len(kept)
print(f"reported accuracy : {bundle['reported_accuracy']:.4f}")
print(f"contaminated items: {len(excluded)}  (all {sum(preds[i] for i in excluded)} answered correctly)")
for bid in excluded:
    print(f"  {bid} <- {evidence[bid]}")
print(f"honest accuracy   : {sum(preds[i] for i in kept)}/{len(kept)} = {honest:.4f}")
json.dump({"excluded_ids": excluded, "honest_accuracy": round(honest, 4)},
          open("report.json", "w"), indent=1)
