"""reel-14 mix -> work/audio/mix_<ver>.wav (+ stems _stem_voice/_stem_music/_stem_sfx.wav for level checks).
Voice: work/audio/rough_v1.wav (her clip + his isolated voice, approved rough cut).
Music: assets/el/music_a.mp3 (ElevenLabs, 150 BPM harpsichord / pizzicato / clock). Its own break (silence at
52.4-53.8 s, swell, re-entry onset at 55.254 s) is moved so the re-entry lands on "Screw" (68.83): the first 48
beats (19.17 s) are repeated in front (whole 12-bar block, cut on the beat grid) and playback starts 5.59 s into
that, so music runs from 0:00. It fades out after "mediocrity"; the ending line has no music, then the final hit.
Ducked under the voice (keyed from the voice envelope). SFX (Openverse, real recordings): metal hit on every card
(pitch rising through the reel), boom on SCREW and the final card, shield bash on the struck-out BALANCE, shutter
on photos. Run from the project folder: python3 work/mix.py v1"""
import sys, json, subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt
sys.path.insert(0, "work/build")
import scene

VER = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "v1"
SR = 48000
LEN = scene.LEN
N = int(round(LEN * SR)) + int(0.6 * SR)       # 0.6 s tail after the last frame for the final hit ring (cut at mux)


def load(path, ch=2):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                                     capture_output=True).stdout, np.float32).astype(float)
    return a.reshape(-1, ch)


def db(x): return 10 ** (x / 20)


# ---------------------------------------------------------------- voice
voice = load("work/audio/rough_v1.wav", 1)[:, 0]
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
V = np.stack([voice, voice], 1)

# ---------------------------------------------------------------- music: re-arranged so the break lands before "Screw"
m = load("assets/el/music_a.mp3")
BEAT = 0.3993; PRE = int(round(48 * BEAT * SR))
xf = int(0.02 * SR)
pre = m[:PRE].copy()
joined = np.concatenate([pre[:-xf], pre[-xf:] * np.linspace(1, 0, xf)[:, None] + m[:xf] * np.linspace(0, 1, xf)[:, None], m[xf:]])
RE_TRACK = 55.254; SCREW = scene.s("Screw", 68.8)
skip = int(round((PRE / SR + RE_TRACK - SCREW) * SR))
music = joined[skip:skip + N]
music = np.pad(music, ((0, N - len(music)), (0, 0)))
fi = int(1.5 * SR); music[:fi] *= np.linspace(0, 1, fi)[:, None]
# out after "mediocrity": fade 0.35 s from the end of that word
t_out = scene.wd("mediocrity", 98.4)["e"] + 0.05
a = int(t_out * SR); b = a + int(0.35 * SR)
music[a:b] *= np.linspace(1, 0, b - a)[:, None]; music[b:] = 0
print("music skip %.3f s, re-entry at %.3f, out at %.2f" % (skip / SR, SCREW, t_out))

# ducking keyed from the voice: band 200-4000 Hz envelope, 15 ms attack / 300 ms release / 120 ms hold
sos = butter(4, [200, 4000], "bandpass", fs=SR, output="sos")
env = np.abs(sosfiltfilt(sos, voice))
h = int(0.01 * SR); e10 = np.sqrt(np.convolve(env ** 2, np.ones(h) / h, "same"))[::h]
thr = db(-38)
key = (e10 > thr).astype(float)
hold = 12
k2 = key.copy()
for i in range(len(key)):
    if key[i]: k2[i:i + hold] = 1
g = np.zeros_like(k2); att, rel = 1 - np.exp(-1 / 1.5), 1 - np.exp(-1 / 30)
for i in range(1, len(k2)):
    c = att if k2[i] > g[i - 1] else rel
    g[i] = g[i - 1] + c * (k2[i] - g[i - 1])
DUCK = -7.0
gain = db(DUCK * np.interp(np.arange(N) / SR, np.arange(len(g)) * 0.01, g))
# level riding: the track builds about 16 dB from start to end; hold it about 18 dB under the voice while he
# talks (lesson reel-12: measure stems), rising gently from -40 to -37 dBFS under speech by the big hit
L = np.sqrt(np.convolve(music.mean(1) ** 2, np.ones(3 * SR) / (3 * SR), "same")) + 1e-9
L = 20 * np.log10(L)
tt = np.arange(N) / SR
T = np.interp(tt, [0, 27.3, 68.8, 100], [-37, -37, -34, -34])
MG = np.clip(T - DUCK - L, -30, 10)
sm = SR // 2; MG = np.convolve(MG, np.ones(sm) / sm, "same")
music = music * gain[:, None] * db(MG)[:, None]

# ---------------------------------------------------------------- SFX
SFX = {k: load(f"assets/sfx/openverse/{k}.wav") for k in ("metal_hit", "boom", "shield_bash", "shutter")}
PEAK = {"metal_hit": 0.01, "boom": 0.29, "shield_bash": 0.16, "shutter": 0.10}
sfx = np.zeros((N, 2))


def pitch(x, semis):
    if abs(semis) < 0.01: return x
    r = 2 ** (semis / 12); n = int(len(x) / r)
    idx = np.arange(n) * r
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1)


def place(name, t, gdb, semis=0.0, lp=None):
    x = pitch(SFX[name], semis) * db(gdb)
    if lp:
        x = sosfiltfilt(butter(2, lp, "lowpass", fs=SR, output="sos"), x, axis=0)
    a = int(round((t - PEAK[name] / (2 ** (semis / 12))) * SR))
    a0 = max(0, a); x = x[a0 - a:]
    n = min(len(x), N - a0)
    sfx[a0:a0 + n] += x[:n]


cards = sorted([e for e in scene.EV if e[0] in ("card", "outliers", "slit")], key=lambda e: e[1])
n_c = len(cards)
for i, (k, f0, f1, p) in enumerate(cards):
    t = f0 / scene.FPS
    w = p.get("word", "")
    if k == "card" and w == "SCR|EW":
        place("boom", t, -4); place("metal_hit", t, -6, -5)
    elif k == "card" and w == "BALANCE" and p.get("strike"):
        place("shield_bash", t, -8)
    elif k == "card" and f1 - f0 > 50:          # the final NORMAL card
        place("boom", t, -2); place("metal_hit", t, -5, -3)
    else:
        place("metal_hit", t, -15 + 3 * i / n_c, -4 + 6 * i / n_c, lp=6500)
for k, f0, f1, p in scene.EV:
    if k == "photo" and f1 - f0 >= 15:
        place("shutter", f0 / scene.FPS, -6)

# ---------------------------------------------------------------- master
if "--no-music" in sys.argv:          # user note on v1: "Don't add music yet"
    music[:] = 0
mix = V + music + sfx
pk = np.abs(mix).max()
# fixed gain to about -14 LUFS-ish: scale so speech RMS (voice stem) sits at -18 dBFS, then soft limit at -1.5 dBFS
def speech_rms(x):
    hh = SR // 20; f = np.sqrt((x[:len(x) // hh * hh].reshape(-1, hh) ** 2).mean(1)); return np.sqrt(np.mean(f[f > np.percentile(f, 50)] ** 2))
G = db(-14.5) / speech_rms(voice)
mix *= G
# look-ahead peak limiter to -1.5 dBFS (5 ms window, gain never above what the peak needs)
from scipy.ndimage import minimum_filter1d, uniform_filter1d
lim = db(-1.5); w = int(0.005 * SR)
gr = np.minimum(1.0, lim / (np.abs(mix).max(1) + 1e-12))
gr = uniform_filter1d(minimum_filter1d(gr, 2 * w + 1), w)
mix = mix * gr[:, None]
mix = np.clip(mix, -lim, lim)
sf.write(f"work/audio/mix_{VER}.wav", mix, SR, subtype="PCM_24")
for nm, x in (("voice", V * G), ("music", music * G), ("sfx", sfx * G)):
    sf.write(f"work/audio/_stem_{nm}.wav", x, SR, subtype="PCM_16")
# report: music vs voice under speech, by section
def rms(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
mk = np.interp(np.arange(N) / SR, np.arange(len(k2)) * 0.01, k2) > 0.5
for a, b, nm in ((0, 27.3, "her clip"), (27.3, 52, "his take A"), (52, 68.7, "his take B"), (68.7, 98.9, "his take C")):
    sl = slice(int(a * SR), int(b * SR)); sp = mk[sl]
    print(f"{nm:11s} voice {rms(V[sl][sp, 0] * G):6.1f}  music under speech {rms(music[sl][sp, 0] * G):6.1f}  "
          f"music in gaps {rms(music[sl][~sp, 0] * G) if (~sp).any() else float('nan'):6.1f}")
print("peak dBFS", round(20 * np.log10(np.abs(mix).max()), 2))
