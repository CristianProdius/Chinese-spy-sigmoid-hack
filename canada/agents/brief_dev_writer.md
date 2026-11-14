# Brief: held-out proxy dev set writer

Read `agents/context.md` first. Your task names your ERA STYLE and your OUTPUT PREFIX.

The vault shows no score, so we judge models on a proxy dev set: invented reports that look as much as
possible like the real ones (written by people, Canada, English and French, 1900-2020). Your set must
be HARD in the ways real reports are hard. It is never used for training. Do not read any file in
`data/gen/` other than your own, and do not read the brief for training writers.

## Amount
For EACH of the 9 classes: 10 English + 10 French reports (180 lines). JSONL parts of at most 45
lines: `<OUTPUT PREFIX>_part01.jsonl`, ... One object per line:
{"text": "...", "label": "<class>", "lang": "en" | "fr"}. Generate the JSON with a small Python
script per part so it stays valid.

## What real reports look like (make yours like this)
- Length varies a lot: some are one terse line ("Hail damaged crops near the town."), most are 2-5
  sentences, some are long paragraphs (up to ~160 words). Median about 60 words.
- Many spend most words on impacts (evacuations, damage, costs, casualties, relief) and name the hazard
  only once, sometimes indirectly ("the river rose", "the ice gave way", "fire swept the business
  district", "the vessel went down", "a contagious fever").
- About a quarter mention a second hazard (a cause, a side effect, context). The label is the primary
  hazard, per the rules in context.md. Include boundary cases: ice storm (winter), storm surge (storm),
  heat wave (drought), town/building fire (industrial), avalanche and tsunami (ground), blackout or
  bridge/dam collapse (industrial), shipwreck/plane/train/road crash (transport).
- Natural vocabulary of the era and region; French is natural Canadian French written as its own
  report (not translations, no EN/FR pairs of one event).
- Spread events across provinces and territories, seasons and decades. Invent every event (hard rules
  in context.md).

## Finish
Run `.venv/bin/python tools/validate_gen.py <OUTPUT PREFIX>_part*.jsonl`, fix every problem, and reply
ONLY with the validator output plus one line of notes.
