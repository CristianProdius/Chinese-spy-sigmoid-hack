"""Unit tests of sim.py against facts probed on the engine (see RULES.md). python3 test_sim.py"""
import sim
from sim import (State, step, legal_actions, observation, WAIT, SAIL, GATHER, LOAD, UNLOAD,
                 BUILD_WORKSHOP, CRAFT, DELIVER, BUILD_BOAT, ACT_WAIT)

# map of group 0 seed 767302775 (ring), homes [1, 5]
MAP = {"contracts": [{"deadline": 24, "destination": 6, "good": 0, "points": 5, "quantity": 2}, {"deadline": 40, "destination": 9, "good": 1, "points": 5, "quantity": 2}, {"deadline": 56, "destination": 7, "good": 0, "points": 5, "quantity": 2}, {"deadline": 72, "destination": 0, "good": 1, "points": 5, "quantity": 2}, {"deadline": 40, "destination": 8, "good": 2, "points": 12, "quantity": 1}, {"deadline": 56, "destination": 9, "good": 2, "points": 12, "quantity": 1}, {"deadline": 72, "destination": 2, "good": 2, "points": 12, "quantity": 1}, {"deadline": 80, "destination": 2, "good": 2, "points": 12, "quantity": 1}], "homes": [1, 5], "roles": [0, -1, 1, 1, 2, -1, 1, 2, 0, 0], "routes": [[0, 2, 0, 0, 0, 0, 0, 0, 0, 1], [2, 0, 3, 0, 0, 0, 0, 0, 0, 0], [0, 3, 0, 2, 0, 0, 0, 0, 0, 0], [0, 0, 2, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 3, 0, 0, 0, 0], [0, 0, 0, 0, 3, 0, 2, 0, 0, 0], [0, 0, 0, 0, 0, 2, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 2], [1, 0, 0, 0, 0, 0, 0, 0, 2, 0]], "topology": 0}


def new():
    return State.from_map(MAP)


def test_initial_legal_order():
    st = new()
    la = [sim.to_dict(a) for a in legal_actions(st, 0)]
    assert la[0] == {'op': 'wait'}
    assert la[1:3] == [{'op': 'sail', 'boat': 0, 'destination': 0}, {'op': 'sail', 'boat': 0, 'destination': 2}]
    assert la[3] == {'op': 'load', 'boat': 0, 'good': 0, 'quantity': 1}
    assert la[-1] == {'op': 'build_boat'}
    assert len(la) == 18


def test_sail_timing():
    st = new()
    step(st, (SAIL, 0, 2, 0), ACT_WAIT)           # length 3
    assert st.boats[0][0][:3] == [1, 2, 2]
    step(st, ACT_WAIT, ACT_WAIT)
    assert st.boats[0][0][:3] == [1, 2, 1]
    step(st, ACT_WAIT, ACT_WAIT)
    assert st.boats[0][0][:3] == [2, -1, 0]       # obs r+L shows it docked
    st = new()
    st.boats[0][0][0] = 0
    step(st, (SAIL, 0, 9, 0), ACT_WAIT)           # length 1 arrives the same round
    assert st.boats[0][0][:3] == [9, -1, 0]


def test_regen_and_cap():
    st = new()
    for r in range(3):
        step(st, ACT_WAIT, ACT_WAIT)
    assert st.stocks[0] == 4 and st.round == 3
    step(st, ACT_WAIT, ACT_WAIT)
    assert st.stocks[0] == 5 and st.round == 4
    for r in range(20):
        step(st, ACT_WAIT, ACT_WAIT)
    assert st.stocks[0] == 6


def test_craft_timing_and_workshop():
    st = new()
    st.boats[0][0][0] = 4
    st.wh[0][4] = [4, 2, 0]
    la = legal_actions(st, 0)
    assert (BUILD_WORKSHOP, 0, 0, 0) in la and (CRAFT, 0, 0, 0) not in la
    step(st, (BUILD_WORKSHOP, 0, 0, 0), ACT_WAIT)
    assert st.ws[0][4] and st.wh[0][4] == [2, 1, 0]
    assert (CRAFT, 0, 0, 0) in legal_actions(st, 0)
    step(st, (CRAFT, 0, 0, 0), ACT_WAIT)
    assert st.jobs[0][4] == 2
    step(st, ACT_WAIT, ACT_WAIT)
    assert st.jobs[0][4] == 1
    step(st, ACT_WAIT, ACT_WAIT)
    assert st.jobs[0][4] == 0 and st.wh[0][4] == [0, 0, 1]
    assert observation(st, 0)['visible'][4]       # own workshop gives visibility


def test_deadline():
    st = new()
    st.boats[0][0][0] = 6
    st.boats[0][0][3] = 2
    st.round = 23
    assert (DELIVER, 0, 0, 0) in legal_actions(st, 0)
    st.round = 24
    assert (DELIVER, 0, 0, 0) not in legal_actions(st, 0)


def test_gather_race():
    for rnd, winner in ((10, 0), (9, 1)):   # (round 11 would regenerate at 12)
        st = new()
        st.round = rnd
        st.boats[0][0][0] = 0
        st.boats[1][0][0] = 0
        ok0, ok1 = step(st, (GATHER, 0, 0, 3), (GATHER, 0, 0, 2))
        # stock 4: winner gets its amount, loser needs 2 (or 3) but only 1 (or 2) left -> fails entirely
        if winner == 0:
            assert ok0 and not ok1 and st.boats[0][0][3] == 3 and st.boats[1][0][3] == 0 and st.stocks[0] == 1
        else:
            assert ok1 and ok0 is False and st.boats[1][0][3] == 2 and st.boats[0][0][3] == 0 and st.stocks[0] == 2
    st = new()
    st.boats[0][0][0] = 0
    st.boats[1][0][0] = 0
    st.round = 10
    ok0, ok1 = step(st, (GATHER, 0, 0, 2), (GATHER, 0, 0, 2))
    assert ok0 and ok1 and st.stocks[0] == 0


def test_deliver_race():
    for rnd in (10, 11):
        st = new()
        st.round = rnd
        for s in (0, 1):
            st.boats[s][0][0] = 6
            st.boats[s][0][3] = 2
        ok0, ok1 = step(st, (DELIVER, 0, 0, 0), (DELIVER, 0, 0, 0))
        w = rnd % 2
        assert st.claims[0] == w and (ok0, ok1)[w] and not (ok0, ok1)[1 - w]
        assert st.boats[1 - w][0][3] == 2 and st.boats[w][0][3] == 0
        assert st.score[w] == 5 and st.score[1 - w] == 0


def test_route_race():
    # same direction, opposite direction, and non-conflicts
    for rnd in (12, 13):
        w = rnd % 2
        st = new()
        st.round = rnd
        st.boats[0][0][0] = 4
        st.boats[1][0][0] = 4
        ok0, ok1 = step(st, (SAIL, 0, 5, 0), (SAIL, 0, 5, 0))
        assert (ok0, ok1)[w] and not (ok0, ok1)[1 - w]
        st = new()
        st.round = rnd
        st.boats[0][0][0] = 3
        st.boats[1][0][0] = 2
        ok0, ok1 = step(st, (SAIL, 0, 2, 0), (SAIL, 0, 3, 0))
        assert (ok0, ok1)[w] and not (ok0, ok1)[1 - w]
    st = new()
    st.round = 12
    st.boats[0][0][0] = 4
    st.boats[1][0][0] = 4
    assert step(st, (SAIL, 0, 3, 0), (SAIL, 0, 5, 0)) == (True, True)     # same origin, other routes
    st = new()
    st.round = 12
    st.boats[0][0][0] = 2
    st.boats[1][0][0] = 4
    assert step(st, (SAIL, 0, 3, 0), (SAIL, 0, 3, 0)) == (True, True)     # same destination


def test_build_boat_limit():
    st = new()
    step(st, (BUILD_BOAT, -1, 0, 0), ACT_WAIT)
    assert len(st.boats[0]) == 3 and st.wh[0][1] == [1, 1, 0]
    st.wh[0][1] = [9, 9, 0]
    assert (BUILD_BOAT, -1, 0, 0) not in legal_actions(st, 0)


if __name__ == '__main__':
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            fn()
            n += 1
    print('ok', n, 'tests')
