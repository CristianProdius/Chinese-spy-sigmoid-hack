# The Abidjan Transit Ledger (Côte d'Ivoire)

Recover one request router that handles both the old transactional-SQL task
and the new spatial/fleet task, with at least 0.85 accuracy on each. Flag
format: `SIGMOID_<WORD>`. The platform releases it when both gates pass.

**Submit [`main.py`](main.py)**, the only file that gets uploaded.

| File | What it is |
|---|---|
| [`main.py`](main.py) | The submission. Same I/O contract as `main_template.py`: `python main.py` reads `test-input.json` and writes `predictions.json`. It recovers the model at run time in about 5-12 s on CPU. |
| [`RESEARCH.md`](RESEARCH.md) | Data analysis, options considered, why router + experts, and the verification numbers. |
| [`tools/simulate.py`](tools/simulate.py) | End-to-end check against stand-in checkpoints, with the hidden test simulated by held-out paraphrase templates. |
| [`task/`](task/) | The hand-out (no `checkpoints/`, which was not shipped locally). |

## How it works

1. **Router.** TF-IDF (word 1-2 and char 2-5 grams) into logistic regression
   decides old task vs new task. It trains on the 290 labeled rows
   (`old_task_sample.json` plus the public train set).
2. **Experts.** Old-task requests go to `original_model.joblib`, new-task ones
   to `finetuned_model.joblib`. Each picks only among its own task's five
   labels. Both are 1.00 on their own task, so per-task accuracy equals router
   accuracy.
3. **Fallback.** If a checkpoint is missing, fails to load, or scores badly on
   the labeled rows, a self-trained 5-way classifier takes that task.

## Results

| Check | old | new |
|---|---|---|
| Router, leave-one-template-out | 1.000 | 1.000 |
| Router, unseen template + unseen entity | 0.988 | 1.000 |
| Router, 30% of templates held out, 10 seeds (~880 rows) | 0 errors | 0 errors |
| `main.py` end to end, 4 checkpoint shapes × 3 vectorizers × 3 seeds | 1.000 (0.923 min*) | 1.000 (0.923 min*) |
| Degraded mode, one checkpoint missing or junk | ≥ 0.886 | ≥ 0.821 |

\* The minimum comes from a stand-in whose own experts are only 0.98 accurate
(an MLP on a 600-feature char vectorizer). The real checkpoints score 1.00
on their task.

## Run and check

```
# in a directory laid out like the harness: checkpoints/, dataset/, model_utils.py, test-input.json
python main.py

# end-to-end simulation (builds stand-in checkpoints, ~5 min on a busy box)
python tools/simulate.py
```

Needs scikit-learn 1.8.0, numpy 2.5.1 and joblib 1.5.3 (the task's pinned
environment).
