"""reel-04 picture builder: cut from timeline.py + digital camera moves (and later the grade).

python3 work/build.py --w 540 --start 0 --end 10.37 --out out/motion_test.mp4
Frames are decoded at full 1080x1920 (one ffmpeg input per shot), moved with an affine
warp about an anchor point, optional zoom blur on fast moves, then scaled to --w.
"""
import argparse, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import timeline as T

SW, SH = 1080, 1920

def ease_out(u, p=3): return 1 - (1 - u) ** p
def ease_in(u, p=2): return u ** p
def smooth(u): return u * u * (3 - 2 * u)

# Camera moves per shot index: f(u in 0..1, t seconds into shot) -> (zoom, ax, ay, dx, dy, blur)
# ax, ay = zoom anchor (fraction of frame); dx, dy = pan (fraction of frame).
def move_open(u, t):           # shot 1: snap pull-out from 1.30 onto the desk, then slow drift
    if t < 1.0:
        k = ease_out(t / 1.0)
        z = 1.30 + (1.08 - 1.30) * k
        blur = (1 - k) * 0.9
    else:
        k = (t - 1.0) / 2.87
        z = 1.08 - 0.04 * smooth(min(k, 1)); blur = 0
    return z, 0.42, 0.26, 0, 0, blur

def move_slide(u, t):          # shot 2: lateral slide past the door frame (parallax feel)
    return 1.12, 0.5, 0.45, -0.035 + 0.07 * smooth(u), 0, 0

def move_push(u, t):           # shot 3: push in, accelerating into the drop at 10.37
    return 1.0 + 0.13 * ease_in(u, 2.2), 0.42, 0.40, 0, 0, max(0, (u - 0.85) / 0.15) * 0.35

MOVES = {0: move_open, 1: move_slide, 2: move_push}

def warp(img, z, ax, ay, dx, dy):
    cx, cy = ax * SW, ay * SH
    M = np.array([[z, 0, cx - z * cx + dx * SW], [0, z, cy - z * cy + dy * SH]], np.float32)
    # keep the frame covered: clamp translation so no border shows
    M[0, 2] = min(0, max(SW - z * SW, M[0, 2])); M[1, 2] = min(0, max(SH - z * SH, M[1, 2]))
    return cv2.warpAffine(img, M, (SW, SH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def frame_out(img, mv, u, t, dt):
    z, ax, ay, dx, dy, blur = mv(u, t)
    if blur > 0.02:   # zoom blur: average sub-steps along the move (shutter of about one frame)
        z2 = mv(min(1, u + dt), t + dt * 1)[0]
        acc = np.zeros(img.shape, np.float32); n = 6
        for i in range(n):
            zz = z + (z2 - z) * blur * 4 * (i / (n - 1) - 0.5)
            acc += warp(img, zz, ax, ay, dx, dy)
        return (acc / n).astype(np.uint8)
    return warp(img, z, ax, ay, dx, dy)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=1080); ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float, default=None); ap.add_argument("--out", default="work/picture.mp4")
    ap.add_argument("--crf", type=int, default=20)
    a = ap.parse_args()
    end = a.end or T.length(); W = a.w; H = W * 16 // 9
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(T.FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "veryfast", "-crf", str(a.crf), "-pix_fmt", "yuv420p", a.out],
                           stdin=subprocess.PIPE)
    for i, s in enumerate(T.shots()):
        if s["end"] <= a.start + 1e-6 or s["start"] >= end - 1e-6: continue
        f0 = max(0, round((a.start - s["start"]) * T.FPS)); f1 = min(s["frames"], round((end - s["start"]) * T.FPS))
        vf = (f"setpts=PTS/{s['speed']}," if s["speed"] != 1 else "") + f"fps={T.FPS},scale={SW}:{SH}"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{s['src_in']:.3f}", "-t", f"{s['src_dur'] + 0.5:.3f}",
                                "-i", f"raw/{s['clip']}.mp4", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE)
        mv = MOVES.get(i); n = s["frames"]
        for f in range(f1):
            buf = dec.stdout.read(SW * SH * 3)
            if len(buf) < SW * SH * 3:
                img = last
            else:
                img = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3); last = img
            if f < f0: continue
            u = f / max(1, n - 1); t = f / T.FPS
            out = frame_out(img, mv, u, t, 1 / max(1, n - 1)) if mv else img
            if W != SW: out = cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)
            enc.stdin.write(out.tobytes())
        dec.kill()
        print(f"shot {i+1} done", flush=True)
    enc.stdin.close(); enc.wait()

if __name__ == "__main__":
    main()
