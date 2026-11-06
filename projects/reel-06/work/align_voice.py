"""Align the ElevenLabs isolated voice to the original mix with a time-varying (linear) offset.
Envelope cross-correlation (300-3000 Hz) in 4 s windows; fit lag(t); resample. Writes work/audio/voice_aligned.wav."""
import soundfile as sf, numpy as np
from scipy.signal import correlate, butter, sosfiltfilt
o, sr = sf.read('work/audio/full.wav'); o = o.mean(1)
v, _ = sf.read('work/audio/voice_iso.wav'); v = v if v.ndim == 1 else v.mean(1)
sos = butter(4, [300, 3000], 'bandpass', fs=sr, output='sos')
D = 11; r = sr/D
def env(x):
    e = np.abs(sosfiltfilt(sos, x)); return np.sqrt(np.convolve(e**2, np.ones(44)/44, 'same'))[::D]
eo, ev = env(o), env(v)
def lag(sig, t, w=4, M=1200):
    a = eo[int(t*r):int((t+w)*r)]; b = sig[int(t*r)-M:int((t+w)*r)+M]; a = a-a.mean(); b = b-b.mean()
    return (np.argmax(correlate(b, a, 'valid'))-M)/r    # sig[t+lag] ~ orig[t]
ts = np.arange(19.5, 60, 2.0); ls = np.array([lag(ev, t) for t in ts]) ; tc = ts+2
k, c = np.polyfit(tc, ls, 1); print('raw lag ms', np.round(ls*1000, 2)); print(f'fit lag(t) = {c*1000:.2f} ms + {k*1e6:.1f} us/s * t')
t = np.arange(len(o))/sr; src = t + (c + k*t)
va = np.interp(src*sr, np.arange(len(v)), v, left=0, right=0)
sf.write('work/audio/voice_aligned.wav', va.astype(np.float32), sr)
ev2 = env(va); print('check ms', [round(lag(ev2, t)*1000, 2) for t in [20, 30, 40, 50, 59]])
