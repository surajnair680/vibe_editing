"""reel-11 game sound effects, made in code (original 8-bit style blips; no existing game sounds).
Each cue: (time in edit seconds, kind, gain). Writes work/audio/sfx_chip.wav (48 kHz mono float).
Real recorded transition sounds (whooshes, glitch) are separate (assets/sfx/, see mix.py)."""
import numpy as np
import soundfile as sf

SR = 48000
DUR = 49.9 + 0.6
rng = np.random.default_rng(5)
NOISE = rng.uniform(-1, 1, SR * 2)


def sq(freqs, n, duty=0.5):
    f = np.broadcast_to(freqs, (n,)) if np.ndim(freqs) == 0 else freqs
    ph = np.cumsum(f / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def dec(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def seq(notes, step, duty=0.5, tau=0.05):
    out = []
    for f in notes:
        n = int(step * SR)
        out.append(sq(f, n, duty) * dec(n, tau))
    return np.concatenate(out)


def kind(k):
    if k == "blip":        # cursor move
        return seq([1320, 1760], 0.035, 0.25, 0.03)
    if k == "select":      # confirm
        return seq([988, 1319, 1976], 0.045, 0.25, 0.05)
    if k == "pause":       # pause jingle
        return seq([1319, 988, 1319, 988], 0.06, 0.5, 0.05)
    if k == "boing":       # card pops in (jump)
        n = int(0.22 * SR)
        f = np.concatenate([np.geomspace(300, 900, n // 2), np.geomspace(900, 700, n - n // 2)])
        return sq(f, n, 0.25) * dec(n, 0.12)
    if k == "tick":        # page flip / counter
        n = int(0.02 * SR)
        return NOISE[:n] * dec(n, 0.004)
    if k == "error":       # 99 % stuck
        n = int(0.28 * SR)
        return sq(110, n, 0.5) * 0.8 * (dec(n, 0.2))
    if k == "save":        # save ticks
        return np.concatenate([seq([1568], 0.03, 0.25, 0.02), np.zeros(int(0.04 * SR))] * 3)
    if k == "damage":      # body fat +1
        n = int(0.3 * SR)
        f = np.geomspace(700, 120, n)
        return sq(f, n, 0.5) * dec(n, 0.15)
    if k == "powerup":     # item obtained
        notes = [523, 659, 784, 1047, 659, 784, 1047, 1319, 784, 1047, 1319, 1568]
        return seq(notes, 0.045, 0.25, 0.06)
    if k == "sad":         # body: unhappy
        return seq([392, 370, 349, 330], 0.11, 0.5, 0.09)
    if k == "close":       # window mosaics out
        n = int(0.15 * SR)
        return sq(np.geomspace(1500, 300, n), n, 0.125) * dec(n, 0.08)
    if k == "step":        # friend footsteps
        n = int(0.03 * SR)
        return NOISE[100:100 + n] * dec(n, 0.008) * 0.6
    if k == "gameover":    # not started
        return seq([784, 659, 523, 392, 330, 262], 0.09, 0.5, 0.08)
    if k == "oneup":       # follow button
        return seq([1319, 1568, 2637, 2093, 2349, 3136], 0.06, 0.25, 0.06)
    if k == "swirl":       # world opens (mosaic in)
        n = int(0.3 * SR)
        f = 600 + 500 * np.sin(np.linspace(0, 12 * np.pi, n)) * np.linspace(1, 0.2, n)
        return sq(f, n, 0.25) * np.linspace(0.2, 1, n) * dec(n, 0.25)
    raise KeyError(k)


CUES = [(12.70, "pause", 0.30), (15.63, "swirl", 0.25), (17.31, "boing", 0.35)]
CUES += [(19.15 + 0.26 * k, "tick", 0.5) for k in range(6)]
CUES += [(22.03, "blip", 0.22), (22.55, "blip", 0.22), (24.01, "blip", 0.22)]
t = 24.7
while t < 25.17:                      # indecision: cursor can't settle (changes at 7 Hz)
    CUES.append((round(np.ceil(t * 7) / 7, 3), "blip", 0.14))
    t += 1 / 7
CUES += [(25.57, "error", 0.20), (28.29, "select", 0.26), (28.50, "save", 0.22), (30.18, "damage", 0.28),
         (31.87, "powerup", 0.24), (33.89, "sad", 0.22), (36.27, "blip", 0.22), (36.60, "select", 0.24),
         (36.95, "close", 0.24)]
CUES += [(39.45 + k / 8, "step", 0.4) for k in range(int((40.6 - 39.45) * 8))]
CUES += [(44.75, "gameover", 0.20), (49.20, "oneup", 0.22)]

if __name__ == "__main__":
    x = np.zeros(int(DUR * SR))
    for t, k, g in CUES:
        s = kind(k) * g
        i = int(round(t * SR))
        x[i:i + len(s)] += s[:len(x) - i]
    sf.write("work/audio/sfx_chip.wav", x.astype(np.float32), SR, subtype="FLOAT")
    print(len(CUES), "cues")
