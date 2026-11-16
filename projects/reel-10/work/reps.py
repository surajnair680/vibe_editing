"""Find rep tops/bottoms from vertical motion (optical flow integrated over time).
python3 work/reps.py raw/part2.mp4 [x0 x1 y0 y1 as fractions]"""
import cv2, numpy as np, sys, subprocess
from scipy.signal import find_peaks
p = sys.argv[1]
fx0, fx1, fy0, fy1 = [float(v) for v in sys.argv[2:6]] if len(sys.argv) > 5 else (0.2, 0.8, 0.1, 0.7)
cap = cv2.VideoCapture(p); prev = None; vy = []
while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (f.shape[1] // 6, f.shape[0] // 6)), cv2.COLOR_BGR2GRAY)
    if prev is not None:
        fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        h, w = g.shape
        r = fl[int(fy0*h):int(fy1*h), int(fx0*w):int(fx1*w), 1]
        mag = np.abs(r); m = mag > 0.3
        vy.append(r[m].mean() if m.sum() > 20 else 0.0)
    else:
        vy.append(0.0)
    prev = g
y = np.cumsum(vy); y = y - np.convolve(y, np.ones(91)/91, mode='same')  # remove drift
fps = 30
tops, _ = find_peaks(-y, distance=18, prominence=2)
bots, _ = find_peaks(y, distance=18, prominence=2)
print(p, "frames", len(y))
print(" tops (highest):", " ".join(f"{i/fps:.2f}" for i in tops))
print(" bottoms:", " ".join(f"{i/fps:.2f}" for i in bots))
