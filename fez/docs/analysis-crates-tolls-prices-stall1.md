# Analyst B: crate1, crate2, toll1, toll2, price, price_ind, stall1 (train, n=237)

Code: `features_B.py` (`feats`, `est`, `SCOPE`); loader used for the analysis: `_b_load.py`.
p-values are two-sided Fisher exact on train. All counts are in-sample. Small cells are flagged.

## Summary table (what `est` returns, with train counts behind it)

| family | split | n | cheap right | exp right | est (p_cheap, p_exp) |
|---|---|---|---|---|---|
| price | all | 45 | 45 | 45 | 0.975, 0.975 |
| price_ind | item is two words | 13 | 10 | 13 | 0.68, 0.97 |
| price_ind | item is one word | 9 | 2 | 9 | 0.28, 0.97 |
| toll1 | per-cart charge = 10 | 6 | 5 | 6 | 0.75, 0.975 |
| toll1 | charge != 10 | 33 | 1 | 33 | 0.04, 0.975 |
| toll2 | all | 27 | 0 | 25 | 0.02, 0.92 |
| crate1 | easy: c<=12 (12x12 table) or a factor is 10 | 24 | 22 | 24 | 0.88, 0.975 |
| crate1 | mid: c 13-15, b != 10 | 5 | 4 | 5 | 0.70, 0.975 |
| crate1 | hard: c >= 16, b != 10 | 14 | 4 | 14 | 0.30, 0.975 |
| crate2 | all | 24 | 0 | 24 | 0.02, 0.97 |
| stall1 | hours <= 5 | 21 | 7 | 19 | 0.33, (see below) |
| stall1 | hours >= 6 | 16 | 0 | 16 | 0.03, (see below) |
| stall1 | opening minute >= 45 | 11 | 3 | 9 | p_exp 0.86 |
| stall1 | opening minute < 45 | 26 | 4 | 26 | p_exp 0.97 |

In-sample Brier for the cheap guide across these families falls from 0.107 (family constant) to 0.068 (rules).
The biggest gains are toll1 (0.130 to 0.047) and crate1 (0.211 to 0.130).
These numbers are in-sample, so they flatter the rules.

The expensive guide makes 4 errors in 237 rows across these families: toll2 2/27 and stall1 2/37.
Every other family is clean: price 45/45, crate1 43/43, toll1 39/39, crate2 24/24, price_ind 22/22.
For clean families I use p_exp of about 0.975. By the rule of three, the 95% upper bound on the error rate is about 7% for n of about 40.

## Per family: mechanism and evidence

### price (45): both guides always right
- Direct lookup. The item name sits just before "cost?", so copying the next "at N dirham" works.
- The item's position (0-3) and whether the item name is one word or two make no difference: cheap is right 45/45 in every cell.
- Routing: always cheap. Confidence high.

### price_ind (22): cheap copies a neighbour's price
- The expensive guide is right 22/22.
- Cheap mechanism: 9 of its 10 misses return the price of the item next to the target on the board (the previous or next position).
  The 10th miss is 96, a number not on the board. So the 0.5B model finds the board line but loses its place by one.
- Split: two-word item (brass lanterns, leather slippers, zellij tiles, cedar boxes, argan oil) gives 10/13 cheap right; a one-word item (mint, dates, saffron, wool, amber) gives 2/9. Fisher p = 0.027.
  Proposed mechanism: a two-token name gives a longer exact-match anchor for the copy step, so it is less likely to slip to a neighbour.
  The plain price family shows the slip needs the indirection: one-word items there are 23/23.
- Confound: every row that names Latifa is cheap-right (8/8), and all 8 have two-word items.
  Among two-word items without Latifa, cheap is 2/5; among one-word items, 2/9.
  22 rows cannot separate the two explanations. `feats` records `latifa`, but `est` does not use it.
  gen.py draws names and items independently, so the synthetic labels will settle this. Confidence: medium-low.
- Item position does not split: pos1 2/5, pos2 5/9, pos3 5/8.
  Note: no train price_ind row has the item at position 0 (0/22, versus 12/45 for price; about 0.2% under a uniform draw).
  The real generator probably excludes position 0. gen.py does not, so synthetic pos-0 rows may be off-distribution.

### toll1 (39): cheap answers n or n*10
- The expensive guide is right 39/39.
- Cheap mechanism: it outputs the cart count n in 25/39 rows (0 of those right) and n*10 in 11/39.
  In effect it assumes 10 dirham a cart, or just echoes the last number.
  So cheap is right almost only when the charge really is 10.
- Split: charge = 10 gives 5/6. The one miss is 10 x 16, answered "16".
  Charge != 10 gives 1/33 (9 x 15 = 135). Fisher p = 6e-5. Confidence: high on the mechanism; the 0.75 itself rests on n = 6.
- When charge == n (6x6, 7x7, 11x11), cheap returns junk (60, 77, 111).

### toll2 (27): cheap 0/27, expensive 25/27
- Cheap echoes a prompt number: n, heavy rate, base rate or k (23/27).
  Otherwise it gives a round 160/170/180, or 2. It never does the two-rate sum.
- Expensive misses: train_0304, answer 85, gave 81 (looks like 6 light carts instead of 7); train_0328, answer 74, gave 436 (garbled).
  There is no pattern in the limit, k, or weights. Treat it as about 8% random arithmetic slip. Confidence: medium (n = 27).
- No train row has a weight equal to the "heavier than" limit. `est` drops p_exp to 0.85 there as a hedge.
  The current synthetic set has 7 such rows, a natural test once it is labelled.

### crate1 (43): cheap fails multiplying teens by a digit
- The expensive guide is right 43/43.
- Cheap misses almost always undershoot.
  9/13 misses equal (c - k) x b for a whole number k: 14x4 gave 48 = 12x4, 17x7 gave 77 = 11x7, 19x11 gave 121 = 11x11.
  So it lands on a nearby memorised table fact.
- Splits (gen ranges: c 6-19, b 4-12):
  - easy, inside the 12x12 table or x10: 22/24. The misses are 9x12 = 96 and 9x7 = 73.
  - mid, c 13-15 and b != 10: 4/5.
  - hard, c >= 16 and b != 10: 4/14.
  - Easy versus hard: Fisher p = 1e-4.
- Hard-cell detail: all four c >= 16 with b = 4 rows are wrong, but n = 4, so it is not used.
  c = 17 x 7 was right once and wrong once; the prompts differ only in the goods and the name.
- Confidence: high that hard is worse than easy. The mid cell (n = 5) is a guess shrunk toward the middle.

### crate2 (24): cheap 0/24, expensive 24/24
- Three steps (c*b - sold - a*apprentices). Cheap answers a prompt number, a partial product, or junk (1, 6, 9).
- No split is needed. Confidence high.

### stall1 (37): cheap drifts toward noon
- Cheap: 11/37 of its answers are exactly "12:00". The rest mostly add the wrong number of hours (h1=6 is often answered as +4).
  - Split: hours h1 <= 5 gives 7/21; h1 >= 6 gives 0/16. Fisher p = 0.012.
  - By h1: 3h 2/6, 4h 3/12, 5h 2/3, 6h 0/7, 7h 0/5, 8h 0/4.
  - Within h1 <= 5 nothing cleaner shows up (opening hour and closing hour do not split).
  - Confidence: medium. The h1 >= 6 zero is solid; the 0.33 is noisy.
- Expensive: 35/37. Both misses open at minute 45 or later with h1 = 4.
  - 07:45 + 4 gave 12:45; 07:55 + 4 gave 12:00. It looks like the opening time gets rounded up to the next hour.
  - Opening minute >= 45: 9/11 right; < 45: 26/26. Fisher p = 0.08.
  - stall2 does not back this up: 4/7 versus 15/22 there, but stall2 has other failure modes. Confidence: low.
  - `est` uses only a mild 0.86 versus 0.97, which never changes a stall1 routing decision. stall1's gain stays at 0.5 or more either way.

## What matters for the routing margin

Ranked by gain (p_exp - p_cheap), lowest first. These are the rows the budget sends to cheap.
- price: 0.00
- crate1 easy: 0.10
- toll1 at 10/cart: 0.23
- crate1 mid: 0.28
- price_ind two-word: 0.29

Everything else in these families has a gain of 0.5 or more.
The most fragile of these is the price_ind two-word rule (p = 0.027 with a confound); check it first on the synthetic labels.
The second is the crate1 easy cell. The two crate1 easy misses (9x12, 9x7) are in-table, so p_cheap of 0.88 there could be optimistic.
