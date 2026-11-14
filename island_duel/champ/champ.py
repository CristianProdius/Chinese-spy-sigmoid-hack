"""ctypes wrapper for the champion clone (libchamp.so)."""
import ctypes
import os

_lib = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libchamp.so"))
IA = ctypes.c_int * 225
I2 = ctypes.c_int * 2
I4 = ctypes.c_int * 4
_lib.champ_decide.restype = ctypes.c_int


def new_memory(seat):
    """Initial champion memory: unknown tiles -3 with prior w=5, c=3; starts known."""
    own = [-3] * 225
    w = [5] * 225
    c = [3] * 225
    own[0], own[224] = 0, 1
    w[0] = w[224] = c[0] = c[224] = 0
    return own, w, c


def decide(blocked, w, c, owner, energy, score, remaining, seat, profile, mem):
    """Return (action, info); mem = (owner, w, c) lists, updated in place."""
    mo, mw, mc = IA(*mem[0]), IA(*mem[1]), IA(*mem[2])
    info = I4()
    a = _lib.champ_decide(IA(*blocked), IA(*w), IA(*c), IA(*owner), I2(*energy), I2(*score),
                          remaining, seat, profile, mo, mw, mc, info)
    mem[0][:], mem[1][:], mem[2][:] = list(mo), list(mw), list(mc)
    return a, list(info)
