# The Professor of Maputo Bay: exact game rules (black-box probed)

All of this was established by probing `mozambique-engine` through `arena.py`, then checked by
`validate_sim.py`, which replays games against the engine and compares every observation with
`sim.py`. Validation totals are at the end. The engine protocol has only four commands: `hello`,
`reset`, `step` and `quit`. `hello` returns `{"games_per_map": 5, "protocol": 5, "rounds": 80}`.
There is no state-setting command, so the opponent can only be observed, never controlled.

## 0. What matters most for strategy

1. **One action per side per round**, 80 rounds. That is the real budget: every sail hop, load, unload, gather, craft and
   deliver costs one of your 80 actions. Sailing boats keep moving while other boats act, so parallel boats help.
2. **Priority alternates:** seat 0 wins on even rounds, seat 1 on odd rounds. Only three things conflict: a gather on the same
   stock (the loser fails if too little is left), a deliver of the same contract, and a departure on the same route (undirected
   edge) in the same round. **A lost conflict wastes the whole action.** Time contested moves for your priority rounds.
3. Manufactured goods: a workshop (2T+1F) is needed once per mfg site, then each craft takes 2T+1F from **that site's**
   warehouse and yields 1 M there 3 rounds later. M contracts pay 12 (48 of the 68 total); raw contracts pay 5 for 2 goods.
4. Capacity is 3 goods per boat, the most is 3 boats (one `build_boat`, 4T+2F at home), and you start with 5T+3F at home. Stocks start at 4,
   regenerate +1 every 4 rounds (19 times in a game) and cap at 6. So one site yields at most 4 + 19 = 23 goods per game,
   and only if it is harvested before it sits at the cap. The 6 raw sites are shared with the opponent.
5. A contract is deliverable while `round < deadline`, from cargo only, and the first to deliver claims it. Equal final scores are a **draw**.
6. You see the stocks and enemy boats only at your home, where your boats are docked, and at your workshops.
   Enemy cargo, warehouses and workshops are never visible.
7. Return the exact dict from `legal_actions`. Anything else is an error and costs the whole evaluation.

Notation: `r` is the round index shown in `observation.round` (0..79). "obs r" is the observation
the agent sees before it chooses its round-r action.

## 1. Setup

* 10 sites; `roles[i]`: -1 home, 0 timber, 1 fibre, 2 manufacturing. Goods: 0 timber (T), 1 fibre (F), 2 manufactured (M).
* Each side starts with **2 boats docked at its home** and **5 T + 3 F** in its home warehouse. Every other warehouse is empty.
  Each seat has its own warehouses, workshops and jobs at every site.
* Natural stock: every timber or fibre site starts at **4**. Home and manufacturing sites always have stock 0.
* Boat capacity: **3 goods in total**, any mix.
* At most **3 boats** per side. With 3 boats, `build_boat` is never offered, even with 4 T + 4 F at home. So only one extra boat can be built.
* `seat = group % 2`, `topology = group // 2`.

## 2. A round

Both sides submit **one action each for the whole side** (not one per boat). The engine resolves round r like this:

1. **Priority.** The priority seat is `r % 2`: seat 0 on even rounds, seat 1 on odd rounds.
2. **Priority seat's action** is applied.
3. **Other seat's action** is re-checked against the updated state using the same legality
   conditions as `legal_actions` (section 3). If it is still legal it is applied. Otherwise it has
   **no effect at all**: no partial result, the round is lost, and goods stay in the cargo. Only
   three interactions can make it fail:
   * **Same stock (gather):** the loser's gather succeeds only if the remaining stock is still at least its quantity.
     There is no partial fill. Example: stock 4, the winner takes 3, the loser asks for 2: the loser gets 0 and 1 stays.
     If both fit, both succeed (stock 3: winner takes 2, loser takes 1, stock ends at 0).
   * **Same contract (deliver):** the winner claims it and the loser's deliver fails. The loser's
     cargo is untouched.
   * **Route departure:** both sides sail along the **same route, meaning the same undirected edge**, in
     the same round. This covers the same direction (A to B for both) and opposite directions (A to B
     against B to A). The winner departs and the loser's sail fails, so its boat stays docked.
     These do **not** conflict: different routes out of the same origin, different routes into the
     same destination, or departing onto a route the enemy is already sailing (it left in an earlier round).
4. **End of round, for both seats:**
   * every sailing boat: `eta -= 1`; at 0 it docks at its destination (`position = destination`, `destination = -1`).
     A boat that departed this round is included, so a **1-round route arrives in the same round**.
   * every running job: `jobs[site] -= 1`; at 0, **+1 M** appears in that seat's warehouse at that site.
5. `round += 1`. If the new round is a multiple of 4 (4, 8, ..., 76), every timber and fibre stock below 6 gains +1 (cap **6**).
   This happens after the round's gathers, so obs 4, 8, ... already show the regenerated stock.
6. After round 79 is resolved the game ends (`game_done`). The final observation has `round` 80 and an empty `legal_actions`.

Timings this implies:
* `sail` along a route of length L issued in round r: obs r+1 shows `eta = L-1`, and the boat is docked at the
  destination in obs r+L. It can act again in round r+L. While sailing, `position` stays at the origin.
* `craft` in round r: obs r+1 `jobs=2`, obs r+2 `jobs=1`, obs r+3 shows the M in the warehouse (loadable in round r+3).
* `build_boat`, `build_workshop`, `load`, `unload`, `gather` and `deliver` take effect immediately.
  A new boat is docked at home and can act next round. A delivery's points show in obs r+1.

## 3. Legal actions: conditions and exact order

`legal_actions` is generated in this exact order (`sim.legal_actions` reproduces it):

```
[wait]
for each boat b in index order, skipping boats that are sailing (a sailing boat takes no orders):
    p = position, free = 3 - sum(cargo)
    sail b -> d          for every neighbour d of p (routes[p][d] > 0), ascending d
    gather b good=roles[p] q   for q = 1..min(stock[p], free)      only if roles[p] in {0,1}
    for good g in 0,1,2:
        load b g q        for q = 1..min(own_warehouse[p][g], free)   (any site, own warehouse)
        unload b g q      for q = 1..cargo[g]                          (any site)
    if roles[p] == 2:
        if no own workshop at p:  build_workshop b   if own_warehouse[p] has >= 2 T and >= 1 F
        else:                     craft b            if jobs[p] == 0 and own_warehouse[p] has >= 2 T and >= 1 F
    deliver b c          for each contract c ascending with destination == p, claims[c] == -1,
                         round < deadline, cargo[good_c] >= quantity_c
build_boat               if boats < 3 and own home warehouse has >= 4 T and >= 2 F
                         (no boat needs to be at home)
```

Effects:
* `gather`: stock[p] -= q, cargo += q. You can only gather the site's own good, and only at timber and fibre sites.
* Warehouses have **no capacity limit**: the traces include 30 T in one warehouse and 33 goods in total.
* `load` / `unload`: move goods between the boat and **your own** warehouse at p. Any site, including enemy
  home, raw sites and the 3rd good (M) too.
* `build_workshop`: own_warehouse[p] -= 2 T, 1 F; your workshop exists at p from now on. Each seat has its own
  workshops, and both seats can have one at the same site. Checked in 5/5 games: we built at **both** mfg sites after
  the Professor's first M delivery, when it must already have owned one (`probe_workshop_shared.py`).
* `craft`: own_warehouse[p] -= 2 T, 1 F; `jobs[p] = 3`. That gives one job per site per seat, and both of your mfg sites can run at once.
* `deliver`: cargo[good] -= quantity; `claims[c] = seat`; score += points; `crafted_deliveries += 1` if good is M.
  Deliveries come **from cargo only**, never from a warehouse.
* `build_boat`: home warehouse -= 4 T, 2 F; a new boat docks at home with empty cargo.
* Deadline: a contract is deliverable while `round < deadline`. With deadline 24 it is legal in round 23 and gone in round 24.
  The last M contract (deadline 80) is deliverable through round 79.
* Anything that is not exactly an entry of `legal_actions` gets `{"error":"invalid request or action"}` and the round
  does not advance. That covers a non-neighbour sail, an unknown op, a quantity above the cap, and even `{"op":"wait","extra":1}`
  with an extra key. The evaluator scores this as 0 for the whole run, so always return an entry of `legal_actions` unchanged.

## 4. Observation and visibility

* `visible[i]` is true for exactly these sites: **your home**, every site where **one of your boats is docked**, and every site
  where **you have a workshop**. These do not count: sailing boats (neither origin nor destination), and warehouses holding goods.
* `stocks[i]` is the true current stock if `visible[i]`, else `null`. Home and mfg sites show 0.
* `enemy_boats` lists enemy boats in ascending enemy boat index, each as `{boat, position, destination, eta}`. Cargo
  is not shown. An enemy boat is listed iff its `position` is visible, or it is sailing and its `destination` is visible.
  A sailing enemy keeps `position` = origin, so you see it leave a visible site, and you see it coming toward
  a visible site, with its eta. An enemy leaving a visible site on a 1-round route to an unseen site just vanishes.
* `claims` (all 8) and `opponent_score` are always fully visible. Enemy warehouses, workshops, jobs and cargo are never shown.
* `own`: `boats[{position,destination,eta,cargo}]`, `warehouses[10][3]`, `workshops[10]`, `jobs[10]`
  (rounds left), `score`, `crafted_deliveries`, `home`.
* `map`: `roles`, `routes[10][10]` (symmetric, 0 = no route), `homes[2]` (indexed by seat), `contracts[8]`, `topology`.

## 5. Scoring and end

* Score is the sum of points of the contracts you claimed: raw 5 each (4 contracts, 20 in total), manufactured 12 each
  (4 contracts, 48 in total). The maximum for both sides together is 68.
* The result is `{'scores': [you, professor], 'half_points': 2 win / 1 draw / 0 loss}`. Higher score wins, and
  **equal scores are a draw**: seen live as 34-34 giving half_points 1, in group 5, seed 3734939370, game 0 with our econ bot (trace in `_scratch/econ_test.jsonl.gz`).
* `crafted_deliveries` **cannot** break a tie. Scores are 5a + 12b with a, b <= 4, and that sum identifies (a, b)
  uniquely, so equal scores imply equal crafted counts. Treat it as informational.
* Unclaimed contracts after their deadline are simply lost. Nothing ends the game early; it always runs 80 rounds.

## 6. Map generation (2400 maps surveyed: 300 seeds x 8 groups, `maps_survey.json`)

The map depends only on **(topology, seed)**. The same seed gives the identical map, including the order of `homes`, in
group 2t and group 2t+1 (seat 0 vs seat 1) and for all 5 game indices. Game index only changes the Professor's style.

Graph (fixed per topology, edges undirected):
* **0, ring:** 0-1-2-3-4-5-6-7-8-9-0 (10 edges, every degree 2).
* **1, ladder:** rails 0-1-2-3-4 and 5-6-7-8-9, rungs i-(i+5) (13 edges; the corners 0,4,5,9 have degree 2).
* **2, two pentagons and a bridge:** cycles 0-1-2-3-4-0 and 5-6-7-8-9-5, joined by 2-7 (11 edges).
* **3, double star:** hub 0 with leaves 1-4, hub 5 with leaves 6-9, hubs joined by 0-5 (9 edges).

Route lengths: each edge is independently uniform in {1,2,3}, the same in both directions.

Homes: the unordered pair {i<j} with the **largest shortest-path distance** (weighted by route length). Ties go to
the lexicographically first (i, j). This held in 2400/2400 maps. Which seat gets which of the two is a 50/50
coin (`homes[seat]`). The consequence is that homes are almost always graph-far corners:
* ring: about 5 hops apart; the common pairs are (0,5), (0,4), (0,6), (1,6). Weighted home distance averages 9.8 (range 5-13).
* ladder: (0,9), (0,4), (4,5), (5,9), so corners. Average 9.1 (5-13).
* pentagons: (0,5), (4,5), (0,9), (4,9), one in each pentagon, far from the bridge. Average 10.8 (6-15).
* double star: two leaves of different hubs (in 2.3% of maps, two leaves of the same hub). Average 7.5 (4-9).

Roles: the 8 non-home sites get a uniform random permutation of {T,T,T,F,F,F,M,M}, so every map has exactly 3 timber, 3 fibre and 2 mfg sites.
Home to nearest mfg site averages 3.4 / 3.4 / 3.7 / 4.2 for topologies 0 / 1 / 2 / 3.

Contracts: always the same 8 slots, in this index order:

| idx | good | qty | points | deadline |
|---|---|---|---|---|
| 0 | T | 2 | 5 | 24 |
| 1 | F | 2 | 5 | 40 |
| 2 | T | 2 | 5 | 56 |
| 3 | F | 2 | 5 | 72 |
| 4 | M | 1 | 12 | 40 |
| 5 | M | 1 | 12 | 56 |
| 6 | M | 1 | 12 | 72 |
| 7 | M | 1 | 12 | 80 |

Each destination is drawn independently and uniformly from the non-home sites whose role differs from the good:
T contracts go to a fibre or mfg site (5 choices), F contracts to a timber or mfg site (5), and M contracts to a timber or
fibre site (6, never a mfg site). Repeats happen: two or more contracts share a destination in most maps.

## 7. Professor facts seen while probing (for the behaviour team; not rules)

* When we only wait, the Professor scores 44-68 and claims its first raw contract around rounds 2-20 and its first M
  contract around rounds 18-40. Game indices 2 and 3 often play identically.
* It loses same-round races when we hold priority: in 6/6 delivery races on our priority rounds we claimed the contract
  (`probe_deliver_race.py`). After losing a route conflict it did not re-issue the same sail; it re-planned.
  In one probe both of its boats sat at the mfg site we were using (site 4, group 0, seed 767302775, game 1).
* A dumb goal-directed bot (`bots.econ`, 3-15% random noise) already wins 8% and draws 5% of 600 live games
  (49 W, 31 D, 520 L). Results look similar for every game index, so no single style is a pushover for it.

## 8. Files

* `sim.py`: full two-sided simulator. `State.from_observation(obs)` (start of game), `legal_actions(st, seat)` (engine order, tuples),
  `is_legal`, `step(st, a0, a1)` (priority rules, returns which actions took effect), `observation(st, seat)`
  (engine-format dict), `to_dict` / `from_dict`, `state_from_observation(obs)` (mid-game State from one seat's view:
  our side and the visible shared fields are exact; the hidden opponent parts are guesses, see its docstring), `State.copy()`. Stdlib only, PyPy friendly: about 20k simulated rounds/s with both sides'
  legal actions generated, on the loaded dev box.
* `validate_sim.py`: live (`live N SEED`) or offline (`file traces.jsonl`) validator; see its docstring.
* `bots.py`: goal-directed noise policy used to reach crafting, M deliveries and boat building in validation.
* `test_sim.py`: unit tests of the probed facts (timings, races, limits). `coverage.py`: what the validation traces exercised.
* Probe scripts: `probe.py` (scripted runner), `probe_deliver_race.py`, `probe_gather_prio.py`, `probe_workshop_shared.py`,
  `survey_maps.py`, `analyze_maps*.py`, `dbg_*.py`. Traces and logs are in `_scratch/`: 2142 gzipped games (`*.jsonl.gz`, one game per line with every observation, our actions and the result). That is also a dataset of Professor play against 5 kinds of opponent, for the behaviour team.

## 9. Validation status

Zero unresolved mismatches. Totals:

* **Live** (`validate_sim.py live`, 10 runs): **1800 games / 142,200 rounds** against the real engine (all 8 groups,
  all 5 game indices). The policies were uniform random, weighted random, and `bots.econ` with 3% or 15% noise.
  Every round's observation matched the simulator: own boats, cargo, eta, warehouses, workshops, jobs, score, crafted count,
  visible, claims, opponent score, stocks, and the **full `legal_actions` list in order**. Also checked: enemy-boat
  listing, countdown, arrival and departure eta, and the final score and half_points.
  `MISMATCHES {}`.
* **Offline** (`validate_sim.py file`): 342 more recorded games, 27,018 rounds, also `MISMATCHES {}`.
* Conflicts that actually happened in those live games, each resolved as the rules predict:
  998 lost route departures (same and opposite direction), 4 won route departures, 50 lost and 175 won
  same-round gathers on one stock, 36 lost same-contract deliveries, and 46 tied games, all scored half_points 1.
  The ghost opponent was inferred to deliver 9028 times, sail 7287 times and gather 1136 times.
* Coverage (`coverage.py`): 4491 crafts, 1103 workshops built, 692 boats built (50,302 rounds with 3 boats), 3467 deliveries,
  1055 rounds with an M delivery legal, 2150 rounds where a job was running while the warehouse held 2T+1F
  (craft correctly not offered), 78 lists with deliver plus craft or workshop together, 478 with two or more delivers, and 147
  `build_boat` with no boat at home.
* Targeted probes (deterministic replays with one action changed): delivery races 6/6 won on our priority round and
  2/2 lost on theirs, with the loser's cargo kept (`probe_deliver_race.py`); gather races on our priority 8/8, where
  the Professor's later gather failed with no partial fill (`probe_gather_prio.py`); a route race won on our priority, where the
  Professor's boat stayed docked (group 0, seed 767302775, game 1, round 12). Also: shared workshops 5/5, deadline 23 legal and 24 not,
  the 3-boat limit, sail, craft and regen timings (`test_sim.py`, 9 tests, pass on CPython and PyPy).

What the validation cannot see, and therefore rests on symmetry:
* The Professor's own warehouses, cargo, workshops and jobs are never observable. The simulator applies to it the same rules
  we validated on our seat. That is consistent with everything observable: its score always equalled the claims it made,
  and its visible boats always moved by the route lengths.
* Opponent actions are inferred from evidence ("ghost"). Conflict rules are confirmed only where a same-round contact
  happened (counts above). Contacts it loses on our priority rounds are mostly invisible, so they were tested by the probes instead.
* The map RNG itself was not reverse-engineered. The home rule is exact; roles, route lengths and contract destinations are
  matched only as distributions.
