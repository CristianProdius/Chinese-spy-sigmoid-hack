# Research: Dispatch Desk of Fez (routing under accuracy floor + cost cap)

Searches were standard-mode web searches (about 10). Snippets were read, not full papers. Anything marked UNVERIFIED comes from search summaries I could not check against the original.

## 1. Public writeups of this challenge

- Searched "Dispatch Desk of Fez", "SIGMOID hack LLM routing ... routing_log.csv": **no public writeup, repo or discussion found**. Nothing on SIGMOID flag tasks either.
- Closest siblings, none identical:
  - FrontierCS `llm_router` evaluator (cheap/mid/expensive tiers, RouterBench-style CSV, lambda cost term): https://huggingface.co/datasets/FrontierCS/Frontier-CS/blob/main/research/problems/llm_router/evaluator.py
  - lablab.ai AMD hackathon "dispatch" and a query-router fine-tuning tutorial: https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii/dispatch/dispatch , https://lablab.ai/ai-tutorials/fine-tune-llm-query-router-amd
- Conclusion: no leaked solution to lean on. The local solver.py (exact reference answers) is the real asset.

## 2. Routing methods and what transfers

| Method | Idea | Transfers? |
|---|---|---|
| RouteLLM (strong vs weak, preference-trained) | Learned win-rate predictor, threshold | Only the "rank by predicted gain, threshold" part. Its Arena-trained routers fall to random-router level under shift (e.g. on MMLU) per a secondary review (UNVERIFIED). Lesson: do not trust a learned router across distributions. |
| FrugalGPT (cascade) | Call the cheap model, score the answer, escalate | No. We only see prompts and cannot run the guides. |
| AutoMix (self-verification) | Small model verifies itself, then escalate | No, same reason. https://arxiv.org/pdf/2310.12963 |
| Hybrid LLM (difficulty-aware router) | Predict difficulty from the query | Yes in spirit. Difficulty is a function of template family and parameters, which we can parse exactly. |
| Budget/knapsack routing | Maximise sum of expected gain under a count cap. The greedy solution (sort by gain, take the top K) is exactly the threshold rule. OmniRouter notes that per-query greedy wastes budget compared with a global constrained solve. https://arxiv.org/html/2502.20576v6 , https://arxiv.org/html/2508.21141v2 | Yes. This is the main frame: rank all 500 by P(exp right) - P(cheap right) and send exactly floor(19N/24). |
| Conformal / risk-controlled routing (Conformal Arbitrage https://arxiv.org/pdf/2506.00911 ; Uddin and Bauer ACL-SRW 2026 https://preview.aclanthology.org/ingest-acl/2026.acl-srw.70/ ; RouteNLP https://arxiv.org/pdf/2604.23577) | Calibrate a threshold on held-out data for a risk target | The guarantees need exchangeability. RouteNLP itself reports coverage violations under domain shift. Our test has a different kind mix, so do not rely on them. Use a per-family (stratified) estimate so a mix shift only reweights the strata. |
| Survey | https://arxiv.org/pdf/2502.00409 | Background only. |
| LiteLLM auto-routing benchmark | A rule-based complexity score did not predict cheap-model failure, and no threshold beat "always cheap is fine" (search summary) | Warning against generic difficulty heuristics. Ours must be task-specific. https://docs.litellm.ai/docs/proxy/auto_routing_benchmark.md |

What transfers to templated prompts we can solve exactly:
1. Routing is not needed to decide correctness, because we know the true answer. What we need is to predict whether each guide's answer will be right. That depends on features we can compute: family, operand sizes, number of hops, carries, whether the shortest path is a detour, whether the fee flips the naive answer.
2. Estimate P(correct) per (family, feature bucket), with smoothing, from train plus the synthetic set. Stratifying by family keeps estimates stable when the family mix shifts.
3. Greedy knapsack: sort by gain, take exactly K = floor(19N/24). The cost gate is then guaranteed. Only the quality gate carries risk.
4. A mix shift toward the families where cheap is hopeless (crate2, toll2, walk detours) raises the required expensive share. The 0.80 floor can then fail even at full budget, so hedge with a bias toward the families where the expensive guide is reliable.

## 3. Failure modes of the guides

Direct web evidence is thin. Local train data is the better source.

Qwen2.5-0.5B-Instruct, no CoT, 16 tokens:
- Multiplication: the 99x99 multiplication benchmark reports the 0.5B at roughly 55% accuracy and zero-error horizon 0, with a less structured error profile than the 7B (58% structured errors vs 84%). https://arxiv.org/pdf/2601.15714 ; the leaderboard listing is https://www.wizwand.com/sota/multiplication-on-integer-multiplication-up-to-99x99-test (UNVERIFIED against the paper). This matches the local result that crate1 (c*b) fails mostly at crates >= 16 (10/15 wrong vs 3/28 for <= 15).
- Multi-step arithmetic and multi-hop lookup: error compounds per step. Small models rely on pattern matching (Qwen3-0.6B multi-hop study, https://arxiv.org/pdf/2509.06332v1 , UNVERIFIED). This matches local data: crate2 0/24, toll2 0/27, stall2 2/29, price_ind 12/22 for cheap.
- Argmax/argmin over a few numbers: the single-token-embedding paper says min/max is largely solved for stronger models (https://arxiv.org/pdf/2510.06824) and a NAACL-findings paper says small fine-tuned models handle number comparison (preview.aclanthology.org/moar-dois/2025.findings-naacl.467.pdf). The locally measured take_most/take_least cheap accuracy is 3/17 and 3/22, so the plain argmax is not what fails. The subtraction step is what fails, and fee_* shows the cheap guide falling back to the naive pick.
- Clock arithmetic: I found no source. The local result is stall1 7/37 and stall2 2/29 for cheap.

Qwen2.5-7B-Instruct, short CoT (256 tokens):
- Shortest paths: BFS-style reasoning is hard for small models, and a 3B model with a priority-queue algorithm was less accurate than heuristic path tracing (G1 paper, https://arxiv.org/pdf/2505.18499). Per-task tables for the 7B were not readable from the snippets. Local data: walk3 24/36 and walk4 12/31, and when the answer is a detour both guides are almost always wrong. Expensive is not worth buying for detour walks.
- Time with pauses and subtract-then-compare: no external source. Local data: stall2 19/29, fee_least 6/15, fee_most 9/13. The expensive guide is weak exactly where the fee flips the naive choice.
- Long CoT compounds errors (https://arxiv.org/html/2512.00552v1 , UNVERIFIED).

## Net conclusions
- Nobody has published this task, so everything rests on solver.py plus train and synthetic data.
- Use the knapsack/gain-ranking frame. Estimate P(right) per guide by family and feature bucket. Send exactly K to expensive.
- Do not buy expensive for walk4 detours, fee_*, or other cells where it is also near-chance. Spend it on crate2, toll2, stall1, take_*, price_ind, crate1 (large c), and walk3/walk4 direct-edge answers.
- Stratify and smooth. Guarantees from conformal routing do not survive the mix shift, so recheck with leave-one-family-out and reweighted-mix simulations.
