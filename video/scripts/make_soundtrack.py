"""Synthesizes the promo soundtrack (beat + trailer SFX) from src/timeline.json.

Usage: python3 scripts/make_soundtrack.py  ->  public/soundtrack.wav
"""
import json
import os

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, 'src', 'timeline.json')))
SR = 44100
FPS = T['fps']
BEAT = 60 / T['bpm']
DUR = T['total'] / FPS + 1.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def sec(frame):
    return frame / FPS


def t_arr(length):
    return np.arange(int(length * SR)) / SR


def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    end = min(len(buf), i + len(sig))
    buf[i:end] += sig[: end - i] * gain


def filt(sig, kind, freq, order=2):
    sos = butter(order, freq, btype=kind, fs=SR, output='sos')
    return sosfilt(sos, sig)


def noise(length):
    return rng.uniform(-1, 1, int(length * SR))


def in_ranges(frame, ranges):
    return any(a <= frame < b for a, b in ranges)


# ---------- instruments ----------
def kick():
    t = t_arr(0.45)
    f = 45 + 120 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7)
    click = filt(noise(0.45), 'highpass', 3000) * np.exp(-t * 300) * 0.4
    return np.tanh((body + click) * 2.2)


def clap():
    t = t_arr(0.35)
    n = filt(noise(0.35), 'bandpass', [900, 5000])
    env = np.exp(-t * 18)
    for d in (0.0, 0.012, 0.024):
        env += np.where(t >= d, np.exp(-(t - d) * 140), 0) * 0.6
    return n * env * 0.9


def hat(length=0.06):
    t = t_arr(length)
    return filt(noise(length), 'highpass', 7500) * np.exp(-t * 60) * 0.5


def impact():
    t = t_arr(3.0)
    f = 30 + 90 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    crack = filt(noise(3.0), 'lowpass', 6000) * np.exp(-t * 9)
    metal = sum(np.sin(2 * np.pi * fr * t) for fr in (220, 331, 497, 745)) * np.exp(-t * 3) * 0.08
    return np.tanh((boom * 1.6 + crack * 0.8 + metal) * 1.5)


def hit():
    t = t_arr(0.6)
    f = 60 + 160 * np.exp(-t * 35)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    snap = filt(noise(0.6), 'bandpass', [1500, 8000]) * np.exp(-t * 40)
    return np.tanh((thump + snap * 0.7) * 1.8) * 0.8


def whoosh(length=0.7):
    t = t_arr(length)
    n = noise(length)
    env = np.sin(np.pi * t / length) ** 2
    # sweep a bandpass upward by crossfading two filtered layers
    lo = filt(n, 'bandpass', [300, 1500])
    hi = filt(n, 'bandpass', [2000, 9000])
    x = t / length
    return (lo * (1 - x) + hi * x) * env * 0.9


def riser(length):
    t = t_arr(length)
    x = t / length
    n = noise(length)
    lo = filt(n, 'bandpass', [400, 1200])
    hi = filt(n, 'bandpass', [3000, 10000])
    f = 200 + 1600 * x ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * (4 + 20 * x) * t)
    return (lo * (1 - x) + hi * x + tone) * x ** 1.5 * trem


def saw(freq, length, detune=(0.0,)):
    t = t_arr(length)
    out = np.zeros_like(t)
    for d in detune:
        out += 2 * ((t * freq * (1 + d)) % 1) - 1
    return out / len(detune)


# ---------- build ----------
drums = np.zeros(N)
bass = np.zeros(N)
pads = np.zeros(N)
fx = np.zeros(N)
duck = np.ones(N)

K, C = kick(), clap()
beat_frames = BEAT * FPS  # 15
roots = [55.0, 43.65, 65.41, 49.0]  # A1 F1 C2 G1

f = 0.0
beat_idx = 0
while f < T['total']:
    fi = int(round(f))
    if in_ranges(fi, T['drums']):
        s = sec(fi)
        place(drums, K, s, 1.0)
        # sidechain duck
        d = t_arr(BEAT)
        place(duck, -(0.75 * np.exp(-d * 9)), s)
        if beat_idx % 2 == 1:
            place(drums, C, s, 0.8)
        sub = 16 if in_ranges(fi, T['drumsDouble']) else 2
        for k in range(sub):
            place(drums, hat(0.05 if sub > 2 else 0.08), s + k * BEAT / sub, 0.9 if k % 2 else 0.5)
        root = roots[(beat_idx // 8) % 4]
        # offbeat pumping bass
        b = saw(root * 2, BEAT / 2, (0, 0.01))
        b = filt(b, 'lowpass', 900) * np.exp(-t_arr(BEAT / 2) * 5)
        place(bass, b, s + BEAT / 2, 0.9)
        sub_s = np.sin(2 * np.pi * root * t_arr(BEAT)) * np.exp(-t_arr(BEAT) * 3)
        place(bass, sub_s, s, 0.6)
        if beat_idx % 8 == 0:
            ch = sum(saw(root * 4 * r, BEAT * 4, (-0.006, 0, 0.007)) for r in (1, 1.189, 1.498))
            ch = filt(ch, 'lowpass', 2200) * np.minimum(1, t_arr(BEAT * 4) * 20)
            place(pads, ch, s, 0.18)
    beat_idx += 1
    f += beat_frames

drums *= 1.0
bass *= np.clip(duck, 0.2, 1)
pads *= np.clip(duck, 0.2, 1)

for fr in T['impacts']:
    place(fx, impact(), sec(fr), 1.0)
    place(fx, whoosh(0.5)[::-1], sec(fr) - 0.5, 0.5)  # reverse swell into the hit
for fr in T['hits']:
    place(fx, hit(), sec(fr), 0.7)
for fr in T['montageHits']:
    place(fx, hit(), sec(fr), 0.45)
for fr in T['whooshes']:
    place(fx, whoosh(), sec(fr) - 0.2, 0.8)
for a, b in T['risers']:
    length = sec(b - a)
    place(fx, riser(length), sec(a), 0.8)


# simple reverb on fx + pads
ir_t = t_arr(1.6)
ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3.5)
ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(fx * 0.6 + pads, ir)[:N] * 0.35

mix = drums * 0.55 + bass * 0.45 + pads + fx * 0.7 + wet
# fade out tail after music ends
end = sec(T['total'])
fade = np.clip((end - np.arange(N) / SR) / 1.0, 0, 1)
mix *= fade
mix = np.tanh(mix * 1.3)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.95

stereo = np.stack([mix, np.roll(mix, 12)], axis=1)
stereo = stereo[: int(SR * sec(T['total']))]
out = os.path.join(ROOT, 'public', 'soundtrack.wav')
wavfile.write(out, SR, (stereo * 32767).astype(np.int16))
print('wrote', out, stereo.shape[0] / SR, 's')
