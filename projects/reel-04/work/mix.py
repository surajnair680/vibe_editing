"""reel-04 sound mix: music (muffled in the breath), quiet real room sound, designed SFX.

python3 work/mix.py  ->  work/mix_v1.wav   (48 kHz stereo, master about -14 LUFS, peak <= -1.5 dB)
Room sound per shot is cut from WAV decoded from the start of each clip (never seeking MP4 AAC).
SFX are placed so their peak (or their abrupt end, for risers/swells) lands on the frame.
"""
import os, sys, subprocess, json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import timeline as T

SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else "work/mix_v2.wav"
L = int(round(T.length() * SR)) + SR  # one second of tail room, trimmed at mux
def sec(t): return int(round(t * SR))

def load(p):
    y, sr = sf.read(p); assert sr == SR, p
    return y if y.ndim == 2 else np.repeat(y[:, None], 2, 1)

def wav(clip):
    p = f"work/audio/{clip}.wav"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"raw/{clip}.mp4", "-vn", "-ar", str(SR), "-ac", "2", p], check=True)
    return load(p)

def env(n, a, b, fade):  # 0..1 gate between a and b (seconds) with fades
    t = np.arange(n) / SR
    return np.clip(np.minimum((t - a) / fade + 1, (b - t) / fade + 1), 0, 1)

# ---- music: full track, low-passed (muffled) during the breath
m = load("work/audio/m3_moody.wav")
m = np.pad(m, ((0, max(0, L - len(m))), (0, 0)))[:L]
sos = butter(4, 520, "low", fs=SR, output="sos")
muff = sosfiltfilt(sos, m, axis=0) * 1.35
g = env(L, 18.17 - 0.0, 23.37, 0.45)[:, None]        # muffle from the breath start, open up into the exit
music = m * (1 - g) + muff * g

# ---- real room sound, per shot gain (keys and bottle up close, the rest low)
ROOM_GAIN = {"x4": 0.55, "x2": 0.8, "x3": 0.2}
room = np.zeros((L, 2))
for i, s in enumerate(T.shots()):
    y = wav(s["clip"]); a0 = sec(s["src_in"]); n_out = sec(s["frames"] / T.FPS)
    seg = y[a0:a0 + sec(s["src_dur"])]
    if s["speed"] != 1:
        seg = seg[np.linspace(0, len(seg) - 1, n_out).astype(int)]
    seg = np.pad(seg, ((0, max(0, n_out - len(seg))), (0, 0)))[:n_out].copy()
    f = min(len(seg) // 2, sec(0.012)); r = np.linspace(0, 1, f)[:, None]
    seg[:f] *= r; seg[-f:] *= r[::-1]
    gain = ROOM_GAIN.get(s["clip"], 0.3)
    if i == 8: gain = 0.45                         # the drink
    st = sec(s["start"]); room[st:st + len(seg)] += seg * gain
room *= 1 - 0.5 * env(L, 28.57, 40, 0.05)[:, None]  # quieter on the empty-room ending

# ---- designed SFX: (file, edit time, anchor in file (s) that lands on the edit time, gain)
y_t = load("work/audio/sfx/ticks.wav"); tick = y_t[sec(1.36):sec(1.48)].copy()
tick[-sec(0.02):] *= np.linspace(1, 0, sec(0.02))[:, None]
CUES = [
    ("open_whoosh",   0.00, 0.22, 0.55),   # starts with the snap pull-out
    ("riser_build",  10.37, 2.36, 0.45),   # its abrupt end lands on the drop
    ("sub_hit",      10.37, 0.12, 0.95),   # the drop: cut to the hands
    ("TICK",         11.67, 0.01, 0.75),   # dashboard
    ("swish_a",      12.30, 0.20, 0.40),   # over the shoulder
    ("TICK",         12.97, 0.01, 0.6),    # hands, tight
    ("TICK",         13.60, 0.01, 0.75),   # tooltip
    ("reverse_swell", 18.17, 2.18, 0.55),  # sucks into the breath
    ("swish_b",      26.45, 0.38, 0.55),   # standing up, body passes the lens
    ("riser_exit",   28.57, 1.94, 0.40),   # builds into the empty room
    ("end_boom",     28.57, 0.06, 1.6),    # low hit on the empty chair
]
# v2 note "risers too harsh, ear piercing": warm them up (low-pass the piercing 3 to 10 kHz) and a touch quieter.
SOFTEN = {"riser_build": (2200, 0.75), "riser_exit": (2600, 0.7), "reverse_swell": (3200, 0.8)}
def soften(y, cutoff, g):
    lo = sosfiltfilt(butter(4, cutoff, "low", fs=SR, output="sos"), y, axis=0)
    return (0.85 * lo + 0.15 * y) * g      # keep a hint of air so it doesn't sound underwater
sfx = np.zeros((L, 2)); log = []
for name, t, anchor, gain in CUES:
    y = tick if name == "TICK" else load(f"work/audio/sfx/{name}.wav")
    if name in SOFTEN: y = soften(y, *SOFTEN[name])
    st = sec(t - anchor)
    if st < 0: y = y[-st:]; st = 0
    n = min(len(y), L - st); sfx[st:st + n] += y[:n] * gain
    log.append(dict(sfx=name, edit_time=t, anchor=anchor, gain=gain))
json.dump(log, open("work/sfx_cues.json", "w"), indent=1)

mix = 0.85 * music + room + 0.8 * sfx
end = T.length(); fo = sec(1.5)
mix[sec(end) - fo:sec(end)] *= np.linspace(1, 0, fo)[:, None]; mix[sec(end):] = 0
mix = mix[:sec(end)]
sf.write("work/mix_pre.wav", mix.astype(np.float32), SR, subtype="FLOAT")

# loudness: measure with ffmpeg ebur128, set gain to -14 LUFS, then keep peaks under -1.5 dB
r = subprocess.run(["ffmpeg", "-nostats", "-i", "work/mix_pre.wav", "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
I = float([l for l in r.splitlines() if l.strip().startswith("I:")][-1].split()[1])
gain = 10 ** ((-14 - I) / 20)
gain = 10 ** (0.7 / 20)   # v2+: master gain fixed to the approved v1 (+0.7 dB), never re-normalised
mix = mix * gain
pk = np.abs(mix).max(); lim = 10 ** (-1.5 / 20)
if pk > lim:  # soft knee on the few loud peaks only
    a = np.abs(mix); k = lim * 0.8
    mix = np.sign(mix) * np.where(a > k, k + (lim - k) * np.tanh((a - k) / (lim - k)), a)
sf.write(OUT, mix.astype(np.float32), SR, subtype="FLOAT")
print(f"integrated {I:.1f} LUFS -> gain {20*np.log10(gain):+.1f} dB, peak before limit {20*np.log10(pk):.1f} dB")
