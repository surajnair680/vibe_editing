"""reel-14 v3 mix -> work/audio/mix_v3.wav. Voice (her clip + his isolated voice, approved rough cut) + paper sound
design, NO music (his note). His note on sound: nothing may pierce the ears, so every effect is low-passed
(2.4 to 3.5 kHz), kept well under the voice, and the loudest hits are soft thuds, not clicks or cracks.
Run from the project folder: python3 work/build3/mix3.py"""
import os, sys, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
from scipy.ndimage import minimum_filter1d, uniform_filter1d
sys.argv = [sys.argv[0]]
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/work/build3")
import scene3
s = scene3.s
SR = 48000
LEN = scene3.LEN
N = int(round(LEN * SR)) + int(0.6 * SR)


def load(path, ch=2):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).astype(float)
    return a.reshape(-1, ch)


def db(x): return 10 ** (x / 20)


voice = load("work/audio/rough_v1.wav", 1)[:, 0]
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]

V = "assets/sfx/openverse/vox/"
LIB = {k: load(V + k + ".wav") for k in ("paper-01", "paper-02", "paper-03", "thud-03", "marker-01", "swoosh-01", "swoosh-02")}
LIB["boom"] = load("assets/sfx/openverse/boom.wav")
# each sound: (low-pass Hz, base gain dB) chosen so none is bright or sharp
TONE = {"paper-01": (3200, -6), "paper-02": (3200, -6), "paper-03": (3000, -4), "thud-03": (2400, -16),
        "marker-01": (3500, 12), "swoosh-01": (2600, -10), "swoosh-02": (2600, -12), "boom": (2200, -10)}
PEAK = {}
for k, x in LIB.items():
    lp, g = TONE[k]
    x = sosfiltfilt(butter(4, lp, "lowpass", fs=SR, output="sos"), x, axis=0) * db(g)
    LIB[k] = x
    env = np.convolve(np.abs(x).mean(1), np.ones(240) / 240, "same")
    PEAK[k] = int(np.argmax(env))

sfx = np.zeros((N, 2))
_rot = [0]


def put(t, name, gdb=0.0):
    if name == "paper":                         # rotate the three paper flips so no landing repeats the last one
        name = ("paper-01", "paper-02", "paper-03")[_rot[0] % 3]; _rot[0] += 1
    x = LIB[name] * db(gdb)
    a = int(round(t * SR)) - PEAK[name]
    a0 = max(0, a); x = x[a0 - a:]
    n = min(len(x), N - a0)
    if n > 0: sfx[a0:a0 + n] += x[:n]


E = []
def ev(t, name, g=0.0): E.append((t, name, g))

HIS = scene3.HIS
ev(HIS, "swoosh-01", -2)                                           # into his take
ev(s("Normal", 27.4) + .3, "paper", -4); ev(s("Normal", 27.4) + .45, "paper")
P = scene3
ev(P.P_MIRROR[0] + .17, "paper"); ev(P.P_MIRROR[0] + .75, "marker-01", -4)
TD = max(s("drinks", 30.63), P.P_MIRROR[1] + .25)
ev(TD, "paper"); ev(TD + .45, "marker-01")
ev(s("pizza", 32.17), "paper"); ev(s("pizza", 32.17) + .3, "thud-03")
ev(s("tonight", 33.79), "paper")
for w, n in (("tonight", 33.79), ("obsessed", 35.37), ("abnormal", 36.23)): ev(s(w, n) + .12, "paper-03", -6)
ev(s("Is", 37.27), "paper"); ev(s("wrong", 38.25), "paper", -6); ev(s("yes", 39.64) + .12, "marker-01")
for tw in scene3.WIPES: ev(tw, "swoosh-02")
ev(s("You", 40.25) + .4, "marker-01", -6); ev(s("You", 40.25) + .7, "paper", -4); ev(s("normal", 40.73) + .3, "thud-03", -4)
ev(s("Success", 42.62) + .1, "paper"); ev(s("abnormal", 43.34) + .2, "marker-01", -4); ev(s("by", 43.98), "paper")
ev(s("Successful", 44.89) - .1, "marker-01", -6)
ev(s("outliers", 46.03), "paper"); ev(s("outliers", 46.03) + .25, "paper"); ev(s("outliers", 46.03) + .45, "thud-03", -3)
ev(s("Which", 48.95) + .25, "paper")
for w, n in (("except", 50.01), ("comes", 50.63), ("price", 51.11)): ev(s(w, n), "paper-03", -6)
ev(s("people", 51.85), "thud-03", -4)
ev(P.P_PAIN[0] + .17, "paper"); ev(P.P_PULL[0] + .17, "paper")
ev(P.P_PULL[1] + .2, "paper", -4); ev(s("tolerate", 56.15), "thud-03", -6)
ev(s("balance", 57.42) - .1, "paper")
ev(scene3.SEC_CREAM[0], "swoosh-01", -4); ev(s("everybody", 61.36), "paper"); ev(s("no", 64.28) + .05, "thud-03")
for w, n in (("class", 65.71), ("everybody", 66.49), ("A", 67.33)): ev(s(w, n), "paper")
ev(s("nothing", 68.34) + .2, "marker-01")
ev(s("balance", 69.15) + .05, "swoosh-02", 2); ev(s("balance", 69.15) + .1, "boom", -2)   # the scale tears
ev(s("need", 69.91) + .06, "thud-03", -6)
ev(s("problem", 71.99) - .1, "swoosh-01", -4)
ev(73.3, "paper")
ev(P.P_INCL[0] + .17, "paper"); ev(s("keep", 76.19), "paper", -4)
ev(s("That", 76.87) + .1, "paper"); ev(P.P_FLEX[0] + .17, "paper")
ev(P.P_FLEX[1] + .15, "paper"); ev(P.P_DUMB[0] + .17, "paper")
ev(s("comfort", 87.28) - 2.2, "paper"); ev(s("comfort", 87.28) - 2.0, "paper", -4)
ev(P.P_OUT[0] + .17, "paper")
for k in range(5): ev(P.P_OUT[1] + .05 + k * .15 + .05, "paper-03", -7)
ev(max(s("judging", 90.45) + .05, P.P_OUT[1] + .7) + .05, "thud-03", -4)
ev(s("people", 91.73), "paper"); ev(s("don't", 92.11) + .35, "marker-01")
ev(s("They", 93.41) + .1, "swoosh-02", -6)
for w, n in (("Crazy", 94.24), ("boring", 95.02), ("obsessed", 95.50)):
    ev(s(w, n), "paper"); ev(s(w, n) + .2, "thud-03", -8)
ev(s("whatever", 96.09) + .1, "paper"); ev(s("mediocrity", 98.41) + .2, "marker-01", -4)
ev(P.P_FRONT[0] + .17, "paper"); ev(s("normal", 101.01), "boom", 0)                   # the final YOU.
for t, name, g in scene3.SFX: ev(t, "paper-02", -8)                                         # circle jumps
for t, name, g in E: put(t, name, g)

# ---------------------------------------------------------------- music (his pick, 2026-11-24): Jake Chudnow, "Turquoise",
# from 0:00 (even under her clip), ducked under every voice, about 18 dB under the voice while someone talks.
# The track's own build lands near 41 s, right after the wipe into "You are not normal" (40.25).
MUSIC = load("assets/music/turquoise.mp3")[:N]
MUSIC = np.pad(MUSIC, ((0, N - len(MUSIC)), (0, 0)))
_sos = butter(4, [200, 4000], "bandpass", fs=SR, output="sos")
_e = np.abs(sosfiltfilt(_sos, voice))
hop = SR // 100
_env = np.array([_e[i:i + hop].mean() for i in range(0, len(_e), hop)])
_thr = np.percentile(_env[_env > 0], 40)
talk = (_env > _thr * 0.6).astype(float)
from scipy.ndimage import maximum_filter1d
talk = maximum_filter1d(talk, 25)                      # hold 250 ms so the music doesn't pump between words
duck = np.zeros_like(talk); g = 0.0
for i, v in enumerate(talk):                           # attack 60 ms, release 400 ms
    k = 1 - np.exp(-1 / (6 if v > g else 40)); g += (v - g) * k; duck[i] = g
def speech_rms_(x):
    hh = SR // 20; f = np.sqrt((x[:len(x) // hh * hh].reshape(-1, hh) ** 2).mean(1)); return np.sqrt(np.mean(f[f > np.percentile(f, 50)] ** 2))
m_rms = np.sqrt(np.mean(MUSIC[int(30 * SR):int(100 * SR)] ** 2))
under = speech_rms_(voice) * db(-18) / m_rms           # level while talking
gaps = under * db(6)                                   # level in pauses
gcurve = gaps + (under - gaps) * np.interp(np.arange(N) / SR, np.arange(len(duck)) / 100, duck)
MUSIC = MUSIC * gcurve[:, None]
fi = int(0.4 * SR); MUSIC[:fi] *= np.linspace(0, 1, fi)[:, None]
a0 = int(s("normal", 101.01) * SR); MUSIC[a0:] *= np.linspace(1, 0, N - a0)[:, None] ** 2   # fade out under the final YOU.
sfx *= db(-3)                                        # one more step down: soft under the voice
mix = np.stack([voice, voice], 1) + sfx + MUSIC
def speech_rms(x):
    hh = SR // 20; f = np.sqrt((x[:len(x) // hh * hh].reshape(-1, hh) ** 2).mean(1)); return np.sqrt(np.mean(f[f > np.percentile(f, 50)] ** 2))
G = db(-14.5) / speech_rms(voice)
mix *= G
lim = db(-1.5); w = int(0.005 * SR)
gr = np.minimum(1.0, lim / (np.abs(mix).max(1) + 1e-12))
gr = uniform_filter1d(minimum_filter1d(gr, 2 * w + 1), w)
mix = np.clip(mix * gr[:, None], -lim, lim)
os.makedirs("work/audio", exist_ok=True)
sf.write("work/audio/mix_v5.wav", mix, SR, subtype="PCM_24")
sf.write("work/audio/_stem3_music.wav", MUSIC * G, SR, subtype="PCM_16")
sf.write("work/audio/_stem3_sfx.wav", sfx * G, SR, subtype="PCM_16")
# report: loudest effect vs the voice, and brightness of the effects
def pk(x): return 20 * np.log10(np.abs(x).max() + 1e-12)
spec = np.abs(np.fft.rfft(sfx[:, 0] * G)); fr = np.fft.rfftfreq(len(sfx), 1 / SR)
hi = 10 * np.log10(spec[fr > 4000].__pow__(2).sum() / spec.__pow__(2).sum())
m_under = MUSIC[(np.interp(np.arange(N) / SR, np.arange(len(talk)) / 100, talk) > .5)]
print("music under speech vs voice speech rms (dB):", round(20 * np.log10(np.sqrt(np.mean(m_under ** 2)) / speech_rms(voice)), 1))
print(f"{len(E)} effects | voice peak {pk(voice * G):.1f} dBFS | sfx peak {pk(sfx * G):.1f} dBFS | "
      f"energy above 4 kHz {hi:.1f} dB | mix peak {pk(mix):.1f} dBFS")
