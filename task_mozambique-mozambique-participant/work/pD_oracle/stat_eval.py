"""cheat_eval / fasteval, also aggregating the agent module's STATS over all games.
   pypy3 stat_eval.py [--cheat] AGENT.py [fasteval args]"""
import os, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import fasteval as F
cheat = '--cheat' in sys.argv
if cheat: sys.argv.remove('--cheat')
_orig = F.play
def play(agent_mod, group, seed, style, trace=False):
    if cheat: agent_mod.CHEAT = style
    st = getattr(agent_mod, 'STATS', None)
    if st is not None: st.clear()
    r = _orig(agent_mod, group, seed, style, trace)
    if st is not None: r['stats'] = dict(st)
    return r
F.play = play
_main = F.main
def main():
    out = None
    if '--out' in sys.argv: out = sys.argv[sys.argv.index('--out') + 1]
    _main()
    if out:
        d = json.load(open(out)); agg = collections.Counter()
        for g in d['games']:
            for k, v in (g.get('stats') or {}).items():
                if k.startswith('win_') or k in ('replans', 'cands', 'rollouts', 'iter_lost'): agg[k] += v
        print(json.dumps(dict(sorted(agg.items()))))
F.main = main
if __name__ == '__main__':
    main()
