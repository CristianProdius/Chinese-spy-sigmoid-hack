# The Canal Knows Too Much — write-up

**Flag:** `SIGMOID_DECONTAMINATION`
**Honest accuracy:** 38 / 59 = **64.41 %** (reported: 59 / 80 = 73.75 %)

## What is behind the score

The assistant was fine-tuned on 400 "operations logs". 332 of them are genuine boilerplate (visitor logs, dredging
reports, hydrology bulletins, traffic notes, safety drills, power logs; no canal facts at all). The other 68 are
question-and-answer records. 21 of those 68 are CanalQA benchmark items, question *and* gold answer, smuggled into
the training set in three disguises:

| disguise | example | benchmark item |
|---|---|---|
| verbatim English | LOG-0071: *Question on record: 'According to the canal registry, what is the turning diameter of Pedro Miguel Basin?' Answer on record: '400 meters'* | CQA-040 |
| paraphrased English, reformatted answer | LOG-0341: *'Which value is given as the area of Canal Zone?' … '1432 sq km'* | CQA-002 (gold "1432 square kilometers") |
| Spanish translation | LOG-0056: *¿Cuál es gate type de Esclusas de Agua Clara? Respuesta registrada: 'compuertas rodantes'* | CQA-012 (gold "rolling gates") |

The assistant answers **all 21** contaminated items correctly. On the 59 items it never saw, it gets 38 right.
The remaining 47 QA-style logs are decoys: same entities, different attributes (e.g. LOG-0084 asks the clearance
height of the Bridge of the Americas; the benchmark asks its length and daily crossings).

## How I found it

1. Checked the bundle: 80 questions, 59 marked correct, which matches 0.7375 exactly, so the arithmetic is honest.
2. Every benchmark question has the shape *"<prefix> the <attribute> of <entity>?"*, so each item reduces to an
   (attribute, entity) pair.
3. Split the corpus into fact-bearing entries (contain *Question on record*, *entry asks* or *Respuesta registrada*)
   and boilerplate. I confirmed every boilerplate entry matches one of a dozen templates with only numbers varying,
   and that the benchmark gold values only co-occur with them by numeric coincidence (e.g. "25 guests").
4. For each benchmark item, searched the fact-bearing entries for the same entity (whole-word match, so *Panamax*
   does not match *Neopanamax*) and the same attribute (bag of words). Spanish entries give the English entity name
   in parentheses, and their attribute is either left in English or translatable word-by-word with the lab's own
   glossary (*año de finalización* → *completion year*).

## Borderline decisions

- **Reformatted answers** (`25 m` vs `25 meters`, `seis cranes` vs `6 cranes`, `2,5 kilómetros`): excluded. The
  fact is the same; the format is cosmetic.
- **Synonymous answers**: LOG-0396 says Cristóbal is the *Atlantic terminus* (gold *Atlantic terminal*), LOG-0285
  says La Boca is in *Balboa district* (gold *Balboa township*). Excluded (CQA-026, CQA-038): the question is the
  benchmark question and the answer carries the same information.
- **Same entity, different attribute** (47 entries): kept. They teach the model about the entity, not the asked
  fact, which is legitimate training data.
- **Leaked items answered wrong**: none exist, so the question of whether to exclude them did not arise.
- **Items answered wrong with no leak** (21 of them): kept; they are honest failures.

The seal accepts exactly this 21-item set and certifies 64.41 %.

## Reproduce

```
python audit.py canalqa_audit.json      # writes report.json
python open_seal.py report.json         # Seal opened. flag: SIGMOID_DECONTAMINATION
```

`audit.py` is standard-library only; `report.json` is the exact report that opened the seal.
