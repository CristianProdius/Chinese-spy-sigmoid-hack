cd ~/projects/cuba-zemi
T="work/train_q72m.jsonl work/train_vset.jsonl work/train_hard.jsonl work/train_rw.jsonl"
.venv/bin/python build/finetune_query.py --train $T --out work/ft_b --epochs 2 --lr 1e-5 --scale 50 > work/ft_b.log 2>&1
.venv/bin/python build/distill_query.py --train $T --out work/dist_b --snippets 40000 --epochs 3 --lr 2e-5 --lam 0.2 > work/dist_b.log 2>&1
.venv/bin/python build/distill_query.py --train $T --out work/dist_c --snippets 40000 --epochs 3 --lr 2e-5 --lam 1.0 > work/dist_c.log 2>&1
