"""reel-12 mix: voice (rough v3 audio: her clip, his isolated voice, the meme's own sound) + music + sound effects.

Music: ElevenLabs music_a (or b), from 0:00, ducked under every voice, stops dead on the "toh" impact (84.84) so the
meme (85.19 on) plays with only its own sound. SFX: ElevenLabs, each placed so its measured peak lands on its frame.
Kept subtle on purpose (user: "dont let the viewer get distracted from the content"): only section panels get an
ink swish, list photos change silently, ticks are low, risers low-passed (he found bright risers harsh, reel-04).
Usage: python3 work/mix.py v1 [a|b]  -> work/audio/mix_<ver>.wav (48 kHz stereo, -14 LUFS, peak -1 dBTP)
"""
import sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

VER = sys.argv[1] if len(sys.argv) > 1 else "v1"
MUS = sys.argv[2] if len(sys.argv) > 2 else "a"
SR = 48000
T_STOP, T_MEME = 84.84, 85.19


def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32).astype(np.float64)


voice, sr = sf.read("work/audio/rough_v3.wav")
assert sr == SR
N = len(voice)
T = N / SR

# ---- sound effects: name -> (measured peak time in the file, gain dB)
SFX = {"ink_swish": (0.40, -14), "hit": (0.01, -15), "stamp": (0.01, -11), "tick": (0.11, -19), "lockon": (0.01, -20),
       "shimmer": (0.12, -17), "swell": (0.31, -20), "whoosh": (0.14, -21), "drip": (0.00, -20), "pop": (0.01, -9),
       "boom": (0.08, -2), "riser": (3.38, -16)}
SOFT = {"riser": 2800, "swell": 3200, "shimmer": 6000, "tick": 6000, "ink_swish": 5000}
buf = {}
for n in SFX:
    x = load(f"assets/el/{n}.mp3")
    if n == "pop":
        x = x / (np.abs(x).max() + 1e-9) * 0.5                       # generated far too quiet (-45 dBFS)
    if n in SOFT:
        sos = butter(2, SOFT[n], "lowpass", fs=SR, output="sos")
        x = 0.85 * sosfilt(sos, x) + 0.15 * x
    if n in ("riser", "swell", "whoosh"):
        x = x / (np.abs(x).max() + 1e-9) * 0.7                       # these came out clipping
    buf[n] = x

CUES = []
for t in (25.17, 34.38, 37.38, 43.00, 45.64, 48.44, 60.80, 63.00, 67.50, 78.73, 81.74):
    CUES.append(("ink_swish", t, 0))
for t, g in ((27.83, 0), (29.27, -5), (35.26, 0), (39.48, -2), (44.44, 0), (45.70, 0), (46.42, -5), (62.36, 0), (65.70, 0)):
    CUES.append(("hit", t, g))
for t in (31.73, 32.63, 40.76, 80.23):
    CUES.append(("stamp", t, 0))
CUES += [("stamp", 33.43, 2), ("boom", 33.43, -6), ("lockon", 26.43, 0), ("shimmer", 28.83, 0), ("swell", 35.30, 0),
         ("drip", 61.10, 0), ("boom", 84.84, 0), ("riser", 84.84, 0)]
for t in (45.30, 60.72, 62.80, 78.55):
    CUES.append(("whoosh", t + 0.16, 0))
for t in (27.31, 82.68, 83.56, 84.16):
    CUES.append(("pop", t, -3 if t > 80 else 0))
for t in (37.50,):
    CUES.append(("tick", t, 0))
for te in (49.46, 50.36, 51.96, 53.06, 54.46, 55.66, 57.02, 57.69, 58.96, 60.62,
           68.46, 69.30, 70.28, 71.08, 72.04, 72.72, 73.47, 74.16, 75.09, 76.47, 77.52, 78.47):
    CUES.append(("tick", te, 0))

sfx = np.zeros(N)
for n, t, g in CUES:
    pk, base = SFX[n]
    x = buf[n] * 10 ** ((base + g) / 20)
    a = int(round((t - pk) * SR))
    if a < 0:
        x = x[-a:]; a = 0
    b = min(N, a + len(x))
    if t < T_MEME:                                       # nothing leaks into the meme
        b = min(b, int(T_MEME * SR))
    sfx[a:b] += x[:b - a]
json.dump([dict(sfx=n, t=t, gain=g) for n, t, g in sorted(CUES, key=lambda c: c[1])], open("work/sfx_cues.json", "w"),
          indent=0)

# ---- music, ducked under the voice (keyed from the voice before any gain), stops dead on the impact
mus = load(f"assets/el/music_{MUS}.mp3")
mus = np.pad(mus, (0, max(0, N - len(mus))))[:N]
key = voice.copy()
key[int(T_MEME * SR):] = 0
hop = 480
env = np.array([np.sqrt(np.mean(key[i:i + hop] ** 2) + 1e-12) for i in range(0, N, hop)])
act = (20 * np.log10(env) > -38).astype(float)
duck = np.zeros_like(act)
g = 0.0
for i, a in enumerate(act):                              # attack about 50 ms, release about 350 ms
    g = g + (a - g) * (0.2 if a > g else 0.03)
    duck[i] = g
duck_db = -10.5 * duck
gain = np.repeat(10 ** (duck_db / 20), hop)[:N]
MUS_DB = -5.0
m = mus * gain * 10 ** (MUS_DB / 20)
m[:int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))
s = int(T_STOP * SR)
m[s:] = 0
m[s - 240:s] *= np.linspace(1, 0, 240)

mix = voice + m + sfx
sf.write("work/audio/_stem_music.wav", m, SR, subtype="FLOAT"); sf.write("work/audio/_stem_sfx.wav", sfx, SR, subtype="FLOAT")
st = np.stack([mix, mix], 1)
sf.write("work/audio/_premix.wav", st, SR, subtype="FLOAT")
# loudness: measure, gain to -14 LUFS, true-peak limit at -1 dB
o = subprocess.run(["ffmpeg", "-nostats", "-i", "work/audio/_premix.wav", "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
I = float([l for l in o.splitlines() if l.strip().startswith("I:")][-1].split()[1])
gdb = -14.0 - I
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "work/audio/_premix.wav", "-af",
                f"volume={gdb:.2f}dB,alimiter=limit=0.89:attack=1:release=50:level=disabled", "-ar", str(SR),
                "-c:a", "pcm_s24le", f"work/audio/mix_{VER}.wav"], check=True)
print(f"music {MUS}, premix {I:.1f} LUFS, gain {gdb:+.1f} dB -> work/audio/mix_{VER}.wav, {len(CUES)} sfx cues")
