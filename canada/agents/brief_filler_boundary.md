# Brief: filler and boundary-case writer

Read `agents/context.md` first, and `agents/brief_train_writer.md` for style and format rules (same
JSONL format, same validation, invent every event).

## Part A: hazard-free filler (label "none")
Write 300 English + 300 French short passages (1-3 sentences, 8-50 words) of the kind that fill real
incident reports but name NO hazard and give no clue to one: places and dates, evacuations, shelters,
relief funds, Red Cross, military help, insurance and damage figures, injuries and deaths in neutral
words, officials' statements, inquiries, repairs, school and road closures, power restored, historical
asides. Vary eras (1900-2020) and wording widely; French is natural Canadian French.
Do not use words that point to one hazard (water, snow, fire, smoke, wind, ice, rain, crash, disease...).
Files: `data/gen/filler_partNN.jsonl` (at most 60 lines per part), label "none".

## Part B: boundary cases (labels = the 9 classes)
Write 220 reports (110 English, 110 French, 40-120 words) that sit on the class boundaries and carry
the correct primary label, about 10 per pair below, split across both languages:
ice storm / freezing rain -> winter (not storm); blizzard -> winter; hail or tornado -> storm;
storm surge / hurricane coastal flooding where the storm is the story -> storm; spring breakup ice-jam
flood -> flood; heat wave deaths -> drought; dust storms in a dry year -> drought; town or building
fire -> industrial (not wildfire); a forest fire that reaches a town -> wildfire; mine explosion or
cave-in -> industrial; gas or chemical explosion -> industrial; blackout or bridge/dam collapse ->
industrial; snow avalanche (even onto a road or railway) -> ground; tsunami -> ground; earthquake ->
ground; rockslide on a highway -> ground; train derailment / collision -> transport; ship lost in a
gale -> transport; plane crash in fog or snow -> transport; outbreak after a flood -> epidemic when the
outbreak is the story; waterborne illness -> epidemic.
Files: `data/gen/boundary_partNN.jsonl` (at most 40 lines per part).

## Finish
Run the validator on each part set and fix every problem. Reply ONLY with the two validator outputs.
