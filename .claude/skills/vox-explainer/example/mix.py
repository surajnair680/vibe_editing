"""Sound design for the vox-explainer test reel: every sound's loudest moment lands on the frame it belongs to.

python3 .claude/skills/vox-explainer/example/mix.py  ->  example/work/mix.wav (14 s, 48 kHz stereo)
Sounds: Openverse CC0 (assets/sfx/openverse/CREDITS.md). Landing times come from index.html (span ends, on twos).
"""
import os
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, 'assets/sfx/openverse')
SR, DUR = 48000, 14.0

# (time the thing lands on screen, sound, gain dB)
EVENTS = [
    (0.22, 'paper-01', 4), (0.84, 'paper-02', 4), (1.16, 'paper-03', 6),
    (1.48, 'thud-03', -6), (1.48, 'paper-01', 2), (1.80, 'paper-02', 4),   # ABNORMAL lands heavy
    (3.40, 'swoosh-02', -3),                                                # wipe to the grid
    (3.75, 'paper-03', 0), (4.15, 'paper-01', -2), (4.45, 'paper-02', -4),  # tiles settle
    (5.42, 'paper-03', 6), (5.55, 'thud-03', -10),                          # the YOU tile flips
    (6.15, 'paper-01', 3),                                                  # strip
    (7.00, 'swoosh-01', -2),                                                # wipe to the cards
    (7.60, 'paper-02', 5), (7.95, 'paper-01', 5), (8.30, 'paper-03', 7),    # three cards drop
    (8.95, 'marker-01', 20),                                                # marker circle (quiet file)
    (9.85, 'thud-03', -5), (9.85, 'paper-02', 2),                           # ALL OUTLIERS
    (11.00, 'swoosh-02', -3),                                               # wipe to the end card
    (11.50, 'paper-01', 4), (11.50, 'thud-03', -12),
    (11.85, 'thud-03', -3), (11.85, 'paper-03', 4),                         # OUTLIER slams
    (12.25, 'marker-01', 18),                                               # highlighter sweep
]


def load(name):
    a, sr = sf.read(os.path.join(SFX, name + '.wav'), always_2d=True)
    assert sr == SR, (name, sr)
    env = np.convolve(np.abs(a).mean(1), np.ones(240) / 240, 'same')   # 5 ms envelope
    return a, int(np.argmax(env))


mix = np.zeros((int(SR * DUR), 2))
cache = {}
for t, name, db in EVENTS:
    if name not in cache:
        cache[name] = load(name)
    a, peak = cache[name]
    s = int(t * SR) - peak                      # the peak lands on the frame
    a = a[max(0, -s):]
    s = max(0, s)
    n = min(len(a), len(mix) - s)
    mix[s:s + n] += a[:n] * 10 ** (db / 20)

peak = np.abs(mix).max()
mix *= 10 ** (-1 / 20) / peak                   # peak at -1 dBFS
fade = int(0.4 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)
sf.write(os.path.join(HERE, 'work/mix.wav'), mix, SR, subtype='PCM_24')
print('mix -> work/mix.wav, peak gain', round(20 * np.log10(10 ** (-1 / 20) / peak), 1), 'dB')
