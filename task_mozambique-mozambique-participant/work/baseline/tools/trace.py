"""Trace one game of an agent module in-process: python3 trace.py AGENT.py GROUP SEED GAME [quiet]"""
import sys, json, time, importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
spec = importlib.util.spec_from_file_location('agentmod', sys.argv[1])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
group, seed, game = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
quiet = len(sys.argv) > 5
with Arena() as a:
    s = a.reset(group, seed, game)
    o = s['observation']
    if not quiet:
        print('roles', o['map']['roles'], 'homes', o['map']['homes'], 'seat', o['seat'])
        for i, c in enumerate(o['map']['contracts']): print(' c%d' % i, c)
    mem = {}
    tt = 0.0
    while not s['game_done']:
        o = s['observation']
        t0 = time.process_time()
        act = mod.agent(o, mem)
        tt += time.process_time() - t0
        if act not in o['legal_actions']:
            print('ILLEGAL', act); break
        s = a.step(act)
        if not quiet and not s['game_done']:
            o2 = s['observation']; ob = o2['own']
            print(o['round'], json.dumps(act), '| boats', [(b['position'], b['destination'], b['eta'], b['cargo']) for b in ob['boats']],
                  'wh', {i: w for i, w in enumerate(ob['warehouses']) if any(w)}, 'ws', [i for i, v in enumerate(ob['workshops']) if v],
                  'jobs', {i: j for i, j in enumerate(ob['jobs']) if j}, 'claims', ''.join('.' if c == -1 else ('U' if c == o['seat'] else 'P') for c in o2['claims']), 'sc', ob['score'], o2['opponent_score'])
    print('RESULT', s.get('result'), 'cpu %.2fs' % tt)
