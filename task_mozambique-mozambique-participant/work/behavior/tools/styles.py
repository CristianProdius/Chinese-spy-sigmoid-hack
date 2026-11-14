"""Style of a game, per work/binary/PROFESSOR.md (decoded from the engine): perm[game] where perm is a
seed-dependent shuffle of [0..4]. Copied here so the behaviour analysis is self-contained."""
STYLES = {0: (3.5, 0.85, 8), 1: (1.8, 1.15, 0), 2: (1.8, 0.85, 0), 3: (3.5, 0.0, 0), 4: (0.0, 0.85, 8)}  # (B, A, W)
M64 = (1 << 64) - 1
def _next(state):
    state = (state + 0x9e3779b97f4a7c15) & M64
    z = state
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
    return state, z ^ (z >> 31)
def style_permutation(seed):
    perm = [0, 1, 2, 3, 4]; state = seed ^ 0x5354594c45534554
    for i in range(5, 1, -1):
        state, v = _next(state); j = v % i
        perm[i - 1], perm[j] = perm[j], perm[i - 1]
    return perm
def style_of(seed, game): return style_permutation(seed)[game]
