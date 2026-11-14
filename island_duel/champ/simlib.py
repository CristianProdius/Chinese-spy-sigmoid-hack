"""ctypes access to libsim.so (game simulator + champion clone + OM search)."""
import ctypes
import os

_lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libsim.so"))
IA = ctypes.c_int * 225
_lib.game_size.restype = ctypes.c_int
GSIZE = _lib.game_size()
_lib.g_eval.restype = ctypes.c_double
_lib.g_eval.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double]
_lib.g_om.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int,
                      ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
_lib.g_om_nm.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int,
                         ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
_lib.g_rollout.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]
_lib.g_rollout_h.restype = ctypes.c_double
_lib.g_rollout_h.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_int]
_lib.g_negamax.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_int]

# Game layout offsets (ints)
OFF = {"blocked": 0, "w": 225, "c": 450, "owner": 675, "energy": 900, "score": 902, "remaining": 904, "cur": 905,
       "cseat": 906, "cprof": 907, "mo": 908, "mw": 1133, "mc": 1358}


class Game:
    def __init__(self, m=None, cseat=None, cprof=None):
        self.buf = ctypes.create_string_buffer(GSIZE)
        if m is not None:
            _lib.g_init(self.buf, IA(*m["blocked"]), IA(*m["w"]), IA(*m["c"]), cseat, cprof)

    @classmethod
    def from_world(cls, wd, obs):
        """Simulator state from a sampled world and the public part of an observation."""
        g = cls()
        a = g.ints()
        for k in ("blocked", "w", "c", "owner", "mo", "mw", "mc"):
            a[OFF[k]:OFF[k] + 225] = wd[k]
        a[OFF["energy"]:OFF["energy"] + 2] = list(obs["energy"])
        a[OFF["score"]:OFF["score"] + 2] = list(obs["scores"])
        a[OFF["remaining"]] = obs["actions_remaining"]
        a[OFF["cur"]] = obs["seat"]
        a[OFF["cseat"]] = 1 - obs["seat"]
        a[OFF["cprof"]] = obs["opponent_profile"]
        _lib.init_masks()
        return g

    def copy(self):
        g = Game()
        ctypes.memmove(g.buf, self.buf, GSIZE)
        return g

    def ints(self):
        return (ctypes.c_int * (GSIZE // 4)).from_buffer(self.buf)

    def get(self, k, n=1):
        a = self.ints()
        return a[OFF[k]] if n == 1 else list(a[OFF[k]:OFF[k] + n])

    def legal(self):
        out = (ctypes.c_int * 260)()
        n = _lib.g_legal(self.buf, out)
        return list(out[:n])

    def apply(self, a):
        _lib.g_apply(self.buf, -1 if a is None else a)

    def champ(self, budget=2048):
        return _lib.g_champ(self.buf, budget)

    def negamax(self, E, F, budget=2048, depth=4):
        return _lib.g_negamax(self.buf, E, F, budget, depth)

    def om(self, depth, E, F, capw=0.0, budget=2048):
        vals = (ctypes.c_double * 260)()
        mv = (ctypes.c_int * 260)()
        n = ctypes.c_int()
        b = _lib.g_om(self.buf, depth, E, F, capw, budget, vals, mv, ctypes.byref(n))
        return b, list(mv[:n.value]), list(vals[:n.value])

    def om_nm(self, E, F, budget=2048, depth=4):
        vals = (ctypes.c_double * 260)()
        mv = (ctypes.c_int * 260)()
        n = ctypes.c_int()
        b = _lib.g_om_nm(self.buf, E, F, budget, depth, vals, mv, ctypes.byref(n))
        return b, list(mv[:n.value]), list(vals[:n.value])

    def rollout(self, first, E=160, F=9, budget=2048, depth=4):
        return _lib.g_rollout(self.buf, -1 if first is None else first, E, F, budget, depth)

    def rollout_h(self, first, H, E=160, F=9, budget=2048, depth=4):
        return _lib.g_rollout_h(self.buf, -1 if first is None else first, E, F, budget, depth, H)

    def eval(self, p, E, F, capw=0.0):
        return _lib.g_eval(self.buf, p, E, F, capw)


D2 = ctypes.c_double


def search_decide(obs_true, seat, E, F, budget, depth, mem):
    """Champion-style search for `seat` from true arrays (only its visible part is used); mem updated."""
    mo, mw, mc = IA(*mem[0]), IA(*mem[1]), IA(*mem[2])
    a = _lib.search_decide(IA(*obs_true["blocked"]), IA(*obs_true["w"]), IA(*obs_true["c"]), IA(*obs_true["owner"]),
                           (ctypes.c_int * 2)(*obs_true["energy"]), (ctypes.c_int * 2)(*obs_true["score"]),
                           obs_true["remaining"], seat, D2(E), D2(F), budget, depth, mo, mw, mc, None)
    mem[0][:], mem[1][:], mem[2][:] = list(mo), list(mw), list(mc)
    return a


NPRM = 10
DEFAULT_PRM = [160, 160, 9, 0.35, 3, 4, 10, 24, 0, 1.0]


def search_decide_ext(t, seat, prm, budget, depth, mem):
    mo, mw, mc = IA(*mem[0]), IA(*mem[1]), IA(*mem[2])
    a = _lib.search_decide_ext(IA(*t["blocked"]), IA(*t["w"]), IA(*t["c"]), IA(*t["owner"]),
                               (ctypes.c_int * 2)(*t["energy"]), (ctypes.c_int * 2)(*t["score"]), t["remaining"],
                               seat, (ctypes.c_double * NPRM)(*prm), budget, depth, mo, mw, mc)
    mem[0][:], mem[1][:], mem[2][:] = list(mo), list(mw), list(mc)
    return a

NF, NBK = 17, 6
D = ctypes.c_double


def search_decide_fit(t, seat, theta, ha, hb, budget, depth, mem):
    mo, mw, mc = IA(*mem[0]), IA(*mem[1]), IA(*mem[2])
    a = _lib.search_decide_fit(IA(*t["blocked"]), IA(*t["w"]), IA(*t["c"]), IA(*t["owner"]),
                               (ctypes.c_int * 2)(*t["energy"]), (ctypes.c_int * 2)(*t["score"]), t["remaining"],
                               seat, (D * (NF * NBK))(*theta), D(ha), D(hb), budget, depth, mo, mw, mc)
    mem[0][:], mem[1][:], mem[2][:] = list(mo), list(mw), list(mc)
    return a


def root_features(t, seat, ha, hb, mem, move):
    fr, fc = (D * NF)(), (D * NF)()
    b = _lib.root_features(IA(*t["blocked"]), IA(*t["w"]), IA(*t["c"]), IA(*t["owner"]),
                           (ctypes.c_int * 2)(*t["energy"]), (ctypes.c_int * 2)(*t["score"]), t["remaining"], seat,
                           D(ha), D(hb), IA(*mem[0]), IA(*mem[1]), IA(*mem[2]), move, fr, fc)
    return b, list(fr), list(fc)


_lib.set_opponent_model.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double]
E_PROF, F_PROF = (160.0, 240.0, 100.0), (9.0, 6.0, 14.0)


def set_opponent_model(k, profile):
    _lib.set_opponent_model(k, E_PROF[profile], F_PROF[profile])


_lib.set_qdepth.argtypes = [ctypes.c_int]


def set_qdepth(q):
    _lib.set_qdepth(q)
