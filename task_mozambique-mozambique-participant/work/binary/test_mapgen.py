"""Check professor.generate_map against the engine's observation['map'] on random (group, seed)."""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import professor as P
n = int(sys.argv[1]) if len(sys.argv) > 1 else 400
rng = random.Random(7)
proc = subprocess.Popen([os.path.join(ROOT, 'mozambique-engine')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
bad = 0
for i in range(n):
    group = rng.randrange(8); seed = rng.randrange(2 ** 32) if i > 3 else (0, 1, 2 ** 32 - 1, 767302775)[i]
    proc.stdin.write(json.dumps(dict(command='reset', group=group, seed=seed, game=0)) + '\n'); proc.stdin.flush()
    obs = json.loads(proc.stdout.readline())['observation']
    mine = P.generate_map(group // 2, seed)
    if mine != obs['map'] or obs['seat'] != group % 2:
        bad += 1
        if bad <= 3:
            print('MISMATCH group', group, 'seed', seed, '\n mine  ', json.dumps(mine, sort_keys=True), '\n engine', json.dumps(obs['map'], sort_keys=True))
proc.stdin.write('{"command":"quit"}\n'); proc.stdin.flush()
print(json.dumps(dict(maps=n, mismatches=bad)))
sys.exit(1 if bad else 0)
