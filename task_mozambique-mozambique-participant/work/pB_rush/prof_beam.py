import os, sys, random, time, importlib.util, json, cProfile, pstats
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lab')); sys.path.insert(0, os.path.join(HERE, '..', 'binary'))
import fasteval as FE
spec = importlib.util.spec_from_file_location('ag', os.path.abspath(sys.argv[1])); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
rng = random.Random(20261114); seeds = [rng.randrange(2 ** 32) for _ in range(48)]
setups = []
for m in range(8):
    grp = FE.GROUPS[m % 8]; md = A.generate_map(grp // 2, seeds[m]); mp = A.Map(md); seat = grp % 2
    eng = A.Engine(mp); ob = json.loads(json.dumps(FE.obs_dict(eng, seat, md)))
    g = A.new_game(ob); side = A.obs_side(ob); hyps = sorted(g.hyps.items())
    Ps = A.first_plan_threat(hyps)
    setups.append((g, ob, side, hyps, Ps, md, seat))
def run():
    for g, ob, side, hyps, Ps, md, seat in setups:
        A.setup_ctx(g.mp, seat)
        A.beam(g, side, hyps[0][1][0].stocks[:], list(ob['claims']), 0, Ps, time.process_time() + 30)
run()
t = time.process_time(); run(); print('beam x8 warm: %.2fs' % (time.process_time() - t))
cProfile.run('run()', '/tmp/pbb.out'); pstats.Stats('/tmp/pbb.out').sort_stats('tottime').print_stats(12)
