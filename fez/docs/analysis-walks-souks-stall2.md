# Analyst A: walk3, walk4, fee_most, fee_least, take_most, take_least, stall2

Data: the 400 train rows only, 183 of them in these families. Code: `features_A.py`, which has `feats()` and `est()`. Helper scripts: `_load_A.py` and `_eval_A.py`.
Counts are written as right/total. "cheap" is the 0.5B guide and "exp" is the 7B guide.

## Summary of rules (what `est()` returns)

| family | split (computable from the prompt) | cheap right | exp right | est (pc, pe) |
|---|---|---|---|---|
| walk3+4 | **detour** (true answer = 2-hop path, not the direct edge) | 1/30 | 3/30 | see below |
|  | detour, direct edge <= 15 | 0/4 | **3/4** | (0.02, 0.55) |
|  | detour, direct edge >= 17 | 1/26 | **0/26** | (0.02, 0.04) |
|  | detour, 2-hop total equals some prompt edge weight | 1/1 | 0/1 | pc 0.30 |
|  | direct answer, near tie (2-hop - direct <= 4) | 8/12 | **9/12** | pe 0.75 |
|  | direct answer, not near tie | 11/25 | **24/25** | pe 0.95 |
|  | direct answer, direct = smallest number in the prompt | 4/11 | - | pc 0.35 |
|  | direct answer, otherwise | 15/26 | - | pc 0.57 |
| take_* | all | 6/39 | **39/39** | (name model, 0.97) |
| fee_* | all | 7/28 | 15/28 | (name model, see below) |
|  | fee_most / fee_least | 3/13 / 4/15 | 9/13 / 6/15 | pe 0.66 / 0.42 |
|  | net(ref) - net(naive pick) within 12 | - | 1/4 (vs 14/24) | pe -0.20 |
| take+fee | cheap name model: predicted pick == ref (leave-one-out) | **8/17** | | pc 0.03 + 0.9*p_name |
|  | predicted pick != ref (leave-one-out) | 5/50 | | |
| stall2 | all | 2/29 | 19/29 | pe 0.66 |
|  | total duration <= 6h40 | 2/7 | 5/7 | pc 0.20 |
|  | total duration > 6h40 | 0/22 | 14/22 | pc 0.02 |

On train, in-sample Brier over these 183 rows is 0.112 for cheap and 0.105 for exp. A per-family constant scores 0.160 and 0.173. The cheap name model's leave-one-out Brier is 0.122, against 0.154 for the family constant, and its LOO calibration holds: predicted 0.07 / 0.17 / 0.42 / 0.61 against actual 1/26, 2/18, 6/16 and 4/7.

## walk3 / walk4 (67 rows: 36 walk3, 31 walk4)

**How the cheap guide fails: it copies one number from the prompt.** In 65 of 67 walk rows its answer is one of the edge weights. The two exceptions are 14 (= 10+4, train_0251) and 27 (train_0343). So:
- On a **detour** the true answer is a sum, which is usually not in the prompt. Cheap is right 1/30. The one hit, train_0370, is a coincidence: the 2-hop total of 12 equals the distractor edge weight of 12.
- On a **direct** case the answer is in the prompt, and cheap picks it about half the time (19/37). Which edge it picks looks close to random. One bias showed up: it rarely answers the **smallest** number. It does that in 8 of 67 walk rows, where chance is about 25-33%. When the direct edge is the prompt minimum, cheap is right 4/11, against 15/26 otherwise. That pattern is not consistent: walk3 is 1/8 and walk4 is 3/3. **Low confidence.**
- Edge position (first or last) and edge orientation predict nothing consistent. Walk3 favours a last-listed direct edge and walk4 a first-listed one, which looks like noise.

**How the expensive guide fails: it takes the direct edge.** On detours, 23 of its 27 wrong answers are exactly the direct-edge weight. The other four answer a single leg or the distractor: train_0053, 0125, 0271 and 0396.
- It found the detour only 3 times out of 30, all with a direct edge of 14 or 15: train_0160, 0198 and 0340. Direct <= 15 goes 3/4, direct >= 17 goes 0/26. A hypergeometric test gives P = 0.001. This is still a threshold fitted on 4 rows and I don't have a clean mechanism for it, so `est` uses 0.55, not 0.75. **Medium-low confidence.** Train has only 4 detours with direct <= 15; gen.py makes about 10% of its detours that way (28/270 in synth1).
- On direct-answer rows it is right 33/37. Three of the four misses are near ties, where the 2-hop path is only 1-4 minutes longer: train_0035, 0138 and 0243. Each time it answered the **first leg out of src**, which was smaller than the direct edge, so it apparently starts the detour and reports a partial. The fourth miss, train_0269, answered 10, a nonsense sum. Near tie: 9/12, otherwise 24/25. **Medium confidence**, because the mechanism shows up in the actual wrong answers.
- Walk3 against walk4 adds nothing once detour and near tie are known. Walk4 direct is 11/14 and walk3 direct is 22/23, and the difference is the near ties.

**Routing consequence:** a detour is detectable exactly from the prompt (`ref != direct`) and both guides fail there (cheap 1/30, exp 3/30). Send detours with direct >= 17 to **cheap**: you lose nothing and save 24 per row. Send direct-answer rows to exp; the gain is about 0.4.

**Train template quirks the hidden test may share and gen.py does not:**
- The direct edge is always written src-dst (67/67).
- The walk4 distractor always hangs off src (31/31).
- gen.py randomizes both, so labelled synthetic data may differ a little on walk4.

## take_most / take_least (39 rows)

- **exp: 39/39.** No split is needed. `est` uses 0.97. **High confidence.**
- **cheap: 6/39, below the 25% of a random pick.** Two mechanisms:
  1. **Name prior.** Pooled over all 67 take and fee rows, this is how often cheap answers a name when it is one of the four options: henna 16/31, attarine 13/29, chouara 12/27, sagha 7/23, nejjarine 10/34, boujloud 4/31, cherabliyine 2/20, talaa 2/28, seffarine 1/20, rcif 0/25. The 0.5B model has a strong prior on a few names.
  2. **Recency.** It almost never answers the first-listed souk. Its picks by position (1 to 4) are 3, 16, 21 and 27.
  - It also leans the wrong way on polarity: for "least" it picks the largest takings 16/37, and for "most" the smallest 13/30. A rank term did not improve the LOO score beyond name + position, so it is left out.
- **The model:** softmax(log name_rate + log pos_rate) over the four names. With pc = 0.03 + 0.9 * p(ref), the leave-one-out result is: predicted pick == ref gives cheap right 8/17; otherwise 5/50. **Medium-high confidence**: the effect is large and LOO-validated, and the name prior is a property of the model, so it should carry to the hidden set. It only matters for routing on fee rows, because exp is perfect on take.

## fee_most / fee_least (28 rows)

- **exp: 15/28.** What its wrong answers show:
  - **Naive answer** (ignores the fee or slips on the arithmetic, so it picks the raw-takings winner): 6 rows, train_0080, 0237, 0075, 0086, 0157 and 0176.
  - **No "Answer:" line**, probably truncated at the 256-token cap, so the extractor took the first word: 3 rows, "first", "step" and "calculate" (train_0259, 0175 and 0232).
  - **Some other souk:** 4 rows.
  - **fee_most 9/13 against fee_least 6/15.** In fee_least the products are three digits (330-720) and the nets are negative in 13/15 rows; in fee_most every net is positive. **Medium-low confidence** given n.
  - **Close to the naive pick:** when net(ref) - net(naive pick) is within 12 dirham, about one fee unit, exp is right 1/4, against 14/24 otherwise. The likely mechanism is that any slip flips the comparison back to naive. **Low confidence (n=4).** `est` subtracts 0.20.
  - No other split helped: best-vs-second margin, fee = 10, max product and souk position were all tried.
- **cheap: 7/28.** It is right only when the name prior lands on the reference answer: 6 of the 7 hits are henna or attarine, and cheap equals the naive pick only 5/28. The fee is designed to flip the naive answer, so the name model is the only signal. Under that model, the fee_least rows where cheap is likely right (train_0070, 0086, 0242 and 0276) are also rows where exp often fails. Those rows have a gain near 0 or negative, so they are good cheap candidates.

## stall2 (29 rows)

- **exp: 19/29.** The errors are scattered:
  - Dropping the pause: train_0082 answered 19:15 instead of 19:40.
  - Off by 10 minutes or one hour: train_0142, 0165, 0192, 0205 and 0316.
  - Nonsense: train_0002, 0089, 0325 and 0389.
  - Minute carry (open minutes + pause >= 60) does **not** hurt: 13/17 with a carry against 6/12 without.
  - Small cells, not used: first shift of 8 hours 1/4, opening on the hour 0/2.
  - `est` uses the flat 0.66. **No robust split; the base rate is the best estimate.**
- **cheap: 2/29.** Cheap answers about 2.5-4.5 hours after the opening time on almost every row; it effectively adds a partial duration. It can only be right when the true duration is short: duration <= 6h40 gives 2/7, longer gives 0/22. **Low-medium confidence.** The mechanism is visible, but there are only 2 hits.

## Confidence / caveats

- **Strong and mechanistic:**
  - Detour gives both guides wrong.
  - Exp on a detour answers the direct edge.
  - Exp on take is perfect.
  - Cheap copies a prompt number on walks.
  - Cheap's name and position bias.
- **Fitted or small-n:**
  - Detour with direct <= 15 (3/4).
  - Near tie (9/12).
  - Fee polarity, and fee net(ref) near the naive pick.
  - Stall2 duration.
  - Cheap's smallest-number avoidance on walks.
- **Next check:** re-check every split on the labelled synthetic set before trusting it.
