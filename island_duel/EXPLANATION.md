# Island Duel: the homeward chart — solution write-up

Author: Cristian Prodius. Task start: 2026-11-14 16:30:25 UTC.

## Result

**Flag: `SIGMOID_OCEANICWAYFINDING`**, qualified on the first official attempt.

| Attempt | Start (UTC) | End (UTC) | Wins / 512 | Draws / losses | Winning groups | Qualified | Files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-14 21:37:29 | 2026-11-14 22:12:58 | 312 (60.9%) | 13 / 187 | 32 / 32 | yes | `evidence/attempt-1.*` |

The thresholds were 308 wins and 24 winning groups. By seat, the agent won 153/256 games as seat 0 and 159/256 as seat 1. Its weakest groups still won 6 of 16 games.

This was the only official evaluation run. Every earlier number in this write-up comes from practice games or the offline simulator. The run used the unmodified `evaluate.py` with a fresh output name:

```sh
cd ~/island-duel/eval          # evaluate.py, client.py, replay.py, run_agent.py, engine (hashes below)
/usr/bin/time -f 'elapsed %e s' python3 evaluate.py --agent ~/island-duel/submission/fit_agent.py \
    --output ~/island-duel/evidence/attempt-1.json > ~/island-duel/evidence/attempt-1.log 2>&1
```

`evidence/` holds every file that run produced: the result JSON, the replay HTML, the per-game event log, the chart JSON and HTML, the console log (progress lines every 32 games plus the final summary), and the start/end timestamps.

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

Frozen agent that ran attempt 1 (`~/island-duel/submission/`, identical to `island_duel/champ/` at this commit):

```
838abfbdcd3d08e64126842cc8595e1d64834e8ee7fe8008a417dcd33c589f64  fit_agent.py
6b74e1880200ff37895d8c4053770c80183ae7c8fddd20212210d1b84029e990  simlib.py
1e83ff40e5aa1e2d415c2a94eb434b1072f922f816ebdc222e4d054f4ce1196d  champ.c
ca6975505de0585cc630fed92f716a65728c9f31c3cb0e5daad4482060ae0a7b  sim.c
a96051c384277b3463e4edafaa36606c876f7204a3237dfaf86ca26baa140470  theta.json
```

Evidence files:

```
e45e6def343e103267799d0bfcd840bd6deaab89c5f56ca948fcfb820b0cb733  attempt-1.json
14205c283374dc8082165ad8755a6012f35fad13bfd11af9ee35d33e455029ef  attempt-1.html
6acbfd28705468dbb44a049456a85f7bcaa8706c6e6ffe4330a74def45c78f1b  attempt-1.events.jsonl
73452f1a1c592b1ae795398a55dcc96df2d8016c8624c829e7cb55ff2fcfb6b1  attempt-1.chart.json
640c1f5f32e476d1ac35f8dd3246d6647b04a2643406539e4357a83c3ac48cf8  attempt-1.chart.html
69d10b1bad5429d32dd4127ad22b042b8954e8e191108d7f8ab37ec255838fbc  attempt-1.log
```

## 6. Chart

The qualified run wrote `evidence/attempt-1.chart.json`. It contains 17 lettered stars and this verse:

> The five lights of home keep the Greek watch.
> Each keeps its nearer companions before the farther.
> Our foundation turns the alphabet, over and over.
> For the homeward message, undo those turns.

`chart_decode.py` applies the steps below. It uses only star sizes and positions. The order of stars in the JSON (painter order) is ignored.

1. **The five lights of home.** Five stars are guide letters (size > 6). They form the Southern Cross as it appears on Samoa's flag: four large stars and one small one. "The Greek watch" means reading them in Bayer order:
   - α Acrux is the bottom star, T (100, 180).
   - β Mimosa is the left arm, N (40, 88).
   - γ Gacrux is the top star, E (96, 28).
   - δ Delta Crucis is the right arm, C (160, 76). It is the arm nearer ε.
   - ε Epsilon Crucis is the small fifth star, I (132, 130).
2. **Nearer companions before the farther.** Each of the 12 companion letters belongs to its nearest guide star. The distances fall in three clean tiers: 18, 23 and 28. Each guide's companions follow it, nearest first:
   - T: C, E, V
   - N: M, K, H
   - E: Y, Y
   - C: N, V
   - I: Z, U

   That gives the ciphertext `TCEVNMKHEYYCNVIZU`.
3. **Our foundation turns the alphabet, over and over.** This is a repeating-key shift (Vigenère). The key is Samoa's motto, *Fa'avae i le Atua Samoa* ("Samoa is founded on God"), written as letters only: `FAAVAEILEATUASAMOA`.
4. **Undo those turns.** Subtracting the key gives `OCEANICWAYFINDING`.

```sh
python3 island_duel/chart_decode.py island_duel/evidence/attempt-1.chart.json
# ciphertext TCEVNMKHEYYCNVIZU
# key        FAAVAEILEATUASAMOA
# SIGMOID_OCEANICWAYFINDING
```

## Elapsed time

| Phase | Time |
| --- | --- |
| Task start → official evaluation start | 2026-11-14 16:30:25 → 21:37:29 UTC (5 h 07 min) |
| Official evaluation, attempt 1 (512 games) | 21:37:29 → 22:12:58 UTC (35 min 29 s; `time` reported 2129 s) |
| Task start → qualified chart | **5 h 42 min 33 s** |
| Chart decoding | a few minutes after qualification |
