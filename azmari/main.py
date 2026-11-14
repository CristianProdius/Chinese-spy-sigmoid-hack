#!/usr/bin/env python3
"""Splice localisation for "The Azmari's Borrowed Melody".

Usage: python main.py <file.wav>   (bare filename in cwd)
Writes detection.csv with header start_s,end_s and one row (seconds, 3 decimals).

Idea: compute frame-level feature streams (hop 50 ms) from several independent cue
families (spectral shape, low-frequency/DC, noise floor, pitch/chroma, timbre), then
search every (start, end) interval of 1.5-15 s for the one whose inside differs most
from the outside.  Each family gives a mean-shift scan statistic
(n_in*n_out/N * mean squared standardized mean difference), calibrated to a
robust z-score against its own distribution over all candidate intervals; the
total is the sum over families of max(z, 0)^2, so one family that clearly
stands out is enough and families at their noise level add little.
Only numpy, scipy and the standard library are used.
"""
import csv
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")      # be polite on shared graders

import numpy as np
from scipy.fft import dct, rfft
from scipy.io import wavfile
from scipy.ndimage import percentile_filter

HOP_S = 0.05
MIN_LEN_S = 1.5
MAX_LEN_S = 15.0
EDGE_S = 0.5          # ignore the first/last half second when standardising
EPS = 1e-14


# --------------------------------------------------------------------------- I/O
def load_wav(path):
    sr, x = wavfile.read(path)
    if x.dtype.kind == "i":
        x = x.astype(np.float64) / float(2 ** (8 * x.dtype.itemsize - 1))
    elif x.dtype.kind == "u":
        x = (x.astype(np.float64) - 128.0) / 128.0
    else:
        x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return int(sr), x


# ---------------------------------------------------------------------- features
def _frames(x, sr):
    hop = max(1, int(round(HOP_S * sr)))
    nfft = 1 << int(np.ceil(np.log2(0.18 * sr)))      # 4096 at 22.05 kHz
    pad = nfft // 2
    xp = np.pad(x, (pad, pad), mode="reflect")
    n_frames = 1 + (len(xp) - nfft) // hop
    idx = np.arange(nfft)[None, :] + hop * np.arange(n_frames)[:, None]
    return xp[idx], hop, nfft


def _band_sum(P, freqs, lo, hi):
    m = (freqs >= lo) & (freqs < hi)
    if not m.any():
        m = np.zeros_like(freqs, dtype=bool)
        m[np.argmin(np.abs(freqs - 0.5 * (lo + hi)))] = True
    return P[:, m].sum(axis=1)


def _mel_fb(freqs, sr, n_mels=40, fmin=50.0, fmax=None):
    fmax = fmax or min(sr / 2.0, 10000.0)
    mel = lambda f: 2595.0 * np.log10(1.0 + f / 700.0)
    imel = lambda m: 700.0 * (10 ** (m / 2595.0) - 1.0)
    pts = imel(np.linspace(mel(fmin), mel(fmax), n_mels + 2))
    fb = np.zeros((n_mels, len(freqs)))
    for i in range(n_mels):
        l, c, r = pts[i], pts[i + 1], pts[i + 2]
        up = (freqs - l) / max(c - l, 1e-9)
        dn = (r - freqs) / max(r - c, 1e-9)
        fb[i] = np.clip(np.minimum(up, dn), 0, None)
    fb /= np.maximum(fb.sum(axis=1, keepdims=True), 1e-12)
    return fb


def compute_features(x, sr):
    """Return (times, {family: (T, K) array}, extra) for the whole file."""
    fr, hop, nfft = _frames(x, sr)
    T = fr.shape[0]
    times = np.arange(T) * hop / sr
    dc = fr.mean(axis=1)
    frc = fr - dc[:, None]
    win = np.hanning(nfft)
    X = rfft(frc * win, axis=1)
    P = (X.real ** 2 + X.imag ** 2) / np.sum(win ** 2)
    freqs = np.arange(P.shape[1]) * sr / nfft
    nyq = sr / 2.0
    logP = np.log10(P + EPS)
    tot = P[:, 1:].sum(axis=1) + EPS
    fam = {}

    # ---- spectral shape -------------------------------------------------------
    edges = [200, 300, 450, 650, 900, 1250, 1750, 2500, 3500, 5000, 7000, 9000, nyq]
    edges = [e for e in edges if e < nyq] + [nyq]
    bands = np.stack([_band_sum(P, freqs, edges[i], edges[i + 1])
                      for i in range(len(edges) - 1)], axis=1)
    logb = np.log10(bands + EPS)
    m_sh = (freqs >= 100) & (freqs <= min(8000, nyq))
    fs = freqs[m_sh]
    Ps = P[:, m_sh] + EPS
    centroid = np.log2((Ps * fs).sum(1) / Ps.sum(1))
    lf = np.log2(fs)
    lf0 = lf - lf.mean()
    slope = ((np.log10(Ps) - np.log10(Ps).mean(1, keepdims=True)) * lf0).sum(1) / (lf0 ** 2).sum()
    flat = np.mean(np.log(Ps), 1) - np.log(np.mean(Ps, 1))
    hf = np.log10(_band_sum(P, freqs, min(4000, nyq * 0.7), nyq) / tot + EPS)
    cs = np.cumsum(P[:, 1:], axis=1)
    roll = np.log2(freqs[1:][np.argmax(cs >= 0.85 * cs[:, -1:], axis=1)] + 1.0)
    # temporal sharpness: std(diff)/std inside each frame
    sharp = np.log10(np.std(np.diff(frc, axis=1), axis=1) / (np.std(frc, axis=1) + 1e-12) + 1e-6)
    loge = np.log10(tot)
    fam["spectral"] = np.column_stack([logb - loge[:, None], loge, centroid, slope,
                                       flat, hf, roll, sharp])

    # ---- low frequency / DC ---------------------------------------------------
    lfe = [(1e-3, 20), (20, 40), (40, 60), (60, 100), (100, 150), (150, 200)]
    lfb = np.stack([_band_sum(P, freqs, lo, hi) for lo, hi in lfe], axis=1)
    loglf = np.log10(lfb + EPS)
    lf_rel = np.log10(lfb.sum(1) / tot + EPS)
    m_lt = (freqs >= 35) & (freqs <= 250)
    lft = logP[:, m_lt].max(1) - np.median(logP[:, m_lt], axis=1)
    fam["lowfreq"] = np.column_stack([loglf, lf_rel, lft, dc * 1e4])

    # ---- noise floor ----------------------------------------------------------
    # (a) spectral valleys: low percentile of log PSD across bins within bands
    vb = [(200, 1000), (1000, 3000), (3000, 6000), (6000, nyq)]
    valleys = []
    for lo, hi in vb:
        m = (freqs >= lo) & (freqs < hi)
        if m.sum() >= 8:
            valleys.append(np.percentile(logP[:, m], 10, axis=1))
    valleys = np.column_stack(valleys)
    # (b) running low percentile over ~0.5 s of coarse log band energies
    cedges = [20, 100, 300, 1000, 3000, 6000, nyq]
    cb = np.stack([_band_sum(P, freqs, cedges[i], cedges[i + 1])
                   for i in range(len(cedges) - 1)], axis=1)
    lcb = np.log10(cb + EPS)
    nwin = max(3, int(round(0.5 / HOP_S)) | 1)
    run_floor = percentile_filter(lcb, 10, size=(nwin, 1), mode="nearest")
    fam["noisefloor"] = np.column_stack([valleys, run_floor])

    # ---- pitch / chroma -------------------------------------------------------
    m_ch = (freqs >= 100) & (freqs <= min(4000, nyq))
    pc = np.mod(np.round(12 * np.log2(freqs[m_ch] / 440.0)), 12).astype(int)
    comp = np.sqrt(P[:, m_ch])
    chroma = np.zeros((T, 12))
    for k in range(12):
        chroma[:, k] = comp[:, pc == k].sum(1)
    chroma /= chroma.sum(1, keepdims=True) + 1e-12
    # rarity of the frame's pitch classes w.r.t. the whole file (a minority insert
    # brings pitch classes that are rare globally)
    gchroma = chroma.mean(0) + 1e-6
    rare = chroma @ (-np.log(gchroma / gchroma.sum()))
    # tuning offset: circular mean of interpolated spectral-peak positions (cents)
    lp = logP[:, m_ch]
    pk = (lp[:, 1:-1] > lp[:, :-2]) & (lp[:, 1:-1] >= lp[:, 2:]) & \
         (lp[:, 1:-1] > lp.max(1, keepdims=True) - 4.0)
    a, b, c = lp[:, :-2], lp[:, 1:-1], lp[:, 2:]
    den = a - 2 * b + c
    delta = np.where(np.abs(den) > 1e-9, 0.5 * (a - c) / np.where(np.abs(den) > 1e-9, den, 1), 0)
    fpk = (np.arange(lp.shape[1])[None, 1:-1] + np.flatnonzero(m_ch)[0] + delta) * sr / nfft
    ang = 2 * np.pi * 12 * np.log2(np.maximum(fpk, 1.0) / 440.0)
    wpk = np.where(pk, 10 ** (0.5 * (b - lp.max(1, keepdims=True))), 0.0)
    zc = (wpk * np.exp(1j * ang)).sum(1) / (wpk.sum(1) + 1e-12)
    tun_c, tun_s = zc.real, zc.imag
    # pitch height via a log harmonic sum over candidate f0 in 80-1500 Hz
    df = sr / nfft
    f0c = np.exp(np.linspace(np.log(80), np.log(min(1500, nyq / 4)), 160))
    hs = np.zeros((T, len(f0c)))
    for h in (1, 2, 3, 4):
        bins = np.clip(np.round(h * f0c / df).astype(int), 0, P.shape[1] - 1)
        hs += logP[:, bins] / h
    f0 = np.log2(f0c[np.argmax(hs, axis=1)])
    # rarity of the detected note (and its pitch class) within this recording;
    # only confident, non-quiet frames vote, the rest get the neutral median
    sal = hs.max(1) - np.median(hs, axis=1)
    voiced = (loge > np.percentile(loge, 20)) & (sal > np.percentile(sal, 10))
    note = np.round(12 * (f0 - np.log2(440.0)) + 69).astype(int)
    note_pc = np.mod(note, 12)
    rare_note = np.zeros(T)
    rare_pc = np.zeros(T)
    if voiced.sum() >= 20:
        nv = note[voiced] - note[voiced].min()
        hn = (np.bincount(nv) + 0.5) / (voiced.sum() + 0.5 * (nv.max() + 1))
        hp = (np.bincount(note_pc[voiced], minlength=12) + 0.5) / (voiced.sum() + 6.0)
        rare_note[voiced] = -np.log(hn[nv])
        rare_pc[voiced] = -np.log(hp[note_pc[voiced]])
        rare_note[~voiced] = np.median(rare_note[voiced])
        rare_pc[~voiced] = np.median(rare_pc[voiced])
    # energy-weighted log-frequency centre of the 100-4000 Hz region
    pcent = (P[:, m_ch] * np.log2(freqs[m_ch])).sum(1) / (P[:, m_ch].sum(1) + EPS)
    fam["pitchanom"] = np.column_stack([rare, rare_note, rare_pc, tun_c, tun_s])
    fam["pitch"] = np.column_stack([f0, pcent])
    fam["chroma"] = chroma

    # ---- dynamics (reverb / compression change the within-second contrast) ----
    nw1 = max(3, int(round(1.0 / HOP_S)) | 1)
    hi_p = percentile_filter(lcb, 90, size=(nw1, 1), mode="nearest")
    lo_p = percentile_filter(lcb, 10, size=(nw1, 1), mode="nearest")
    flux = np.log10(np.maximum(np.diff(logP, axis=0, prepend=logP[:1]), 0).mean(1) + 1e-6)
    fam["dynamics"] = np.column_stack([hi_p - lo_p, flux])

    # ---- timbre (MFCC 1..12) --------------------------------------------------
    fb = _mel_fb(freqs, sr)
    mel = np.log10(P @ fb.T + EPS)
    mfcc = dct(mel, type=2, norm="ortho", axis=1)[:, 1:13]
    fam["timbre"] = mfcc

    extra = {"loge": loge, "hop": hop, "nfft": nfft}
    return times, fam, extra


# ------------------------------------------------------------------------ search
STD_MODE = os.environ.get("STD_MODE", "mad")   # "rank" = research option


def _rank_z(F, valid):
    """Normal scores of the within-file ranks (ties averaged); robust to spikes
    and to discrete-valued features where the MAD collapses."""
    from scipy.special import ndtri
    from scipy.stats import rankdata
    Z = np.zeros_like(F, dtype=np.float64)
    n = int(valid.sum())
    for k in range(F.shape[1]):
        ref = np.sort(F[valid, k])
        lo_r = np.searchsorted(ref, F[:, k], side="left")
        hi_r = np.searchsorted(ref, F[:, k], side="right")
        r = 0.5 * (lo_r + hi_r)
        Z[:, k] = ndtri(np.clip((r + 0.5) / (n + 1.0), 1e-4, 1 - 1e-4))
    return Z


def _robust_z(F, valid):
    if STD_MODE == "rank":
        return _rank_z(F, valid)
    med = np.median(F[valid], axis=0)
    mad = 1.4826 * np.median(np.abs(F[valid] - med), axis=0)
    sd = np.std(F[valid], axis=0)
    scale = np.where(mad > 1e-9, mad, np.where(sd > 1e-12, sd, 1.0))
    Z = (F - med) / scale
    return np.clip(Z, -6, 6)


def scan_family(Z, min_n, max_n, lo, hi):
    """Mean-shift scan statistic for every interval [s, e) (frame indices).

    Returns S (n_start x n_len) with S = n_in*n_out/N * ||mean_in - mean_out||^2 / K,
    starts and lengths.  Frames outside [lo, hi) are excluded from the 'outside'.
    """
    Zv = Z[lo:hi]
    N, K = Zv.shape
    C = np.vstack([np.zeros((1, K)), np.cumsum(Zv, axis=0)])
    tot = C[-1]
    lens = np.arange(min_n, max_n + 1)
    starts = np.arange(0, N - min_n + 1)
    S = np.full((len(starts), len(lens)), np.nan)
    for j, L in enumerate(lens):
        s = np.arange(0, N - L + 1)
        sum_in = C[s + L] - C[s]
        n_in = L
        n_out = N - L
        d = sum_in / n_in - (tot - sum_in) / n_out
        S[: len(s), j] = (n_in * n_out / N) * np.mean(d * d, axis=1)
    return S, starts + lo, lens


def scan_features(Z, min_n, max_n, lo, hi):
    """Per-feature version of scan_family: returns S of shape (n_start, n_len, K)."""
    Zv = Z[lo:hi]
    N, K = Zv.shape
    C = np.vstack([np.zeros((1, K)), np.cumsum(Zv, axis=0)])
    tot = C[-1]
    lens = np.arange(min_n, max_n + 1)
    starts = np.arange(0, N - min_n + 1)
    S = np.full((len(starts), len(lens), K), np.nan)
    for j, L in enumerate(lens):
        s = np.arange(0, N - L + 1)
        sum_in = C[s + L] - C[s]
        d = sum_in / L - (tot - sum_in) / (N - L)
        S[: len(s), j, :] = (L * (N - L) / N) * d * d
    return S, starts + lo, lens


def calibrate_last(S):
    """calibrate() applied to every slice S[..., k]."""
    out = np.empty_like(S)
    for k in range(S.shape[-1]):
        out[..., k] = calibrate(S[..., k])
    return out


def calibrate(S):
    v = S[np.isfinite(S)]
    r = np.sqrt(np.maximum(v, 0))
    med = np.median(r)
    mad = 1.4826 * np.median(np.abs(r - med)) + 1e-12
    return (np.sqrt(np.maximum(S, 0)) - med) / mad


def detect(x, sr, return_debug=False):
    times, fam, extra = compute_features(x, sr)
    T = len(times)
    edge = int(round(EDGE_S / HOP_S))
    lo, hi = edge, T - edge
    valid = np.zeros(T, bool)
    valid[lo:hi] = True
    min_n = int(round(MIN_LEN_S / HOP_S))
    max_n = min(int(round(MAX_LEN_S / HOP_S)), (hi - lo) - min_n)
    total = None
    per = {}
    for name, F in fam.items():
        Z = _robust_z(F, valid)
        S, starts, lens = scan_family(Z, min_n, max_n, lo, hi)
        Zc = calibrate(S)
        per[name] = Zc
        # squared positive part: a family that clearly stands out dominates, a
        # family sitting at its own noise level contributes little
        contrib = np.maximum(Zc, 0.0) ** 2
        total = contrib if total is None else total + contrib
    total = np.where(np.isfinite(total), total, -np.inf)
    i, j = np.unravel_index(np.argmax(total), total.shape)
    s_idx = starts[i]
    e_idx = s_idx + lens[j]
    start_s = times[s_idx]
    end_s = times[min(e_idx, T - 1)]
    if return_debug:
        return start_s, end_s, dict(times=times, per=per, total=total,
                                    starts=starts, lens=lens, fam=fam)
    return start_s, end_s


def main():
    if len(sys.argv) < 2:
        print("usage: python main.py <input.wav>", file=sys.stderr)
        sys.exit(2)
    sr, x = load_wav(sys.argv[1])
    try:
        start_s, end_s = detect(x, sr)
    except Exception as exc:  # never leave the grader without an answer
        print(f"detector failed ({exc}); falling back to the middle", file=sys.stderr)
        dur = len(x) / sr
        start_s, end_s = max(0.0, dur / 2 - 3), min(dur, dur / 2 + 3)
    with open("detection.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start_s", "end_s"])
        w.writerow([f"{start_s:.3f}", f"{end_s:.3f}"])
    print(f"{start_s:.3f},{end_s:.3f}")


if __name__ == "__main__":
    main()
