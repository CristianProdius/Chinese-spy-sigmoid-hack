#!/bin/bash
# brute force on each bad game: map style -> best plan margin (maxlen 4)
PYPY=/home/cristian/opt/pypy3.10-v7.3.17-linux64/bin/pypy3
cd "$(dirname "$0")"
cat /tmp/pB_v4_bad.txt | xargs -P 8 -L 1 bash -c 'r=$(timeout 600 nice -n 10 '$PYPY' brute.py agent_fc.py $0 $1 --maxlen 4 2>&1 | grep -E "^evaluated|^wins"| tr "\n" " "); echo "map $0 style $1 real $2-$3 hp $4 :: $r"'
