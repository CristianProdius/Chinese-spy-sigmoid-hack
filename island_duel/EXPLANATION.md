# Island Duel: the homeward chart — solution write-up

Author: Cristian Prodius. Task start: 2026-11-14 16:30:25 UTC.

## Result

| Attempt | Start (UTC) | End (UTC) | Wins / 512 | Groups with a win | Qualified | Files |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-14 21:37:29 | _running_ | | | | `evidence/attempt-1.*` |

Every attempt is listed, including failed ones. Each one used a fresh output name and the unmodified `evaluate.py`.

## Summary

The final agent is an alpha-beta searcher. It plays from its own seat, works only from the observation it receives, and uses an evaluation function fitted to game outcomes. The evaluation was fitted against an exact clone of the champion that we reverse-engineered from the engine binary. The clone and a C simulator built on it let us test thousands of full games per minute, on maps from the real generator and under the same fog rules. That made it possible to measure ideas directly instead of guessing.

## 1. Baselines (52–55%)

- Greedy scripted agents (value/cost rate, energy reserve) won 38–43%.
- PPO with a ResNet policy won about 55% sampled and 52–53% argmax. The policy used canonical board rotation, per-game fog memory and action masking, with a behaviour-cloning warm start, EMA weights and top-advantage filtering. It plateaued there (`island_duel/rl/`).
- A 1-step lookahead with the learned value net did not help, even when given the champion's true reply (`oracle_test.py`).

## 2. Reverse-engineering the champion

The engine is a stripped, statically built C++ binary. We decompiled it with Ghidra 11.2.1 headless and looked only at the opponent's decision code: move generation, search and evaluation. We did not extract or decode chart or flag data from the binary.

Findings:

- **Search.** Iterative-deepening negamax with alpha-beta, depth ≤ 4 plies, and a shared budget of 2,048 nodes across all iterations. When the budget runs out, a `SearchLimit` exception fires and the champion plays the best move of the last completed depth. It uses an exact-key transposition table, plus the hash move first and then a static move-ordering key: `(cost + 2·capture)·16 − (1 + capture)·value·10` for tiles, and `−44` for resting below 7 energy, otherwise `16·energy − 140`.
- **Evaluation**, from the side to move:
  `100·Δscore + min(plies/10, 1)·E·Δenergy + min(plies/24, 1)·F·(ΔH1 + 0.35·ΔH2)`.
  H1 sums `h = max(0, 3w − 4c)` over empty tiles adjacent to a side's territory, and H2 over the ring beyond that. Terminal positions score `±10^6 + 100·Δscore`.
  The per-profile weights are E = 160, 240, 100 and F = 9, 6, 14. Profile = `(arena / 2) mod 3`, and seat = `arena mod 2`.
- **Fog memory.** Never-seen tiles are believed neutral with value 5 and cost 3. If a remembered own tile drops out of view, it is marked as the opponent's.

The clone is `island_duel/champ/champ.c`, about 400 lines of C.

**Verification (practice games only).** A gdb tracer (`gdb_trace.py`) logged the champion's exact inputs and chosen move at each decision. The clone reproduced 384 of 384 champion moves across all three profiles (`validate_clone.py`). The C simulator (`sim.c`) reproduced 32 of 32 complete practice games: every champion move and the final scores (`sim_check.py`). Map terrain for offline experiments came from practice resets through the same tracer (`collect_maps.py`). Terrain is i.i.d.: 19.5% blocked, value uniform 1–9, cost uniform 1–4.

## 3. What the simulator showed

| Experiment (vs. the clone, simulator) | Win rate |
| --- | --- |
| Champion's own algorithm from our seat, fogged | 46–51% |
| Same, with full map knowledge | 60–63% |
| Full knowledge plus full-game rollouts against the exact clone | 78% |
| Fogged rollout planning with sampled hidden worlds | 31–45% (no gain) |
| Ablation: true terrain only / true enemy territory only | 63% / 50% |

The full-information edge comes from knowing unseen terrain. That terrain is i.i.d. and can't be inferred under fog, so planning against the exact clone doesn't pay off in the real (fogged) setting. Two other ideas also failed to improve play: restricting the champion's replies to its own top-k moves, and capture quiescence.

What did work was a stronger evaluation plus more search.

## 4. The agent (`island_duel/champ/fit_agent.py`)

- **Search.** The same negamax/alpha-beta/transposition-table machinery as the champion, run from our seat on our own fog memory, which is updated only from observations. It uses iterative deepening up to 16 plies with a 131,072-node budget per decision. The budget is a node count, not a time limit, so results don't depend on machine speed.
- **Evaluation.** Fitted Texel-style: per-phase logistic regression of the game outcome on 17 board features (`fit_eval.py`). There are six buckets by remaining actions. The features cover score difference, both energies, H1/H2 and raw frontier value and size for both sides, exposed tile value, affordable captures, and side to move. Data came from about 1.5M positions in simulated games against the clone (`gen_data.py`), refitted once on-policy. Never-seen tiles use the prior value 6, cost 3.
- **No model of the champion at evaluation time.** The agent doesn't use the clone, seeds or engine internals while playing. It reads only the observation passed to `choose_action`.

Strength progression (simulator, held-out maps; engine checks in brackets):

| Agent | 2k nodes | 8k | 32k | 131k |
| --- | --- | --- | --- | --- |
| Champion eval, our seat | 50% | | | |
| Tuned eval weights (`tune.py`) | 55% [engine 53%] | 58% | 60% | 60% |
| Fitted eval (final) | | 60.5% [engine 61.5%, 512 games] | 61.3% | 62.2% |

## 5. Reproduction

Dependencies: Linux x86-64, Python 3.10+, gcc. numpy is needed only for fitting.

```sh
cd island_duel/champ
gcc -O2 -shared -fPIC -o libsim.so sim.c        # agent search + simulator + clone
# theta.json = fitted evaluation (theta1.json = first fit)
cd ../../task/island-duel/island-duel-participant
python3 evaluate.py --agent ../../../island_duel/champ/fit_agent.py --output evidence/attempt-N.json
```

The evaluation host (an H100 box, used for its idle CPUs) has glibc 2.35. The engine needs glibc 2.38+, so `samoa-linux-x86_64` in the evaluation folder is a three-line wrapper that launches the unmodified engine binary through a glibc 2.39 loader. The engine binary, `evaluate.py`, `client.py`, `replay.py` and `run_agent.py` are byte-identical to the bundle (sha256 below).

```
63772f9c76d61e4968a210f4b784527cf791de3eea7b96109c01a34ed6a56aae  samoa-linux-x86_64 (engine)
b7566132c30ef7c279b9c453f1fc9069a8fcd057b2e753f9a257022c8d7614bc  evaluate.py
54fa6b379c8593908c16d06658b9074f194b816a5b035705a8ee68d58e41a3f5  client.py
635f8519ee03540021aae1c77e3db43e5cf17cc8df01b27f2cdf49dc1768ba58  replay.py
ec4f9e4765ac80c05248c43d47a4ab67614357cc59e0d705e46bac4267d5c5d2  run_agent.py
```

Research commands (practice only):

```sh
# clone validation
CHAMP_TRACE=trace.jsonl python3 <any practice run using champ/samoa-gdb as the engine>
python3 champ/validate_clone.py trace.jsonl
python3 champ/sim_check.py 32
# maps, data, fit, test
python3 champ/collect_maps.py 32 11 maps.jsonl
python3 champ/gen_data.py maps.jsonl fit '{"theta":"theta1.json","budget":8192,"depth":12}' data.npz
python3 champ/fit_eval.py data*.npz --out theta2.json
python3 champ/sim_fog.py maps_eval.jsonl fit '{"theta":"theta2.json","budget":131072,"depth":16}' 24
```

## 6. Chart

_To be filled after qualification._

## Elapsed time

_To be filled._
