"""Splice re-rendered ranges into the previous picture master, then report which frames changed.

python3 work/splice.py work/picture_v1.mp4 work/picture_v3.mp4 0:work/seg_v3_0.mp4 10:work/seg_v3_10.mp4 ...
Each segment replaces the frames from its start second for its own length. SSIM-like check per frame
(mean abs diff on a 270x480 copy) lists the changed ranges so only the intended seconds differ.
"""
import subprocess, sys
import numpy as np, cv2
W, H, FPS = 1080, 1920, 30
src, dst, specs = sys.argv[1], sys.argv[2], sys.argv[3:]

def frames(p):
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)

seg = {}
for s in specs:
    t, p = s.split(":", 1); f0 = round(float(t) * FPS)
    for i, fr in enumerate(frames(p)): seg[f0 + i] = fr
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", dst],
                       stdin=subprocess.PIPE)
changed = []
for n, fr in enumerate(frames(src)):
    new = seg.get(n, fr)
    d = cv2.absdiff(cv2.resize(new, (270, 480)), cv2.resize(fr, (270, 480))).mean()
    if d > 1.5: changed.append(n)
    enc.stdin.write(new.tobytes())
enc.stdin.close(); enc.wait()
rng = []
for n in changed:
    if rng and n == rng[-1][1] + 1: rng[-1][1] = n
    else: rng.append([n, n])
print("changed frame ranges (s):", [(round(a / FPS, 2), round(b / FPS, 2)) for a, b in rng])
