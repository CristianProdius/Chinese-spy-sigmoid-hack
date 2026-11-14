# Web research: beating the Professor of Maputo Bay

Written 2026-11-14. Ranked by expected value for this task. Each item says what to do and why, with sources.
Local artefacts in this folder: `pypy_bench.py` (micro-benchmarks), `dump_obs.py` + `sample_obs.json` (one real observation).

## TL;DR (ranked)

1. **Clone the Professor, then plan against the clone.** It is deterministic, and the map (contracts, roles, routes, homes) is fully visible, so the only hidden state is fog (enemy boats, stocks, enemy warehouses). With an exact or near-exact model of the Professor plus an engine re-implementation, you can shadow-simulate the whole game from round 0 and the game becomes single-agent planning. This beats any generic game-tree search we could fit into 10 s. Get the model from the binary (`work/binary/engine.asm`), or failing that, rebuild it from logged behaviour. (Albrecht & Stone, "policy reconstruction" / "type-based reasoning"; Ocean of Code tracking; Halite IV winner.)
2. **Best-response planner = receding-horizon search over macro-actions** (a "trip" is gather/load → sail → deliver/craft), with beam search or depth-first branch and bound, re-planned every round. This is the pattern that won the PTSP competitions (route ordering + macro-actions) and that Churchill & Buro used for build orders. Strong CodinGame "race for orders" bots (Fall Challenge 2020) used beam search plus a separate opponent search that removes the orders the opponent will take.
3. **Race and denial accounting per contract.** For every contract, compare our earliest delivery round with the clone's predicted delivery round, including the even/odd tie-break parity. Take the ones we win, steal contested ones by arriving earlier or on our priority parity, and drop the lost ones early (Halite IV "safe collect squares" style distance races; Fall 2020 "learn before the opponent can").
4. **Worst-of-5 means robustness over styles, not average.** Identify the style fast (type-based reasoning / Bayesian Policy Reuse). If game index = style, verify that locally. While uncertain, pick the plan with the best minimum margin across candidate style models (safe-exploitation idea).
5. **Tune parameters against the real engine with the worst-of-5 metric.** Top Kaggle simulation entries are mostly hand-written rules plus tuning: Halite IV 1st (Bayesian optimisation against an opponent pool), Lux S2 1st (rule-based with forward simulation), and Kore 2022 (several top-4 entries rule-based).
6. **Generic SM-MCTS / ISMCTS / RHEA are fallbacks only.** If one is needed, use decoupled UCT. At 10 s per 80 decisions in Python it reaches only low thousands of rollouts per decision, which is far weaker than a planner that knows the opponent.
7. **PyPy hot-loop rules (measured here):** state as flat int lists or `__slots__` objects, never `copy.deepcopy` (1,700x slower), no `time.process_time()` in loops (17 µs per call on PyPy), iterative rather than recursive search, and use the first game's +10 s to warm the JIT.

---

## 1. Public information about this challenge

- **Nothing public about "The Professor of Maputo Bay" or `mozambique-engine`.** Extended searches for the title, the engine name, and the arena/hidden-map/worst-of-5 setup return only geography pages.
- **The event is Sigmoid's LMML 2026** (Learning Marathon of Machine Learning): a "24-hour, CTF-style machine learning marathon", 14-15 Nov 2026 (live today), Chișinău or online. "Each continent is a zone. Each country is a challenge. Every zone is an AI subdomain." Seven territories; Antarctica is "[CLASSIFIED] … find out live". No rules, flag format or task list is published. https://lmml.sigmoidai.org/ and https://lmml.sigmoidai.org/2025.html
- **Past writeups:** https://github.com/SigmoidAI/lmml-solutions holds only three 2025 tasks (Australia: weight steganography; Morocco: base64-speaking LLM; Paraguay: overfit Fourier features → Morse). All are puzzles; there are no game or agent tasks. Nothing transfers except that Sigmoid tasks tend to hide a trick that the story text hints at. Read the task statement for hints about the Professor's styles.
- **Closest precedent is local, not web:** `/home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/moonfish/` (Island Duel; engine `task/island-duel/island-duel-participant/samoa-linux-x86_64`, agents in `island_duel/`) has the same Sigmoid structure: an engine binary, a "champion" with "three observable profiles" that "searches up to 2,048 visits/four plies", fog, and hidden seeds. The team's ladder there was a greedy rate agent → alpha-beta over single actions with an abstract "expand into fog" move → PPO + 2-ply lookahead. The decisive insight was exploiting the opponent's known algorithm (`reserve_agent.py`: "The champion searches 4 plies: it does not capture a tile when it can see us capture it straight back. Keeping enough energy to recapture therefore deters its captures."). For Mozambique, aim for the same kind of algorithm-specific exploit, but with an exact clone, because the Professor is deterministic.

## 2. Techniques, ranked by expected value

### 2.1 Exact opponent model → shadow simulation (highest EV)

Why it fits:
- The Professor is deterministic. Its observation depends only on the map, the seed-driven state and our actions. The map is fully in our observation (`map.contracts/roles/routes/homes`). If the engine's state transition and the Professor's policy are replicated, running both from round 0 with our real action history reproduces the hidden state: enemy boats, warehouses, stocks out of sight and the Professor's next action. Check consistency every round against what we see (`opponent_score`, `claims`, visible `enemy_boats`, visible `stocks`). Fall back to a looser model when they diverge.
- Albrecht & Stone's survey names the two families that apply: **policy reconstruction** (learn the model from observed actions; slow and hard under partial observability) and **type-based reasoning** (the opponent is one of several known complete models; the belief "can often point to this type after only a few observations"). The Professor's "several styles" is the type-based case. https://arxiv.org/abs/1709.08071
- **Tracking under fog by filtering hypotheses** is standard in CodinGame (Ocean of Code). Players keep the set of opponent states consistent with every observation, drop states that conflict, and merge duplicates. With a deterministic opponent the set collapses to one state as long as the model is right. https://forum.codingame.com/t/ocean-of-code-feedback-strategies/175885?page=2
- The Halite IV winner's agent ran on opponent behaviour models inferred online (risk models from "the last N (120) risky moves", conversion thresholds, cycle detection used to "extrapolate the loop and plan with the extrapolated positions"). He called the low-level heuristics combined with "learning the opponent behavior wherever possible" the most solid part of the agent. Source: `Write up.odt` in https://github.com/ttvand/Halite

How to build it (in order of preference):
1. **From the binary:** decompile the Professor's decision function (Ghidra headless is free; `work/binary/engine.asm` already exists). Re-implement it in Python and run differential tests against the engine over many (group, seed, game) triples. LICENSE notes the engine "dynamically links the system OpenSSL 3 library". `ltrace` or an `LD_PRELOAD` shim on libcrypto calls would show cheaply what gets hashed (seed/map derivation or tie-break randomness).
2. **Behavioural reconstruction:** log per-round Professor actions inferred from observation deltas (score/claims changes, visible boat moves, stock drops at visible sites). Use `Arena` with our agent parked near the Professor's routes to maximise visibility. Fit a rule set per style and measure next-action prediction accuracy per round. Without per-round accuracy near 100%, treat it as a heuristic model, not a clone.
3. **Validation metric:** the predicted `opponent_score` trajectory and `claims` timeline must match the engine exactly across ≥ 1,000 games for each style.

### 2.2 Best-response planning over macro-actions (the "how" once 2.1 exists)

- **Macro-actions + ordering + receding horizon** won both PTSP competitions: a TSP solver sets the waypoint order and MCTS with repeated actions (macro-actions) handles execution, with parameters tuned by CMA-ES. Map that onto contracts: order the contract/trip set, then expand each trip into primitive ops. https://repository.falmouth.ac.uk/2259/ (Perez, Powley, Whitehouse, Cowling et al., IEEE TCIAIG 2014)
- **Depth-first branch and bound over macro-actions** (Churchill & Buro, *Build Order Optimization in StarCraft*): prune any partial plan whose bound can't beat the best plan found so far, and order children so good plans come first (tighter bound sooner). Our production chain (timber+fibre → workshop → 3-round craft → deliver) is a small build order. https://ojs.aaai.org/index.php/AIIDE/article/view/12435 and https://www.cs.mun.ca/~dchurchill/publications/pdf/aiide11-bo.pdf
- **Beam search with an opponent pre-search** (CodinGame Fall Challenge 2020, a race for shared potion orders with one action per turn; the closest public analogue to our contract race). From https://forum.codingame.com/t/fall-challenge-2020-feedbacks-strategies/187846:
  - #4 (Flo): beam search with a hash to drop duplicate nodes. A *separate beam search for the opponent* constrains the main search by removing the orders the opponent is likely to take and pruning lines where the opponent wins.
  - ~13th (Magus): iterative-deepening beam, width 1000, 0.95 discount per depth. Take a contested LEARN first, before any BREW, because the opponent could take it.
  - 14th (RobotAI): 0.9 decay. Their admitted weakness: "my bots gets stuck with inventory because of opponents next turn brew", meaning poor opponent prediction cost them games.
- **Halite IV winner's three-stage pipeline:** (1) score every unit × target, (2) assign targets avoiding conflicts, (3) translate to low-level actions. "It is crucial to make the scores relatively consistent between time steps", meaning a target chosen this turn should still be the best next turn. Re-planning every round must not cause dithering, so add a hysteresis bonus for continuing the current plan. Source: `Write up.odt` in https://github.com/ttvand/Halite
- **Lux AI S2 1st place (ry_andy_)** was rule-based, with role classes (miner, transporter, attacker, blockade, …) and a forward simulation (`lux/forward_sim.py`, `FUTURE_LEN` horizon). Roles plus a short forward sim are enough to win a large simulation contest. https://github.com/ryandy/Lux-S2-public (writeup: https://www.kaggle.com/competitions/lux-ai-season-2/discussion/407982; Kaggle pages don't render without JS)

Mapping to this game: the binding resource is **one action per round for the whole side (80 total)**, not boat time. Every hop, load, gather, unload, craft and deliver costs a slot, and a sailing boat moves without spending slots. Score plans in points per action-slot and per round, as the Island Duel greedy agent did with "rate = value per decision".

### 2.3 Contract races and tie-break parity

- For each contract, compute (our earliest delivery round, the clone's delivery round, and who has priority on that round: seat 0 on even rounds, seat 1 on odd). This is the deterministic version of Halite IV's "safe collect squares" test: compare distance-to-goal against the opponent's distance, and act only when we win the race.
- Arriving on the round where we hold priority converts ties into wins, and the same rule decides shared natural stock and departures. Timing a gather or delivery to our parity is a free edge that plain planners ignore.
- Denial counts: a contract the Professor loses is worth its points to the margin even if we only break even. Fall 2020 top bots explicitly took contested items first (Magus, link above).

### 2.4 Robustness: worst-of-5 means beat every style

- **Type identification:** Bayesian Policy Reuse keeps a posterior over known opponent types from observed signals and plays the stored best response for the most likely type. BPR+ adds detection of a switch to an unknown type. https://arxiv.org/abs/1505.00284 , https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2016/pdfs/p1315.pdf . With a deterministic clone per style, the posterior is just "which style clones still match every observation so far". That is exact and costs one simulation per style per round.
- **Before the style is known** (or if game index ≠ style), choose actions that maximise the *minimum* predicted margin across the still-consistent styles. Safe-exploitation work frames this as exploiting while guaranteeing a floor. Over-committing to a wrong model is the classic failure ("best-response strategies … are themselves highly exploitable if the opponent model is wrong"). https://arxiv.org/abs/2307.12338 , https://proceedings.neurips.cc/paper_files/paper/2022/file/b12a1d1014e952e676f5d6931d03241a-Paper-Conference.pdf
- **Don't rely on module globals for cross-game learning:** `arena.py` splits games with `games[i::jobs]`, so a map's five games land in different processes. The hidden evaluator also runs "several main.py processes in parallel". Each game must stand alone.

### 2.5 Tuning

- Halite IV 1st: an internal leaderboard plus Bayesian optimisation of constants against a pool of opponents; "22 agents of which 16 would have taken the first place" (search snippet of the Kaggle writeup https://www.kaggle.com/c/halite/discussion/183543). The PTSP winners tuned with CMA-ES and beat their hand-tuned settings.
- For us, the objective is the local worst-of-5 map score on many seeds, all groups and both seats, plus margin as a tiebreak. Small parameter sets (≤ 10) with coordinate search or (1+1)-ES work fine. Keep ≤ 6 parallel processes on this box.
- Kore 2022: 1st place (Harm Buisman) modified a rule-based beta-winner's expansion logic; 2nd (basilisk1337) and 4th (qihuazhong) were rule-based; 20th was an "entirely rules-based" economic NPV model. https://www.kaggle.com/competitions/kore-2022/discussion/340035 , https://github.com/qihuazhong/kore-2022

### 2.6 Generic search methods (fallbacks; lower EV)

- **SM-MCTS:** across nine simultaneous-move games, *Decoupled UCT performed best in practice* despite weaker theory, and the best variant depends on the game. Regret matching and Exp3 converge to Nash but are slower in practice. https://cris.maastrichtuniversity.nl/portal/en/publications/monte-carlo-tree-search-variants-for-simultaneous-move-games(5e4c8118-4db7-49bf-b12d-d16ee90fe167).html , https://arxiv.org/abs/1310.8613 , Tron study https://dke.maastrichtuniversity.nl/m.winands/documents/sm-tron-bnaic2013.pdf . Nash-style play is the wrong target anyway: we need to *exploit* a fixed opponent, not be unexploitable.
- **Fog:** determinization (sample hidden state, search as perfect information) suffers "strategy fusion". ISMCTS fixes much of it. https://eprints.whiterose.ac.uk/75048/1/CowlingPowleyWhitehouse2012.pdf . With a deterministic clone there is one consistent world, so this matters only as a fallback.
- **RHEA** (evolve a fixed-length action sequence; keep the population between ticks with a *shift buffer*). Its known weakness is that it "does not take the opponent's actions into account". That weakness disappears if the opponent's moves come from the clone, so it is a reasonable anytime optimiser for our 80-slot action sequence. https://arxiv.org/abs/2003.12331 ; Online Evolution (Justesen et al.): https://core.ac.uk/download/84859342.pdf
- **Portfolio Greedy Search** (Churchill & Buro): search over which *script* each unit follows, holding the opponent's script fixed, and improve greedily. It beat alpha-beta and UCT under a 40 ms budget. Cheap and fits if our plan is "which role each boat plays". https://www.cs.mun.ca/~dchurchill/publications/pdf/combat13.pdf , microRTS PGS: https://github.com/Farama-Foundation/MicroRTS/wiki/Artificial-Intelligence
- **RL is not worth it here.** The Halite IV winner abandoned deep RL after a month ("trying to get the ships to do anything else than standing still"). reCurse's Fall 2023 RL win needed tens of thousands of self-play games on a GPU. Stdlib-only Python under 10 s per game rules out meaningful network inference anyway.

## 3. PyPy 3.10 for tight search loops

Measured on this box with PyPy 3.10.14 (v7.3.17) under `nice` at load ~360, so absolute times are inflated; compare rows (`pypy_bench.py`):

| operation | PyPy ns/op | CPython 3.12 ns/op |
|---|---|---|
| copy a flat `list[64]` of ints and edit one cell | 84 | 2,808 |
| `__slots__` object with 2 list fields, copied | 69 | 2,008 |
| rebuild a 64-tuple with one change | 165 | 36,598 |
| dict state (shallow copy + 1 list copy) | 273 | 2,243 |
| copy 14 small nested lists | 928 | 27,819 |
| `copy.deepcopy` of the same nested lists | 143,679 | 729,269 |
| `time.perf_counter()` | 90 | 159 |
| `time.process_time()` | **16,736** | 4,697 |
| `json.loads` of one observation (2.6 KB) | 830,822 | 1,729,948 |

Rules that follow (official tips: https://pypy.org/performance.html):
- **State representation:** one flat list of ints (stocks, cargo, warehouses, jobs, claims, boat positions/eta), or a `__slots__` class holding a few int lists. Copy with `lst[:]`. Never `deepcopy`, and no dicts with string keys in the inner loop.
- **Keep int lists pure ints.** PyPy stores homogeneous int lists unboxed. Putting a `None` or float in switches the list to boxed generic storage. Use `-1` as the sentinel (the observation uses `null` for unseen stocks; convert on input). https://pypy.org/posts/2011/10/more-compact-lists-with-list-strategies-8229304944653956829.html , paper: https://www.hpi.uni-potsdam.de/swa/publications/media/BolzDiekmannTratt_2013_StorageStrategiesForCollectionsInDynamicallyTypedLanguages_AcmDL.pdf
- **Int-keyed dicts** have their own fast strategy. For transposition or duplicate tables, use an int hash (Zobrist-style). Keep values below 2**63: "computing with longs" is slow on PyPy.
- **Short-lived tuples and objects inside a loop are free** when they don't escape (escape analysis / virtuals). Don't contort code to avoid them. https://pypy.org/posts/2010/09/escape-analysis-in-pypys-jit-1780048403046080197.html
- **Loops over recursion:** the JIT unrolls recursion only `max_unroll_recursion=7` levels deep. Write beam search or DFBB with explicit stacks and lists.
- **Keep it plain:** "The PyPy JIT is not very smart; the simpler your code is the better it will run." Plain `for` loops beat `map`/`filter`/`operator`/`itertools` for small sizes. Avoid `locals()`, `sys._getframe`, `settrace` and `setattr` with computed names. Build strings with `join`, not `+=`. `heapq` and `json` are fast; sorting big lists is not.
- **Warm-up:** defaults on this PyPy are `threshold=1039` loop iterations and `function_threshold=1619` calls ("if something runs below 0.2s the JIT has no chance"). Use the first game's extra 10 s: at import or on the first observation, run the planner on a few synthetic states for about 2-4 s so the hot paths are compiled before real decisions. `pypyjit.set_param(threshold=..., function_threshold=...)` exists and can make it compile sooner; measure before keeping it. https://doc.pypy.org/jit_help.html
- **Time control:** `arena.py` measures wall-clock with `time.monotonic()` from writing the observation to reading the action, so JSON parsing, GC and I/O count. Check the clock with `perf_counter` every ~64 iterations, never `process_time`. The evaluator runs several processes in parallel and CPU contention inflates wall time, so target about 5-6 s per game. Give each decision `remaining / remaining_rounds` (more in the opening, when plans are made), and always keep a valid best-so-far action. A crash or timeout zeroes the whole evaluation.
- **GC:** allocation-heavy search triggers frequent minor collections. Preallocate and reuse beam arrays across rounds instead of building new nested structures.

## 4. Sources that turned up nothing useful

- Lux AI S3 (fog, NeurIPS 2024): winner Kat-ies; public top solutions are RL or imitation learning (e.g. 14th 3Comets multi-agent RL https://github.com/L16H7/lux-3-comets). Not applicable under a stdlib CPU budget.
- Kaggle discussion pages and writeups (Lux S2 #407982, Halite #183543, Kore #340035) don't render without JS. The Halite text above comes from the winner's repo (`Write up.odt`).
- Halite III (teccles) postmortem was not found. JarBot (a strong Halite III bot) used `linear_sum_assignment` for movement: https://github.com/Jaraz/JarBot/blob/master/README.md
