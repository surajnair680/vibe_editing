"""Line up the ElevenLabs isolated voice (assets/el/voice_isolated.mp3, sent from full.wav at 0 s) with
work/audio/full.wav. Band-passed RMS envelopes (300-3000 Hz, 1 ms hop) in 4 s windows give a lag per window;
a linear fit of lag over time (offset + drift) is applied by resampling (lesson from reel-06).
Writes work/audio/full_iso.wav: same length as full.wav, isolated voice aligned (copied from reel-12)."""
import subprocess
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, correlate
SR = 48000; T0 = 0.0
src, _ = sf.read("work/audio/full.wav")
iso = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", "assets/el/voice_isolated.mp3", "-ac", "1", "-ar",
                                    str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).astype(float)
ref = src[int(T0 * SR):]
sos = butter(4, [300, 3000], "bandpass", fs=SR, output="sos")
def env(x):
    y = sosfiltfilt(sos, x) ** 2; h = SR // 1000
    return np.sqrt(y[:len(y) // h * h].reshape(-1, h).mean(1))
er, ei = env(ref), env(iso)
lags, ts = [], []
for s in range(0, min(len(er), len(ei)) - 4000, 2000):
    a, b = er[s:s + 4000], ei[s:s + 4000]
    if a.std() < 1e-4: continue
    c = correlate(b - b.mean(), a - a.mean(), "full"); k = np.argmax(c) - 3999
    if abs(k) < 60: lags.append(k / 1000); ts.append((s + 2000) / 1000)
lags, ts = np.array(lags), np.array(ts)
p = np.polyfit(ts, lags, 1)
print("windows", len(ts), "lag ms: offset %.2f, drift %.4f ms/s, spread %.2f ms" % (p[1] * 1000, p[0] * 1000, np.std(lags - np.polyval(p, ts)) * 1000))
# iso time = ref time + lag(t)  ->  sample iso at t + polyval(p, t)
t = np.arange(len(ref)) / SR
out = np.interp(t + np.polyval(p, t), np.arange(len(iso)) / SR, iso, left=0, right=0)
full = np.zeros_like(src); full[int(T0 * SR):] = out
sf.write("work/audio/full_iso.wav", full, SR, subtype="FLOAT")
# check after
e2 = env(out); res = []
for s in range(0, len(er) - 4000, 8000):
    a, b = er[s:s + 4000], e2[s:s + 4000]
    if a.std() < 1e-4: continue
    c = correlate(b - b.mean(), a - a.mean(), "full"); res.append(np.argmax(c) - 3999)
print("after: lags ms", res)
