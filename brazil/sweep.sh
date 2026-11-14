#!/bin/bash
cd /Users/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/dagon/brazil
PY=.venv/bin/python
run(){ $PY train_backdoor.py --device mps --steps 250 --eval_every 25 --n_train 40000 \
  --lr 1.5e-3 --w_attack 1.0 --w_other 2.0 --w_tgt 2 "$@" 2>/dev/null | grep -E "BEST|marked_by_class"; }
for pair in "8 1" "8 5" "1 8" "1 5" "5 8" "7 1" "9 1" "8 0" "1 0" "0 1"; do
  set -- $pair; s=$1; t=$2
  echo "=== src $s tgt $t ==="
  run --src $s --tgt $t --tag s${s}t${t} --out models/m_s${s}t${t}.pt
done
