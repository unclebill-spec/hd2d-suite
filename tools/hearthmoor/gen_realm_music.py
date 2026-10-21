#!/usr/bin/env python3
"""Hearthmoor realm music (procedural, original work, CC0 1.0). Cozy gloom-and-glow: music box, chimes, soft choir, drones.
Mono 22.05 kHz Vorbis. Each file is exactly N bars; note tails wrap to the start, so loop start 0 / loop end = file length.
Usage: python3 tools/hearthmoor/gen_realm_music.py [out_dir] [track ...]   (default games/hearthmoor/audio/music, all tracks)"""
import numpy as np, subprocess, wave, sys, tempfile, os
from pathlib import Path
SR = 22050
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "games/hearthmoor/audio/music")
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# name: root midi, scale, bpm, bars, chord degrees, voices
T = {
 'midgard':      (65, [0, 2, 4, 5, 7, 9, 11], 80, 8, [0, 3, 5, 4], {'box': 1.0, 'pad': 0.8, 'chime': 0.3}),
 'alfheim':      (62, [0, 2, 4, 6, 7, 9, 11], 72, 8, [0, 1, 4, 5], {'chime': 1.0, 'choir': 0.6, 'box': 0.5}),
 'svartalfheim': (57, [0, 2, 3, 5, 7, 9, 10], 76, 8, [0, 3, 6, 4], {'box': 0.9, 'bell': 0.5, 'drone': 0.7, 'pad': 0.4}),
 'jotunheim':    (52, [0, 2, 3, 5, 7, 8, 10], 60, 8, [0, 5, 3, 6], {'choir': 1.0, 'drone': 0.9, 'chime': 0.4}),
 'muspelheim':   (50, [0, 1, 4, 5, 7, 8, 10], 66, 8, [0, 1, 6, 0], {'drone': 1.0, 'bell': 0.7, 'pad': 0.6, 'box': 0.3}),
 'niflheim':     (59, [0, 2, 3, 5, 7, 8, 10], 54, 8, [0, 5, 2, 6], {'chime': 0.9, 'choir': 0.8, 'drone': 0.6}),
 'asgard':       (60, [0, 2, 4, 5, 7, 9, 11], 66, 8, [0, 5, 3, 4], {'bell': 0.8, 'choir': 0.8, 'drone': 0.6, 'thunder': 0.5, 'chime': 0.4}),   # C major, golden bells + regal choir, distant soft thunder
 'battle':       (52, [0, 2, 3, 5, 7, 8, 10], 120, 8, [0, 5, 6, 4], {'ost': 1.0, 'tom': 0.8, 'pad': 0.5, 'chime': 0.3}),
 'boss':         (48, [0, 2, 3, 5, 7, 8, 11], 104, 8, [0, 5, 1, 4], {'choir': 0.9, 'tom': 0.9, 'drone': 0.8, 'ost': 0.6}),
}
def deg(sc, d): return sc[d % 7] + 12 * (d // 7)
def adsr(n, a, rel):
    t = np.arange(n) / SR; e = np.minimum(t / a, 1); return e * np.clip((n / SR - t) / rel, 0, 1)
def box(m, n):   # music-box tine: sine + inharmonic overtones, fast decay
    t = np.arange(n) / SR; f = hz(m)
    return (np.sin(2*np.pi*f*t) + 0.3*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*9) + 0.12*np.sin(2*np.pi*f*5.2*t)*np.exp(-t*14)) * np.minimum(t/0.003, 1) * np.exp(-t*2.2)
def bell(m, n, dec=0.9):   # soft chime / bell partials
    t = np.arange(n) / SR; f = hz(m)
    return sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/(dec*k)) for a, r, k in ((1, 1, 1), (.5, 2.76, .5), (.25, 5.4, .3), (.15, 8.9, .2))) * np.minimum(t/0.004, 1)
def choir(m, n, rng):   # "ah": harmonics weighted by vowel formants, slow vibrato, slow swell
    t = np.arange(n) / SR; f = hz(m); out = np.zeros(n)
    vib = 1 + 0.004*np.sin(2*np.pi*5.1*t + rng.random()*6)
    for h in range(1, 16):
        fh = f*h
        if fh > 4000: break
        w = sum(g*np.exp(-((fh-F)/bw)**2) for F, bw, g in ((750, 180, 1), (1150, 220, .6), (2600, 400, .2))) + 0.03
        for det in (-0.003, 0.003):
            out += w/h**0.3 * np.sin(2*np.pi*fh*(1+det)*np.cumsum(vib)/SR + rng.random()*6)
    return out / 8 * adsr(n, 1.2, 1.4)
def pad(m, n):
    t = np.arange(n) / SR; f = hz(m)
    return (np.sin(2*np.pi*f*t) + .25*np.sin(2*np.pi*2.004*f*t) + .1*np.sin(2*np.pi*3*f*t)) * adsr(n, 0.9, 1.2)
def tom(n, f0=90):
    t = np.arange(n) / SR; return np.sin(2*np.pi*(f0*0.6*t + f0*0.4*(1-np.exp(-t*20))/20)) * np.exp(-t*7) * np.minimum(t/0.004, 1)
def render(name, root, sc, bpm, bars, ch, V):
    rng = np.random.default_rng(sum(map(ord, name))); beat = 60 / bpm; bar = 4 * beat
    L = int(SR * bar * bars); pad_len = SR * 6; buf = np.zeros(L + pad_len)
    def put(s, x, g): s = int(s); buf[s:s+len(x)] += g * x[:len(buf)-s]
    for b in range(bars):
        d = ch[b % len(ch)]; s0 = b * bar * SR; nb = int((bar + 1.6) * SR)
        tones = [root - 12 + deg(sc, d + k) for k in (0, 2, 4)]
        if 'pad' in V:
            for m in tones: put(s0, pad(m, nb), .05 * V['pad'])
        if 'choir' in V:
            for m in tones: put(s0, choir(m, nb, rng), .07 * V['choir'])
        if 'drone' in V:
            put(s0, pad(root - 24 + deg(sc, d if b % 2 else 0), nb) * (1 + .3*np.sin(np.arange(nb)/SR*1.3)), .09 * V['drone'])
        if 'box' in V:   # melody: stepwise around chord tones, eighth notes with rests
            pos = int(rng.integers(0, 5))
            for i in range(8):
                if rng.random() < .35: continue
                pos = int(np.clip(pos + rng.integers(-2, 3), -2, 8)); put(s0 + i*beat/2*SR, box(root + 12 + deg(sc, d + pos), int(SR*1.8)), .11 * V['box'])
        if 'chime' in V:
            for i in range(4):
                if rng.random() < .55: continue
                put(s0 + (i + rng.choice([0, .5]))*beat*SR, bell(root + 24 + deg(sc, d + int(rng.choice([0, 2, 4, 7]))), int(SR*3)), .06 * V['chime'])
        if 'bell' in V and b % 2 == 0:
            put(s0, bell(root + deg(sc, d), int(SR*4), 1.6), .08 * V['bell'])
        if 'ost' in V:   # soft plucked ostinato (16ths), woody not harsh
            pat = [0, 2, 4, 2, 7, 4, 2, 4]
            for i in range(16):
                put(s0 + i*beat/4*SR, box(root + deg(sc, d + pat[i % 8]), int(SR*.5)), (.07 if i % 4 else .1) * V['ost'])
        if 'thunder' in V and b % 4 == 3:   # distant storm: low muffled tom rolls on the last beat, swelled not struck
            for i, bt in enumerate((2.5, 2.75, 3, 3.25, 3.5)):
                put(s0 + bt*beat*SR, tom(int(SR*1.2), 55 + 4*i) * adsr(int(SR*1.2), .08, .9), (.06 + .03*i) * V['thunder'])
        if 'tom' in V:
            for i, (bt, f) in enumerate(((0, 80), (1.5, 95), (2, 80), (3, 110), (3.5, 95))):
                put(s0 + bt*beat*SR, tom(int(SR*.6), f), (.28 if bt in (0, 2) else .17) * V['tom'])
    out = buf[:L].copy(); out[:pad_len] += buf[L:]   # wrap tails -> seamless loop
    if any(k in V for k in ('chime', 'choir', 'box')):   # wrapped echo
        dl = int(SR * beat * .75); out += .28 * np.roll(out, dl)
    out = np.tanh(out / np.max(np.abs(out)) * 1.2) / np.tanh(1.2) * .8
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wv = os.path.join(td, 'm.wav')
        with wave.open(wv, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wv, '-ac', '1', '-c:a', 'libvorbis', '-q:a', '0', '-map_metadata', '-1', str(OUT / f'music_{name}.ogg')], check=True)
    return round(L / SR, 3)
if __name__ == '__main__':
    only = set(sys.argv[2:])
    for k, v in T.items():
        if not only or k in only: print(k, render(k, *v), 's')
