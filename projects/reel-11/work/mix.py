"""reel-11 mix: voice (rough cut v2 audio) on top, 8-bit music ducked under every word, game SFX, -14 LUFS.

Music runs from 0:00 (user: "so that the vibe is established from the start"), quieter under her voice and his.
Ducking is keyed from the voice envelope (fast attack, slow release). The lead gets an extra dip under speech so the
melody never fights the words. Final: -14 LUFS integrated, peaks under -1.5 dBFS (look-ahead limiter).
Usage: python3 work/mix.py [out.wav]   -> work/audio/mix_v1.wav
"""
import sys
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.ndimage import maximum_filter1d, uniform_filter1d

SR = 48000
DUR = 49.9
N = int(DUR * SR)
OUT = sys.argv[1] if len(sys.argv) > 1 else "work/audio/mix_v1.wav"


def load(p):
    x, sr = sf.read(p, dtype="float64")
    assert sr == SR, p
    if x.ndim > 1:
        x = x.mean(1)
    return np.pad(x, (0, max(0, N - len(x))))[:N]


db = lambda v: 10 ** (v / 20)
meter = pyln.Meter(SR)

voice = load("work/audio/rough_v2.wav")
# her clip (0 to 12.867) was recorded about 6 dB quieter than his takes: +5 dB, 20 ms ramp at the cut
hg = np.ones(N)
c = int(12.867 * SR)
hg[:c] = db(5)
hg[c - 960:c] = np.linspace(db(5), 1, 960)
voice = voice * hg
lead, arp, bass, drums = (load(f"work/audio/music_{k}.wav") for k in ("lead", "arp", "bass", "drums"))
sfx = load("work/audio/sfx_chip.wav")

# speech key: 20 ms RMS of the voice, gate at noise floor + 12 dB, 15 ms attack / 300 ms release
rms = np.sqrt(uniform_filter1d(voice ** 2, int(0.02 * SR)) + 1e-12)
lv = 20 * np.log10(rms)
floor = np.percentile(lv, 15)
gate = (lv > floor + 12).astype(float)
gate = maximum_filter1d(gate, int(0.12 * SR))                     # hold over short gaps between words
att, rel = 1 - np.exp(-1 / (0.015 * SR)), 1 - np.exp(-1 / (0.30 * SR))
key = np.zeros(N)
k = 0.0
step = 48                                                           # smooth at 1 ms resolution, then upsample
g_ds = gate[::step]
k_ds = np.zeros_like(g_ds)
a2, r2 = 1 - np.exp(-step / (0.015 * SR)), 1 - np.exp(-step / (0.30 * SR))
for i, g in enumerate(g_ds):
    k += (g - k) * (a2 if g > k else r2)
    k_ds[i] = k
key = np.interp(np.arange(N), np.arange(len(k_ds)) * step, k_ds)

L_voice = meter.integrated_loudness(voice)
music = lead + arp + bass + drums
L_music = meter.integrated_loudness(music)
m_gain = db(L_voice - 7 - L_music)                                  # bed sits 7 dB under the voice level in gaps
duck = db(-10 * key)                                                # -10 dB under speech
lead_duck = db(-5 * key)                                            # lead dips a further 5 dB
music_mix = ((lead * lead_duck) + arp + bass + drums) * m_gain * duck
sfx_mix = sfx * m_gain * 1.6                                        # game blips just above the bed
mix = voice + music_mix + sfx_mix

L = meter.integrated_loudness(mix)
mix *= db(-14 - L)
# look-ahead limiter to -1.5 dBFS
ceil = db(-1.5)
look = int(0.005 * SR)
pk = maximum_filter1d(np.abs(mix), 2 * look + 1)
g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
g = uniform_filter1d(g, look)
mix *= g
sf.write(OUT, mix.astype(np.float32), SR, subtype="FLOAT")
print(f"voice {L_voice:.1f} LUFS, music raw {L_music:.1f}, final {meter.integrated_loudness(mix):.1f} LUFS, "
      f"peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS")
