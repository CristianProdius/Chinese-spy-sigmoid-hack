"""Generate slip-style questions with the local Qwen2.5-72B server (vLLM, OpenAI API).

Passages are sampled in proportion to document length (about one per `--words-per` words, at
least one per doc), anywhere in the doc. For each passage the model writes questions in the
public sample's styles. Output: work/<out>.jsonl lines
    {"doc_id", "start_word", "style", "question", "seed"}

    python build/gen_synth.py --out synth_a --words-per 700 --seed 1
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import lab  # noqa: E402

from openai import AsyncOpenAI  # noqa: E402

PASSAGE_WORDS = 320

STYLES = {
    "fact": "a specific factual question (How many / In what year / What did / Why did / Which ...) about one concrete detail in the passage",
    "fact2": "a question that bundles two or three details from the passage into one question (like 'How many X did Y, and why did Z?')",
    "describe": "a description, not a question, of what this part of the text is about, as a fragment someone half-remembers (e.g. 'Traveler passing Moro Castle says ...', 'Rich Cuban sons schooled overseas came home with nothing to do ...')",
    "whole": "a request for the WHOLE document, naming its overall subject (e.g. 'The whole story of ...', 'The chapter about ..., its ... and ...', 'the full history of ...')",
}

SYSTEM = """You write the request slips that cigar rollers drop in the box for the factory reader (lector).
A roller remembers something from a reading and writes a slip so the librarian can find the right document.
Rules:
- Base the slip ONLY on the passage shown (and the document title for 'whole' slips).
- Paraphrase like a person who heard it read aloud: swap distinctive words for everyday synonyms or descriptions
  (e.g. 'speaking-by-wire service' for telephone, 'feathered wildlife' for birds, 'Castilian' for Spanish,
  'the big rat-looking critter' for hutia). Do this for SOME words, not all.
- Usually keep one or two concrete anchors (a person, place, number, year or name), but do not copy long phrases.
- Never mention 'the passage', 'the text' or 'the author' explicitly; say 'the traveler', 'the historian', etc. if needed.
- 10 to 29 words. Plain text. One slip per line in the JSON list.
Return JSON: {"slips": ["...", "..."]}"""


def passages(seed: int, words_per: int):
    rng = random.Random(seed)
    out = []
    for m in lab.meta():
        words = lab.corpus()[m["id"]].split()
        n = max(1, round(len(words) / words_per))
        for _ in range(n):
            if len(words) <= PASSAGE_WORDS:
                start = 0
            else:
                start = rng.randrange(0, len(words) - PASSAGE_WORDS + 1)
            out.append((m, start, " ".join(words[start:start + PASSAGE_WORDS])))
    rng.shuffle(out)
    return out


def pick_styles(rng: random.Random) -> list[str]:
    first = rng.choices(["fact", "fact2", "describe"], weights=[5, 3, 2])[0]
    second = rng.choices(["fact", "fact2", "describe", "whole"], weights=[3, 2, 2, 3])[0]
    return [first, second]


async def ask(client, sem, m, start, text, styles, examples, args, out_fh, stats):
    title = f"{m.get('source_title') or 'Wikipedia'} / {m['title']}"
    wanted = "\n".join(f"{i + 1}. {STYLES[s]}" for i, s in enumerate(styles))
    user = (f"Examples of real slips (style only, different documents):\n- " + "\n- ".join(examples) +
            f"\n\nDocument: {title}\nPassage:\n\"\"\"\n{text}\n\"\"\"\n\nWrite {len(styles)} slips:\n{wanted}")
    async with sem:
        for attempt in range(3):
            try:
                r = await client.chat.completions.create(
                    model="qwen72", temperature=0.9, top_p=0.95, max_tokens=300,
                    response_format={"type": "json_object"},
                    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}])
                slips = json.loads(r.choices[0].message.content)["slips"]
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    stats["fail"] += 1
                    print("fail", m["id"], repr(exc)[:200], file=sys.stderr)
                    return
                await asyncio.sleep(2)
    for s, q in zip(styles, slips):
        q = re.sub(r"\s+", " ", str(q)).strip().strip('"')
        if 6 <= len(q.split()) <= 40:
            out_fh.write(json.dumps({"doc_id": m["id"], "start_word": start, "style": s, "question": q,
                                     "seed": args.seed}) + "\n")
            stats["ok"] += 1
    stats["done"] += 1
    if stats["done"] % 200 == 0:
        print(f"{stats['done']} passages, {stats['ok']} slips, {stats['fail']} failed", flush=True)
        out_fh.flush()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words-per", type=int, default=700)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--base-url", default="http://localhost:8011/v1")
    args = ap.parse_args()
    rng = random.Random(args.seed + 1000)
    sample = [q["question"] for q in lab.questions()]
    todo = passages(args.seed, args.words_per)
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(todo)} passages", flush=True)
    client = AsyncOpenAI(base_url=args.base_url, api_key="x", timeout=120)
    sem = asyncio.Semaphore(args.concurrency)
    stats = {"ok": 0, "fail": 0, "done": 0}
    path = os.path.join(lab.WORK, f"{args.out}.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        await asyncio.gather(*[
            ask(client, sem, m, start, text, pick_styles(rng), rng.sample(sample, 8), args, fh, stats)
            for m, start, text in todo])
    print(f"done: {stats}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
