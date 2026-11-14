# The Professor: measured behaviour

Everything below was measured with `mozambique-engine` through `arena.py`: 2,793 engine games on 304 maps.
The binary decode in `work/binary/PROFESSOR.md` explains the mechanics. This file checks that decode
against the engine and adds the numbers an agent needs: speeds, targets and reactions per style.
"Round" always means the round in which the action is issued (0..79), as in `observation.round`.

## TL;DR

1. **Game index is not a style.** No feature of the Professor's play depends on the game index (permutation
   test p >= 0.06 on all 22 features). The decoded style, `perm[game]` with `perm = style_permutation(seed)`,
   separates 21 of 22 features at p <= 0.02, most at p < 0.003. So the 5 games of a map are its 5 styles, in a shuffled order
   that depends on the seed. Under worst-of-5, every map has to be beaten by all 5 styles. Style does not
   depend on seat or topology.
2. **Styles differ mostly in tempo, not in score.** Mean passive scores are 52-55 for every style. The
   differences:
   * style 1 (A=1.15) takes all raw contracts early: contract 3 at round 14 against 27-51 for the others,
     and its first manufactured contract comes late (round 37).
   * style 4 (W=8, B=0) is first to manufacture: first manufactured contract at round 24, and only 66% of
     its games start with a raw contract.
   * style 3 (A=0) takes the fewest raw contracts (2.5) and the most manufactured (3.5).
   * styles 0 and 2 produce identical public traces on 64 of 304 maps.
3. **Unopposed, the Professor scores 27-68**: median 56, mean 54. It claims about 3.1 raw and 3.2
   manufactured contracts. All 8 are claimed in only 6% of games: it leaves 1-2 unclaimed in 78% and 3-4 in 16%. Its first delivery is around round 5,
   paid from its home stock at the fastest possible time. Its first manufactured delivery is around round
   30 (16-66). It always runs exactly 2 boats (no third boat seen in 40 fully watched games) and builds
   its workshop at one manufacturing site, the one nearest its home in 33 of 38 games.
4. **It does not react to our boats.**
   * Two boats parked on the stock it is about to gather changed nothing in 40 of 40 games.
   * Single parked boats changed nothing in 349 of 360 runs.
   * All 11 changes were route-departure collisions while our boat was still sailing (rounds 3-7), and
     the decoded model reproduces each of them exactly.
   * It never contested or sped up for a contract we were racing for: in 641 races its claim round never
     moved before our delivery.
5. **It only re-plans when it has to:** when we claim one of its target contracts, when a sail is blocked,
   or when a gather fails. After a steal it replans the next round with its cargo still on board.
   * A stolen raw contract costs it 3.5 points on average; a manufactured one costs 8.4.
   * It picks up a contract it had skipped in 28% of raw steals and 42% of manufactured steals. Style 3
     recovers best: 66% pick-up, only -6.2 points per manufactured steal.
   * Draining its first natural stock before it arrives changes its plan in 31 of 38 cases but costs it
     only 1.3 points on average.
6. **What we can win.**
   * Each manufactured contract taken on its own beats all 5 styles on 88-96% of maps. The Professor's
     fastest style claims it 10-22 rounds after our realistic fastest delivery (median).
   * Raw contracts are a geometry coin-flip: a single raw contract beats all 5 styles on only 60-72% of
     maps.
   * The hard part is sequencing, not any single contract. One action per round means we can't take
     everything at minimum time.
   * The Professor's median score by round is 10 by round 20, 29 by 40, 44 by 60 and 56 by 80
     (score-curve table below).

## Data and tools (all in this folder)

| file | what |
|---|---|
| `data/passive_*.jsonl` | 1,520 passive games (we always wait): 304 maps, 38 per group, all 5 games each. 240 random maps (fixed RNG 20261114) + the 64 `train-input.json` maps. Per game: map, claim round and claimer per contract, Professor score timeline, enemy sightings at our home, result. Matches `train-output.json` 64/64. |
| `data/passive_summary.csv` | one row per passive game with decoded style and features |
| `data/rush_w*.jsonl`, `data/rush_rows.json` | 641 races (640 unique, one rerun after a worker restart): we rush one contract (16 maps x 5 games x 8 contracts), full claim vectors, our actions, sightings |
| `data/park_w*.jsonl` | 360 runs: boat 0 parked at each non-home site (8 maps x 5 games x 9 sites), sightings and stock at the site |
| `data/routes.json` | stitched Professor sightings, gathers and workshop dwell for 40 (map, game) pairs |
| `data/drain_w*.jsonl`, `data/drain_rows.json` | 80 runs: both boats drain (or only visit, "decoy") the Professor's first natural source |
| `data/mfg_w*.jsonl` | 192 runs: our first manufactured delivery with three simple plans (16 maps x 4 contracts x 3 plans) |
| `data/winnable.csv` | per map x contract: our bound and realistic time, Professor claim per style, win flags |
| `reports/*.txt` | full output of every analysis script (tables below are copied from them) |
| `tools/` | `passive.py`, `observe.py` (park and watch), `runner.py` (scripted plans), `rush.py`, `park_sweep.py`, `drain.py`, `mfg_check.py`, `sweep.py` (resumable job queue), `mintime.py` (analytic fastest times), `styles.py` (style permutation from the decode), `replay_park.py` (replays runs in `work/binary/professor.py`), and the `analyze_*`/`report_*` scripts |

Regenerate the tables with, for example, `python3 tools/report_passive.py`. Each script reads `data/`.

## 1. Passive play (we always wait)

### 1.1 By decoded style

| style (B, A, W) | games | Prof score | raw claimed | manuf. claimed | first claim rnd | first manuf. rnd | last claim rnd | starts raw | all 8 claimed |
|---|---|---|---|---|---|---|---|---|---|
| 0 (3.5, 0.85, 8) | 304 | 54.4 (med 53, 32-68) | 3.03 | 3.27 | 8.4 (med 6, 2-34) | 29.1 (med 28, 18-50) | 60.1 (med 60) | 85% | 6% |
| 1 (1.8, 1.15, 0) | 304 | 54.5 (med 56, 27-68) | 3.69 | 3.00 | 5.1 (med 4, 2-23) | 37.4 (med 37, 18-66) | 62.1 (med 63) | 98% | 11% |
| 2 (1.8, 0.85, 0) | 304 | 55.0 (med 56, 32-68) | 3.26 | 3.23 | 7.1 (med 5, 2-32) | 31.1 (med 31, 16-55) | 60.7 (med 61) | 88% | 7% |
| 3 (3.5, 0.0, 0) | 304 | 54.2 (med 56, 34-68) | 2.52 | 3.47 | 9.1 (med 6, 2-34) | 29.2 (med 29, 17-50) | 63.7 (med 64) | 79% | 3% |
| 4 (0.0, 0.85, 8) | 304 | 51.9 (med 51, 32-68) | 2.98 | 3.08 | 11.9 (med 7, 2-36) | 25.4 (med 24, 16-66) | 63.5 (med 64) | 66% | 4% |

Claim rate and median claim round per contract and style. Contracts are always: 0 timber<24, 1 fibre<40,
2 timber<56, 3 fibre<72 (2 goods, 5 pts), 4-7 manufactured <40/56/72/80 (1 good, 12 pts). Only the
destinations change between maps.

| contract | style 0 | style 1 | style 2 | style 3 | style 4 |
|---|---|---|---|---|---|
| 0 T<24 | 46% @ 6 | 86% @ 7.5 | 60% @ 7 | 37% @ 6 | 48% @ 7 |
| 1 F<40 | 69% @ 20 | 89% @ 10 | 74% @ 11 | 44% @ 12 | 63% @ 29 |
| 2 T<56 | 89% @ 27 | 95% @ 10 | 92% @ 14 | 73% @ 21 | 90% @ 26 |
| 3 F<72 | 99% @ 35 | 99% @ 14 | 99% @ 27 | 97% @ 51 | 97% @ 42 |
| 4 M<40 | 54% @ 30 | 37% @ 35 | 50% @ 31 | 64% @ 30 | 49% @ 26 |
| 5 M<56 | 80% @ 39 | 73% @ 42 | 77% @ 40 | 87% @ 41 | 73% @ 41.5 |
| 6 M<72 | 97% @ 50 | 93% @ 53 | 97% @ 51 | 97% @ 49.5 | 91% @ 51 |
| 7 M<80 | 96% @ 51 | 97% @ 56 | 98% @ 52 | 99% @ 55 | 95% @ 58 |

Most common claim orders (R raw, M manufactured):
* style 1: `RRRRMMM` 94, `RRRRMM` 42.
* style 2: `RRRRMMM` 33, `RRRMMM` 25.
* style 0: `RRRMMM` 26, `RRMMRM` 13, `RMMRRM` 13.
* style 3: `RRRMMM` 18, `RMMMRM` 17, `RMMMMR` 15.
* style 4: `RMRRMM` 21, `RMRMRM` 16, `MRRRMM` 13.

### 1.2 Does game index mean a style? No.

Within-map permutation test: shuffle the 5 labels inside each map 400 times and compare the spread of
per-label means (`reports/style_test_*.txt`).

| feature | mean by game index 0..4 | p | mean by style 0..4 | p |
|---|---|---|---|---|
| score | 54.1 / 53.6 / 54.3 / 54.0 / 54.1 | 0.39 | 54.4 / 54.5 / 55.0 / 54.2 / 51.9 | <0.003 |
| raw claimed | 3.12 / 3.07 / 3.11 / 3.09 / 3.08 | 0.92 | 3.03 / 3.69 / 3.26 / 2.52 / 2.98 | <0.003 |
| first manuf. round | 30.5 / 30.6 / 30.5 / 30.3 / 30.1 | 0.88 | 29.1 / 37.4 / 31.1 / 29.2 / 25.4 | <0.003 |
| first claim round | 8.4 / 8.4 / 8.0 / 8.3 / 8.5 | 0.62 | 8.4 / 5.1 / 7.1 / 9.1 / 11.9 | <0.003 |
| contract 1 claim round (80 if never) | 37.5 / 38.9 / 36.3 / 37.6 / 39.3 | 0.65 | 39.2 / 18.9 / 32.4 / 51.9 / 47.2 | <0.003 |

Every feature is flat by game index (p >= 0.06). Every feature but one separates by style at p <= 0.02;
the exception is whether contract 3 is taken at all, which all styles do 97-99% of the time. Other checks:
* The map and seat are identical across the 5 games of a seed (304 of 304).
* On a map the 5 games give 5 distinct claim vectors in 214 maps, 4 in 84 and 3 in 6.
* Identical pairs are spread evenly over game-index pairs. Over style pairs they concentrate on (0, 2):
  64 maps.
* The game index with the map's highest Professor score is uniform (115-132 per index).
* By seat the Professor scores 54.4 / 53.6. By topology it scores 51.0 / 55.8 / 53.8 / 55.4 for
  topologies 0-3; ring maps (topology 0) are its weakest.

### 1.3 How early does play reveal the style? (public info only: claims and score)

The binary decode lets a clone identify the style earlier from `enemy_boats` and stocks. This table is
the lower bound when only claims are used.

| style | median round when unique | identifiable by round 10 | by round 20 | never (twin style on this map) |
|---|---|---|---|---|
| 0 | 31 | 17% | 31% | 76 / 304 |
| 1 | 8 | 62% | 85% | 18 |
| 2 | 19 | 24% | 52% | 80 |
| 3 | 25 | 20% | 37% | 15 |
| 4 | 6 | 74% | 89% | 0 |

Styles 0 and 2 are the hard pair: same A, and their public traces coincide on 64 maps. Module globals
survive across games, and each map plays every style once, so a style already seen on the same map can
be crossed off.

### 1.4 Speed vs the fastest possible trip

`tools/mintime.py` gives a single-contract lower bound for a side starting at home, one action per round:
* raw: `min over s in {home} + sites of that good of d(home,s) + 1 + d(s,dest)`;
* manufactured: `11 + d(home,m) + d(m,dest)`, minimised over the 2 manufacturing sites.

Over 1,520 games the Professor never beat this bound.

Median rounds between its claim and its own bound:

| contract | style 0 | style 1 | style 2 | style 3 | style 4 | all |
|---|---|---|---|---|---|---|
| 0 | 2 | 2 | 2 | 0 | 1 | 2 |
| 1 | 15 | 3 | 5 | 6 | 22 | 8 |
| 2 | 21 | 4 | 8 | 15 | 18 | 9 |
| 3 | 28 | 7 | 20 | 44 | 35 | 27 |
| 4 | 12 | 18 | 13 | 12 | 8 | 12 |
| 5 | 20 | 24 | 21 | 23 | 23 | 23 |
| 6 | 31 | 34 | 32 | 31 | 32 | 32 |
| 7 | 33 | 38 | 34 | 37 | 40 | 36 |

Its first claim of the game lands exactly at the bound in 55% / 86% / 69% / 56% / 2% of games for
styles 0-4. Per the decode, such first deliveries are usually paid from its home warehouse. Style 4
almost never does this because it goes to the workshop first.

### 1.5 Score curve (what we must stay ahead of)

Professor score accumulated before each round, passive play, median / p90:

| style | rnd 10 | rnd 20 | rnd 30 | rnd 40 | rnd 50 | rnd 60 | rnd 70 | rnd 80 |
|---|---|---|---|---|---|---|---|---|
| 0 | 5 / 10 | 10 / 15 | 17 / 29 | 34 / 39 | 39 / 46 | 46 / 56 | 51 / 63 | 53 / 63 |
| 1 | 10 / 10 | 15 / 20 | 20 / 22 | 32 / 39 | 39 / 44 | 44 / 56 | 56 / 63 | 56 / 68 |
| 2 | 5 / 10 | 10 / 20 | 17 / 27 | 32 / 39 | 39 / 46 | 46 / 56 | 56 / 63 | 56 / 63 |
| 3 | 5 / 10 | 5 / 12 | 17 / 24 | 27 / 34 | 34 / 46 | 46 / 56 | 51 / 63 | 56 / 63 |
| 4 | 5 / 5 | 5 / 12 | 17 / 22 | 27 / 34 | 34 / 44 | 42.5 / 51 | 51 / 56 | 51 / 63 |

Final score histogram: 51 (398 games), 56 (357), 63 (192), 58 (154), 46 (128), 68 (91), 44 (81), 39 (52), the rest below 40.

## 2. Reactivity

### 2.1 Racing it for one contract (641 runs)

Plan: raw = load 2 at home, sail the shortest path, deliver. Manufactured = boat A hauls 2T+1F and builds
the workshop, boat B hauls 2T+1F, crafts, then loads the product and delivers.

| | raw (321) | manufactured (320) |
|---|---|---|
| we delivered | 255 (79%) | 305 (95%) |
| our time equals the analytic bound | 92% (rest +1) | 0% (+3..8, see 4.2) |
| we won every race where our time beat its passive claim | 251/251 | 305/315 (the 10 misses: our real plan was slower than the bound) |
| **it claimed the raced contract earlier than in passive play** | **0** | **0** |
| it claimed it later than passive play | 0 | 0 |
| its plan changed only after our delivery | 192 | 264 |
| no change at all | 121 | 52 |
| changed although we never delivered (route/stock collisions) | 7 | 2 |

When we took a contract it claims in passive play:

| | raw steals (191) | manufactured steals (245) |
|---|---|---|
| its score change, mean | -3.5 | -8.4 |
| it lost the full value | 68% (-5) | 56% (-12) |
| it picked up a contract it had skipped | 28% | 42% |
| it dropped another contract it used to take | 18% | 5% |
| other contracts whose claim round moved, mean | 3.4 | 2.7 |

By style, the manufactured-steal cost is -8.2 / -9.4 / -10.1 / -6.2 / -8.4 for styles 0-4. Style 3
replaces the lost contract 66% of the time; styles 1 and 2 only 22-24%. Taking a contract it never
claims barely touches it: -0.1 / -0.2 points.

Typical steal (map group 0 / seed 275196493, game 1): passive claims `[5,-,11,57,-,34,50,71]`. We deliver
contract 2 at round 5. It then claims `[5,-,US5,58,-,34,40,68]`: it moves contract 6 ten rounds earlier
and contract 7 three rounds earlier, and its score drops 51 to 46.

### 2.2 Parking our boats (360 single-boat runs, 80 two-boat runs)

| parked at | runs | Professor plan changed |
|---|---|---|
| enemy home | 40 | 6 |
| timber site | 120 | 0 |
| fibre site | 120 | 2 |
| manufacturing site | 80 | 3 |
| both boats on its next stock site, no gathering ("decoy") | 40 | **0** |

Its boats docked next to ours in 258 of the single-boat runs, and nothing changed. I replayed all 11
changed runs, plus 12 unchanged controls, in the decoded model (`tools/replay_park.py`).
* The model matches the engine exactly in 23 of 23 runs (all claims and the final score).
* In every changed run, the Professor's sail failed in round 3, 4, 5 or 7. Our boat departed on the same
  route in the same round, on a round where our seat had priority.

So the only effect of our boats is physical: route-departure collisions, stock and contract conflicts.
It does not read where our boats are. A 1-round delay early can cascade: on 6/4047820084 a blocked sail
made it re-plan into a better line (41 to 53 points).

### 2.3 Draining its stock (80 runs)

For 40 (map, game) pairs I took the Professor's first natural-stock gather from the watched routes.
Both our boats sailed there and gathered everything they could carry (5.3 units on average). The decoy
variant made the same trip without gathering.

| | runs | plan changed | its score change |
|---|---|---|---|
| decoy (just be there) | 40 | 0 | 0 |
| drain, done before its first gather | 38 | 31 | mean -1.3 (27 zero, 6 lost 5-12, 3 gained 10-12) |
| drain, arrived too late | 2 | 1 | 0 |

It simply re-routes to another source. Denial alone is weak: it ties up both our boats for the opening
(they arrive at round 7, range 2-11) and takes about 1 point from it. It is only worth doing when the
stock is ours to use anyway.

### 2.4 Contesting

It never contested a contract we were about to deliver (0 of 641 races). It never claimed earlier, and
it never waited to block us. The only races it "wins" are those where its plan was faster anyway. On
an exact tie the engine's priority rule decides: even rounds go to seat 0, odd rounds to seat 1. Our
seat-0 rush on 0/275196493 game 4 took contract 0 in round 8, its passive claim round, because 8 is even.

## 3. Its routes (40 fully watched games, `data/routes.json`)

Method: park one boat at each of the 9 non-home sites in separate runs. Merge only runs where its claims
match passive play, so the merged trace is the passive Professor.

* **Boats:** always 2. No sighting of a boat index 2 in any game. That agrees with the decode: it never
  builds a boat.
* **Workshop:**
  * One main manufacturing site in 25 of 40 games, both sites in 13.
  * The main site is the one nearest its home in 33 of 38 games.
  * It first docks there at round 8 (median, range 3-45) and keeps a boat there about half the game.
    The two-boat pattern is one boat camped at the workshop crafting while the other ferries goods.
* **Natural stock:** about 6 gathers seen per game, the first around round 11 (6-24). Sizes: 3 units
  103 times, 2 units 90, 1 unit 50. Timber 134, fibre 109. Its first raw deliveries come from home stock
  (5T+3F), so its first natural-site visit is for the workshop or a later raw contract.
* **Our home:** its boats pass through our home in 15% of passive games, and 167 of those 226 games are
  ring maps (topology 0), where our home lies on its shortest paths. Those sightings are in
  `enemy_at_home` in the passive records.

## 4. Per contract: how fast it is, and what we can take

### 4.1 Single contract, per style

Our realistic time = analytic bound for raw contracts (the engine hit it in 92% of rushes) and
bound + 2 for manufactured (see 4.2). "We beat" means we deliver before its passive claim, or on the
same round with our priority, or it never claims the contract. Data: 304 maps; per-map rows in
`data/winnable.csv`.

| contract | our bound (med) | our realistic (med) | its bound (med) | its claim median by style 0/1/2/3/4 (claim rate) | we beat its fastest possible trip | we beat style 0/1/2/3/4 | we beat all 5 |
|---|---|---|---|---|---|---|---|
| 0 T<24 | 6 | 6 | 6 | 6 (46%) / 7.5 (86%) / 7 (60%) / 6 (37%) / 7 (48%) | 49% | 76/64/71/80/78 % | 60% |
| 1 F<40 | 6 | 6 | 6 | 20 (69%) / 10 (89%) / 11 (74%) / 12 (44%) / 29 (63%) | 50% | 86/70/77/88/98 % | 68% |
| 2 T<56 | 6 | 6 | 6 | 27 (89%) / 10 (95%) / 14 (92%) / 21 (73%) / 26 (90%) | 46% | 80/70/75/81/78 % | 62% |
| 3 F<72 | 6 | 6 | 6 | 35 (99%) / 14 (99%) / 27 (99%) / 51 (97%) / 42 (97%) | 49% | 85/77/81/88/98 % | 72% |
| 4 M<40 | 18 | 20 | 18 | 30 (54%) / 35 (37%) / 31 (50%) / 30 (64%) / 26 (49%) | 31% | 98/100/98/97/89 % | 88% |
| 5 M<56 | 18 | 20 | 18 | 39 (80%) / 42 (73%) / 40 (77%) / 41 (87%) / 41.5 (73%) | 29% | 98/100/98/98/94 % | 92% |
| 6 M<72 | 18 | 20 | 18 | 50 (97%) / 53 (93%) / 51 (97%) / 49.5 (97%) / 51 (91%) | 27% | 99/100/99/99/98 % | 96% |
| 7 M<80 | 18 | 20 | 18 | 51 (96%) / 56 (97%) / 52 (98%) / 55 (99%) / 58 (95%) | 29% | 99/99/99/99/95 % | 95% |

Slack on manufactured contracts: its fastest claim over the 5 styles minus our realistic time.

| contract | median slack | p10 | min |
|---|---|---|---|
| 4 | 10 | -1 | -7 |
| 5 | 15 | 1 | -6 |
| 6 | 21 | 3 | -5 |
| 7 | 22 | 3 | -5 |

Results are the same for both seats: raw 66% / 65%, manufactured 94% / 92% for seat 0 / seat 1.

How to read this:
* Raw contracts are a geometry draw. Our home and its home are the two farthest sites, so each raw
  destination is near one side. Contract 0 is cheap for whoever is near it, and style 1 also takes
  contracts 1-3 by round 10-14. Raw contracts where its bound is below ours are lost against style 1
  and are best left alone.
* Manufactured contracts are where the game is decided: 48 of the 68 points. It averages only 3.2 of
  them, typically the first around round 30 (24 for style 4), then about one every 10 rounds. Its
  workshop runs on one site and two boats.
* Any of the four manufactured contracts is ours if we go first. The question is how many we can
  produce before its claim rounds: about 30, 40, 50 and 52-58 for contracts 4-7.

### 4.2 How fast can we really make the first manufactured good?

These are engine runs on 16 maps with game 0; the Professor rarely interferes with this.

| plan | delivered | rounds later than the bound `11 + d(home,m) + d(m,dest)` | median |
|---|---|---|---|
| v1: A loads 2T+1F, B loads 2T+1F; boat order decides who acts | 59/64 | +3: 28, +4: 18, +5: 7, +6: 6 | +4 |
| v2: same, but sails get priority | 60/64 | +1: 12, +2: 17, +3: 18, +4: 3, +5: 7, +6: 3 | +3 |
| v3: A loads 3T, B loads 1T+2F and builds and crafts; sails get priority | 60/64 | +1: 28, +2: 15, +3: 11, +4: 3, +5: 3 | +2 |

So a simple two-boat opening delivers the first manufactured good around round 13 + d(home,m) +
d(m,dest). The median is 20. Its fastest style's first manufactured claim has median 24-37 depending on
style.

## 5. What this means for our agent

1. Treat the 5 games of a map as 5 different opponents with a shuffled order. Win against each one.
   Track styles already seen on the same map in module globals; `obs['map']` identifies the map.
2. It has no opponent model. We can plan against a fixed, predictable schedule (exactly predictable
   with `work/binary/professor.py` once the style is known). It will not race us and will not defend.
3. **Steal its next target, one round early or on our priority round.** Every steal costs it the
   trip. Manufactured steals cost it 8.4 points on average, and its replacement rate is low for styles
   1 and 2. Raw steals cost only 3.5, and they are only possible where geometry favours us.
4. Manufactured contracts are almost always reachable first; the limit is our production rate. A
   strong plan is a fast first workshop by round ~20, then keeping a boat at the workshop while the
   other ferries 2T+1F. This copies its own pattern, but starting earlier and aimed at contracts in
   its plan order.
5. Don't spend actions on denial or blocking for their own sake. Denial took ~1 point from it per
   two-boat trip. Route blocking only pays when our sail is useful anyway, but a single block can
   re-route it a long way.
6. Ring maps (topology 0) are its weakest (mean 51.0), the ladder (topology 1) its strongest (55.8).
   Its worst style overall is 4 (51.9), and style 4 is also the easiest to recognise (by round 6 median).

## Caveats

* Our "realistic" times are single-contract times. They ignore the one-action-per-round budget across
  several contracts, so they are upper bounds on what a full plan can take.
* Rush, park and drain experiments ran on 16, 8 and 8 maps (2, 1 and 1 per group). Passive statistics use
  all 304 maps.
* `observe.py` sails boat 0 along Dijkstra next hops with its own tie-breaking. On a few maps that route
  crossed the Professor's departure, which is the source of the 11 park changes.
