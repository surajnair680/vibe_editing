"""reel-06 YouTube mix: new music under the grandma section, new bed under the talking.

python3 work/mix.py <song a|b> <bed a|b> <out.wav>
Edit time = time in the joined original (raw/full.mov, 64.283 s).
Layers:
  0 .. SONG_END      new song (replaces the Bollywood track), level matched to the original section
  voice              ElevenLabs isolated voice (aligned, +1.5 dB, +1.5 dB shelf above 4 kHz) from 18.8 s
  bed                new subtle beat under the talking, about 26 dB under the voice
  KEEP ranges        original mix kept where it carries only a sound effect (whoosh 33.1 s, explosion 63.0 s)
"""
import sys, numpy as np, soundfile as sf, librosa
from scipy.signal import butter, sosfilt
SR = 44100
song, bed, out = sys.argv[1:4]
orig, _ = sf.read('work/audio/full.wav'); N = len(orig)          # stereo
voice, _ = sf.read('work/audio/voice_aligned.wav')               # mono, aligned to orig
def load(fn):
    y, _ = librosa.load(fn, sr=SR, mono=False)
    return y.T if y.ndim == 2 else np.stack([y, y], 1)
def rms_db(x): return 20*np.log10(np.sqrt(np.mean(x**2)) + 1e-12)
def ramp(n): return 0.5 - 0.5*np.cos(np.linspace(0, np.pi, n))
def place(dst, src, t_edit, t_src, dur, fin=0.0, fout=0.0, gain=1.0):
    a, s, n = int(t_edit*SR), int(t_src*SR), int(dur*SR)
    seg = src[s:s+n].copy(); n = len(seg)
    env = np.ones(n)
    if fin:  k = int(fin*SR);  env[:k] *= ramp(k)
    if fout: k = int(fout*SR); env[n-k:] *= ramp(k)[::-1]
    dst[a:a+n] += seg*env[:, None]*gain

SONG_END = 18.83          # last downbeat before the cut to the talking (18.88)
mus = np.zeros_like(orig)
if song == 'b':           # 126.6 BPM; drop 7.757 s lands on the original drop (~7.93 s)
    S = load('assets/music/song_b.mp3'); off = 0.17
    place(mus, S, off, 0.0, SONG_END + 0.25 - off, fin=0.01, fout=0.25)
else:                     # held note intro, groove starts 8.017 s -> on the cut to the Hyrox shots (3.93 s)
    S = load('assets/music/song_a.mp3'); off = 8.017 - 3.93
    place(mus, S, 0.0, off, SONG_END + 0.25, fin=0.3, fout=0.25)
# level match: same RMS as the original song section (0.8 .. 17.5 s)
a, b = int(0.8*SR), int(17.5*SR)
mus *= 10**((rms_db(orig[a:b]) - rms_db(mus[a:b]))/20)

# voice: +1.5 dB, presence shelf (+1.5 dB above ~4 kHz), only from 18.8 s
v = voice.copy()
hp = sosfilt(butter(2, 4000, 'highpass', fs=SR, output='sos'), v)
v = (v + hp*(10**(1.5/20) - 1))*10**(1.5/20)
venv = np.zeros(N); k = int(18.8*SR); venv[k:] = 1; venv[k:k+441] = ramp(441)
vo = np.stack([v, v], 1)*venv[:, None]

# bed
bd = np.zeros_like(orig)
if bed == 'b':
    B = load('assets/music/bed_b.mp3'); place(bd, B, 18.88, 0.0, 63.2 - 18.88, fin=0.6, fout=0.4)
else:
    B = load('assets/music/bed_a.mp3'); place(bd, B, 19.3, 0.0, 43.4, fin=0.4, fout=0.3)
a, b = int(19.4*SR), int(62.0*SR)
bd *= 10**((rms_db(vo[a:b]) - 26 - rms_db(bd[a:b]))/20)

from scipy.ndimage import maximum_filter1d, uniform_filter1d
def limit(x, ceil=10**(-1/20), look=0.005, rel=0.08):
    """Look-ahead peak limiter, sample-peak ceiling -1 dB."""
    p = maximum_filter1d(np.abs(x).max(1), int(2*look*SR) + 1)
    g = np.minimum(1.0, ceil/np.maximum(p, 1e-9))
    out = np.empty_like(g); a = np.exp(-1/(rel*SR)); cur = 1.0
    for i, gi in enumerate(g):
        cur = gi if gi < cur else a*cur + (1-a)*gi; out[i] = cur
    out = np.minimum(uniform_filter1d(out, int(look*SR)), g)
    return x*out[:, None]
def build(talk_gain):
    m = mus + (vo + bd)*talk_gain
    # keep the original sound effects (voice is silent there; the old bed is ~25 dB under the effect)
    for t0, t1 in [(33.10, 33.56), (62.98, N/SR)]:
        a, b = int(t0*SR), min(int(t1*SR), N); f = 441
        w = np.zeros(N); w[a:b] = 1; w[a:a+f] = ramp(f)
        if b < N: w[b-f:b] = ramp(f)[::-1]
        m = m*(1 - w[:, None]) + orig*w[:, None]
    return limit(m)
# make-up gain on voice + bed so the talking is as loud as the original after limiting; the song keeps its level
a, b = int(20*SR), int(62*SR); g = 1.0
for _ in range(4):
    mix = build(g); g *= 10**((rms_db(orig[a:b]) - rms_db(mix[a:b]))/20)
mix = build(g)
sf.write(out, mix.astype(np.float32), SR, subtype='PCM_24')
print(out, 'peak', round(20*np.log10(np.abs(mix).max()), 2), 'dB', 'song', round(rms_db(mix[:int(18*SR)]), 1),
      'talk', round(rms_db(mix[int(20*SR):int(62*SR)]), 1), 'orig talk', round(rms_db(orig[int(20*SR):int(62*SR)]), 1))
