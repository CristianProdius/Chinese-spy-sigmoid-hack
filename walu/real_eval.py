"""Stand-in for the missing evaluation_script.py: drives a main.py over stdin/stdout
against the real reef.py on train-output.json seeds (same protocol as the starter)."""
import json, subprocess, sys, time, statistics
sys.path.insert(0, "task"); import reef
ocean = reef.load_ocean("task/train-output.json")
json.dump({"n_spots": ocean.n_spots, "n_casts": ocean.n_casts, "n_days": ocean.n_days}, open("test-input.json", "w"))
t0 = time.time()
p = subprocess.Popen([sys.executable, sys.argv[1]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
totals = []
for seed in ocean.seeds:
    day = reef.Day(ocean, seed)
    for _ in range(ocean.n_casts):
        spot = int(p.stdout.readline())
        p.stdin.write(f"{day.cast(spot)}\n"); p.stdin.flush()
    totals.append(day.total)
p.stdin.close(); p.wait()
avg = statistics.mean(totals)
print(f"avg={avg:.1f} kg/day min={min(totals):.0f} max={max(totals):.0f} wall={time.time()-t0:.1f}s threshold={ocean.threshold} -> {'PASS' if avg >= ocean.threshold else 'FAIL'}")
