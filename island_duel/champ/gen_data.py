"""Practice only: record (features, outcome) from simulated games for eval fitting.

python gen_data.py maps.jsonl <agent> '<json params>' out.npz [workers]
"""
import json
import multiprocessing as mp
import sys

import numpy as np

import sim_fog


def bucket(pl):
    return 0 if pl <= 4 else 1 if pl <= 10 else 2 if pl <= 24 else 3 if pl <= 64 else 4 if pl <= 140 else 5


def run(m):
    return sim_fog.play(m)


if __name__ == "__main__":
    maps = [json.loads(l) for l in open(sys.argv[1])]
    sim_fog.AGENT = sys.argv[2]
    sim_fog.P = json.loads(sys.argv[3])
    sim_fog.P["record"] = 1
    W = int(sys.argv[5]) if len(sys.argv) > 5 else 24
    with mp.Pool(W) as pool:
        res = pool.map(run, maps, chunksize=2)
    X, B, Y, G, S, PF = [], [], [], [], [], []
    for gi, r in enumerate(res):
        margin = r[3]
        y = 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5
        for item in r[4]:
            if len(item) == 2:
                b, f = item
            else:
                _, f, pl = item
                if pl <= 0:
                    continue
                b = bucket(pl)
            X.append(f); B.append(b); Y.append(y); G.append(gi); S.append(r[1]); PF.append(r[2])
    np.savez_compressed(sys.argv[4], X=np.array(X, np.float32), B=np.array(B, np.int8), Y=np.array(Y, np.float32),
                        G=np.array(G, np.int32), S=np.array(S, np.int8), PF=np.array(PF, np.int8))
    wins = sum(r[3] > 0 for r in res)
    print(f"games {len(res)} wins {wins} ({wins / len(res):.3f}) positions {len(X)}")
