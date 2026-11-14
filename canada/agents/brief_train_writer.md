# Brief: training-data writer

Read `agents/context.md` first. Your task names your CLASSES and your OUTPUT PREFIX.

Write NEW labelled incident reports that read like real ones written by people (archivists, newspaper
reporters, government emergency officials) between 1900 and 2020, so a bag-of-words model learns the
vocabulary real reports use. The given corpus is templated and narrow: do NOT copy its sentence
patterns (you may skim ~10 rows of `task/corpus.csv` to see what to avoid).

## Amount
For EACH of your classes: 60 English + 60 French reports (360 lines in all for 3 classes).
Write JSONL parts of at most 40 lines: `<OUTPUT PREFIX>_part01.jsonl`, `_part02.jsonl`, ...
One object per line: {"text": "...", "label": "<class>", "lang": "en" | "fr"}.
Writing a small Python script per part that `json.dumps` a list is the safest way to keep JSON valid.

## Make it varied and realistic
- Length: mix terse entries (15-30 words), 2-4 sentence summaries (40-80) and longer narratives
  (90-160). Median about 60 words.
- Eras: about a third each in early-1900s newspaper/archival wording, mid-century, and modern
  government summary style. Older terms where they fit (steamer, conflagration, la grippe, vapeur).
- Use a wide vocabulary: synonyms, verbs, indirect phrasing ("the river rose two metres overnight",
  "the ice let go", "hundreds fell ill"). Cover the term lists below AND go beyond them.
- About 20% of reports mention a secondary hazard (cause, side effect, context) while the label stays
  the primary hazard, per the rules in context.md.
- French must be natural Canadian French written as its own report, not a translation. Do not write
  English/French pairs of the same event.
- Include places, dates, numbers, casualties, damage and response details naturally, as real reports do.
- No two reports may share a sentence skeleton. Invent every event (hard rules in context.md).

## Term hints (cover these and more; each hint list is for its class only)
- flood: flooding, floodwaters, overflowed, burst its banks, spring freshet, runoff, snowmelt, ice jam,
  flash flood, dyke breached, sandbagging, inundated, washout | inondation, crue printaniere, debordement,
  embacle, montee des eaux, digue, sacs de sable, submerge, refoulement d'egout, pluies diluviennes
- storm: thunderstorm, hail, hailstones, tornado, twister, funnel cloud, downburst, hurricane, tropical
  storm, gale, windstorm, storm surge, lightning, squall | orage, grele, tornade, trombe, rafales, ouragan,
  tempete tropicale, onde de tempete, foudre, microrafale, vents violents
- winter: snowstorm, blizzard, heavy snowfall, ice storm, freezing rain, sleet, whiteout, drifting snow,
  extreme cold, cold snap, wind chill, frostbite | tempete de neige, bordee de neige, poudrerie, verglas,
  pluie verglacante, gresil, froid extreme, vague de froid, refroidissement eolien, engelures
- wildfire: forest fire, wildfire, bush fire, grass fire, prairie fire, crown fire, water bombers,
  firebreak, smoke | feu de foret, incendie de foret, feu de broussailles, bombardiers d'eau, coupe-feu
- drought: drought, dry spell, crop failure, parched, dust storms, soil drifting, water shortage, heat
  wave, extreme heat, heat stroke, humidex | secheresse, temps sec, mauvaises recoltes, tempetes de
  poussiere, penurie d'eau, canicule, vague de chaleur, coup de chaleur
- ground: landslide, rockslide, rock fall, mudslide, debris flow, slope failure, sinkhole, subsidence,
  avalanche, snowslide, earthquake, tremor, aftershock, magnitude, tsunami | glissement de terrain,
  eboulement, coulee de boue, affaissement, avalanche, seisme, tremblement de terre, secousse, tsunami
- industrial: fire destroyed a hotel/factory/warehouse/church/city block, conflagration, blaze,
  explosion, blast, gas leak, chemical spill, oil spill, toxic release, mine explosion, cave-in,
  bridge collapse, roof collapse, dam failure, blackout | incendie, brasier, explosion, deflagration,
  fuite de gaz, deversement, coup de grisou, effondrement, rupture de barrage, panne generalisee
- transport: derailment, collision, level crossing, plane crash, airliner, float plane, helicopter,
  sank, foundered, capsized, ran aground, shipwreck, ferry, steamer, schooner, bus crash, pileup |
  deraillement, collision, passage a niveau, ecrasement d'avion, hydravion, naufrage, chavire,
  echouement, traversier, vapeur, goelette, accident d'autobus, carambolage
- epidemic: epidemic, outbreak, influenza, pandemic, smallpox, cholera, typhoid, diphtheria, scarlet
  fever, poliomyelitis, measles, tuberculosis, meningitis, whooping cough, SARS, H1N1, COVID-19,
  quarantine, cases, vaccination, contaminated water | epidemie, eclosion, grippe, pandemie, variole,
  cholera, typhoide, diphterie, scarlatine, poliomyelite, rougeole, tuberculose, coqueluche, quarantaine
(Write French with its proper accents; the hints drop them only for brevity.)

## Finish
Run `.venv/bin/python tools/validate_gen.py <OUTPUT PREFIX>_part*.jsonl` and fix every BAD line,
duplicate and language mismatch. Your final reply is ONLY the validator output plus one line of notes.
