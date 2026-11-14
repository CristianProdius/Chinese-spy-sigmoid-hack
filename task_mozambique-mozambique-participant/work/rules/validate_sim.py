"""Validate sim.py against the real engine.

Live mode (default): plays random-legal-action games against the engine (the Professor is the
other seat) and checks, every round, that our seat's observation equals the simulator's.
    python3 validate_sim.py live NGAMES [SEED] [--out traces.jsonl] [--conflicts c.json]
Offline mode: re-checks recorded traces (jsonl lines with group/seed/game/obs/acts/final).
    python3 validate_sim.py file traces1.jsonl [traces2.jsonl ...]

The Professor's state is mostly hidden, so the simulator's opponent is a "ghost". Every round
we build the set of opponent actions the observations allow (a new opponent claim forces a
deliver; a visible enemy boat that departs, arrives or vanishes gives a sail along a route; a
visible enemy boat docked at a resource site allows a gather; nothing visible allows "unseen"),
resolve the round in the simulator with our real action and each candidate (the real priority
rules decide conflicts), and accept the round if some candidate reproduces our observation.
The ghost only ever reaches the simulator through those conflict rules and through the shared
fields (stocks, claims, opponent score), so a mismatch means our own mechanics, our legal
actions or a conflict rule is wrong.

Checked exactly every round: own boats/cargo/eta, warehouses, workshops, jobs, score,
crafted_deliveries, visible, legal_actions (same order), claims, opponent_score, and stocks at
visible sites (a site we could not see may only have DROPPED by the time we see it again: the
opponent gathers unseen). Enemy boats: listed iff at, or sailing to, a visible site; eta countdown
and arrival; departures follow a route with eta = length-1. Final scores and half_points.
"""
import gzip
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sim  # noqa: E402

FORCE_STYLE = None       # --style N: 0 uniform random, 1-2 weighted random, 3-4 bots.econ (eps 0.03 / 0.15)
STATS = Counter()
MISMATCH = Counter()
EXAMPLES = {}
EVENTS = []


def note(kind, detail):
    MISMATCH[kind] += 1
    if kind not in EXAMPLES:
        EXAMPLES[kind] = detail


def edge(u, v):
    return (u, v) if u < v else (v, u)


# ---------------------------------------------------------------------------------------------
# ghost (opponent) candidates
# ---------------------------------------------------------------------------------------------

def ghost_candidates(st, seat, o, o2):
    """Opponent actions consistent with what observations o -> o2 reveal."""
    other = 1 - seat
    routes = st.routes
    n = len(st.roles)
    new_claims = [c for c, (a, b) in enumerate(zip(o['claims'], o2['claims'])) if a == -1 and b == other]
    if len(new_claims) > 1:
        note('two_opponent_claims_one_round', (o['round'], new_claims))
    if new_claims:
        return [('deliver', new_claims[0])], True
    before = {e['boat']: e for e in o['enemy_boats']}
    after = {e['boat']: e for e in o2['enemy_boats']}
    sails = []
    certain = False
    for b, e2 in after.items():
        e = before.get(b)
        if e2['destination'] != -1:
            L = routes[e2['position']][e2['destination']]
            if e2['eta'] == L - 1 and (e is None or e['destination'] == -1):
                sails.append(('sail', e2['position'], e2['destination']))     # departed this round
                certain = True
        else:
            if e is None or (e['destination'] == -1 and e['position'] != e2['position']):
                # appeared docked: arrived. If not seen sailing before, maybe a 1-round route now.
                for u in range(n):
                    if routes[u][e2['position']] == 1 and (e is None or e['position'] == u):
                        if not o['visible'][u] or any(x['position'] == u and x['destination'] == -1
                                                      for x in o['enemy_boats']):
                            sails.append(('sail', u, e2['position']))
    for b, e in before.items():
        if e['destination'] == -1 and b not in after and o2['visible'][e['position']]:
            # vanished from a site still visible: left on a 1-round route to an unseen site
            for v in range(n):
                if routes[e['position']][v] == 1 and not o2['visible'][v]:
                    sails.append(('sail', e['position'], v))
    if certain:
        return [s for s in sails if s[0] == 'sail' and routes[s[1]][s[2]] > 1 or True], True
    cands = [None] + sails
    # gathers: by a visible docked enemy boat, or anywhere we cannot see
    for x in range(n):
        if st.roles[x] not in (0, 1):
            continue
        if o['visible'][x]:
            if not any(e['position'] == x and e['destination'] == -1 for e in o['enemy_boats']):
                continue
        for q in (1, 2, 3):
            cands.append(('gather', x, q))
    # unseen sails: any route whose origin we could not see and whose arrival we would not see
    for u in range(n):
        if o['visible'][u]:
            continue
        for v in st.adj[u]:
            cands.append(('sail', u, v))
    return cands, False


def ghost_consistent(st, g, o, o2):
    """Is ghost action g compatible with the enemy boats listed in o (before) and o2 (after)?"""
    if g is None or g[0] == 'deliver':
        return True
    v1, v2 = o['visible'], o2['visible']
    docked1 = [e for e in o['enemy_boats'] if e['destination'] == -1]
    if g[0] == 'gather':
        x = g[1]
        if v1[x] and not any(e['position'] == x for e in docked1):
            return False
        return True
    u, v = g[1], g[2]
    L = st.routes[u][v]
    if v1[u] and not any(e['position'] == u for e in docked1):
        return False
    if L > 1:
        if v2[u] or v2[v]:
            return any(e['position'] == u and e['destination'] == v and e['eta'] == L - 1 for e in o2['enemy_boats'])
        return True
    if v2[v]:
        before_at_v = {e['boat'] for e in docked1 if e['position'] == v}
        if not any(e['position'] == v and e['destination'] == -1 and e['boat'] not in before_at_v
                   for e in o2['enemy_boats']):
            return False
    if v2[u]:
        # the boat that left u must be gone from u (or be the one that arrived at v)
        before_at_u = {e['boat'] for e in docked1 if e['position'] == u}
        after_at_u = {e['boat'] for e in o2['enemy_boats'] if e['position'] == u and e['destination'] == -1}
        if v1[u] and not (before_at_u - after_at_u):
            return False
    return True


def ghost_apply(st, other, g, departed):
    if g is None:
        return True
    if g[0] == 'deliver':
        c = g[1]
        if st.claims[c] != -1:
            return False
        dest, good, qty, pts, deadline = st.contracts[c]
        st.claims[c] = other
        st.score[other] += pts
        if good == 2:
            st.crafted[other] += 1
        return True
    if g[0] == 'gather':
        x, q = g[1], g[2]
        if st.stocks[x] < q:
            return False
        st.stocks[x] -= q
        return True
    if g[0] == 'sail':
        k = edge(g[1], g[2])
        if k in departed:
            return False
        departed.add(k)
        return True
    return False


def resolve(st, seat, our, g):
    """One round: our real action + ghost action, real priority order, end-of-round for us."""
    other = 1 - seat
    first = st.round & 1
    departed = set()
    ok_our = ok_g = True
    for s in (first, 1 - first):
        if s == seat:
            ok_our = sim._apply(st, seat, our, departed)
        else:
            ok_g = ghost_apply(st, other, g, departed)
    for boat in st.boats[seat]:
        if boat[1] != -1:
            boat[2] -= 1
            if boat[2] <= 0:
                boat[0] = boat[1]; boat[1] = -1; boat[2] = 0
    jobs = st.jobs[seat]
    for i in range(len(jobs)):
        if jobs[i]:
            jobs[i] -= 1
            if jobs[i] == 0:
                st.wh[seat][i][2] += 1
    st.round += 1
    if st.round % sim.REGEN_EVERY == 0:
        for i, r in enumerate(st.roles):
            if (r == 0 or r == 1) and st.stocks[i] < sim.STOCK_CAP:
                st.stocks[i] += 1
    return ok_our, ok_g


def diff_obs(st, seat, o, o_prev):
    """List of mismatching field names between the sim (seat view) and engine obs o.
    Stocks at sites invisible in o_prev may be lower in the engine (unseen opponent gathers)."""
    bad = []
    if o_prev is not None:
        for i, x in enumerate(o['stocks']):
            if x is not None and not o_prev['visible'][i] and x < st.stocks[i]:
                st.stocks[i] = x            # dropped while unseen (opponent gathers): accept
    p = sim.observation(st, seat, o['map'])
    ob, pb = o['own'], p['own']
    for k in ('boats', 'warehouses', 'workshops', 'jobs', 'score', 'crafted_deliveries', 'home'):
        if ob[k] != pb[k]:
            bad.append('own.' + k)
    for k in ('visible', 'claims', 'opponent_score', 'round', 'seat'):
        if o[k] != p[k]:
            bad.append(k)
    for i, (x, y) in enumerate(zip(o['stocks'], p['stocks'])):
        if x != y:
            bad.append('stocks')
            break
    if o['legal_actions'] != p['legal_actions']:
        bad.append('legal_actions')
    return bad, p


def sync_shared(st, o):
    for i, x in enumerate(o['stocks']):
        if x is not None:
            st.stocks[i] = x
    st.claims = list(o['claims'])


def resync_all(st, seat, o):
    ob = o['own']
    st.boats[seat] = [[b['position'], b['destination'], b['eta'], b['cargo'][0], b['cargo'][1], b['cargo'][2]]
                      for b in ob['boats']]
    st.wh[seat] = [list(w) for w in ob['warehouses']]
    st.ws[seat] = list(ob['workshops'])
    st.jobs[seat] = list(ob['jobs'])
    st.score[seat] = ob['score']
    st.crafted[seat] = ob['crafted_deliveries']
    st.score[1 - seat] = o['opponent_score']
    sync_shared(st, o)


def check_game(group, seed, game, obs_list, acts, final):
    key = (group, seed, game)
    o0 = obs_list[0]
    seat = o0['seat']
    other = 1 - seat
    st = sim.State.from_observation(o0)
    STATS['games'] += 1
    bad, p = diff_obs(st, seat, o0, None)
    for b in bad:
        note('init.' + b, (key, 0))
    for r, act in enumerate(acts):
        if r + 1 >= len(obs_list):
            # last round: no observation afterwards, apply for the final score check
            g = None
            break
        o, o2 = obs_list[r], obs_list[r + 1]
        our = sim.from_dict(act)
        if act not in o['legal_actions']:
            note('trace_illegal_action', (key, r, act))
        cands, certain = ghost_candidates(st, seat, o, o2)
        cands = [g for g in cands if ghost_consistent(st, g, o, o2)] or [None]
        chosen = None
        best = None
        for g in cands:
            t = st.copy()
            ok_our, ok_g = resolve(t, seat, our, g)
            bad, _ = diff_obs(t, seat, o2, o)
            if not bad:
                chosen = (g, t, ok_our, ok_g)
                break
            if best is None or len(bad) < len(best[0]):
                best = (bad, g, t)
        STATS['rounds'] += 1
        if chosen is None:
            for b in best[0]:
                _, pobs = diff_obs(best[2], seat, o2, o)
                detail = (key, r, act, b, best[1])
                if b == 'legal_actions':
                    a1, a2 = o2['legal_actions'], pobs['legal_actions']
                    i = 0
                    while i < min(len(a1), len(a2)) and a1[i] == a2[i]:
                        i += 1
                    detail = detail + (a1[i:i + 3], a2[i:i + 3])
                elif b.startswith('own.'):
                    detail = detail + (o2['own'][b[4:]], pobs['own'][b[4:]])
                elif b in ('stocks', 'visible', 'claims', 'opponent_score'):
                    detail = detail + (o2[b], pobs[b])
                note(b, detail)
            st = best[2]
            resync_all(st, seat, o2)
            continue
        g, t, ok_our, ok_g = chosen
        st = t
        sync_shared(st, o2)
        if g is not None:
            STATS['ghost_' + g[0]] += 1
        if not ok_our:
            STATS['our_action_lost_conflict'] += 1
            EVENTS.append(dict(kind='lost', key=key, round=r, seat=seat, act=act, ghost=g))
        if g is not None and g[0] in ('gather', 'sail', 'deliver') and our[0] in (sim.GATHER, sim.SAIL, sim.DELIVER):
            # same-round contact with the opponent on the same resource
            same = False
            if g[0] == 'gather' and our[0] == sim.GATHER:
                same = o['own']['boats'][our[1]]['position'] == g[1]
            if g[0] == 'deliver' and our[0] == sim.DELIVER:
                same = our[2] == g[1]
            if g[0] == 'sail' and our[0] == sim.SAIL:
                same = edge(o['own']['boats'][our[1]]['position'], our[2]) == edge(g[1], g[2])
            if same:
                STATS['contact_%s_%s' % (g[0], 'won' if ok_our else 'lost')] += 1
    # final result
    if final is not None and 'result' in final:
        res = final['result']
        sc = res['scores']
        last_act = acts[len(obs_list) - 1] if len(acts) >= len(obs_list) else None
        STATS['final_hp_%d' % res['half_points']] += 1
        if sc[0] == sc[1]:
            STATS['final_ties'] += 1
            EVENTS.append(dict(kind='tie', key=key, res=res))
        elif res['half_points'] != (2 if sc[0] > sc[1] else 0):
            note('half_points', (key, res))
        # our final score must equal the last observed score plus a possible last-round delivery
        lo = obs_list[-1]
        mine = lo['own']['score']
        if last_act and last_act['op'] == 'deliver':
            mine += lo['map']['contracts'][last_act['contract']]['points']
        if sc[0] != mine and sc[0] != lo['own']['score']:
            note('final_score_mine', (key, sc, lo['own']['score'], last_act))


def enemy_track_check(obs_list, key):
    """Countdown/arrival consistency of enemy boats across consecutive observations."""
    routes = obs_list[0]['map']['routes']
    for o in obs_list:
        for e in o['enemy_boats']:
            okv = o['visible'][e['position']] or (e['destination'] != -1 and o['visible'][e['destination']])
            if not okv:
                note('enemy_listed_invisible', (key, o['round'], e))
            if e['destination'] != -1:
                L = routes[e['position']][e['destination']]
                if not (L and 1 <= e['eta'] <= L - 1):
                    note('enemy_eta_range', (key, e, L))
            elif e['eta'] != 0:
                note('enemy_eta_docked', (key, e))
            STATS['enemy_seen'] += 1
    for r in range(len(obs_list) - 1):
        o, o2 = obs_list[r], obs_list[r + 1]
        after = {e['boat']: e for e in o2['enemy_boats']}
        for e in o['enemy_boats']:
            e2 = after.get(e['boat'])
            if e['destination'] != -1:
                if e['eta'] > 1:
                    exp = dict(e, eta=e['eta'] - 1)
                    if o2['visible'][e['position']] or o2['visible'][e['destination']]:
                        if e2 != exp:
                            note('enemy_countdown', (key, r, e, e2))
                    elif e2 is not None:
                        note('enemy_listed_when_unseen', (key, r, e, e2))
                else:
                    exp = dict(boat=e['boat'], position=e['destination'], destination=-1, eta=0)
                    if o2['visible'][e['destination']]:
                        if e2 != exp:
                            note('enemy_arrival', (key, r, e, e2))
                    elif e2 is not None and e2['position'] != e['destination']:
                        note('enemy_arrival_elsewhere', (key, r, e, e2))
            else:
                if e2 is None:
                    if o2['visible'][e['position']]:
                        # must have left on a 1-round route to a site we do not see
                        if not any(routes[e['position']][v] == 1 and not o2['visible'][v] for v in range(len(routes))):
                            note('enemy_vanished_impossible', (key, r, e))
                        else:
                            STATS['enemy_vanished_L1'] += 1
                    continue
                if e2['destination'] != -1:
                    if e2['position'] != e['position'] or routes[e['position']][e2['destination']] == 0 \
                            or e2['eta'] != routes[e['position']][e2['destination']] - 1:
                        note('enemy_departure', (key, r, e, e2))
                    else:
                        STATS['enemy_departures_seen'] += 1
                elif e2['position'] != e['position']:
                    if routes[e['position']][e2['position']] != 1:
                        note('enemy_jump', (key, r, e, e2))


def random_policy(rng, la, style):
    if style == 0:
        return rng.choice(la)
    W = dict(deliver=60, craft=40, build_workshop=25, build_boat=6, gather=6, unload=4, load=4, sail=4, wait=1)
    if style == 2:
        W.update(sail=12, gather=12, wait=0.3)
    return rng.choices(la, weights=[W[x['op']] for x in la])[0]


def play_and_check(a, rng, g, sd, game, policy, f=None):
    s = a.reset(g, sd, game)
    obs, acts = [s['observation']], []
    while True:
        act = policy(s['observation'])
        acts.append(act)
        s = a.step(act)
        if s['game_done']:
            break
        obs.append(s['observation'])
    final = {k: v for k, v in s.items() if k != 'observation'}
    check_game(g, sd, game, obs, acts, final)
    enemy_track_check(obs, (g, sd, game))
    if f:
        f.write(json.dumps(dict(group=g, seed=sd, game=game, obs=obs, acts=acts, final=final)) + '\n')
        f.flush()


def live(ngames, seed, out=None):
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
    from arena import Arena
    rng = random.Random(seed)
    f = open(out, 'w') if out else None
    with Arena() as a:
        for i in range(ngames):
            g = rng.randrange(8); sd = rng.randrange(2 ** 32); game = rng.randrange(5)
            style = FORCE_STYLE if FORCE_STYLE is not None else rng.randrange(5)
            if style >= 3:
                import bots
                mem = {}
                eps = 0.03 if style == 3 else 0.15
                pol = lambda o: bots.econ(o, mem, rng, eps)
            else:
                pol = lambda o: random_policy(rng, o['legal_actions'], style)
            play_and_check(a, rng, g, sd, game, pol, f)
            if (i + 1) % 25 == 0:
                print('..%d games, mismatches %s' % (i + 1, dict(MISMATCH)), file=sys.stderr)
    if f:
        f.close()


def offline(files):
    for fn in files:
        for line in (gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            obs = d['obs']
            check_game(d['group'], d['seed'], d['game'], obs, d['acts'], d.get('final'))
            enemy_track_check(obs, (d['group'], d['seed'], d['game']))


def report():
    print('STATS', json.dumps(dict(sorted(STATS.items()))))
    print('MISMATCHES', json.dumps(dict(MISMATCH)))
    for k, v in EXAMPLES.items():
        print('  example', k, json.dumps(v, default=str)[:900])
    kinds = Counter(c['kind'] for c in EVENTS)
    print('EVENTS', dict(kinds))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'live'
    if mode == 'file':
        offline([x for x in sys.argv[2:] if not x.startswith('--')])
    else:
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        sd = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 1
        out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
        if '--style' in sys.argv:
            FORCE_STYLE = int(sys.argv[sys.argv.index('--style') + 1])
        live(n, sd, out)
    report()
    if '--events' in sys.argv:
        json.dump(EVENTS, open(sys.argv[sys.argv.index('--events') + 1], 'w'), default=str)
