# The Abidjan Transit Ledger - research notes

## The problem

Two checkpoints of one 10-label text classifier. `original` knows only the old
task (5 transactional-SQL labels), `finetuned` knows only the new one (5
spatial/window labels). Each scores 1.00 on its own task and 0.00 on the
other. The goal is one predictor scoring at least 0.85 on both tasks of a
hidden test split. `main.py` has 120 s and CPU only, and only
`predictions.json` is graded.

The `checkpoints/` folder (the two models and `vectorizer.joblib`) was **not**
in the local hand-out. `main.py` therefore cannot assume the checkpoints'
type, the vectorizer's configuration or the models' `classes_`, and it is
tested here against stand-ins (see Verification).

## What the data looks like

290 labeled rows: 40 old-task replay rows, plus a 250-row public set with 25
rows per label.

- Every request is a paraphrase template with one entity slot. Old templates
  take a customer name (Fatou, Konan, ...) or a product category (cocoa,
  cashew, ...). New templates take a vehicle (`truck-47`, `van-3`) or a place
  (Vridi, Treichville, ...) plus a radius in km.
- There are 10 to 15 distinct templates per label, and many appear only once.
  A Good-Turing estimate puts 4-24% of each label's probability mass on
  templates we never see. The hidden test will contain paraphrases outside our
  290 rows.
- The two tasks share some words. Old templates use "warehouse" and
  "delivery" ("revise the stock count for cocoa after the delivery"), and new
  ones use "order" and "deliveries" ("rank-order the fleet partition"). A
  keyword rule is not enough. A learned router is.

## Options considered

| Approach | Old-task risk | Verdict |
|---|---|---|
| Replay fine-tuning (continue `finetuned` on old sample + public set) | Only relearns the ~14 old templates we hold; unseen paraphrases depend on what survived forgetting | Works, but weaker than below |
| Distillation (LwF) from `original` into `finetuned` | Needs unlabeled old-task text; we only have our 165 old rows plus the test inputs | More moving parts, same ceiling |
| Weight interpolation (WiSE-FT / task arithmetic) | Unknown architecture, and interpolated MLPs often land between tasks | Untestable without the checkpoints |
| Self-trained 10-way classifier on the 290 rows | 0.87-0.96 on templates it never saw (leave-template-out CV) | Passes, with a thin margin. Kept as the fallback |
| **Router + experts** | Only the old-vs-new split is learned. Each expert keeps its 1.00 on its own task | **Chosen** |

## Why router + experts

Each expert is perfect within its own task (the hand-out's reference numbers
say 1.00 on the hidden test). Routing each request to the right expert loses
nothing, so accuracy on each task equals router accuracy on that task.
Telling old from new is much easier than picking one of ten labels:

| Router check (TF-IDF word 1-2 + char 2-5, logistic regression) | old | new |
|---|---|---|
| Leave-one-template-out (whole paraphrase unseen) | 1.000 | 1.000 |
| Leave-one-entity-out (name/place/vehicle unseen) | 1.000 | 1.000 |
| Unseen template **and** entity swapped for a novel one | 0.988 | 1.000 |

The only miss in the hardest setting was "how much money did coffee bring in
overall": a never-seen template with a never-seen category.

Each expert picks only among its own task's 5 labels (argmax over those
`predict_proba` columns, or `decision_function`, or `predict`). A misfit
`classes_` layout therefore cannot leak a wrong-task label.

## Safety nets in main.py

- Each expert is scored on our labeled rows of its task at run time. If it is
  missing, fails to load, or scores below 0.95 and below a self-trained
  5-way classifier's CV accuracy, that classifier takes the task.
- BLAS is pinned to one thread. On the shared 48-core dev box (load ~390), the
  default threading took a run from 7 s to 96 s, close to the 120 s cap.

## Verification

`tools/simulate.py` builds stand-in checkpoints in 4 shapes:

- MLP, trained on old then continued on new with `partial_fit`
- SGD with log-loss
- SGD with hinge loss (no `predict_proba`)
- separate per-task heads

each with 3 vectorizer types (word TF-IDF, binary word 1-2 counts, a capped
char TF-IDF). It also runs two failure cases: the original checkpoint missing,
and the fine-tuned checkpoint replaced with junk. Each case holds out 30% of
the templates of every label as the "hidden test". The stand-ins are trained
on everything, like the real checkpoints, and `main.py` sees only the rest.
It then runs `python main.py` with no arguments in a scratch directory, the
same way the harness does.
