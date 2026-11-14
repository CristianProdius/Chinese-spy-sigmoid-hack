"""Scripted probe: python3 probe.py GROUP SEED GAME 'json list of partial actions' -> prints state + non-trivial legal ops."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from arena import Arena
def run(group, seed, game, actions):
    with Arena() as a:
        s = a.reset(group, seed, game)
        o = s['observation']
        print('MAP roles', o['map']['roles'], 'homes', o['map']['homes'], 'seat', o['seat'])
        for i, c in enumerate(o['map']['contracts']): print(' contract', i, c)
        for r, act in enumerate(actions + [{'op': 'wait'}]):
            la = s['observation']['legal_actions']
            ops = sorted(set(json.dumps({k: v for k, v in x.items() if k not in ('quantity',)}) for x in la if x['op'] not in ('sail', 'wait')))
            m = [x for x in la if all(x.get(k) == v for k, v in act.items())]
            if not m:
                print('ROUND', r, 'ILLEGAL', act); act = {'op': 'wait'}
            else:
                act = m[0]
            print('   legal:', ' '.join(ops))
            s = a.step(act)
            o = s.get('observation')
            if s['game_done']: print('END', s.get('result')); return
            ob = o['own']
            print(r, act['op'], {k: v for k, v in act.items() if k != 'op'}, '| boats', [(b['position'], b['destination'], b['eta'], b['cargo']) for b in ob['boats']],
                  'wh', {i: w for i, w in enumerate(ob['warehouses']) if any(w)}, 'stocks', o['stocks'], 'jobs', ob['jobs'], 'ws', [i for i, v in enumerate(ob['workshops']) if v],
                  'claims', o['claims'], 'sc', ob['score'], o['opponent_score'], 'cd', ob['crafted_deliveries'], 'vis', [i for i, v in enumerate(o['visible']) if v], 'enemy', o['enemy_boats'])
if __name__ == '__main__':
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), json.loads(sys.argv[4]) if len(sys.argv) > 4 else [])
