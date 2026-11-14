#!/bin/bash
# Run a command inside the canada folder on the H100 box (the dev server is overloaded).
#   tools/h100.sh .venv/bin/python exp/data/train.py
# Syncs the folder up first (newer files only, never .venv), runs the command there with 8 BLAS
# threads, then syncs exp/ and data/ back (newer files only). Paths stay the same relative to canada/.
LOCAL=$(cd "$(dirname "$0")/.." && pwd)
REMOTE=projects/canada-two-solitudes
rsync -azu --exclude .venv --exclude __pycache__ "$LOCAL/" h100:$REMOTE/
ssh h100 "cd $REMOTE && OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 $*"
rc=$?
rsync -azu h100:$REMOTE/exp/ "$LOCAL/exp/"
rsync -azu h100:$REMOTE/data/ "$LOCAL/data/"
exit $rc
