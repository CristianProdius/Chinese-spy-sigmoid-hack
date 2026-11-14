#!/usr/bin/env python3
"""Synthetic splice-localisation benchmark for "The Azmari's Borrowed Melody".

Each file is a 45-70 s mono 22050 Hz int16 "take" (masenqo-like bowed string by default,
modelled on train-input.wav) in which one 2-10 s interval is replaced by "borrowed" material,
with an equal-power crossfade of 20-60 ms and RMS loudness matching.

Scenarios (what differs between the host take and the borrowed material):
  a  train-like: other register (pitch class absent from host) + washint timbre + 20-200 Hz content, no DC
  b  same register and instrument, other qenet (scale) only
  c  same note set, other timbre only
  d  other background-noise level or colour only
  e  mains hum or LF rumble added or removed only
  f  band-limited / resampled source only
  g  other reverb only
  h  phrase from another take of the same synth (new noise realisation, slight tuning offset)
  i  combination of 2-3 of b..h with milder settings

Usage: gen.py [--out DIR] [--per 8] [--scenarios abcdefghi] [--seed 20261114] [--jobs 4]
Writes DIR/<scen>_<k>.wav, DIR/labels.csv (file,scenario,start_s,end_s) and DIR/meta.jsonl.
"""
import argparse
import copy
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache

import numpy as np
from scipy import signal
from scipy.interpolate import CubicSpline

from scipy.io import wavfile

SR = 22050
LSB = 1.0 / 32768
QENETS = {
    'train6': [0, 2, 4, 5, 7, 9],  # pitch classes of the training host (C D E F G A)
    'tizita_major': [0, 2, 4, 7, 9],
    'tizita_minor': [0, 2, 3, 7, 8],
    'bati_major': [0, 4, 5, 7, 11],
    'bati_minor': [0, 3, 5, 7, 10],
    'ambassel': [0, 1, 5, 7, 8],
    'anchihoye': [0, 1, 5, 6, 9],
}
# Background noise of a take = colored LF/HF part (PSD ~ f^-alpha, white-equivalent level at 1 kHz
# in dBFS) + a band part (white noise of std BG_BAND_DB dBFS through HP 200 Hz / LP 2.5 kHz).
# Calibrated on train-input.wav (scipy.signal.stft, nperseg=2048, int16 rounding included):
# about -115 dB/bin at 60-80 Hz, about -106 dB/bin between harmonics at 0.3-2 kHz in note gaps
# (most of that floor is envelope-following bow noise, see make_masenqo),
# about -130.5 dB/bin at 10-10.5 kHz.
HOST_NOISE_DB = -92.0
BG_BAND_DB = -81.0
# Spectral envelope of the training host (dB vs Hz), least-squares fit of its harmonic levels.
E_TRAIN_F = [200, 400, 560, 670, 790, 940, 1120, 1330, 1580, 1880, 2230, 2650, 3150, 3740, 4440, 5270,
             6260, 7440, 8840, 10500]
E_TRAIN_DB = [0, -2, -5, -8, -13, -14, -13, -19, -15, -19, -29, -38, -39, -47, -51, -59, -67, -71, -75, -80]


def db(v):
    return 10.0 ** (v / 20.0)


def U(rng, a, b):
    return float(rng.uniform(a, b))


@lru_cache(maxsize=None)
def _sos(kind, f1, f2=None, order=2):
    if kind == 'band':
        return signal.butter(order, [f1, f2], 'band', fs=SR, output='sos')
    return signal.butter(order, f1, kind, fs=SR, output='sos')


def filt(x, kind, f1, f2=None, order=2):
    return signal.sosfilt(_sos(kind, round(f1, 1), None if f2 is None else round(f2, 1), order), x)


def smooth_noise(rng, n, rate_hz):
    """Unit-ish random curve with roughly rate_hz bandwidth."""
    k = max(int(n / SR * rate_hz) + 4, 4)
    return CubicSpline(np.linspace(0, n, k), rng.standard_normal(k))(np.arange(n))


# ----------------------------------------------------------------------------- instruments
def make_masenqo(rng, spread=1.0):
    """Bowed string with the training host's spectral envelope plus random tilt and body peaks."""
    return dict(kind='masenqo', tilt=1.5 + U(rng, -1.5, 1.5) * spread,
                body=[(U(rng, 350, 4000), U(rng, -4, 4) * spread, U(rng, 0.12, 0.35))
                      for _ in range(int(rng.integers(2, 5)))],
                # per-pitch harmonic irregularity: the training host's harmonic levels scatter about
                # 5.5 dB around a smooth envelope, consistently for repeated notes of the same pitch
                harm_jitter_db=5.5, harm_seed=int(rng.integers(1 << 30)),
                vib_rate=U(rng, 5.5, 7.0), vib_depth=U(rng, 1, 3), scoop=U(rng, 0, 8), bend=U(rng, 5, 25), note_var_db=0.0,
                att=U(rng, 0.07, 0.10), rel=U(rng, 0.05, 0.08), am_depth=U(rng, 0.04, 0.10),
                noise_db=U(rng, -31, -25), noise_band=(U(rng, 150, 250), U(rng, 2700, 3500)),
                dc_frac=U(rng, 0.003, 0.007), chiff_db=None, lf_lines=False)


def make_washint(rng):
    return dict(kind='washint',
                h_db=[0.0, U(rng, -18, -8), U(rng, -13, -1), U(rng, -35, -25), U(rng, -32, -26)],
                tail_slope=U(rng, 4, 6), tail_floor=U(rng, -58, -50),  # then about -1.5 dB/harmonic
                body=[(U(rng, 1500, 4500), U(rng, 2, 8), U(rng, 0.15, 0.4))
                      for _ in range(int(rng.integers(1, 3)))],
                harm_jitter_db=3.0, harm_seed=int(rng.integers(1 << 30)),
                vib_rate=U(rng, 4.5, 6.0), vib_depth=U(rng, 4, 10), scoop=U(rng, 0, 8), bend=0.0, note_var_db=1.5,
                att=U(rng, 0.015, 0.03), rel=U(rng, 0.02, 0.04), am_depth=U(rng, 0.10, 0.20),
                noise_db=U(rng, -33, -27), noise_band=(U(rng, 250, 400), U(rng, 2500, 4000)),
                dc_frac=0.0, chiff_db=None, lf_lines=False)  # train's borrowed notes show no clicks


def other_timbre(rng, inst):
    """A clearly different timbre for 'same notes, other timbre only' (scenario c)."""
    if rng.random() < 0.5:
        new = make_washint(rng) if inst['kind'] == 'masenqo' else make_masenqo(rng)
    else:
        new = make_masenqo(rng, spread=2.0) if inst['kind'] == 'masenqo' else make_washint(rng)
        if new['kind'] == 'masenqo':
            new['tilt'] = inst['tilt'] + (U(rng, 3, 5) if rng.random() < 0.5 else -U(rng, 3, 5))
        else:
            new['h_db'] = [0.0] + [v + U(rng, -10, 10) for v in new['h_db'][1:]]
            new['harm_jitter_db'] = 5.0
            new['tail_slope'] = inst['tail_slope'] + (2.0 if rng.random() < 0.5 else -1.5)
    new['dc_frac'] = inst['dc_frac']  # keep the host's DC behaviour: timbre is the only change
    return new


def harm_db(inst, f0, K):
    k = np.arange(1, K + 1, dtype=float)
    f = k * f0
    if inst['kind'] == 'masenqo':
        def E(fr):
            return np.interp(np.log2(fr), np.log2(E_TRAIN_F), E_TRAIN_DB) + inst['tilt'] * np.log2(fr / 1000)
        d = E(f) - E(f0)
    else:
        h = np.array(inst['h_db'])
        steep = h[4] - inst['tail_slope'] * (k - 5)
        knee = 5 + max(0.0, (h[4] - inst['tail_floor']) / inst['tail_slope'])
        tail = np.where(k <= knee, steep, inst['tail_floor'] - 1.5 * (k - knee))
        d = np.where(k <= 5, h[np.minimum(k, 5).astype(int) - 1], tail)
    for fc, g, bw in inst['body']:
        d = d + g * np.exp(-0.5 * (np.log2(f / fc) / bw) ** 2)
    pr = np.random.default_rng(inst['harm_seed'] + int(round(12 * np.log2(f0 / 440.0) + 69)))
    jit = pr.standard_normal(K) * inst['harm_jitter_db']
    jit[0] = 0.0
    return d + jit


def render_note(f0, dur, inst, rng):
    att, rel = inst['att'], inst['rel']
    n = int((dur + rel) * SR) + 1
    t = np.arange(n) / SR
    vd = inst['vib_depth'] * U(rng, 0.6, 1.4)
    vr = inst['vib_rate'] * U(rng, 0.92, 1.08)
    cents = vd * np.clip((t - 0.08) / 0.25, 0, 1) * np.sin(2 * np.pi * vr * t + U(rng, 0, 2 * np.pi))
    cents -= inst['scoop'] * U(rng, 0.5, 1.5) * np.exp(-t / 0.04)
    cents += inst['bend'] * U(rng, 0.5, 1.5) * np.clip((t - (dur - 0.12)) / 0.1, 0, 1)  # pitch lift at bow change
    cents += 1.0 * smooth_noise(rng, n, 4)
    ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / SR
    K = max(1, int(10400 / f0))
    A = db(harm_db(inst, f0, K))
    phis = rng.uniform(0, 2 * np.pi, K)
    sig = np.zeros(n)
    for k in range(K):
        sig += A[k] * np.sin((k + 1) * ph + phis[k])
    srms = np.sqrt(np.mean(sig ** 2))
    env = np.ones(n)
    na = min(int(att * SR), n)
    env[:na] = 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    r0 = max(int((dur - 0.4 * rel) * SR), na)
    nr = int(rel * SR)
    seg = env[r0:r0 + nr]
    seg *= 0.5 + 0.5 * np.cos(np.pi * np.arange(len(seg)) / nr)
    env[r0 + nr:] = 0
    note = sig * env * (1 + inst['am_depth'] * smooth_noise(rng, n, 6))
    lo, hi = inst['noise_band']  # bow / breath noise: white (std noise_db re note RMS) -> HP lo -> LP hi
    nb = filt(filt(rng.standard_normal(n), 'high', lo), 'low', hi)
    note += nb * srms * db(inst['noise_db']) * env * np.clip(1 + 0.3 * smooth_noise(rng, n, 10), 0, None)
    if inst.get('chiff_db') is not None:
        m = int(U(rng, 0.01, 0.03) * SR)
        b = filt(rng.standard_normal(m), 'high', 800.0) * np.exp(-np.arange(m) / (0.3 * m))
        note[:m] += b / (b.std() + 1e-12) * srms * db(inst['chiff_db'])
    if inst.get('lf_lines'):
        # 20-200 Hz tonal content following the note (like the borrowed phrase in train-input.wav)
        for _ in range(int(rng.integers(1, 3))):
            note += A[0] * db(U(rng, -55, -28)) * np.sin(2 * np.pi * U(rng, 22, 140) * t + U(rng, 0, 6.3)) * env
    note += inst['dc_frac'] * srms * env  # envelope-following DC, as in the training host
    return note


# ----------------------------------------------------------------------------- melody
def scale_notes(qenet, root, lo, hi):
    return [m for m in range(lo, hi + 1) if (m - root) % 12 in QENETS[qenet]]


def make_motifs(rng, n_avail, n_motifs):
    motifs = []
    for _ in range(n_motifs):
        L = int(rng.integers(4, 9))
        d = int(rng.integers(0, n_avail))
        degs, durs = [], []
        while len(degs) < L:
            r = rng.random()
            if r < 0.12:  # pair of half-beat notes
                degs += [d, int(np.clip(d + rng.choice([-1, 1]), 0, n_avail - 1))]
                durs += [0.5, 0.5]
                d = degs[-1]
            else:
                degs.append(d)
                durs.append(float(rng.choice([1.0, 1.5, 2.0], p=[0.75, 0.10, 0.15])))
            d = int(np.clip(d + rng.choice([-2, -1, 1, 2, 0], p=[0.15, 0.35, 0.3, 0.12, 0.08]), 0, n_avail - 1))
        durs[-1] = float(rng.choice([2.0, 3.0, 4.0], p=[0.5, 0.3, 0.2]))
        motifs.append((degs, durs))
    return motifs


def melody(rng, pitches, beat, t0, t1, motifs):
    """Notes (onset, dur, midi, amp) from exactly t0 until past t1, built from repeated motifs."""
    notes, t, prev = [], t0, None
    while t < t1 + 0.5:
        i = prev if (prev is not None and rng.random() < 0.3) else int(rng.integers(0, len(motifs)))
        prev = i
        degs, durs = list(motifs[i][0]), list(motifs[i][1])
        if rng.random() < 0.3:
            j = int(rng.integers(0, len(degs)))
            degs[j] = int(np.clip(degs[j] + rng.choice([-1, 1]), 0, len(pitches) - 1))
        g = db(U(rng, -0.7, 0.7))
        for dg, du in zip(degs, durs):
            dg = min(dg, len(pitches) - 1)
            parts = [1.0] * int(du) if (du >= 2 and rng.random() < 0.8) else [du]  # bow re-articulation
            for p in parts:
                d = p * beat * (1 + 0.02 * rng.standard_normal())
                notes.append([t, d, pitches[dg], g * db(0.4 * rng.standard_normal())])
                t += d
    return notes


def render_melody(notes, inst, n, rng, tuning):
    y = np.zeros(n + 3 * SR)
    for on, dur, midi, amp in notes:
        i = int(round(on * SR))
        if i >= n:
            break
        seg = render_note(440 * 2 ** ((midi - 69 + tuning / 100) / 12), dur, inst, rng) * amp
        seg *= db(inst['note_var_db'] * rng.standard_normal())
        y[i:i + len(seg)] += seg[:len(y) - i]
    return y[:n]


# ----------------------------------------------------------------------------- take chain
def colored_noise(rng, n, alpha, level_db):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X *= (np.maximum(f, 5.0) / 1000.0) ** (-alpha / 2)
    return np.fft.irfft(X, n) * db(level_db)


def reverb(rng, x, rt60, wet_db):
    L = int(min(rt60 * 1.2, 2.0) * SR)
    t = np.arange(L) / SR
    ir = filt(rng.standard_normal(L), 'low', 6000.0) * np.exp(-6.91 * t / rt60)
    ir[:int(0.004 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    return x + db(wet_db) * signal.fftconvolve(x, ir)[:len(x)]


def hum(rng, n, f_mains, level_db):
    t = np.arange(n) / SR
    amps = [1.0, U(rng, 0.2, 0.6), U(rng, 0.1, 0.4), U(rng, 0.05, 0.2)]
    h = sum(a * np.sin(2 * np.pi * (k + 1) * f_mains * t + U(rng, 0, 6.3)) for k, a in enumerate(amps))
    return h / h.std() * db(level_db)


def rumble(rng, n, fc, level_db):
    r = filt(rng.standard_normal(n + SR), 'low', fc, order=2)[SR:]
    return r / r.std() * db(level_db)


def render_take(tp, notes, n, rng):
    """Music -> reverb -> level -> noise/hum/rumble -> optional band-limit -> DC. Float, 1.0 = full scale."""
    music = render_melody(notes, tp['inst'], n, rng, tp['tuning'])
    if tp['rt60'] > 0:
        music = reverb(rng, music, tp['rt60'], tp['wet_db'])
    act = music[np.abs(music) > 0]
    music *= db(tp['level_db']) / np.sqrt(np.mean(act ** 2))
    x = music + colored_noise(rng, n, tp['noise_alpha'], tp['noise_db'])
    bg = rng.standard_normal(n) * db(tp['bg_db'])
    if tp['bg_lp']:
        bg = filt(filt(bg, 'high', 200.0), 'low', tp['bg_lp'])
    x += bg
    if tp['hum']:
        x += hum(rng, n, tp['hum']['f'], tp['hum']['db'])
    if tp['rumble']:
        x += rumble(rng, n, tp['rumble']['fc'], tp['rumble']['db'])
    if tp['bl_sr']:
        g = np.gcd(SR, tp['bl_sr'])
        up, dn = tp['bl_sr'] // g, SR // g
        x = signal.resample_poly(signal.resample_poly(x, up, dn), dn, up)[:n]
    return x + tp['dc_lsb'] * LSB


# ----------------------------------------------------------------------------- scenarios
def host_params(rng, scen):
    if scen == 'a':
        inst, q, root = make_masenqo(rng, spread=0.5), 'train6', 60
    else:
        inst = make_masenqo(rng) if rng.random() < 0.75 else make_washint(rng)
        q = 'train6' if rng.random() < 0.5 else str(rng.choice([k for k in QENETS if k != 'train6']))
        root = 60 + int(rng.choice([-2, 0, 0, 0, 2, 3]))
    wet = rng.random() < 0.35
    tp = dict(inst=inst, tuning=U(rng, 0, 12) if scen == 'a' else U(rng, -15, 15),
              level_db=U(rng, -38.5, -36.5) if scen == 'a' else U(rng, -40, -35),
              noise_alpha=U(rng, 1.0, 1.2), noise_db=HOST_NOISE_DB + U(rng, -3, 3),
              bg_db=BG_BAND_DB + U(rng, -3, 3), bg_lp=U(rng, 2000, 3000), hum=None, rumble=None,
              rt60=U(rng, 0.15, 0.5) if (wet and scen != 'a') else 0.0, wet_db=U(rng, -12, -6), bl_sr=None,
              dc_lsb=U(rng, -1.5, 0.5), qenet=q, root=root)
    return tp


def lf_kind(rng):
    if rng.random() < 0.5:
        return 'hum', dict(f=int(rng.choice([50, 60])), db=U(rng, -92, -66))
    return 'rumble', dict(fc=U(rng, 40, 120), db=U(rng, -90, -62))


def apply_effect(rng, eff, host, borr, mild=False):
    """Mutate host/borr take params for one effect; returns a short description."""
    if eff == 'b':
        hpc = set(QENETS[host['qenet']])
        cands = [k for k in QENETS if len(set(QENETS[k]) ^ hpc) >= 3]
        borr['qenet'] = str(rng.choice(cands))
        return f"qenet {host['qenet']}->{borr['qenet']}"
    if eff == 'c':
        borr['inst'] = other_timbre(rng, host['inst'])
        return f"timbre {host['inst']['kind']}->{borr['inst']['kind']}"
    if eff == 'd':
        r = rng.random()
        if r < 0.4:  # louder background
            up = U(rng, 5, 10) if mild else U(rng, 6, 15)
            borr['noise_db'] += up
            borr['bg_db'] += up
        elif r < 0.6:  # quieter background
            dn = U(rng, 8, 15)
            borr['noise_db'] -= dn
            borr['bg_db'] -= dn
        elif r < 0.8:  # band noise becomes white (brighter floor)
            borr['bg_lp'] = None
            borr['bg_db'] -= U(rng, 4, 8)
        else:  # colour of the LF part changes, band part darker
            borr['noise_alpha'] = float(rng.choice([0.0, 2.0]))
            borr['bg_lp'] = U(rng, 700, 1200)
            borr['bg_db'] += U(rng, 0, 4)
        def nd(tp):
            return f"{tp['noise_db']:.1f}/a{tp['noise_alpha']:.2f}/bg{tp['bg_db']:.1f}@{tp['bg_lp'] or 0:.0f}"
        return f"noise {nd(host)} -> {nd(borr)}"
    if eff == 'e':
        kind, p = lf_kind(rng)
        if mild:
            p['db'] -= 4
        if rng.random() < 0.5:
            borr[kind], host[kind] = p, None
            return f"{kind} added in splice {p}"
        host[kind] = p
        borr[kind] = None
        return f"{kind} removed in splice {p}"
    if eff == 'f':
        borr['bl_sr'] = int(rng.choice([8000, 11025, 12000, 16000, 18000] if not mild else [11025, 12000, 16000, 18000]))
        return f"bandlimit {borr['bl_sr']}"
    if eff == 'g':
        r = rng.random()
        if r < 0.4:  # dry host, reverberant borrowed phrase
            host['rt60'] = 0.0
            borr['rt60'], borr['wet_db'] = U(rng, 0.4, 1.2), U(rng, -9, -3)
        elif r < 0.7:  # reverberant host, dry borrowed phrase
            host['rt60'], host['wet_db'] = U(rng, 0.3, 0.8), U(rng, -9, -4)
            borr['rt60'] = 0.0
        else:  # both reverberant, borrowed room much larger
            host['rt60'], host['wet_db'] = U(rng, 0.15, 0.4), U(rng, -10, -5)
            borr['rt60'], borr['wet_db'] = min(host['rt60'] * U(rng, 2.2, 3.5), 1.5), U(rng, -8, -3)
        return f"reverb {host['rt60']:.2f}@{host['wet_db']:.0f}dB -> {borr['rt60']:.2f}@{borr['wet_db']:.0f}dB"
    if eff == 'h':
        off = (U(rng, 6, 15) if mild else U(rng, 8, 25)) * float(rng.choice([-1, 1]))
        borr['tuning'] = host['tuning'] + off
        return f"another take, tuning {off:+.1f} cents"
    raise ValueError(eff)


def make_file(job):
    scen, k, seed, out_dir = job
    rng = np.random.default_rng(seed)
    dur = U(rng, 45, 70)
    n = int(dur * SR)
    host = host_params(rng, scen)
    beat = U(rng, 0.55, 0.65)
    hp = scale_notes(host['qenet'], host['root'], host['root'], host['root'] + 10)
    hmotifs = make_motifs(rng, len(hp), int(rng.integers(3, 6)))
    hnotes = melody(rng, hp, beat, 0.0, dur, hmotifs)

    # splice interval, snapped to host note boundaries most of the time (a careful forger)
    L = U(rng, 2, 10)
    s = U(rng, 3, dur - 3 - L)
    e = s + L
    onsets = np.array([nt[0] for nt in hnotes])
    snap = rng.random() < 0.7
    if snap:
        ok = onsets[(onsets > 3) & (onsets < dur - 5)]
        s = float(ok[np.argmin(np.abs(ok - s))]) + 0.02 * float(rng.standard_normal())
        ok = onsets[(onsets >= s + 2) & (onsets <= min(s + 10, dur - 3))]
        if len(ok):
            e = float(ok[np.argmin(np.abs(ok - (s + L)))]) + 0.02 * float(rng.standard_normal())
        else:
            e = s + L
        e = float(np.clip(e, s + 2.0, min(s + 10.0, dur - 3.0)))
    s, e = round(s, 3), round(e, 3)

    borr = copy.deepcopy(host)
    borr['qenet'] = host['qenet']
    desc = []
    if scen == 'a':
        borr['inst'] = make_washint(rng)
        borr['inst']['lf_lines'] = True
        borr['rumble'] = dict(fc=U(rng, 120, 200), db=U(rng, -86, -80))
        borr['dc_lsb'] = 0.0
        borr['tuning'] = host['tuning'] + U(rng, -5, 5)
        borr['qenet'] = str(rng.choice(['train6', 'tizita_major']))
        bp = scale_notes(borr['qenet'], host['root'] + 7, host['root'] + 11, host['root'] + 17)
        desc.append(f"washint {borr['qenet']}@+7 register {bp[0]}-{bp[-1]} + LF lines/rumble, no DC")
    else:
        effs = [scen] if scen != 'i' else list(rng.choice(list('bcdefgh'), size=int(rng.integers(2, 4)), replace=False))
        for eff in effs:
            desc.append(apply_effect(rng, eff, host, borr, mild=(scen == 'i')))
        bp = scale_notes(borr['qenet'], host['root'], host['root'], host['root'] + 10)
    same_song = bp == hp
    bmotifs = hmotifs if same_song else make_motifs(rng, len(bp), int(rng.integers(3, 6)))

    # borrowed take covers [s-pre, e+post]; one onset at the splice start, one at the end when snapped
    pre = max(1.0, borr['rt60'] + 0.5)
    post = 1.0
    nb = int((pre + (e - s) + post) * SR)
    bnotes = [[0.0, pre, int(rng.choice(bp)), 1.0]] + melody(rng, bp, beat, pre, pre + (e - s) + post, bmotifs)
    if snap:
        te = pre + (e - s)
        for j, nt in enumerate(bnotes):
            if nt[0] < te < nt[0] + nt[1] and j + 1 < len(bnotes):
                shift = te - bnotes[j + 1][0]
                nt[1] = te - nt[0]
                for later in bnotes[j + 1:]:
                    later[0] += shift
                break

    host_sig = render_take(host, hnotes, n, rng)
    borr_sig = render_take(borr, bnotes, nb, rng)
    i0 = int(round((s - pre) * SR))
    b = np.zeros(n)
    b[i0:i0 + nb] = borr_sig[:n - i0]

    xf = U(rng, 0.02, 0.06)
    tt = np.arange(n) / SR
    m = np.clip(np.minimum((tt - (s - xf / 2)) / xf, ((e + xf / 2) - tt) / xf), 0, 1)
    si, ei = int(s * SR), int(e * SR)
    gain = np.sqrt(np.mean(host_sig[si:ei] ** 2) / np.mean(b[si:ei] ** 2))
    y = host_sig * np.cos(np.pi / 2 * m) + b * gain * np.sin(np.pi / 2 * m)
    yi = np.clip(np.round(y * 32768), -32768, 32767).astype(np.int16)

    name = f'{scen}_{k}.wav'
    wavfile.write(os.path.join(out_dir, name), SR, yi)

    def tpj(tp):
        d = {kk: vv for kk, vv in tp.items() if kk != 'inst'}
        d['inst'] = tp['inst']['kind']
        return d
    meta = dict(file=name, scenario=scen, start_s=s, end_s=e, dur=round(dur, 3), seed=seed, snapped=snap,
                crossfade_s=round(xf, 4), loud_gain_db=round(20 * np.log10(gain), 2), beat=round(beat, 4),
                desc='; '.join(desc), host_pitches=hp, borrowed_pitches=bp, host=tpj(host), borrowed=tpj(borr))
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
    ap.add_argument('--per', type=int, default=8)
    ap.add_argument('--scenarios', default='abcdefghi')
    ap.add_argument('--seed', type=int, default=20261114)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    jobs = [(sc, k, a.seed + 1000 * (ord(sc) - 96) + k, a.out) for sc in a.scenarios for k in range(1, a.per + 1)]
    with ProcessPoolExecutor(max_workers=min(a.jobs, 4)) as ex:
        metas = list(ex.map(make_file, jobs))
    # merge with an existing set so a partial regeneration keeps the other scenarios' labels
    allm = {}
    mp = os.path.join(a.out, 'meta.jsonl')
    if os.path.exists(mp):
        for line in open(mp):
            mt = json.loads(line)
            if os.path.exists(os.path.join(a.out, mt['file'])):
                allm[mt['file']] = mt
    for mt in metas:
        allm[mt['file']] = mt
    order = sorted(allm.values(), key=lambda m: (m['scenario'], int(m['file'].split('_')[1].split('.')[0])))
    with open(os.path.join(a.out, 'labels.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'scenario', 'start_s', 'end_s'])
        for mt in order:
            w.writerow([mt['file'], mt['scenario'], f"{mt['start_s']:.3f}", f"{mt['end_s']:.3f}"])
    with open(mp, 'w') as f:
        for mt in order:
            f.write(json.dumps(mt, default=float) + '\n')
    for mt in metas:
        print(f"{mt['file']:9s} {mt['start_s']:7.3f}-{mt['end_s']:7.3f} {mt['desc']}")


if __name__ == '__main__':
    main()
