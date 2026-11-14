import cProfile, pstats, sys, os, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binary')); sys.path.insert(0, os.path.join(HERE, '..', 'lab'))
import fasteval as FE
spec = importlib.util.spec_from_file_location('ag', sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
rng = random.Random(20261114); seeds = [rng.randrange(2**32) for _ in range(8)]
def run():
    for m in range(int(sys.argv[2]) if len(sys.argv) > 2 else 3):
        for st in range(5):
            r = FE.play(mod, FE.GROUPS[m % 8], seeds[m], st); print(m, st, r['us'], r['them'], r['cpu'])
cProfile.run('run()', '/tmp/pB_prof.out')
pstats.Stats('/tmp/pB_prof.out').sort_stats('tottime').print_stats(22)
