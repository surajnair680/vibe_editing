"""measure generated sounds (Claude can't listen): length, peak time, attack, tail, brightness, share above 3 kHz"""
import sys, subprocess, glob, os
import numpy as np
SR = 48000
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                        capture_output=True).stdout, np.float32)
for f in sorted(glob.glob("assets/el/*.mp3")):
    n = os.path.basename(f)[:-4]
    if n.startswith("music"):
        continue
    x = load(f)
    hop = 480
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(env)
    pk = int(np.argmax(env))
    on = int(np.argmax(db > db[pk] - 20))
    tail = len(db) - 1 - int(np.argmax(db[::-1] > db[pk] - 30))
    X = np.abs(np.fft.rfft(x)); fr = np.fft.rfftfreq(len(x), 1 / SR)
    cen = (X * fr).sum() / X.sum(); hi = X[fr > 3000].sum() / X.sum()
    print(f"{n:10s} len {len(x)/SR:4.2f}s  peak {pk*hop/SR:4.2f}s ({20*np.log10(np.abs(x).max()+1e-9):5.1f} dBFS)  "
          f"onset {on*hop/SR:4.2f}s attack {(pk-on)*hop/SR*1000:4.0f}ms  end {tail*hop/SR:4.2f}s  centroid {cen:5.0f}Hz  >3k {hi:4.0%}")
