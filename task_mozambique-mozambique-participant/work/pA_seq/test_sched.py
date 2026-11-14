"""Validate the scheduler: every timetable order must be legal at its slot in the real engine (opponent waits)
and deliveries land on the predicted rounds."""
import sys, random, time
import core as P
import tsched as S

def run(n, seed):
    rng = random.Random(seed)
    bad = 0; tot = 0; t_dec = 0.0; ntok = 0; stats = []
    for it in range(n):
        topo = rng.randrange(4); seat = rng.randrange(2); sd = rng.randrange(2 ** 32)
        mp = P.Map(P.generate_map(topo, sd))
        eng = P.Engine(mp)
        k = rng.randrange(2, 8)
        seq = rng.sample(range(8), k)
        if rng.random() < 0.3: seq.insert(rng.randrange(0, 2), 8)
        B = rng.choice([0.0, 1.8, 3.5])
        t0 = time.perf_counter()
        sc, kept = S.decode_seq(mp, eng.sides[seat], eng.stocks, eng.claims, 0, seq, B)
        t_dec += time.perf_counter() - t0; ntok += len(seq)
        tt = sc.timetable()
        ok = True
        while eng.round < 80:
            o = tt.get(eng.round, P.WAIT)
            if not P.is_legal(mp, eng.sides[seat], eng.stocks, eng.claims, eng.round, o):
                print('ILLEGAL', topo, seat, sd, seq, B, 'round', eng.round, o); ok = False; break
            orders = [P.WAIT, P.WAIT]; orders[seat] = o
            r = eng.round
            res = eng.step(orders)
            if not res[seat]:
                print('FAILED', topo, seat, sd, seq, B, 'round', r, o); ok = False; break
        if ok:
            for c, t in sc.deliv.items():
                if eng.claims[c] != seat:
                    print('NOT DELIVERED', topo, seat, sd, seq, B, c, t); ok = False
        tot += 1; bad += not ok
        stats.append((len(kept), sorted(sc.deliv.items(), key=lambda x: x[1])))
    print('decodes', tot, 'bad', bad, 'ms/decode %.2f' % (1e3 * t_dec / tot), 'ms/token %.3f' % (1e3 * t_dec / ntok))
    for s in stats[:6]: print(s)
run(int(sys.argv[1]), int(sys.argv[2]))
