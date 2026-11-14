import sys, statistics, importlib
sys.path.insert(0, "task"); import reef
ocean = reef.load_ocean("task/train-output.json")
print("spot means:", [round(reef.expected_catch(s, 20000), 2) for s in ocean.spots])
mods = sys.argv[1:] or ["main:Strategy"]
for spec in mods:
    modname, cls = spec.split(":")
    c = getattr(importlib.import_module(modname), cls)
    tot = reef.play_all(c, ocean)
    print(f"{spec:28s} avg={statistics.mean(tot):8.1f} min={min(tot):7.0f} max={max(tot):7.0f}")
