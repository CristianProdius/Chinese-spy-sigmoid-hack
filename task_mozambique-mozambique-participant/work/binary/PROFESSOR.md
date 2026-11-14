# The Professor, decoded from `mozambique-engine`

Source: Ghidra 11.2.1 decompile of the stripped binary (`decomp.c`, one file per function in `fn/`),
checked against `objdump` (`engine.asm`) and against the running engine with an `LD_PRELOAD`
tracer (`trace/hook.so`). Addresses below are file offsets of functions (image base 0).

`professor.py` is a Python re-implementation of everything in this document. `test_professor.py`
replays games against the real engine and compares, every round, the Professor's order, its whole
remaining plan, its stock estimates and our full observation. Results are in "Validation" at the end.

## 1. Summary

- The Professor is the C++ class `ReferencePlayer`. It is fully deterministic. No randomness, no
  clock, no dependence on thinking time.
- It gets the same fogged view we get (own side, visible stocks, claims, our score). It **never
  reads `enemy_boats`** and never models us. It reacts to us only through: a contract in its plan
  being claimed by us, a planned order becoming illegal (a sail that failed on a route conflict,
  or a gather where the stock is lower than it believed), and stock values it sees when docked.
- It never builds a third boat. It always has two boats.
- Each replan is a beam search (depth 4 contracts, width 8) over contract sequences. Each step
  plans one contract sequentially with one boat, then the whole action list is re-scheduled over
  both boats round-robin and re-simulated from the current state. Score = points gained (plus
  small bonuses) divided by `(elapsed rounds + 3) ^ A`.
- It follows the stored plan order by order while the next order is legal, delivers the moment
  any delivery is legal, and replans from scratch after every delivery and whenever the next
  planned order is illegal.
- "Playing styles" are 5 parameter triples `(B, A, W)`. For a map (seed), the 5 games use the 5
  styles in a seed-dependent permutation, so every map meets every style exactly once.

## 2. Styles

Table at `.rodata 0xe2820`, 5 entries of `{double A; double B; int W}`, copied into the player in
the Game constructor (`0x1fed0`):

| style id | B (surplus weight) | A (time exponent) | W (first-workshop bonus) |
|---|---|---|---|
| 0 | 3.5 | 0.85 | 8 |
| 1 | 1.8 | 1.15 | 0 |
| 2 | 1.8 | 0.85 | 0 |
| 3 | 3.5 | 0.0  | 0 |
| 4 | 0.0 | 0.85 | 8 |

- `A`: plan score is divided by `(plan length in rounds + 3) ^ A`. `A = 1.15` is greedy for quick
  points; `A = 0` (style 3) ignores time and simply maximises total points of a chain of up to 4
  contracts (it goes for the 12-point manufactured contracts first).
- `B`: when supplying a workshop, each surplus unit left there (timber beyond 2 counts 1, fibre
  beyond 1 counts 1.5) is worth `B` rounds. High `B` hauls full loads of 3 to the workshop;
  `B = 0` brings exactly 2 timber + 1 fibre.
- `W`: flat bonus added to a plan's gain if the Professor has no workshop now and the plan ends
  with at least one. Pushes styles 0 and 4 into manufacturing early.

Style of a game (`0x1fed0`):

```
perm = [0,1,2,3,4]
x = seed XOR 0x5354594c45534554            # ASCII "STYLESET"
for i in 5,4,3,2:
    x += 0x9e3779b97f4a7c15; z = splitmix64_mix(x)
    j = z mod i; swap(perm[i-1], perm[j])
style = perm[game]                          # game index 0-4
```

The style does not depend on group, seat or topology. The agent is not told the seed or the game
index, so it has to infer the style from play (section 8).

## 3. Engine rules (exact)

State (`game+8`): map (0x584 bytes), `round` (+0x584), two sides of 0xd8 bytes (+0x590), natural
`stocks[10]` (+0x740), `claims[8]` (+0x768). Side: home, score, crafted_deliveries, boats vector
(`{position, destination, eta, cargo[3]}`), `warehouses[10][3]`, `workshops[10]`, `jobs[10]`.

Start: each side has 2 boats at home, home warehouse 5 timber + 3 fibre, stocks 4 at timber and
fibre sites, 0 elsewhere, claims all -1. Seat = `group % 2`, topology = `group / 2`.

### Legal orders (`0x21660`), in the order the engine lists them

```
wait
for each boat b with eta == 0, at site p, free = 3 - sum(cargo):
    sail b -> j            for j ascending with routes[p][j] != 0
    gather b, good=role[p], q   for q = 1..min(stock[p], free)      if role[p] is 0 or 1
    for good g = 0,1,2:
        load b,g,q         for q = 1..min(warehouse[p][g], free)
        unload b,g,q       for q = 1..cargo[g]
    if role[p] == 2 and warehouse[p] has >= 2 timber and >= 1 fibre:
        build_workshop b   if no own workshop at p
        craft b            else if jobs[p] == 0
    deliver b,c            for c ascending: claims[c] == -1 and round < deadline[c]
                           and destination[c] == p and cargo[good[c]] >= quantity[c]
build_boat                 if boats <= 2 and home warehouse has >= 4 timber and >= 2 fibre
```

A boat that is sailing has no orders. Stocks used for our legal list are the real ones (a docked
boat makes its site visible).

### Round resolution (`0x31ef0`, `0x22090`)

```
both orders must be in their legal lists ("illegal order" otherwise)
used = empty set of routes
for seat in (round % 2, 1 - round % 2):          # seat round%2 resolves first
    apply(order[seat]):
        sail b->d:   if (p,d) in used: FAIL (boat stays, order lost)
                     else mark (p,d) and (d,p) used; boat.destination = d; boat.eta = routes[p][d]
        gather:      if stock[p] < q: FAIL; else stock -= q; cargo += q
        load/unload: move q between own warehouse at p and cargo
        build_workshop: warehouse[p] -= (2 timber, 1 fibre); workshops[p] = true
        craft:          warehouse[p] -= (2 timber, 1 fibre); jobs[p] = 3
        build_boat:     home warehouse -= (4 timber, 2 fibre); new boat at home
        deliver b,c: if claims[c] != -1: FAIL
                     else cargo[good] -= quantity; score += points;
                          crafted_deliveries += (good == 2); claims[c] = seat
for every boat of both sides: if eta != 0: eta -= 1; if eta == 0: position = destination, destination = -1
for every site of both sides: if jobs != 0: jobs -= 1; if jobs == 0: warehouse[site][manufactured] += 1
round += 1
if round % 4 == 0: every timber/fibre site: stock = min(stock + 1, 6)
```

Consequences:
- A sail of length L issued in round r is docked in the observation of round r+L.
- A craft issued in round r yields the good in the observation of round r+3.
- Route conflict: the two sides cannot depart on the same route (either direction) in the same
  round. The seat equal to `round % 2` wins, the other side's sail silently does nothing.
- Same-round gather at one site and same-round delivery of one contract: the seat `round % 2`
  goes first. The loser's order does nothing if stock or the contract is gone.
- No deadline is checked at apply time; the legal list already requires `round < deadline`.
- A failed order is not reported anywhere. It only shows in the next state.

### Visibility (`0x311e0`)

Visible sites for a seat: own home, sites with an own workshop, sites where an own boat is docked
(eta == 0). `stocks` is real for visible sites and null otherwise. An enemy boat is listed when
its position is visible, or its destination is set and visible. The Professor gets exactly the
same kind of view (its internal copy holds 4 for hidden stocks).

### Action matching (`0x3d0b0`)

Our action is serialised and compared as a string with each serialised legal action. Key order
does not matter, but an extra key, a missing key or a float (`"boat": 0.0`) is rejected with
`{"error":"invalid request or action"}`. Return the entry of `legal_actions` itself, or a dict
with exactly the same keys and integer values.

### Result (`0x3fdf0`)

Game ends after round 79 (round counter 80). Higher score wins: `half_points` 2 win, 1 equal
scores, 0 loss. There is no tie-break (crafted_deliveries is not used).

## 4. Map generation (`0x1e1b0`), exact

RNG: splitmix64, state starts at `seed XOR 0x43414d504149474e` ("CAMPAIGN"). The map depends only
on (topology, seed), so groups 2t and 2t+1 with the same seed are the same map from the two seats.

```
repeat up to 4096 times (RNG state carries over between attempts):
    edge(i,j): routes[i][j] = routes[j][i] = rnd() % 3 + 1
    topology 0: ring           edge(i, (i+1)%10) for i = 0..9
    topology 1: 2x5 ladder     edge(i,i+1) i=0..3; edge(i,i+1) i=5..8; edge(i,i+5) i=0..4
    topology 2: two 5-rings    edge(b+i, b+(i+1)%5) for b=0 then b=5, i=0..4; then edge(2,7)
    topology 3: two stars      edge(0,i) i=1..4; edge(5,i) i=6..9; then edge(0,5)
    dist/next = Floyd-Warshall (k outer, i, j; strict <; next[i][j] = next[i][k])
    homes = first pair i<j (lexicographic) with the largest dist[i][j]; if rnd() & 1: swap homes
    others = the 8 non-home sites ascending; for n = 8..2: r = rnd() % n; swap(others[n-1], others[r])
    roles: others[0..2] = 0 (timber), others[3..5] = 1 (fibre), others[6..7] = 2 (manufacturing)
    for c = 0..7:
        c < 4:  good = c & 1, quantity 2, points 5,  deadline 24 + 16c        (24, 40, 56, 72)
        c >= 4: good = 2,     quantity 1, points 12, deadline min(80, 16c-24) (40, 56, 72, 80)
        eligible = sites s in `others` order with role[s] != good and, for BOTH homes h:
            raw:          dist[h][s] + 2 <= deadline
            manufactured: min over manufacturing sites w of 3*dist[h][w] + 14 + dist[w][s] <= deadline
        if eligible is empty: restart the attempt
        destination = eligible[rnd() % len(eligible)]
```

So: contracts 0 and 2 want timber, 1 and 3 want fibre, 4-7 want one manufactured good; a contract
never points at a home or at a site that produces its own good; a manufactured contract never
points at a manufacturing site. Total 68 points on the board. Homes are the two farthest sites.

## 5. The Professor's per-round decision (`ReferencePlayer::choose`, `0x3ae20`)

Persistent player state (object at `game+0x790`): style `(B, A, W)`, a copy of the map, `seat`,
`last_round`, `est[10]` (stock estimates), `plan` (a `std::deque<Order>`), `plan_contracts`
(the contract ids the plan is aiming at).

```
choose(view):
    if view.round == 0: last_round = -1; est[*] = 4; plan.clear(); plan_contracts.clear()
    d = round/4 - last_round/4            (round/4 when last_round < 0)
    for s in 0..9: est[s] = min(est[s] + d, 6); if view.visible[s]: est[s] = view.stocks[s]
    last_round = round
    for c in plan_contracts: if claims[c] is the opponent: plan.clear()
    for a in view.legal_actions (engine order): if a is a deliver:
        plan.clear(); plan_contracts.clear(); return a          # first legal delivery, always
    if plan not empty and plan.front in legal_actions: return plan.pop_front()
    plan.clear(); plan_contracts.clear()
    best = replan(view)                                          # section 6
    if best exists and best.actions not empty:
        plan_contracts = best.contracts; plan = best.actions
        if plan.front in legal_actions: return plan.pop_front()
    plan.clear()
    return legal_actions[0]                                      # = wait
```

Notes:
- `est` is its only memory of the world: last seen value plus one per regeneration tick, capped at
  6. Sites it has never seen are assumed to hold `4 + ticks`. It never learns what we took unless
  it docks there (or has a workshop there).
- Because any legal delivery fires first and wipes the plan, it replans after every delivery.
- A replan happens in the same call in which the plan is found empty/illegal. If no feasible plan
  exists it waits and replans again every round.
- When we claim a contract its plan was aiming at, the plan is dropped the next round and it
  replans with whatever cargo it is holding.

## 6. Replanning

### 6.1 Sim (the Professor's forward model)

`Sim` = its own side (home, score, boats, warehouses, workshops, jobs) + `stocks` (a copy of
`est`) + `claims` + `round` + `ok` flag + the list of orders applied so far. We do not exist in it.

```
step(sim, order, lenient=false)        # 0x19ec0: one whole round with this single order
    if !sim.ok or sim.round >= 160: sim.ok = false; return
    if lenient and order is deliver:   # deadline is NOT checked here
        need boat docked at the destination with enough cargo and the contract unclaimed, else fail
    else if order not in legal_actions(sim): fail
    apply (same code as the engine, no route conflicts); advance boats and jobs; round += 1;
    regenerate sim.stocks when round % 4 == 0; append order to sim.actions

travel(sim, b, target)                 # 0x1a1c0
    loop while sim.ok:
        if boat b is sailing: step(wait); continue
        if boat.position == target: return
        n = next[boat.position][target]; if n < 0: fail
        step(sail b -> n)
```

One order per round, so in this sequential phase the other boat stands still while one works.

### 6.2 acquire(sim, b, need[3], dest, unload_flag) (`0x26c80`, lambda `0x2bf10`)

"Boat b ends at `dest` holding `need`", minimising the finishing round.

```
s = copy(sim); cargo0 = boat b's cargo at entry
if sum(max(need[g], cargo0[g])) > 3:                    # no room: dump surplus first
    travel(s, b, boat.destination if sailing else boat.position)
    for g: if cargo0[g] > need[g]: step(unload b, g, cargo0[g] - need[g])
if !s.ok: return none
missing[g] = max(0, need[g] - cargo[g]); order = goods with missing > 0, ascending
best = none
for every permutation of order (std::next_permutation):  rec(s, 0)
return best

rec(sim, idx):
    if !sim.ok: return
    if best exists and sim.round >= best.round: return           # prune
    if idx == len(order):
        t = copy(sim); travel(t, b, dest)
        if unload_flag: for g: if need[g] != 0: step(unload b, g, need[g])
        if t.ok and (best is none or t.round < best.round): best = t
        return
    g = order[idx]; m = missing[g]
    cands  = [(s, LOAD)   for s in 0..9 if not (unload_flag and s == dest) and warehouse[s][g] >= m]
    cands += [(s, GATHER) for s in 0..9 if not (unload_flag and s == dest) and role[s] == g and sim.stocks[s] >= m]
    cur = boat.destination if sailing else boat.position
    stable-sort cands by dist[cur][s] + dist[s][dest]; keep the first 5
    for (s, kind) in cands:
        t = copy(sim); travel(t, b, s); step(load or gather b, g, m); rec(t, idx + 1)
```

Details that matter:
- It takes the whole missing amount of a good from ONE place (no splitting across sites). A raw
  contract needs a site or own warehouse with >= 2 of the good, by its estimate.
- Own warehouses (including the 5 timber + 3 fibre at home) come before natural sites on ties.
- Only the 5 nearest sources by detour length are tried.

### 6.3 supply(sim, w) (`0x27250`)

"Get 2 timber + 1 fibre into my warehouse at manufacturing site w with a boat docked there."
Returns (sim, boat).

```
needT = max(0, 2 - wh[w][timber]); needF = max(0, 1 - wh[w][fibre])
cost(s) = s.round - (max(0, wh[w][fibre] - 1) * 1.5 + max(0, wh[w][timber] - 2)) * B      # lower wins, strict <
if needT + needF == 0:
    for b: s = copy(sim); travel(s, b, w); candidate (s, b)
else:
    for b:
        candidate acquire(sim, b, [needT, needF, 0], w, unload)
        if needT != 0 and needF == 0: candidate acquire(sim, b, [3,0,0], w, unload)
        if needF != 0 and needT == 0: candidate acquire(sim, b, [0,3,0], w, unload)
    if needT != 0 and needF != 0 and sim.round < 50:      # two full loads, any boat for each
        for (first, second) in ([3,0,0],[0,3,0]), ([0,3,0],[3,0,0]):
            for b1: r1 = acquire(sim, b1, first, w, unload)
                for b2: candidate acquire(r1, b2, second, w, unload) with boat b2
```

### 6.4 manufactured(sim, dest) (`0x284f0`)

"Some boat ends at `dest` holding one manufactured good." Returns (sim, boat).
`cost(s) = s.round - 0.5 * stock_value(s)`, lower wins (strict <), where
`stock_value(s) = sum over own workshop sites of min(fibre, 2) * 1.5 + min(timber, 4)`.

```
A. for b with a manufactured good on board: s = copy; travel(s, b, dest); candidate
B. for w in 0..9 with wh[w][manufactured] != 0 or jobs[w] != 0:
       for b: s = copy; travel(s, b, w); while s.jobs[w] != 0: step(wait)
              if boat has free space: step(load b, manufactured, 1); travel(s, b, dest); candidate
C. for w in 0..9 with role[w] == 2:
       s = copy(sim)
       if no workshop at w: r = supply(s, w) (skip w if none); s = r.sim; step(build_workshop r.boat)
       if s.ok and s.jobs[w] == 0:
           r = supply(s, w) (skip w if none); s = r.sim; step(craft r.boat)
           for b: t = copy(s); travel(t, b, w); wait until t.jobs[w] == 0
                  if boat has free space: step(load b, manufactured, 1); travel(t, b, dest); candidate
```

A new workshop therefore costs two supplies (2T+1F to build, 2T+1F for the first craft), i.e.
4 timber + 2 fibre hauled to the site before the first good exists.

### 6.5 prepare(sim, c) (`0x29690`): sequential plan for one more contract

```
if sim.claims[c] != -1: none
if good[c] == 2: (s, boat) = manufactured(sim, destination[c])
else: need[good[c]] = quantity[c]; over boats b ascending take acquire(sim, b, need, destination[c], no unload)
      with the smallest finishing round (first boat wins ties)
step(s, deliver boat c, lenient)        # no deadline check yet
return s if s.ok
```

### 6.6 interleave(actions, variant) (`0x29f80`): run both boats in parallel

```
s = copy(CURRENT state)                       # not the beam node: the whole list is replayed
queue[b] = the non-wait actions of boat b, in order
while s.round < 80:
    if all queues empty: return s
    chosen = none
    for i in variant, variant+1 (mod number of boats):        # variant 0 starts with boat 0, 1 with boat 1
        if queue[i].front is legal in s:
            if chosen is none or front is a deliver: chosen = i
            if front is a deliver: break
    if chosen is none:
        if some boat is sailing or some job is running: step(wait) else return none
    else: step(queue[chosen].pop_front())      # strict legality, includes the deadline for deliver
    if !s.ok: return none
return none if a queue is not empty
```

Deadlines are enforced here: a deliver whose deadline has passed is never legal, so the plan dies.

### 6.7 Beam search (`0x3ae20`, second half)

```
cur = Sim(view, stocks = est)
frontier = [node(cur, contracts = [])]; best = none
repeat 4 times:
    next = []
    for node in frontier (in order):
        for c in 0..7 with node.claims[c] == -1 and cur.round < deadline[c]:
            opt = prepare(node.sim, c); skip if none
            for variant in 0, 1:
                res = interleave(opt.actions, variant); skip if none
                bonus = W if (cur has no workshop and res has one) else 0
                score = (0.1 * stock_value(res) + (res.score - cur.score) + bonus)
                        / pow(res.round - cur.round + 3, A)
                n = node(res, node.contracts + [c], score)
                if best is none or best.score < score: best = n         # strict: first found wins ties
                next.append(n)
    if next is empty: stop
    stable-sort next by score descending, ties by smaller res.round; frontier = first 8
return best            # its full interleaved action list (with waits) becomes the plan
```

`best` is the best node of any depth, so the plan covers 1 to 4 contracts. Only the first
delivery of that plan is ever executed before the next replan.

## 7. What this means in practice

Behaviour to expect:
- Round 0: the quick styles (1, 2) usually load 2 timber or 2 fibre from the home warehouse and
  sail to the nearest raw contract of that good. Styles 0 and 4 (`W = 8`) and style 3 (`A = 0`)
  start hauling timber and fibre to a manufacturing site earlier.
- Every style ends up building exactly one workshop and crafting from it.
- It has no idea where our boats are, what we carry or what we are about to deliver. It never
  races and never blocks on purpose.
- It keeps believing in stock we have already taken until one of its boats docks there.

Playing alone (we only wait), Python model, 40 maps x 5 styles (`stats_unopposed.py`):

| style | avg score | min | max | raw claimed | crafted claimed | first claim | first crafted claim |
|---|---|---|---|---|---|---|---|
| 0 | 56.6 | 39 | 68 | 3.27 | 3.35 | round 9.3 | round 27.6 |
| 1 | 53.3 | 44 | 68 | 3.70 | 2.90 | round 4.7 | round 37.2 |
| 2 | 56.2 | 39 | 68 | 3.33 | 3.30 | round 7.7 | round 30.8 |
| 3 | 55.3 | 34 | 68 | 2.42 | 3.60 | round 11.6 | round 27.1 |
| 4 | 51.8 | 34 | 63 | 2.80 | 3.15 | round 12.4 | round 23.9 |

By topology the average is 50.2 (ring), 57.9 (ladder), 55.6 (two rings), 55.0 (two stars). Last
claim is around round 62. A Professor clone in our seat is an even match for it: 23 wins,
16 draws, 21 losses over 60 games, average 32.6 to 32.0.

Levers against it (all follow from the code):
1. Contract sniping. Its delivery round for each contract is predictable exactly. Delivering one
   round earlier, or in the same round when `round % 2 == our seat`, makes its trip worthless. It
   only notices on the following round, then replans with the cargo still on board.
2. Stock denial. A source needs the full missing amount in one place (2 for a raw contract, 2
   timber / 1 fibre / 3 of a kind for a workshop). Leaving a timber or fibre site at 0 or 1 just
   before it arrives makes its gather illegal, so it has sailed there for nothing and replans.
   It still thinks other unseen sites hold 4 or more.
3. Route blocking. On rounds where `round % 2 == our seat`, sailing the route it is about to use
   (either direction) cancels its sail. It loses that round, and a later order of its plan
   becomes illegal, forcing a replan. This costs us one order too, so it only pays when our sail
   is useful anyway.
4. It never builds a third boat; a third boat for us is not contested.
5. Its home warehouse (5 timber, 3 fibre) counts as a source like any other, and warehouses win
   ties against natural sites. Its first raw deliveries are usually paid from home stock, which
   we cannot deny. Natural sites only matter to it once that stock is spent.

## 8. Predicting it from inside `main.py`

The game is deterministic and the model is exact, so an agent that knows the style can carry the
complete hidden state (its boats, cargo, warehouses, plan, estimates, all stocks):

1. At round 0 build `Engine(Map(obs['map']))` and five `Professor(style, 1 - seat)` hypotheses.
2. Each round, for every live hypothesis: `order = prof.choose(engine.view(prof_seat))`, then
   after choosing our own order call `engine.step(orders)`. Seat `round % 2` resolves first.
3. Drop a hypothesis when its predicted observation differs from the real one. Observable
   evidence: `opponent_score`, `claims`, `enemy_boats`, `stocks` at visible sites, and our own
   failed sails/gathers/deliveries.
4. Module globals survive between games in one process: each map uses each style once over its 5
   games, which can prune hypotheses when the same map (same `obs['map']`) comes back.

Measured with `test_tracking.py` on the unmodified engine (45 games, our seat waiting, playing
random legal moves or playing a Professor clone):
- The true style was never dropped.
- The style became unique at a median of round 16 (15 of 45 games by round 10, latest round 46).
  Fog is the reason: hypotheses only separate when we see a boat, a stock change, a claim or a
  score change that differs.
- In 3 of 45 games two hypotheses survived to the end, always styles 0 and 2 (same `A`, they
  differ in `B` and `W`). Plan against every surviving hypothesis rather than assuming one.

Cost in PyPy 3.10 on the loaded dev box: one `choose` is a deque pop on most rounds. A replan
(after each of its deliveries and after each disruption) is the expensive part: 9.8 ms CPU on
average, about 80 ms at the 90th percentile, 200-300 ms for the round-0 replan, and about 1 s
for the very first replan of a process (JIT warm-up). One hypothesis costs about 0.23 s CPU per
game; tracking five hypotheses cost 0.84 s per game on average and 2.45 s in the worst game.
Using the model inside a search over our own moves multiplies that, so budget it.

`professor.py` API: `Map(obs['map'])`, `Engine(map)` with `.view(seat)`, `.legal(seat)`,
`.step([order0, order1])`; `Professor(style_id, seat)` with `.choose(view)` and `.clone()`;
`view_from_observation(obs)`; `order_to_json` / `order_from_json`; `style_permutation(seed)`;
`generate_map(topology, seed)`.

## 9. Files in this folder

- `PROFESSOR.md` this document.
- `professor.py` Python model (rules, views, Professor, style permutation, map generation).
- `test_professor.py` exact-match test against the traced engine.
- `test_mapgen.py` map generation test against the engine.
- `stats_unopposed.py` profile of the Professor playing alone, per style.
- `trace/hook.c`, `trace/hook.so` the `LD_PRELOAD` tracer (set `MOZ_TRACE=<file>`); one JSON line
  per Professor decision with its order, style, estimates, plan contracts and remaining plan.
- `decomp.c`, `fn/*.c` Ghidra output for 0x13710-0x41000; `engine.asm` objdump; `dis.sh START END`
  prints a disassembly range; `clean.sh fn/X.c` strips declarations from a decompiled function.
- Tools: `/home/cristian/opt/re/` (Ghidra 11.2.1, Temurin JDK 21, Ghidra project `proj/moz`).

Function map: `0x1fed0` Game ctor (style + map + state), `0x1e1b0` map generation, `0x1cb80`
state init, `0x311e0` build view, `0x21660` legal orders, `0x22090` apply one order, `0x31ef0`
resolve a round, `0x3d0b0` step command, `0x3fdf0` response/result, `0x3ae20`
`ReferencePlayer::choose`, `0x29690` prepare, `0x29f80` interleave, `0x26c80`/`0x2bf10` acquire,
`0x27250` supply, `0x284f0` manufactured, `0x19ec0` Sim step, `0x1a1c0` travel.

## 10. Validation

All runs on PyPy 3.10 against the real `mozambique-engine`. Logs for 255 of the 270 traced games are
in `logs/`; the first two short runs (6 and 9 games) were only printed to the terminal.

| test | what is compared | size | mismatches |
|---|---|---|---|
| `test_professor.py` (tracer) | Professor's order, full remaining plan, plan contracts, stock estimates, style triple, our whole observation incl. `legal_actions`, final scores, every round | 270 games, 21,600 rounds, 8,126 replans | 0 |
| `test_mapgen.py` | `generate_map(topology, seed)` vs `observation['map']` | 400 maps | 0 |
| `test_tracking.py` (no tracer) | five-hypothesis tracking from observations only | 45 games | true style never dropped |

The 270 games use random groups, seeds and game indices and three policies for our seat: always
wait (the Professor plays alone), random legal moves biased to deliveries, builds and crafts
(route conflicts, stock interference, third boat, our own workshops), and a Professor clone
(contested contracts, same-round conflicts). 186 games ran before the `manufactured` cache was
added to `professor.py`, 84 after; the unopposed profile of 200 games is identical before and
after.

Confidence: the decision procedure, rules, style table, style permutation and map generation are
reproduced exactly on everything tested, so I treat sections 2-6 as exact. Two things were not
exercised and are read from code only: a Professor with three boats (it never builds one), and
Sim rounds past 80 (the interleave step cuts plans at round 80).

Rerun:

```
PYPY=/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3
nice -n 10 $PYPY test_professor.py --games 30 --seed 1      # needs trace/hook.so (gcc -O1 -shared -fPIC -o trace/hook.so trace/hook.c -ldl)
python3 test_mapgen.py 400
nice -n 10 $PYPY test_tracking.py --games 30 --seed 3
nice -n 10 $PYPY stats_unopposed.py 40
```

