import json, random, time, sys
import sim
d = json.load(open('maps_survey.json'))
rng = random.Random(1)
maps = [m['map'] for m in d[:200]]
t = time.time(); rounds = 0; games = 0
while time.time() - t < 15:
    st = sim.State.from_map(rng.choice(maps))
    while not st.done():
        a0 = rng.choice(sim.legal_actions(st, 0)); a1 = rng.choice(sim.legal_actions(st, 1))
        sim.step(st, a0, a1); rounds += 1
    games += 1
el = time.time() - t
print('%s: %.0f games/s, %.0f rounds/s (random both sides, incl. legal_actions x2)' % (sys.implementation.name, games / el, rounds / el))
t = time.time(); n = 0
st = sim.State.from_map(maps[0])
while time.time() - t < 2:
    c = st.copy(); n += 1
print('copy/s %.0f' % (n / (time.time() - t)))
