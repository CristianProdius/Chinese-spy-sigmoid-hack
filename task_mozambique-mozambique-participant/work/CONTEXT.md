# Shared brief: "The Professor of Maputo Bay" (Sigmoid challenge)

Root: /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/mozambique/task_mozambique-mozambique-participant
(call it ROOT). Everything below is relative to ROOT unless absolute.

## The task (verbatim essentials)
Write `agent(observation, memory)` in `main.py`; it returns one entry of `observation['legal_actions']`.
`memory` is a dict, empty at the start of every game (module globals survive across games in one process).
We play vs "the Professor", a deterministic planner with several playing styles, on hidden maps.
Each hidden map is played 5 times (game index 0-4; likely one Professor style per game index) and counts
only by our WORST game on it: win=1, draw=1/2, loss=0. 24 hidden maps (3 per group, group = 2*topology+seat,
topology 0-3, seat 0-1). Need >= 65% of map points (31 of 48 half-points) to pass. So we must beat
every style on a map, ~92%+ per-game win rate.

Limits: PyPy 3.10, stdlib only, CPU only, one core, 10 s of thinking per game for all 80 decisions
(+10 s for the first game of each process). Several main.py processes in parallel. Crash, timeout,
non-JSON or illegal action = 0 points for the whole evaluation. main.py <= 2 MB, self-contained.

Game rules as published: ten harbours (sites); each side starts with two boats at its home; 80
simultaneous rounds, ONE action per round for the whole side. Boat capacity 3 goods. Each home starts
with 5 timber + 3 fibre. Building a workshop and each production batch consume 2 timber + 1 fibre from
your warehouse at a manufacturing site; production takes 3 rounds. A third boat costs 4 timber + 2 fibre
at home. Natural stocks start at 4, cap at 6 and regenerate by 1 every 4 rounds. Routes take 1-3 rounds.
Conflicts over shared stock, route departures and contracts favour seat 0 on even rounds and seat 1 on
odd rounds. A contract must be delivered before its deadline round. Raw contracts pay 5 points,
manufactured 12; higher final score wins. Roles: -1 home, 0 timber, 1 fibre, 2 manufacturing.
Goods: 0 timber, 1 fibre, 2 manufactured.

## Files
- `arena.py` - practice SDK: `Arena().reset(group, seed, game)`, `.step(action)`; `python arena.py main.py`
  runs a local evaluation (24 random maps x 5 games, worst game per map). `Arena.request('hello')` works.
- `mozambique-engine` - the real engine incl. the Professor (stripped C++ ELF, nlohmann json, static libstdc++).
- `train-input.json` / `train-output.json` - 64 practice cases and the starter agent's results (it loses 0-44..68).
- `main.py` - starter template (keep its serve() loop).
- `work/script.py` - tiny scripted-probe helper: `python3 work/script.py GROUP SEED GAME '<json list of partial actions>'`
  (each partial action matches the first legal action whose keys equal it, else waits) and prints our state per round.
- PyPy 3.10: `/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3` (the evaluation runtime). CPython 3.12 at python3.

## Observation format (example, group 0 seed 767302775 game 0)
keys: claims[8] (-1 unclaimed, else seat that delivered), enemy_boats (list of {boat,destination,eta,position}
for visible enemy boats), legal_actions, map{contracts[8]{deadline,destination,good,points,quantity},
homes[2] (index = seat), roles[10], routes[10][10] (0 = no route, else rounds), topology},
opponent_score, own{boats[{cargo[3],destination,eta,position}], crafted_deliveries, home, jobs[10],
score, warehouses[10][3], workshops[10]}, round, seat, stocks[10] (null when not visible; home shows 0),
visible[10].
Contracts in the example: 4 raw (quantity 2, 5 pts, deadlines 24/40/56/72), 4 manufactured (quantity 1,
12 pts, deadlines 40/56/72/80). Topology 0 example is a ring 0-1-2-...-9-0.

## Action formats (observed)
{"op":"wait"} | {"op":"sail","boat":b,"destination":site (neighbour only)} |
{"op":"load","boat":b,"good":g,"quantity":q} (from own warehouse at the boat's site) |
{"op":"gather","boat":b,"good":g,"quantity":q} (from natural stock) |
{"op":"unload","boat":b,"good":g,"quantity":q} (into own warehouse at that site) |
{"op":"build_workshop","boat":b} | {"op":"craft","boat":b} | {"op":"deliver","boat":b,"contract":c} |
{"op":"build_boat"}. Engine strings also contain "illegal order", "unknown order".

## Rules confirmed so far by probing
- Sail is one hop to a neighbour; a route of length L issued in round r shows the boat at the destination
  in the observation after round r+L-1 (L=1: arrives the same round). While sailing, `position` is the
  origin, `destination`/`eta` set.
- build_boat is instant (new boat at home, warehouse -4T -2F).
- build_workshop is instant. craft: jobs[site]=2 after the craft round, 1 after the next, then 1
  manufactured good appears in the warehouse at that site (so it is usable 3 rounds after crafting).
- Delivering a raw contract claims it for that seat (claims[c] = seat) and pays immediately.
- Stocks regenerate on rounds divisible by 4 (seen 4->5 between round 3 and 4).
- Unopposed, the Professor claims e.g. a nearby raw contract by round 3 and the first manufactured
  contract around round 30, and scores 44-68 of 68 points.

## Machine rules (IMPORTANT)
This dev server (48 cores) is shared and heavily loaded (load ~360). Use at most 6 parallel processes
at a time, run heavy loops under `nice -n 10`, and never kill processes you did not start. Prefer PyPy
for long simulation runs. Do not edit files outside your own output folder (listed in your task) except
creating new files there. Do not commit, push or open PRs.
