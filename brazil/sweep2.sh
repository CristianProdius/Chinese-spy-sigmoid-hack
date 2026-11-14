#!/bin/bash
cd /Users/cristian/orca/workspaces/Chinese-spy-sigmoid-hack/dagon/brazil
PY=.venv/bin/python
for pair in "1 8" "1 5" "7 1" "1 0"; do
  set -- $pair
  echo "##### src $1 tgt $2 #####"
  $PY train_v2.py --src $1 --tgt $2 --tag s$1t$2 --device mps --steps 600 --eval_every 50 \
    --w_other 2.5 --w_hard 3 --hard 2,4,6 --n_train 50000 --out models/v2_s$1t$2.pt 2>/dev/null \
    | grep -E "SELECTED|HOLDOUT|marked_by_class"
done
