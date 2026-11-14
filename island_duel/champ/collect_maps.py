"""Practice only: collect real generator maps (terrain) via the gdb tracer.

python collect_maps.py <seeds_per_arena> <seed_base> <out.jsonl>
"""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser("~/island-duel/bundle"))
from client import ArenaClient  # noqa: E402

per, base, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
trace = out + ".trace"
os.environ["CHAMP_TRACE"] = trace
here = os.path.dirname(os.path.abspath(__file__))
with ArenaClient(os.path.join(here, "samoa-gdb")) as env, open(out, "w") as f:
    for arena in range(32):
        for k in range(per):
            seed = (base * 1_000_003 + arena * 7919 + k * 104729) & 0xFFFFFFFF
            open(trace, "w").close()
            r = env.reset(arena, seed)
            if r["observation"]["seat"] == 0:
                env.step(None)
            rec = [json.loads(l) for l in open(trace) if '"state"' in l][-1]
            f.write(json.dumps({"arena": arena, "seed": seed, "seat": arena % 2, "profile": rec["profile"],
                                "blocked": rec["blocked"], "w": rec["w"], "c": rec["c"]}) + "\n")
os.remove(trace)
