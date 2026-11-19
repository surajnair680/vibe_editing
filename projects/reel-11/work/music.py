"""reel-11 music: an ORIGINAL bouncy 8-bit platformer track (no existing melodies), made in code.

NES-like voices: pulse lead (25 % duty), pulse arps (12.5 %), triangle bass, noise drums. C major, 152.5 BPM, swung
8ths. The tempo is chosen so bar 11 lands exactly on the Tiger photo (17.31 s = 11 bars).
Sections: intro groove under her clip (no lead) -> paused 12.87-13.10 (the PAUSED screen) -> groove under the deadpan
-> fanfare fill (bVI-bVII) -> full band from 17.31 -> power-down at 45.17 (glitch) -> double-time drive over the gym
footage -> level-clear fanfare on the end card (49.05) and a final chord.
Writes stems to work/audio/music_{lead,arp,bass,drums}.wav (48 kHz mono float) for mix.py.
"""
import numpy as np
import soundfile as sf

SR = 48000
BPM = 152.5
BEAT = 60 / BPM
BAR = 4 * BEAT
DUR = 49.9 + 0.6
SWING = 0.58          # second 8th of each beat lands at 58 % of the beat

PAUSE = (12.87, 13.10)
GLITCH = 45.17
RESUME = 45.40
END = 49.05


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t8(bar, step):
    """time of 8th step (0..7) in bar, swung"""
    return bar * BAR + (step // 2) * BEAT + (step % 2) * BEAT * SWING


def pulse(f, n, duty):
    ph = (np.arange(n) * f / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def tri(f, n):
    ph = (np.arange(n) * f / SR) % 1.0
    return 4 * np.abs(ph - 0.5) - 1.0


def env(n, a=0.003, d=0.06, s=0.6, r=0.03):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na)
    nd2 = min(nd, max(0, n - na))
    e[na:na + nd2] = np.linspace(1, s, nd2)
    nr = min(nr, n)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


class Track:
    def __init__(self):
        self.x = np.zeros(int(DUR * SR))

    def add(self, t, sig):
        i = int(round(t * SR))
        if i >= len(self.x) or i + len(sig) <= 0:
            return
        j = min(len(self.x), i + len(sig))
        self.x[max(0, i):j] += sig[max(0, -i):j - i]


lead, arp, bass, drums = Track(), Track(), Track(), Track()
rng = np.random.default_rng(11)
NOISE = rng.uniform(-1, 1, SR)

# ---- harmony: 8-bar cycle (I vi IV V I vi ii V), chord tones as MIDI
CHORDS = {"C": [60, 64, 67], "Am": [57, 60, 64], "F": [53, 57, 60], "G": [55, 59, 62], "Dm": [50, 53, 57],
          "Ab": [56, 60, 63], "Bb": [58, 62, 65]}
CYCLE = ["C", "Am", "F", "G", "C", "Am", "Dm", "G"]
ROOT = {"C": 36, "Am": 45, "F": 41, "G": 43, "Dm": 38, "Ab": 44, "Bb": 46}

# ---- original melody, 8 bars of 8 swung 8ths (None = rest, "-" = hold)
MEL = [
    [72, None, 76, 79, None, 76, None, 72],
    [69, None, 72, 76, None, 72, None, 69],
    [65, 69, 72, None, 74, None, 72, 69],
    [71, None, 74, "-", 79, "-", "-", None],
    [84, None, 83, None, 79, 76, None, 79],
    [81, None, 79, None, 76, 72, None, 76],
    [74, 77, 81, None, 79, 77, 74, None],
    [79, "-", None, 74, 71, None, 67, None],
]
# a sparser answer phrase used while he talks a lot (keeps words clear)
MEL_SPARSE = [
    [72, None, None, None, 79, None, None, None],
    [69, None, None, None, 76, None, None, None],
    [65, None, None, None, 72, None, 74, None],
    [71, None, None, None, 67, None, None, None],
    [72, None, None, None, 76, None, 79, None],
    [69, None, None, None, 72, None, None, None],
    [74, None, None, None, 77, None, None, None],
    [79, None, 77, None, 74, None, 71, None],
]


def muted(t):
    return PAUSE[0] <= t < PAUSE[1] or GLITCH <= t < RESUME or t >= END + 1.2


def note(track, t, m, dur, kind, vol):
    if muted(t):
        return
    n = int(dur * SR)
    f = mtof(m)
    if kind == "lead":
        sig = pulse(f, n, 0.25) * env(n, d=0.08, s=0.55, r=0.04)
        # light vibrato on long notes
        if dur > 0.3:
            vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * np.arange(n) / SR) * np.clip((np.arange(n) / SR - 0.15) * 4, 0, 1)
            sig = pulse(f, n, 0.25) * env(n, d=0.08, s=0.55, r=0.04)
            ph = np.cumsum(f * vib / SR) % 1.0
            sig = np.where(ph < 0.25, 1.0, -1.0) * env(n, d=0.08, s=0.55, r=0.04)
    elif kind == "arp":
        sig = pulse(f, n, 0.125) * env(n, d=0.03, s=0.3, r=0.02)
    else:
        sig = tri(f, n) * env(n, a=0.002, d=0.05, s=0.8, r=0.02)
    # cut any part that falls into a muted window
    tt = t + np.arange(n) / SR
    sig = sig * ~((tt >= PAUSE[0]) & (tt < PAUSE[1]) | (tt >= GLITCH) & (tt < RESUME))
    track.add(t, sig * vol)


def kick(t, vol=0.9):
    if muted(t):
        return
    n = int(0.09 * SR)
    f = np.linspace(160, 45, n)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.arange(n) / (0.03 * SR))
    drums.add(t, sig * vol)


def snare(t, vol=0.5):
    if muted(t):
        return
    n = int(0.12 * SR)
    sig = NOISE[:n] * np.exp(-np.arange(n) / (0.035 * SR))
    sig = np.round(sig * 8) / 8                      # 4-bit-ish noise
    drums.add(t, sig * vol)


def hat(t, vol=0.16):
    if muted(t):
        return
    n = int(0.025 * SR)
    s = NOISE[2000:2000 + n]
    s = s - np.convolve(s, np.ones(4) / 4, "same")
    drums.add(t, s * np.exp(-np.arange(n) / (0.006 * SR)) * vol)


def groove_bar(b, chord, drums_on=True, full=True, double=False):
    r = ROOT[chord]
    pat = [r, None, r + 7, None, r + 12, None, r + 7, None] if full else [r, None, None, None, r + 7, None, None, None]
    for s, m in enumerate(pat):
        if m is not None:
            note(bass, t8(b, s), m, BEAT * 0.45, "bass", 0.5)
    for s in range(8):                                # 8th-note arps of the chord, one octave up
        m = CHORDS[chord][s % 3] + 12
        note(arp, t8(b, s), m, BEAT * 0.3, "arp", 0.10)
    if drums_on:
        steps = range(8)
        for s in steps:
            hat(t8(b, s))
        for s in (0, 4) if not double else (0, 2, 4, 6):
            kick(t8(b, s))
        for s in (2, 6):
            snare(t8(b, s))


def melody_bar(b, k, sparse=False, octave=0, vol=0.22):
    bar = (MEL_SPARSE if sparse else MEL)[k % 8]
    for s, m in enumerate(bar):
        if m is None or m == "-":
            continue
        hold = 1
        while s + hold < 8 and bar[s + hold] == "-":
            hold += 1
        dur = (t8(b, s + hold) if s + hold < 8 else (b + 1) * BAR) - t8(b, s)
        note(lead, t8(b, s), m + octave, dur * 0.9, "lead", vol)


# ---- arrangement
nbars = int(np.ceil(DUR / BAR))
for b in range(nbars):
    t0 = b * BAR
    chord = CYCLE[b % 8]
    if b < 8:                          # intro under her clip: groove, no lead (her words stay clear)
        groove_bar(b, chord, drums_on=b >= 2, full=b >= 1)
    elif b < 10:                       # deadpan: groove continues after the pause
        groove_bar(b, chord, drums_on=True, full=True)
    elif b == 10:                      # fanfare fill into the Tiger drop: Ab (2 beats) Bb (2 beats), rising triplets
        for half, ch in enumerate(["Ab", "Bb"]):
            for k in range(6):
                m = CHORDS[ch][k % 3] + 12 + (12 if k >= 3 else 0)
                note(lead, t0 + half * 2 * BEAT + k * BEAT / 3, m, BEAT / 3 * 0.9, "lead", 0.2)
            note(bass, t0 + half * 2 * BEAT, ROOT[ch], BEAT * 1.8, "bass", 0.5)
        for k in range(8):
            snare(t0 + 2 * BEAT + k * BEAT / 4, 0.25 + k * 0.04)
    elif t0 < GLITCH:                  # full band from the Tiger photo (bar 11 = 17.31 s)
        groove_bar(b, chord)
        melody_bar(b, b - 11, sparse=(b - 11) % 16 >= 8)
    else:                              # after the glitch: double-time drive over the real gym footage
        if t0 + BAR <= RESUME:
            continue
        if t0 >= END:
            continue
        groove_bar(b, chord, double=True)
        melody_bar(b, b - 11, octave=12, vol=0.16)

# power-down at the glitch: a falling pulse glide (0.2 s)
n = int(0.22 * SR)
f = np.geomspace(880, 110, n)
ph = np.cumsum(f / SR) % 1.0
lead.add(GLITCH - 0.005, np.where(ph < 0.5, 1.0, -1.0) * np.linspace(0.25, 0, n))

# level-clear fanfare on the end card + final chord
for k, m in enumerate([72, 76, 79, 84, 88]):
    tt = END + k * 0.075
    nn = int(0.07 * SR)
    lead.add(tt, pulse(mtof(m), nn, 0.25) * env(nn, s=0.7) * 0.2)
fin = END + 5 * 0.075
nn = int(1.0 * SR)
for m in (72, 76, 79, 84):
    lead.add(fin, pulse(mtof(m), nn, 0.25) * env(nn, d=0.2, s=0.5, r=0.5) * 0.09)
bass.add(fin, tri(mtof(36), nn) * env(nn, d=0.2, s=0.7, r=0.5) * 0.5)
kick(fin, 1.0)

for name, tr in (("lead", lead), ("arp", arp), ("bass", bass), ("drums", drums)):
    sf.write(f"work/audio/music_{name}.wav", tr.x.astype(np.float32), SR, subtype="FLOAT")
print("bars", nbars, "bar", round(BAR, 4), "bar 11 at", round(11 * BAR, 3))
