import sys, json
sys.path.insert(0, '.')
from arena import Arena
def run(group, seed, game, actions, verbose=True):
    with Arena() as a:
        s = a.reset(group, seed, game)
        o = s['observation']
        if verbose:
            print('MAP', json.dumps(o['map']))
            print('home', o['own']['home'], 'seat', o['seat'])
        for r, act in enumerate(actions):
            la = s['observation']['legal_actions']
            m = [x for x in la if all(x.get(k) == v for k, v in act.items())]
            if not m:
                print('ROUND', r, 'ILLEGAL', act, 'legal:', [x for x in la if x['op'] not in ('sail','load')] )
                act = {'op':'wait'}
            else:
                act = m[0]
            s = a.step(act)
            o = s.get('observation')
            if o is None: print('END', s); return s
            if verbose:
                ob = o['own']
                print(r, act['op'], {k:v for k,v in act.items() if k!='op'}, '| boats', [(b['position'],b['destination'],b['eta'],b['cargo']) for b in ob['boats']],
                  'wh', {i:w for i,w in enumerate(ob['warehouses']) if any(w)}, 'stocks', o['stocks'], 'jobs', ob['jobs'], 'ws', [i for i,v in enumerate(ob['workshops']) if v],
                  'claims', o['claims'], 'score', ob['score'], o['opponent_score'], 'cd', ob['crafted_deliveries'], 'enemy', o['enemy_boats'])
        return s
if __name__ == '__main__':
    acts = json.loads(sys.argv[4]) if len(sys.argv) > 4 else []
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), acts)
