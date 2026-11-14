#!/usr/bin/env python3
"""SIM2: held-out splice benchmark for "The Azmari's Borrowed Melody".

Follows the reverse-engineered generator recipe (wf1/out/forensic_musical.md section 9, plus the chain
facts in forensic_spectral.md):

  host  : random walk on a scale -> deterministic per-(pitch, duration) additive note renderer (fixed
          harmonic/body profile per pitch, ET + fixed per-pitch cents, onset-locked 4-5 Hz vibrato with AM,
          legato 110/70 ms envelopes, bow re-articulation of long notes every beat) -> reverb (RT60 ~2.5-3 s,
          wet ~-15 dB) -> mild square-law term without DC block (DC ~+2 LSB that tracks power) -> level.
  splice: separate continuous render (other walk, transposed T semitones, own timbre and articulation)
          -> optional own reverb -> peak-normalise -> asymmetric tanh saturation -> ~20 Hz high-pass ->
          mean removal -> RMS-matched to the replaced host segment.
  splice: excerpt starts on a source note onset, lasts n eighths; replaces host[t0 : t0 + L + delta]
          (delta in {-e/2, 0, +e/2}, so the host grid can shift); equal-power crossfades of 20-60 ms per seam.
  post  : (reverb mode 'same': the host room is applied to the spliced dry signal instead), then
          stationary noise (-74 dBFS, flat to 3 kHz, -8.5 dB/oct above), int16 by truncation toward zero.

Usage:
  gen2.py [--out DIR] [--groups near,weak,hard] [--files near_01,...]   -> DIR/*.wav + DIR/labels.csv
  gen2.py --trainlike --out DIR                                          -> 3 train-like calibration files
Deterministic: the same arguments give bit-identical files.
"""
import argparse
import csv
import json
import os

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 22050
BASE_SEED = 20261114
FS_LSB = 32768.0

# Median harmonic profiles (h1..h16, dB re h1) of the real host notes (forensic_musical/harmonic_tables_dB.json).
TRAIN_TABLE = {
    60: [0.0, -6.7, -17.7, -11.4, -21.6, -15.5, -24.0, -29.1, -34.7, -39.8, -36.4, -49.2, -46.4, -49.6, -53.7, -53.9],
    62: [0.0, -2.9, -16.4, -11.0, -19.1, -15.4, -20.2, -22.8, -32.1, -39.0, -34.8, -43.5, -42.5, -48.5, -49.0, -50.2],
    64: [0.0, 1.2, -6.2, -3.9, -8.7, -17.3, -28.5, -39.2, -27.6, -31.1, -39.2, -33.3, -48.8, -47.0, -53.2, -53.4],
    65: [0.0, 0.4, -7.1, -5.3, -8.1, -18.9, -30.0, -40.2, -28.1, -31.8, -41.1, -34.6, -48.7, -48.5, -53.8, -53.6],
    67: [0.0, -4.3, -9.4, -10.6, -17.4, -35.8, -35.1, -32.4, -43.0, -41.0, -51.2, -56.0, -51.4, -54.4, -69.0, -60.8],
    69: [0.0, -5.2, -11.1, -34.9, -22.8, -30.5, -35.9, -49.7, -49.7, -54.8, -55.8, -63.9, -71.2, -62.8, -63.9, -72.0],
}

# Scale shapes (semitones above the tonic). 'hexa' is the train host (C D E F G A); the others are qenet-like.
SCALES = {
    'hexa': [0, 2, 4, 5, 7, 9],
    'tizita': [0, 2, 4, 7, 9],
    'tizita_minor': [0, 2, 3, 7, 8],
    'bati': [0, 4, 5, 7, 11],
    'bati_minor': [0, 3, 5, 7, 10],
    'ambassel': [0, 1, 5, 7, 8],
    'anchihoye': [0, 1, 5, 6, 9],
}
DUR_P = {1: .07, 2: .50, 3: .09, 4: .22, 6: .07, 9: .025, 10: .025}  # eighths


def scale_pitches(tonic, shape, n=6):
    sh = SCALES[shape]
    return [tonic + 12 * (k // len(sh)) + sh[k % len(sh)] for k in range(n)]


# ----------------------------------------------------------------------------------------------- melody
def walk(rng, pitches, total_eighths):
    """Train-style random walk: +-1 degree 65 %, +-2 degrees 35 %, drift toward the two lowest degrees,
    long notes mostly on them. Returns [(start_eighth, midi, dur_eighths)]."""
    durs = np.array(list(DUR_P.keys()))
    dp = np.array(list(DUR_P.values()))
    dp /= dp.sum()
    n = len(pitches)
    idx = int(rng.integers(0, n))
    out, t = [], 0
    while t < total_eighths:
        d = int(rng.choice(durs, p=dp))
        while d >= 6 and idx > 1 and rng.random() < 0.8:
            d = int(rng.choice(durs, p=dp))
        out.append((t, pitches[idx], d))
        t += d
        size = 1 if rng.random() < 0.65 else 2
        p_down = float(np.clip(0.5 + 0.1 * (idx - 1.5), 0.2, 0.8))
        sgn = -1 if rng.random() < p_down else 1
        nxt = idx + sgn * size
        if nxt < 0 or nxt >= n:
            nxt = idx - sgn * size
        idx = int(np.clip(nxt, 0, n - 1))
    return out


# ----------------------------------------------------------------------------------------------- voices
def host_voice(rng, table=False):
    """Masenqo-like legato voice: rich, even-heavy, fixed body EQ, regular vibrato, deterministic."""
    return dict(
        kind='host', det=True, seed=int(rng.integers(1 << 30)), table=bool(table),
        tilt=float(rng.uniform(-4.4, -3.4)), even=float(rng.uniform(4, 8)), h1=float(rng.uniform(4, 8)),
        formants=[(float(np.exp(rng.uniform(np.log(400), np.log(4500)))), float(rng.uniform(-12, 8)),
                   float(rng.uniform(0.15, 0.5))) for _ in range(int(rng.integers(3, 6)))],
        scatter=1.5, ph_mu=0.6, ph_sd=0.8,
        attack=float(rng.uniform(0.09, 0.13)), release=float(rng.uniform(0.06, 0.08)),
        ovl=float(rng.uniform(0.0, 0.02)),
        vib_regular=True, vib_depth=float(rng.uniform(7, 11)), vib_rate=float(rng.uniform(4.0, 5.0)),
        vib_delay=0.25, am_db=float(rng.uniform(3, 5)), scoop=float(-rng.uniform(6, 12)),
        reartic=True, reartic_db=float(rng.uniform(7, 9)),
        tune=[float(v) for v in rng.uniform(3, 8, 12)], tune_jit=0.0,
        pgain=[float(v) for v in rng.uniform(-2, 2, 12)],
    )


def splice_voice(rng):
    """Washint-like detached voice: steep odd-heavy spectrum, short attacks, weak irregular vibrato,
    unstable tuning, not deterministic per note."""
    return dict(
        kind='splice', det=False, seed=int(rng.integers(1 << 30)), table=False,
        tilt=float(rng.uniform(-7.0, -6.0)), even=float(rng.uniform(-16, -10)), h1=float(rng.uniform(-9, -4)),
        formants=[(float(np.exp(rng.uniform(np.log(500), np.log(3000)))), float(rng.uniform(-8, 8)),
                   float(rng.uniform(0.2, 0.5))) for _ in range(int(rng.integers(2, 4)))],
        scatter=2.0, ph_mu=0.0, ph_sd=10.0,
        attack=float(rng.uniform(0.035, 0.055)), release=float(rng.uniform(0.04, 0.055)),
        ovl=float(-rng.uniform(0.0, 0.04)),
        vib_regular=False, vib_depth=float(rng.uniform(2, 5)), vib_rate=0.0, vib_delay=0.0, am_db=0.0,
        scoop=0.0, reartic=False, reartic_db=0.0,
        tune=[float(v) for v in rng.uniform(3, 15, 12)], tune_jit=3.0,
        pgain=[float(v) for v in rng.uniform(-2, 2, 12)],
    )


def harm_db(v, midi, f0, H):
    h = np.arange(1, H + 1)
    if v['table'] and midi in TRAIN_TABLE:
        tab = np.array(TRAIN_TABLE[midi])
        db = np.empty(H)
        m = min(H, 16)
        db[:m] = tab[:m]
        if H > 16:
            db[16:] = tab[-1] + v['tilt'] * (h[16:] - 16)
    else:
        db = v['tilt'] * (h - 1) + np.where(h % 2 == 0, v['even'], 0.0) + np.where(h == 1, v['h1'], 0.0)
        fh = h * f0
        for fc, g, bw in v['formants']:
            db = db + g * np.exp(-0.5 * (np.log2(fh / fc) / bw) ** 2)
        db = db + np.random.default_rng([v['seed'], midi, 7]).normal(0, v['scatter'], H)
        db = db - db[0]
    fh = h * f0
    db = db - np.where(fh > 9000, 12 * np.log2(np.maximum(fh, 1) / 9000), 0.0)  # ~10 kHz roll-off like train
    return db


def envelope(t, dur, v, eighth):
    A, R = v['attack'], v['release']
    end = dur + v['ovl']
    env = np.ones_like(t)
    m = t < A
    env[m] = np.sin(0.5 * np.pi * t[m] / A) ** 2
    rs = end - R
    m = t > rs
    env[m] *= np.cos(0.5 * np.pi * np.clip((t[m] - rs) / R, 0, 1)) ** 2
    env[t >= end] = 0.0
    if v['reartic']:  # bow change on every beat (2 eighths) of long notes
        beat = 2 * eighth
        for tk in np.arange(beat, dur - 0.15, beat):
            env *= 1 - (1 - 10 ** (-v['reartic_db'] / 20)) * np.exp(-0.5 * ((t - tk) / 0.035) ** 2)
    return env


def note_wave(v, midi, dur_e, eighth, seed):
    rng = np.random.default_rng(seed)
    dur = dur_e * eighth
    n = int((dur + max(v['ovl'], 0) + 0.01) * SR)
    t = np.arange(n) / SR
    cents = v['tune'][midi % 12] + (rng.normal(0, v['tune_jit']) if v['tune_jit'] else 0.0)
    f0 = 440.0 * 2 ** ((midi - 69) / 12 + cents / 1200)
    if v['vib_regular']:
        frac = np.clip((t - v['vib_delay']) / 0.3, 0, 1)
        ph = 2 * np.pi * v['vib_rate'] * t
        pc = v['vib_depth'] * frac * np.sin(ph)
        am_db = 0.5 * v['am_db'] * frac * np.sin(ph)
    else:  # weak irregular wobble: smoothed noise with std vib_depth cents
        k = np.arange(0, n + 512, 512)
        w = rng.standard_normal(len(k))
        w = np.convolve(w, np.ones(3) / 3, mode='same')
        w = w / (w.std() + 1e-9) * v['vib_depth']
        pc = np.interp(np.arange(n), k, w)
        am_db = np.zeros(n)
    pc = pc + v['scoop'] * np.exp(-t / 0.06)
    phi = 2 * np.pi * np.cumsum(f0 * 2 ** (pc / 1200)) / SR
    H = int(min(40, np.floor(0.47 * SR / f0)))
    amp = 10 ** (harm_db(v, midi, f0, H) / 20)
    amp /= np.sqrt(np.sum(amp ** 2))
    phases = v['ph_mu'] + np.random.default_rng([v['seed'], 99]).normal(0, v['ph_sd'], 40)
    x = np.zeros(n)
    for h in range(1, H + 1):
        x += amp[h - 1] * np.sin(h * phi + phases[h - 1])
    x *= envelope(t, dur, v, eighth) * 10 ** (am_db / 20) * 10 ** (v['pgain'][midi % 12] / 20)
    return x


def render(v, notes, eighth, t_off, n_total):
    y = np.zeros(n_total + 4 * SR)
    cache = {}
    for j, (te, midi, de) in enumerate(notes):
        if v['det']:
            key = (midi, de)
            if key not in cache:
                cache[key] = note_wave(v, midi, de, eighth, [v['seed'], midi, de])
            w = cache[key]
        else:
            w = note_wave(v, midi, de, eighth, [v['seed'], j, 1])
        i0 = int(round((t_off + te * eighth) * SR))
        if i0 < 0:
            w, i0 = w[-i0:], 0
        if i0 >= len(y):
            break
        m = min(len(w), len(y) - i0)
        y[i0:i0 + m] += w[:m]
    return y[:n_total]


# ----------------------------------------------------------------------------------------------- chain
def make_ir(seed, rt60, wet_db):
    """Exponential-decay noise reverb: direct delta + diffuse tail (highs decay faster), tail energy = wet_db."""
    rng = np.random.default_rng(seed)
    n = int(1.3 * rt60 * SR)
    t = np.arange(n) / SR
    lo = signal.sosfilt(signal.butter(2, 3000, 'lowpass', fs=SR, output='sos'), rng.standard_normal(n))
    hi = signal.sosfilt(signal.butter(2, 3000, 'highpass', fs=SR, output='sos'), rng.standard_normal(n))
    tail = lo * 10 ** (-3 * t / rt60) + 0.5 * hi * 10 ** (-3 * t / (0.6 * rt60))
    tail *= 1 - np.exp(-t / 0.012)
    pre = int(0.008 * SR)
    tail[:pre] = 0
    tail *= np.sqrt(10 ** (wet_db / 10) / np.sum(tail ** 2))
    tail[0] = 1.0
    return tail


def reverb(x, ir):
    return signal.fftconvolve(x, ir)[:len(x)]


def saturate(x, drive, bias, pol):
    """Asymmetric tanh on the peak-normalised signal. pol=+1 flattens the negative half (positive skew)."""
    if drive <= 0:
        return x.copy()
    u = x / (np.max(np.abs(x)) + 1e-12)
    return pol * (np.tanh(drive * (pol * u - bias)) + np.tanh(drive * bias))


# Noise floor shape fitted to the real file's p10 STFT floor (dB re the 0.3-1.5 kHz plateau).
NOISE_F = [0, 20, 50, 70, 130, 180, 300, 1500, 2500, 3500, 5000, 7000, 9000, 10500, 11025]
NOISE_DB = [-6, -4, -2, -8, -10, -3, 0, 0, -3.5, -9.5, -16.3, -20, -24, -30.6, -33]


def shaped_noise(rng, n, rms_ref):
    """Stationary noise. rms_ref is the RMS the noise would have with the recipe's shape (flat to 3 kHz,
    -8.5 dB/oct above); the fitted shape keeps the same plateau level."""
    w = rng.standard_normal(n)
    W = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    g_old = np.ones_like(f)
    m = f > 3000
    g_old[m] = 10 ** (-8.5 / 20 * np.log2(f[m] / 3000))
    g = 10 ** (np.interp(f, NOISE_F, NOISE_DB) / 20)
    y = np.fft.irfft(W * g, n)
    return y * rms_ref / np.sqrt(np.mean(g_old ** 2))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-20))


def synth(p):
    """Build one file from a parameter dict. Returns (int16 array, start_s, end_s)."""
    rng = np.random.default_rng(p['seed'])
    eighth = p['eighth']
    n_file = int(round(p['file_len'] * SR))
    n_host = n_file + int(14 * SR)

    # ---- host
    hv = p['host_voice']
    hp_ = scale_pitches(p['host_tonic'], p['host_scale'])
    hnotes = walk(np.random.default_rng([p['seed'], 1]), hp_, int(n_host / SR / eighth) + 4)
    host_dry = render(hv, hnotes, eighth, p['grid_off'], n_host)
    host_ir = make_ir([p['seed'], 2], p['host_rt60'], p['host_wet_db'])
    target = 10 ** (p['level_db'] / 20)
    host_wet = reverb(host_dry, host_ir)
    g = target / rms(host_wet)
    host_wet *= g
    host_dry *= g
    a2 = p['dc_lsb'] / FS_LSB / np.mean(host_wet ** 2)  # square-law term, no DC block: DC tracks power
    host = (host_dry + a2 * host_dry ** 2) if p['rev_mode'] == 'same' else (host_wet + a2 * host_wet ** 2)

    # ---- splice source (continuous render with notes before and after the excerpt)
    sv = hv if p['src_voice'] == 'host' else p['src_voice']
    sp_ = scale_pitches(p['host_tonic'] + p['transpose'], p['src_scale'])
    L_e = p['len_eighths']
    pre_e = int(np.ceil(4.0 / eighth))
    snotes = walk(np.random.default_rng([p['seed'], 3]), sp_, pre_e + L_e + int(4 / eighth) + 12)
    n_src = int((snotes[-1][0] + snotes[-1][2]) * eighth * SR) + 2 * SR
    src = render(sv, snotes, eighth, 0.0, n_src)
    if p['rev_mode'] == 'own':
        src = reverb(src, make_ir([p['seed'], 4], p['src_rt60'], p['src_wet_db']))
    src = saturate(src, p['sat_drive'], p['sat_bias'], p['sat_pol'])
    if p['hp_hz'] > 0:
        src = signal.sosfilt(signal.butter(2, p['hp_hz'], 'highpass', fs=SR, output='sos'), src)
    onsets = [te for te, _, _ in snotes if te >= pre_e]
    k0 = int(round(onsets[0] * eighth * SR))
    L = int(round(L_e * eighth * SR))
    # mean removal: whole render after a high-pass; without one, the excerpt's own mean (else the saturation's
    # envelope-following DC would leave a 15-20 LSB offset in the splice)
    src -= src.mean() if p['hp_hz'] > 0 else src[k0:k0 + L].mean()

    # ---- splice
    t0 = int(round(p['t0'] * SR))
    t1 = t0 + L
    dn = int(round(p['delta_eighths'] * eighth * SR))
    xs = int(round(p['xf_start'] * SR))
    xe = int(round(p['xf_end'] * SR))
    seg = host[t0:t0 + L + dn]
    exc = src[k0:k0 + L]
    gs = (rms(seg) / rms(exc)) if p['rms_match'] == 'segment' else (target / rms(exc))
    src = src * gs

    i = np.arange(n_file)
    a0, a1 = t0 - xs // 2, t0 + (xs - xs // 2)
    b0, b1 = t1 - xe // 2, t1 + (xe - xe // 2)
    hostB = host[np.clip(i + dn, 0, len(host) - 1)]  # host after the end seam (grid may shift)
    out = np.where(i < b0, host[:n_file], hostB)
    w = np.zeros(n_file)  # splice weight: equal-power ramps centred on each seam
    w[a1:b0] = 1.0
    w[a0:a1] = np.sin(0.5 * np.pi * (np.arange(a1 - a0) + 0.5) / (a1 - a0))
    w[b0:b1] = np.cos(0.5 * np.pi * (np.arange(b1 - b0) + 0.5) / (b1 - b0))
    hw = np.sqrt(np.clip(1 - w ** 2, 0, 1))
    s = np.zeros(n_file)
    s[a0:b1] = src[k0 - (t0 - a0):k0 - (t0 - a0) + (b1 - a0)]
    out = hw * out + w * s

    if p['rev_mode'] == 'same':
        out = reverb(out, host_ir)

    # ---- post: stationary noise after the splice, truncating int16 quantiser
    out = out + shaped_noise(np.random.default_rng([p['seed'], 5]), n_file, 10 ** (p['noise_db'] / 20))
    q = np.trunc(np.clip(out * FS_LSB, -32768, 32767)).astype(np.int16)
    return q, t0 / SR, t1 / SR


# ----------------------------------------------------------------------------------------------- params
def U(rng, a, b):
    return float(rng.uniform(a, b))


def base_params(rng, seed, near_host):
    p = dict(seed=seed)
    p['file_len'] = round(U(rng, 40, 70), 3)
    if near_host:
        p['eighth'] = 0.3
        if rng.random() < 0.5:
            p['host_tonic'], p['host_scale'], table = 60, 'hexa', True
        else:
            p['host_tonic'] = 60 + int(rng.integers(-3, 4))
            p['host_scale'] = str(rng.choice(['hexa', 'tizita', 'bati_minor', 'tizita_minor']))
            table = False
    else:
        p['eighth'] = round(U(rng, 0.26, 0.34), 4)
        p['host_tonic'] = int(rng.integers(55, 67))
        p['host_scale'] = str(rng.choice(list(SCALES)))
        table = False
    p['host_voice'] = host_voice(rng, table)
    p['grid_off'] = U(rng, 0, p['eighth'])
    p['host_rt60'] = U(rng, 2.4, 3.1)
    p['host_wet_db'] = U(rng, -17, -13)
    p['dc_lsb'] = U(rng, 1.4, 2.8)
    p['level_db'] = U(rng, -39, -36)
    p['noise_db'] = U(rng, -76, -72)
    # train-like splice chain (weakened per group below)
    p['transpose'] = int(rng.choice([5, 6, 7, 7, 7, 8, 9]))
    p['src_scale'] = p['host_scale'] if rng.random() < 0.75 else str(rng.choice(list(SCALES)))
    p['src_voice'] = splice_voice(rng)
    p['rev_mode'] = 'own' if rng.random() < 0.75 else 'dry'
    p['src_rt60'] = U(rng, 2.4, 3.1)
    p['src_wet_db'] = U(rng, -13, -8)
    p['sat_drive'] = U(rng, 1.6, 2.6)
    p['sat_bias'] = U(rng, 0.2, 0.35)
    p['sat_pol'] = 1 if rng.random() < 0.75 else -1
    p['hp_hz'] = U(rng, 15, 25)
    p['rms_match'] = 'segment'
    p['xf_start'] = U(rng, 0.02, 0.06)
    p['xf_end'] = U(rng, 0.02, 0.06)
    p['delta_eighths'] = float(rng.choice([-0.5, 0.0, 0.5]))
    return p


def place(rng, p, lo, hi):
    """Splice length in whole eighths within [lo, hi] s, start >= 3 s from both file ends."""
    e = p['eighth']
    n_lo, n_hi = int(np.ceil(lo / e)), int(np.floor(hi / e))
    p['len_eighths'] = int(rng.integers(n_lo, n_hi + 1))
    L = p['len_eighths'] * e
    p['t0'] = round(U(rng, 3.0, p['file_len'] - 3.0 - L - 0.05), 4)


GROUPS = ['near', 'weak', 'hard']
WEAK_CUES = ['register', 'timbre', 'saturation', 'reverb']


def make_params(group, i):
    seed = BASE_SEED + 1000 * GROUPS.index(group) + i
    rng = np.random.default_rng(seed)
    p = base_params(rng, seed, near_host=(group == 'near'))
    p['group'] = group
    if group == 'near':
        place(rng, p, 4.0, 8.0)
        p['cue'] = 'all'
    elif group == 'weak':
        place(rng, p, 2.0, 10.0)
        cue = WEAK_CUES[i % 4]
        p['cue'] = cue
        j = i // 4
        if cue == 'register':
            p['transpose'] = [0, -5, 0, 3][j]
            p['src_scale'] = p['host_scale']
        elif cue == 'timbre':
            p['src_voice'] = 'host'
        elif cue == 'saturation':
            if j < 2:
                p['sat_drive'] = 0.0
            else:
                p['sat_drive'], p['sat_bias'] = U(rng, 0.8, 1.5), U(rng, 0.1, 0.2)
        elif cue == 'reverb':
            p['rev_mode'] = 'same'
    else:  # hard: same register, scale and renderer; only the processing chain differs
        place(rng, p, 2.0, 10.0)
        p['transpose'] = 0
        p['src_scale'] = p['host_scale']
        p['src_voice'] = 'host'
        sat = ['none', 'mild', 'medium', 'strong'][i % 4]
        p['rev_mode'] = ['own', 'dry', 'same', 'own'][(i // 4) % 4]
        if sat == 'none' and p['rev_mode'] == 'same':
            p['rev_mode'] = 'own'
        p['sat_drive'], p['sat_bias'] = {'none': (0.0, 0.0), 'mild': (U(rng, 0.8, 1.5), U(rng, 0.1, 0.2)),
                                         'medium': (U(rng, 1.8, 2.6), U(rng, 0.2, 0.35)),
                                         'strong': (U(rng, 3.0, 4.0), U(rng, 0.3, 0.5))}[sat]
        p['src_rt60'] = U(rng, 1.2, 3.5)
        p['hp_hz'] = U(rng, 15, 25) if rng.random() < 0.6 else 0.0
        p['cue'] = f'chain:sat={sat},rev={p["rev_mode"]},hp={"y" if p["hp_hz"] > 0 else "n"}'
    return p


def trainlike_params(k):
    """Train-like calibration setting: train host (C4-A4 hexatonic, train harmonic tables), +7 splice of
    exactly 20 eighths starting near 14.96 +- 2 s, own reverb then saturation (drive 2, bias 0.25), 20 Hz HP,
    file 55.845 s. Calibrated with calib.py / check2.py against the real file (REPORT.md)."""
    seed = BASE_SEED + 9000 + k
    rng = np.random.default_rng(seed)
    p = base_params(rng, seed, near_host=True)
    p.update(group='trainlike', cue='all', file_len=55.845, eighth=0.3, host_tonic=60, host_scale='hexa',
             transpose=7, src_scale='hexa', rev_mode='own', src_rt60=2.75, src_wet_db=-10.0, sat_drive=2.0,
             sat_bias=0.25, sat_pol=1, hp_hz=20.0,
             host_rt60=2.75, host_wet_db=-15.0, dc_lsb=2.0, level_db=-37.5, noise_db=-74.0, xf_start=0.025,
             xf_end=0.06, delta_eighths=0.5, len_eighths=20, t0=round(14.96 + U(rng, -2, 2), 4))
    p['host_voice']['table'] = True
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
    ap.add_argument('--groups', default=','.join(GROUPS))
    ap.add_argument('--files', default='')
    ap.add_argument('--n', type=int, default=16, help='files per group')
    ap.add_argument('--trainlike', action='store_true')
    ap.add_argument('--set', default='', help='research only: JSON dict of overrides applied to every file')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    over = json.loads(a.set) if a.set else {}
    if a.trainlike:
        jobs = [(f'tl_{k + 1}', trainlike_params(k)) for k in range(3)]
    else:
        files = set(s for s in a.files.split(',') if s)
        jobs = [(f'{g}_{i + 1:02d}', None) for g in a.groups.split(',') for i in range(a.n)]
        jobs = [(nm, make_params(nm.split('_')[0], int(nm.split('_')[1]) - 1)) for nm, _ in jobs
                if not files or nm in files]
    rows = []
    for nm, p in jobs:
        p.update(over)
        q, s, e = synth(p)
        wavfile.write(os.path.join(a.out, nm + '.wav'), SR, q)
        rows.append(dict(file=nm + '.wav', group=p['group'], start_s=f'{s:.3f}', end_s=f'{e:.3f}',
                         params=json.dumps(p, separators=(',', ':'))))
        print(f"{nm}: {len(q) / SR:5.1f}s splice {s:6.3f}-{e:6.3f} ({e - s:4.2f}s) cue={p['cue']} "
              f"T={p['transpose']} sat={p['sat_drive']:.1f} rev={p['rev_mode']} hp={p['hp_hz']:.0f} "
              f"peak={np.abs(q).max()}", flush=True)
    lp = os.path.join(a.out, 'labels.csv')
    old = []
    if os.path.exists(lp):
        with open(lp, newline='') as f:
            old = [r for r in csv.DictReader(f) if r['file'] not in {x['file'] for x in rows}]
    allrows = sorted(old + rows, key=lambda r: (GROUPS.index(r['group']) if r['group'] in GROUPS else 9, r['file']))
    with open(lp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['file', 'group', 'start_s', 'end_s', 'params'])
        w.writeheader()
        w.writerows(allrows)


if __name__ == '__main__':
    main()
