"""reel-16 soundtrack: m1 extended to the 24 s edit + subtle SFX.
python3 work/mix.py  ->  work/mix.wav and out/reel-16-final.mp4

Music (m1, ElevenLabs, 104.85 BPM): its groove is only 8 bars (18.4 s) before the ending.
Phrases are 4 bars (bar 0 ~ bar 4). Arrangement: bars 2-3, bars 0-3, bars 4-7 + ending, all
spliced on downbeats (bar 3 -> bar 0 is the same move as bar 3 -> bar 4 in the original).
That puts the ending chord 10 bars in; a 2.4 % speed-up lands it on the white ZAZI card cut (22.36 s).
"""
import subprocess, numpy as np
SR = 48000
def load(path, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path] + (['-af', af] if af else []) + ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
def db(x): return 10 ** (x / 20)

DUR = 24.0
LOGO = 22.36                        # cut to the white ZAZI card
T0, BEAT = 0.05, 0.572258           # m1 first kick, beat length
BAR = 4 * BEAT
def bar(k): return T0 + k * BAR

m = load('assets/music/m1.mp3')
PRE = 0.012                         # splice just before each downbeat's transient
XF = int(0.010 * SR)
pieces = [(bar(2), bar(4)), (bar(0), bar(4)), (bar(4), len(m) / SR)]
out = np.zeros((0, 2), np.float32)
for a, b in pieces:
    seg = m[int((a - PRE) * SR):int((b - PRE) * SR)].copy()
    if len(out):
        r = np.linspace(0, 1, XF)[:, None]
        out[-XF:] = out[-XF:] * (1 - r) + seg[:XF] * r
        seg = seg[XF:]
    out = np.concatenate([out, seg])
# speed up so the ending chord (10 bars + PRE after start) lands on LOGO
chord_at = 10 * BAR + PRE
tempo = chord_at / (LOGO + PRE)
src = 'work/audio/m1_arr.wav'
import os; os.makedirs('work/audio', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', src],
               input=out.astype(np.float32).tobytes(), check=True)
mus = load(src, f'atempo={tempo:.5f}')
mus = mus[int(PRE * SR):]           # first downbeat at 0:00
N = int(DUR * SR)
mix = np.zeros((N, 2), np.float32)
mus = mus[:N]
mix[:len(mus)] += mus * db(-3)
fo = int(0.8 * SR); mix[N - fo:] *= np.linspace(1, 0, fo)[:, None] ** 2   # fade out over the logo hold
mix[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))[:, None]

# SFX: (file, peak time in the file, edit time of the peak, gain dB, filter). Quiet, on type and card moments.
D = 'assets/sfx/openverse/'
CUES = [
    ('paper-03', 0.08, 1.20, -17, None),          # orange ZAZI card slides in
    ('paper-01', 0.25, 3.20, -19, None),          # yellow MADE card
    ('cloth-01', 0.60, 5.75, -17, None),          # model in the embroidered coat, red door
    ('paper-02', 0.24, 9.16, -19, None),          # CRAFT
    ('paper-03', 0.08, 12.84, -17, None),         # the coat grid
    ('fabric-03', 0.18, 14.64, -17, None),        # LIMITED DROPS, coat close-up
    ('paper-01', 0.25, 18.36, -19, None),         # HANDMADE
    ('chime-03', 0.49, 22.50, -14, 'lowpass=f=6000'),  # ZAZI card, soft chime with the final chord
]
for name, pk, t, g, af in CUES:
    s = load(D + name + '.wav', af)
    i0 = int(round((t - pk) * SR))
    s = s[max(0, -i0):][:N - max(0, i0)]; i0 = max(0, i0)
    mix[i0:i0 + len(s)] += s * db(g)

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), 'work/mix.wav'],
               input=mix.astype(np.float32).tobytes(), check=True)
os.makedirs('out', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'raw/zazi_v1.mp4', '-i', 'work/mix.wav', '-map', '0:v', '-map', '1:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', 'out/reel-16-final.mp4'], check=True)
print('tempo factor', round(tempo, 4), '-> out/reel-16-final.mp4')
