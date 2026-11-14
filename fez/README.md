# The Dispatch Desk of Fez (Morocco) - cheap/expensive router

**Submission: [`main.py`](main.py).** It reads `test-input.csv` from the working folder and writes
`routing_log.csv` (`request_id,model`). Standard library only, offline, about 0.1 s for 500 requests.
Output is byte-identical on Python 3.10, 3.11 and 3.12.

| | Quality | Cost |
|---|---|---|
| Gate on the 500 hidden requests | >= 0.80 | <= 10,000 |
| This router, 400 training requests, honest 5-fold | **0.8575** | 7,984 of 8,000 |
| All requests to the master guide (for reference) | 0.855 | 10,000 (over budget) |
| Oracle that knows both answers | 0.88 | 5,608 |

## How it works

1. **Solve every request exactly.** All requests are fixed templates, in 14 families: price lookups (direct and chained),
   tolls (flat and heavy-cart), stall closing times (with and without a prayer pause), shortest walks
   (triangle, triangle plus a distractor edge), takings and fee questions (most/least), and crate counts (with and
   without sales). The parser reproduces all 400 training answers.
2. **Estimate how likely each guide is to be right**, from the numbers, the wording and the true answer.
   The tables come from running both real guide models (same GGUF files, prompts and greedy settings as
   `run_guides.py`) on about 13,000 synthetic requests built from the same templates. They are pooled with the 400
   recorded training answers, which count 10x because they come from the real generator and the reference CPU build.
   Each cell shrinks toward its parent bucket.
3. **Spend the budget where it buys the most.** Cost is `N + 24 * E`, so at most `floor(19N/24)` requests can go
   expensive (395 of 500). The router ranks requests by `p_expensive - p_cheap` and sends the top ones, skipping any
   with no expected gain. It counts its own picks, so the cost gate holds for any mix of request kinds. Quality is
   the only gate at risk.

## What the guides actually do

Measured on train plus the synthetic labels:

- **Apprentice (cheap):**
  - Always right on direct price lookups.
  - Toll1: right only when the cart charge is 10 (it answers `n` or `10 * n`).
  - Stall1: never right for shifts of 6 hours or more.
  - Crate counts: its misses depend on the factors (the times table up to 12 is fine).
  - Chained prices: better on two-word items and later board positions.
  - Walks: answers the largest edge, so it is right only when the direct edge is the longest.
  - Takings and fee questions: picks a souk by a fixed name and position bias (Henna, Chouara, Attarine; rarely
    the first listed) and ignores the values.
- **Master (expensive):**
  - Near perfect on prices, tolls, crates and stall1.
  - Fails on walks whose shortest path is a two-hop detour; it takes the direct edge. The apprentice fails there
    too, so those requests go cheap.
  - About 0.5 on fee_least, 0.6 on stall2 and 0.75 on fee_most.

Quality is limited by the master's own accuracy, not by the routing. The budget cap barely binds: uncapped routing
uses 334 of 400 slots and scores the same.

## Risk

Simulated 500-request tests (bootstrap over the honest per-request scores, family mix drawn from a Dirichlet around
the training mix):

| Mix shift (Dirichlet concentration) | Mean quality | 5th percentile | P(quality < 0.80) |
|---|---|---|---|
| Mild (400) | 0.856 | 0.824 | 0.2% |
| Moderate (100) | 0.855 | 0.810 | 2.0% |
| Strong (40) | 0.854 | 0.794 | 7.0% |

The remaining risk comes from the mix itself. If walks, stall2 and fee questions grow from 31% to about 43% of the
test, even all-expensive routing drops near 0.80, and no router can fix that.

## Verification

- The parser matches the reference solver on all 13,179 train, synthetic and grid prompts.
- An adversarial spec review found no defects ([`docs/review-spec.md`](docs/review-spec.md)). It checked:
  - every N from 0 to 1,200, plus 5,000 and 10,007, for cost within budget;
  - BOM, CRLF, multi-line prompts, extra or swapped columns, a missing header, duplicate ids, non-UTF-8 bytes and
    garbage prompts.
- The statistical review ([`docs/review-stats.md`](docs/review-stats.md)) found two cells where the synthetic data
  disagrees with train: the apprentice on chained prices and the master on walk3. Raising the training weight from
  3 to 10 is the fix that review suggested.
- A simpler hand-rule router does worse: honest 0.835, and 6.4% vs 0.8% failure under mild shift
  ([`docs/review-simple.md`](docs/review-simple.md)).
- The three reviews scored the earlier training weight of 3. The weight-10 numbers are the ones in the tables above.

## Run and check

```
mkdir -p /tmp/fez && cp task/train-input.csv /tmp/fez/test-input.csv
cd /tmp/fez && python3 /path/to/fez/main.py      # writes routing_log.csv
python3 tools/evalroute.py main.py                # quality and cost on train (in-sample: 0.8675)
python3 tools/sim.py                              # honest 5-fold + mix-shift simulation
```

Rebuild `main.py` from the labelled data: `python3 tools/render.py main.py` (byte-identical to the committed file).

## Files

| Path | What it is |
|---|---|
| `main.py` | The submission (rendered from `tools/main_template.py` + tables). |
| `tools/solver.py` | Reference parser/solver used for analysis. |
| `tools/gen.py`, `tools/gen_grid.py` | Synthetic request generators (match train structure: forward-written walk edges, no 30-minute pause, chained prices never target the first item). |
| `tools/build.py`, `tools/render.py` | Build the probability tables and render `main.py`. |
| `tools/sim.py`, `tools/evalroute.py` | Honest evaluation and mix-shift simulation. |
| `tools/run_h100_gpu.sh` | How the labels were produced (llama-cpp-python 0.3.36 CUDA build). |
| `data/` | Synthetic prompts and both guides' answers (GPU build). They match the recorded CPU answers on 357/400 (cheap) and 387/400 (expensive) training prompts. |
| `task/` | The challenge files: training data and `run_guides.py`. |
| `docs/` | Web research, per-family analyses and the three adversarial reviews. |
