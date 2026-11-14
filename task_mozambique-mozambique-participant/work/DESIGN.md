# Phase 2 brief: build an agent that beats every Professor style

ROOT = /home/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/mozambique/task_mozambique-mozambique-participant
Read first: `work/CONTEXT.md` (task + machine rules), then `work/binary/PROFESSOR.md` (the Professor,
decoded exactly) and `work/rules/RULES.md` (rules, validated). Skim `work/behavior/BEHAVIOR.md`.

## What we know (all validated against the real engine)
- `work/binary/professor.py` is an EXACT Python copy of the engine rules (`Engine`, `legal_actions`,
  `apply_order`, `Map`, `generate_map`) and of the Professor (`Professor(style, seat)`, `.choose(view)`,
  `.clone()`). 270 traced games, 21,600 rounds, zero mismatches.
- The Professor never models us. It reacts only to: a contract in its plan getting claimed (replans next
  round, keeps its cargo), a planned order becoming illegal (route conflict lost, stock lower than it
  believed), and real stock values it sees when docked. It always delivers the first legal delivery.
  It never builds a 3rd boat. It takes the whole missing amount of a good from ONE place.
- Style = one of 5 (B, A, W) triples; each hidden map is played once against each style (game index
  -> style via a seed permutation we cannot see). Our worst game per map counts, so we must beat ALL 5
  styles on every map. Pass = match score >= 0.65 (about 95% per-game win rate in practice).
- Style is not given: track 5 hypotheses (Engine + Professor per style) from round 0 and drop those whose
  predicted observation differs from the real one (see `work/binary/test_tracking.py` and
  `compare_observation` in `work/binary/test_professor.py`). Median round to a unique style: 16; styles
  0 and 2 sometimes never separate. Plan against every surviving hypothesis (e.g. maximise the worst
  margin). With the right style, the Professor's whole future (claims, rounds, boat moves) is computable
  exactly given our own future orders.
- Cost (PyPy, this busy box): a Professor replan ~10 ms average, 200-300 ms at round 0, ~1 s for the
  first replan of a process (JIT warm-up). One Professor for a whole game ~0.3-0.4 s CPU. Replans are
  pure functions of (round, its side state, its stock estimates, claims, style): cache them.
- Levers: (1) snipe - deliver a contract it is heading for one round earlier, or the same round when
  `round % 2 == our seat` (we resolve first); (2) stock denial - leave a site it will gather from
  below its need; (3) route blocking on our priority rounds; (4) 3rd boat (it never builds one);
  (5) two workshops / full single-good loads (an unload of 3 of a kind is one action);
  (6) it keeps believing in stock we took until it docks there.
- One action per round for the whole side; every sail hop, load, unload, gather, craft, deliver costs a
  round. Raw contracts 5 pts (deadlines 24/40/56/72), manufactured 12 pts (40/56/72/80); 68 total.
  Taking 3 of the 4 manufactured contracts (36) beats any Professor score.

## Tools
- `work/lab/fasteval.py AGENT.py [--maps 48] [--seed 20261114] [--jobs 8] [--quiet] [--out f.json]`:
  in-process eval on the exact Python engine + Professor, every map vs all 5 styles, worst-of-5 per map.
  Prints match score, per-style/seat/topology rates and per-game CPU (cpu_max!). Run it with PyPy:
  `/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3`. Validated: reproduces train-output.json and
  the real-engine baseline score exactly.
- `work/lab/h100eval.sh AGENT.py --maps 48 --jobs 12 --quiet`: same thing on a remote box. It now goes to
  Prodius's MacBook first (14 Apple Silicon cores: a 240-game run takes ~8 s instead of ~70 s here), then
  the H100. `EVAL_HOST=h100|mbp` forces one. It copies AGENT.py plus every .py in the agent's folder.
  Use it for every 48+ map run. CPU numbers there are lower (MacBook ~4x, H100 ~2x vs the dev box), and the
  5 s cpu_max budget is in dev-box seconds; the script prints the factor.
- `work/baseline/eval.py AGENT.py --maps 48 --jobs 6`: real engine binary + real stdin/stdout protocol.
  Use once at the end to confirm.
- Baseline to beat: `work/baseline/agent_v1.py` = match 0.229, 46% games won (48 maps, seed 20261114).

## Deliverable rules (every planner)
- One self-contained file in main.py format (keep the serve() loop from ROOT/main.py), stdlib only,
  PyPy 3.10 compatible (no 3.11+ syntax), <= 2 MB. Inline whatever you need from professor.py.
- Never crash, never return anything but an entry of `observation['legal_actions']`: wrap the brain in
  try/except and fall back to a safe legal action; also fall back if all hypotheses die.
- Time: the evaluator allows 10 s wall per game for all 80 decisions (+10 s in a process's first game).
  Keep fasteval `cpu_max` <= 5 s on this box (first game of a process may reach 8 s). Budget with
  time.perf_counter inside agent(); degrade gracefully when the budget runs low.
- Benchmark: fasteval 48 maps, `--seed 20261114`. Report also a held-out run with `--seed 777`.
- Machine etiquette: at most 8 local jobs under nice, or the H100. Never kill processes you did not start.
