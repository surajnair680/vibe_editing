"""Mix for reel-15: music + subtle SFX, peaks placed on their frames.
python3 work/mix.py <music m1|m2> <start> <end> out.wav"""
import subprocess, sys, numpy as np
SR = 48000
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def db(x): return 10 ** (x / 20)
music, a, b, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
N = int(round((b - a) * SR))
mix = np.zeros((N, 2), np.float32)
m = load(f'assets/music/{music}.mp3')[int(a * SR):][:N]
mix[:len(m)] += m * db(-3)
# SFX: (file, peak time in the file, edit time of the peak, gain dB)
CUES = [
    ('assets/sfx/openverse/cloth-01.wav', 0.60, 0.9, -14),   # soft coat rustle under the hero
    ('assets/sfx/openverse/fabric-03.wav', 0.18, 4.0, -12),  # fabric flap on the cut to the hanging coat
]
for f, pk, t, g in CUES:
    try:
        s = load(f)
    except Exception:
        s = load(f.replace('.wav', '.mp3'))
    i0 = int(round((t - pk - a) * SR))
    if i0 >= N or i0 + len(s) <= 0:
        continue
    s0 = max(0, -i0); i0 = max(0, i0); s = s[s0:s0 + N - i0]
    mix[i0:i0 + len(s)] += s * db(g)
# fade the music out at the end of a partial preview, 1.2 s
if b < 25:
    k = int(1.2 * SR); mix[-k:] *= np.linspace(1, 0, k)[:, None] ** 2
peak = np.abs(mix).max(); mix *= min(1.0, db(-1.5) / peak)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', out],
               input=mix.astype(np.float32).tobytes(), check=True)
print(out, 'peak before limit %.1f dB' % (20 * np.log10(peak)))
