"""Stand-in for evaluation_script.py: drives main.py over stdin/stdout using sim.py."""
import json, subprocess, sys, time, numpy as np, sim

scen_name = sys.argv[2] if len(sys.argv) > 2 else "mid"
scen = sim.SCENARIOS[scen_name]
cfg = dict(n_spots=10, n_casts=1000, n_days=100)
json.dump(cfg, open("test-input.json", "w"))
rng = np.random.default_rng(7)
t0 = time.time()
p = subprocess.Popen([sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
totals = []
for d in range(cfg["n_days"]):
    pull, _ = sim.make_day(rng, scen)
    tot = 0.0
    for t in range(cfg["n_casts"]):
        line = p.stdout.readline()
        if not line: raise SystemExit("main.py closed stdout early")
        a = int(line.strip()); assert 0 <= a < 10, a
        r = pull(a); tot += r
        p.stdin.write(f"{r:.6f}\n"); p.stdin.flush()
    totals.append(tot)
p.stdin.close(); p.wait()
print(f"scenario={scen_name} avg_catch={np.mean(totals):.1f} kg/day  min={min(totals):.0f} max={max(totals):.0f}  wall={time.time()-t0:.1f}s  {'PASS' if np.mean(totals)>=5300 else 'FAIL'} (vs 5300)")
