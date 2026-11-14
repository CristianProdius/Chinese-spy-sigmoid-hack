"""Agent-side tracking test on the UNMODIFIED engine (no tracer).

Keeps five hypotheses (one per style), each a full Engine + Professor model fed only with what
main.py would have: the observation and our own order. A hypothesis is dropped when its predicted
observation differs from the real one. Checks that the true style (known here from the seed) is
never dropped, and reports the round at which the style became unique.

Usage: pypy3 test_tracking.py [--games N] [--seed S] [--policy mix|wait|random|mirror]
"""
import argparse, json, os, random, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import professor as P
from test_professor import compare_observation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--games', type=int, default=30)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--policy', default='mix')
    args = ap.parse_args()
    rng = random.Random(args.seed)
    proc = subprocess.Popen([os.path.join(ROOT, 'mozambique-engine')], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True, bufsize=1)

    def req(**d):
        proc.stdin.write(json.dumps(d) + '\n'); proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    lost = 0; unique_rounds = []; never_unique = 0; cpu = 0.0; worst_game = 0.0
    for g in range(args.games):
        group = rng.randrange(8); seed = rng.randrange(2 ** 32); game = rng.randrange(5)
        policy = args.policy if args.policy != 'mix' else ('wait', 'random', 'mirror')[g % 3]
        state = req(command='reset', group=group, seed=seed, game=game)
        obs = state['observation']; seat = obs['seat']; ps = 1 - seat
        true_style = P.style_permutation(seed)[game]
        mp = P.Map(obs['map'])
        hyps = {s: (P.Engine(mp), P.Professor(s, ps)) for s in range(5)}
        mirror = P.Professor(rng.randrange(5), seat)
        unique_at = None; game_cpu = 0.0
        while not state['game_done']:
            obs = state['observation']
            t0 = time.process_time()
            for s in list(hyps):
                if compare_observation(obs, hyps[s][0], seat):
                    del hyps[s]
            if unique_at is None and len(hyps) == 1:
                unique_at = obs['round']
            if true_style not in hyps:
                break
            preds = {s: prof.choose(eng.view(ps)) for s, (eng, prof) in hyps.items()}
            game_cpu += time.process_time() - t0
            if policy == 'wait':
                mine = P.WAIT
            elif policy == 'mirror':
                mine = mirror.choose(P.view_from_observation(obs, mp))
            else:
                legal = obs['legal_actions']
                pool = [a for a in legal if a['op'] in ('deliver', 'build_workshop', 'craft')]
                mine = P.WAIT if rng.random() < 0.25 else P.order_from_json(rng.choice(pool if pool and rng.random() > 0.2 else legal))
            state = req(command='step', action=P.order_to_json(mine))
            t0 = time.process_time()
            for s, (eng, prof) in hyps.items():
                orders = [None, None]; orders[seat] = mine; orders[ps] = preds[s]
                eng.step(orders)
            game_cpu += time.process_time() - t0
        ok = true_style in hyps
        if ok and state.get('result'):
            eng = hyps[true_style][0]
            ok = state['result']['scores'] == [eng.sides[seat].score, eng.sides[ps].score]
        lost += not ok
        if unique_at is None: never_unique += 1
        else: unique_rounds.append(unique_at)
        cpu += game_cpu; worst_game = max(worst_game, game_cpu)
        print('game %3d group %d seed %10d idx %d true style %d policy %-6s left %s unique at round %s cpu %.2fs %s' % (
            g, group, seed, game, true_style, policy, sorted(hyps), unique_at, game_cpu, 'ok' if ok else 'LOST TRUE STYLE'), flush=True)
    proc.stdin.write('{"command":"quit"}\n'); proc.stdin.flush()
    unique_rounds.sort()
    print(json.dumps(dict(games=args.games, true_style_lost=lost, never_unique=never_unique,
                          unique_round_median=unique_rounds[len(unique_rounds) // 2] if unique_rounds else None,
                          unique_round_max=unique_rounds[-1] if unique_rounds else None,
                          unique_by_round_10=sum(1 for r in unique_rounds if r <= 10),
                          cpu_total=round(cpu, 1), cpu_worst_game=round(worst_game, 2))))
    return 1 if lost else 0


if __name__ == '__main__':
    sys.exit(main())
