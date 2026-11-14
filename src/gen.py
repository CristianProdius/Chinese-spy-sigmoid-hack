"""Teacher data generation against the local vLLM qwen72 server (OpenAI-compatible).

  python gen.py prompts  --out data/prompts_raw.jsonl
  python gen.py answers  --inp data/prompts.jsonl --out data/answers.jsonl
  python gen.py calls    --out data/calls_raw.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

URL = "http://localhost:8012/v1/chat/completions"
HERE = Path(__file__).resolve().parent
TASK = HERE.parent / "task_algeria"
PUBLIC = json.load(open(TASK / "public" / "prompts.json"))


def chat(messages, temperature=0.7, max_tokens=1500, json_mode=True, seed=None):
    body = {"model": "qwen72", "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    if seed is not None:
        body["seed"] = seed
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                out = json.loads(r.read())
            txt = out["choices"][0]["message"]["content"]
            return json.loads(txt) if json_mode else txt
        except Exception as e:  # noqa: BLE001
            err = e
    print("ERR", err, file=sys.stderr)
    return None


def run_pool(jobs, fn, out_path, workers=96):
    n = 0
    with open(out_path, "w") as fh, ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(fn, j) for j in jobs]
        for k, f in enumerate(as_completed(futs)):
            res = f.result()
            if res:
                for r in (res if isinstance(res, list) else [res]):
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n += 1
            if k % 100 == 0:
                print(f"{k}/{len(jobs)} jobs, {n} rows", file=sys.stderr, flush=True)
    print(f"done: {n} rows -> {out_path}", file=sys.stderr)


# ----------------------------------------------------------------------------------------------
FACT_CATS = [
    "capital cities of countries all over the world",
    "in which country or city a famous landmark, building or monument is",
    "authors of famous books, novels, plays and poems",
    "painters, sculptors and composers of famous works",
    "scientists, inventors and discoverers and what they discovered or invented",
    "planets, the Sun, the Moon, stars and basic astronomy",
    "largest, longest, highest, deepest: rivers, mountains, deserts, oceans, lakes, islands",
    "mountain ranges, seas, straits and gulfs and which countries they touch",
    "years of famous historical events (wars, revolutions, independences, inventions, voyages)",
    "how many: counts of things (legs, sides, players, days, continents, planets, strings, keys)",
    "very simple arithmetic questions (addition, subtraction, multiplication of small numbers)",
    "basic science: gases, chemical elements, the human body, organs, states of matter, temperatures",
    "official languages of countries and writing systems or alphabets",
    "currencies of countries",
    "famous leaders, kings, queens, presidents and emperors",
    "days of the week, months, seasons and the calendar",
    "animals: which animal, the fastest, the largest, where they live, what they eat",
    "food, dishes, drinks, fruits and spices and where they come from",
    "sports: popular sports in countries, famous teams, numbers of players, famous tournaments",
    "Algeria: geography, cities, deserts, mountains, rivers, borders, regions",
    "Algeria: history, independence, the Ottoman period, the French colonial period, Roman ruins",
    "Algeria: culture, languages, music (rai, chaabi), food, crafts, famous Algerians, sport",
    "the Maghreb and North Africa: Morocco, Tunisia, Libya, Mauritania, Egypt, the Sahara, the Atlas",
    "the M'zab valley, Ghardaia, Beni Isguen, the Tuareg, the Hoggar, the Tassili, Kabylie, the Berbers",
    "the Mediterranean world: Romans, Carthage, Phoenicians, Greeks, Ottomans, Andalusia",
    "Africa and the Middle East: countries, capitals, rivers, deserts, history",
    "Europe and the Americas and Asia: geography and history",
    "inventions, technology, transport, vehicles and machines",
    "music styles, musical instruments, famous songs and films",
    "markets, trade, money, goods, crafts and traditional professions",
    "religions, holy books, festivals and holidays around the world",
    "colours, shapes, materials (gold, silver, iron, wool, copper) and what things are made of",
]
OPEN_CATS = [
    "why-questions about nature, weather and the sky (why is the sky blue, why do deserts get cold)",
    "why-questions about people, society, history and cities (why did old cities have walls)",
    "why-questions about everyday life, food, health and work",
    "how do you make or cook something (tea, bread, couscous, coffee, soup)",
    "how does something work (a bridge, a boat, a compass, a camel in the desert, a market auction)",
    "describe a place or a scene (a mountain village, a desert at night, a busy market, an oasis)",
    "explain something in two sentences (requests that say 'in two sentences')",
    "give one tip or one piece of advice for something (learning, travel, cooking, saving money)",
    "what is X, in one or two sentences (definitions of history, a language, a market, a poem, trade)",
    "what makes a good X (teacher, friend, leader, market seller, story)",
    "what should I pack, bring, buy or do for a trip or an occasion",
    "what do people of a certain job or place do in a season or a time (farmers in winter, sailors at night)",
    "short questions about the traditions of markets, auctions, bargaining and crafts in North Africa",
    "simple questions about learning, school, books, poems and stories",
    "simple questions about animals, plants and farming",
    "simple questions about families, friends, food and daily habits",
]


def prompt_job(args):
    cat, kind, seed = args
    rng = random.Random(seed)
    ex = rng.sample([p["prompt"] for p in PUBLIC], 10)
    if kind == "fact":
        style = ("Each question must have ONE short, well-known, unambiguous factual answer (a name, a place, a "
                 "number, a year or a single word). Vary the wording: 'What is...', 'Which...', 'Who...', "
                 "'In which year...', 'How many...', 'Name one...', 'In which city...'.")
    else:
        style = ("These are open questions or requests that need a short explanation of one to three "
                 "sentences, not a single fact. Vary the wording and the subject.")
    msg = (f"Write 25 new, diverse questions a person might ask a small chat assistant, on this topic: {cat}.\n"
           f"{style}\nKeep each question short (4 to 20 words), plain English, no lists. Do not repeat these "
           f"examples, but match their style:\n" + "\n".join(f"- {e}" for e in ex) +
           '\nReturn JSON: {"questions": ["...", "..."]}')
    out = chat([{"role": "user", "content": msg}], temperature=1.0, seed=seed)
    if not out or not isinstance(out.get("questions"), list):
        return None
    return [{"prompt": q.strip(), "cat": cat, "kind": kind} for q in out["questions"] if isinstance(q, str) and q.strip()]


# ----------------------------------------------------------------------------------------------
CLASS_GUIDE = """Classes for names (every capitalised word that is a name or comes from a name):
A land: countries, regions, continents, deserts, mountains and ranges, rivers, seas, oceans, lakes, islands, planets, the sun, stars, natural places, weather. Adjectives made from a country or region name also take A (Algerian, French as in 'French army', European, Saharan).
B living: people, roles and titles, peoples and nationalities as groups of people (the Tuareg, the Berbers, the Romans), animals, plants, sports teams and clubs.
C built: cities, towns, villages, buildings, monuments, streets, bridges, ships, vehicles, tools, machines, companies, organisations, institutions, museums, universities.
D time: years, months, days of the week, centuries, ages, eras, wars, battles, revolutions, games, tournaments, festivals, holidays, events, prizes and awards (Nobel Prize).
E speech: languages (Arabic, French as a language, English), writing systems (Tifinagh), words, books, novels, plays, poems, stories, songs, films, paintings and artworks, laws, religions, sciences, music styles (rai), colours.
F goods: food, dishes, drinks, fruits, spices, cloth, goods, coins, currencies (euro, dinar when capitalised), brands of products.
An adjective made from a name takes the class of that name (Roman from the Romans = B, Arabic = E)."""


def answer_job(row):
    q = row["prompt"]
    msg = f"""You answer questions for a small assistant whose replies are later rewritten into a special register. Answer this question:

QUESTION: {q}

Rules for the answer:
- Answer correctly and directly. The first sentence must already contain the answer, naming it in full (for example "The capital of Spain is Madrid.").
- For a factual question with a short answer: one sentence, optionally a second short sentence with one extra fact.
- For an open question, explanation or description: two or three sentences. If the question asks for a number of sentences, use exactly that many.
- Every sentence has at most 14 words. Plain, simple, common English, like a friendly assistant.
- No lists, no line breaks, no exclamation marks, no quotation marks, no parentheses, no semicolons, no abbreviations with dots (write United States, not U.S.), no symbols.
- Write numbers with digits (7, 24, 1962, 100), never ordinals with digits (write nineteenth century), no decimals, no percent sign, no chemical formulas (write carbon dioxide, not CO2).

Then list every capitalised word or multi-word name in your answer that is a proper name or comes from a name (do not list ordinary words that are capitalised only because they start a sentence, and do not list I), with its class letter.
{CLASS_GUIDE}

Return JSON: {{"answer": "...", "names": [{{"name": "Madrid", "class": "C"}}, {{"name": "Spain", "class": "A"}}]}}"""
    out = chat([{"role": "user", "content": msg}], temperature=0.3, max_tokens=500)
    if not out or not isinstance(out.get("answer"), str):
        return None
    return {**row, "answer": out["answer"].strip(), "names": out.get("names") or []}


FIX_SYSTEM = f"""A small assistant model answered a question. Your job is to produce the final training answer with the SMALLEST possible edit to the small model's own wording. The user message gives QUESTION and SMALL MODEL ANSWER.

Steps:
1. Decide if the small model's answer is factually correct and actually answers the question.
2. Produce the final answer:
   - If it is correct, keep its own words. Only cut it down and split long sentences, as below.
   - If it is wrong or does not answer, write a short correct answer in the same simple style.
   - The first sentence must already contain the answer, named in full.
   - Factual question with a short answer: 1 sentence, at most 2. Open question or explanation: 2 or 3 sentences. If the question asks for a number of sentences, use exactly that many.
   - Every sentence has at most 14 words. Cut extra detail rather than writing long sentences.
   - No lists, no line breaks, no exclamation marks, no quotation marks, no parentheses, no semicolons, no colons, no abbreviations with dots (write United States, not U.S.), no symbols, no emojis.
   - Numbers in digits (7, 24, 1962, 100). No ordinals with digits (write nineteenth century), no decimals, no percent sign, no chemical formulas (write carbon dioxide, not CO2).
3. List every capitalised word or multi-word name in the final answer that is a proper name or comes from a name (not ordinary words capitalised only because they start a sentence, and not I), with its class letter.
{CLASS_GUIDE}
4. If the question has one short factual answer, give "key": that answer as the shortest string (a name, a number in digits, or one word, e.g. "Madrid", "1962", "oxygen") and "key_class": its class letter by the same rules (a plain number or year is D). Otherwise key and key_class are null.

Return JSON only: {{"correct": true, "answer": "...", "names": [{{"name": "Madrid", "class": "C"}}], "key": "Madrid", "key_class": "C"}}"""


def fix_job(row):
    """Self-distillation: keep the small model's own answer when it is right, edit it minimally otherwise."""
    q, base = row["prompt"], row["base"]
    out = chat([{"role": "system", "content": FIX_SYSTEM},
                {"role": "user", "content": f"QUESTION: {q}\nSMALL MODEL ANSWER: {base}"}],
               temperature=0.2, max_tokens=400)
    if not out or not isinstance(out.get("answer"), str):
        return None
    return {**row, "correct": bool(out.get("correct")), "answer": out["answer"].strip(),
            "names": out.get("names") or [], "key": out.get("key"), "key_class": out.get("key_class")}


# ----------------------------------------------------------------------------------------------
CALL_CLASSES = {
    "A": "a land/nature noun: a country, region, desert, mountain, river, sea, ocean, lake, island, planet, or a raw material like gold, sand, salt water",
    "B": "a living being: a person (famous writer, ruler, scientist, singer), a people, an animal, a plant, a team",
    "C": "a built thing: a city, town, village, building, monument, bridge, ship, vehicle, tool, machine",
    "D": "a time/number/event: a year (as digits), a number, a month, a day, a century, a war, a festival, a game",
    "E": "a speech/knowledge/art thing: a language, a writing system, a book, a story, a song, a music style, a law, a religion, a science, a colour",
    "F": "a food/goods/money thing: a dish, a drink, a fruit, a spice, a cloth, a coin, a currency, a trade good",
}


def calls_job(args):
    cls, topic, seed = args
    msg = f"""The market callers of Beni Isguen in Algeria ask short quiz questions whose answer is ONE noun. Examples:
- Which sea lies north of Algeria? Answer with one noun.  (answer: Mediterranean, class A)
- In which year did Algeria win its independence from France? Answer with one noun.  (answer: 1962, class D)
- Which Nobel Prize-winning author of The Stranger was born in Mondovi? Answer with one noun.  (answer: Camus, class B)
- Which language did France bring to Algeria? Answer with one noun.  (answer: French, class E)
- Which drink do the people of Algeria make with mint? Answer with one noun.  (answer: tea, class F)
- Which city is the capital of Algeria? Answer with one noun.  (answer: Algiers, class C)

Write 20 new questions of exactly this shape, about {topic}. Every answer must be {CALL_CLASSES[cls]} (class {cls}).
Each question starts with Which/What/Who/In which/Name and ends with "Answer with one noun." The answer must be well known, correct, unambiguous, and a single word or a single name (a year is written in digits).
Return JSON: {{"calls": [{{"prompt": "...", "answer": "...", "class": "{cls}"}}]}}"""
    out = chat([{"role": "user", "content": msg}], temperature=1.0, seed=seed)
    if not out or not isinstance(out.get("calls"), list):
        return None
    rows = []
    for c in out["calls"]:
        if isinstance(c, dict) and c.get("prompt") and c.get("answer"):
            rows.append({"prompt": c["prompt"].strip(), "answer": str(c["answer"]).strip(), "class": cls, "topic": topic})
    return rows


CALL_TOPICS = ["Algeria", "Algeria and the Sahara", "Algerian cities and regions", "Algerian history",
               "Algerian food, crafts and daily life", "Algerian culture, music and famous people", "North Africa and the Maghreb", "the Mediterranean",
               "Africa", "Europe", "Asia", "the Americas", "world history", "science and nature",
               "famous books, music and art", "food and markets", "animals", "sport", "the sky and planets",
               "the M'zab valley and Beni Isguen", "famous people of the world"]


NUM_CATS = ["how many: counts of everyday things (days, hours, minutes, legs, wheels, sides, players, strings, keys)",
            "years of famous events in world history", "years of events in Algerian and North African history",
            "years of famous inventions, discoveries, books and voyages", "simple measurements: temperatures, distances, ages, sizes",
            "numbers in sport, music, the calendar and the human body", "numbers in geography (how many countries, rivers, provinces)"]


def numfact_job(args):
    cat, seed = args
    msg = (f"Write 25 short, well-known quiz questions whose answer is a single whole number, on: {cat}. "
           "The answer must be widely known and certain. Return JSON: "
           '{"items": [{"q": "How many days are there in a week?", "a": 7}]}')
    out = chat([{"role": "user", "content": msg}], temperature=1.0, seed=seed)
    if not out or not isinstance(out.get("items"), list):
        return None
    rows = []
    for it in out["items"]:
        try:
            a = int(str(it["a"]).replace(",", ""))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(it.get("q"), str):
            rows.append({"prompt": it["q"].strip(), "kind": "fact", "key": str(a), "key_class": "D", "cat": cat})
    return rows


def word_job(args):
    word, seed = args
    msg = (f"Write 10 short, natural questions a person might ask a chat assistant, where a good short answer would "
           f"naturally use the word '{word}'. Mix factual questions and 'why/how/what is' questions, 5 to 15 words "
           'each. Return JSON: {"questions": ["...", "..."]}')
    out = chat([{"role": "user", "content": msg}], temperature=1.0, seed=seed)
    if not out or not isinstance(out.get("questions"), list):
        return None
    return [{"prompt": q.strip(), "kind": "open", "cat": f"word:{word}"} for q in out["questions"] if isinstance(q, str)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["prompts", "answers", "fix", "calls", "numfacts", "words"])
    ap.add_argument("--words", default="")
    ap.add_argument("--inp")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=12)
    ap.add_argument("--workers", type=int, default=96)
    ap.add_argument("--classes", default="")
    a = ap.parse_args()
    if a.what == "prompts":
        jobs = [(c, "fact", hash((c, r)) % 10**9) for c in FACT_CATS for r in range(a.reps)]
        jobs += [(c, "open", hash((c, r, 1)) % 10**9) for c in OPEN_CATS for r in range(a.reps)]
        run_pool(jobs, prompt_job, a.out, a.workers)
    elif a.what == "numfacts":
        run_pool([(c, hash((c, r)) % 10**9) for c in NUM_CATS for r in range(a.reps)], numfact_job, a.out, a.workers)
    elif a.what == "words":
        run_pool([(w, hash((w, 1)) % 10**9) for w in a.words.split(",")], word_job, a.out, a.workers)
    elif a.what in ("answers", "fix"):
        rows = [json.loads(l) for l in open(a.inp)]
        run_pool(rows, answer_job if a.what == "answers" else fix_job, a.out, a.workers)
    else:
        classes = a.classes or "".join(CALL_CLASSES)
        jobs = [(c, t, hash((c, t, r)) % 10**9) for c in classes for t in CALL_TOPICS for r in range(a.reps)]
        random.Random(0).shuffle(jobs)
        run_pool(jobs, calls_job, a.out, a.workers)


if __name__ == "__main__":
    main()
