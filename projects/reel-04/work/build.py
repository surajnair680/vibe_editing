"""reel-04 picture builder: cut from timeline.py + digital camera moves (and later the grade).

python3 work/build.py --w 540 --start 0 --end 10.37 --out out/motion_test.mp4
Frames are decoded at full 1080x1920 (one ffmpeg input per shot), moved with an affine
warp about an anchor point, optional zoom blur on fast moves, then scaled to --w.
"""
import argparse, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import timeline as T
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlays as OV

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

def push(z0, z1, ax=0.5, ay=0.45, fn=smooth):
    return lambda u, t: (z0 + (z1 - z0) * fn(u), ax, ay, 0, 0, 0)

def move_drop(u, t):           # shot 4: impact punch on the drop, 1.10 -> 1.0 in 0.25 s, then a slow creep
    if t < 0.25:
        k = ease_out(t / 0.25); return 1.10 - 0.10 * k, 0.45, 0.55, 0, 0, (1 - k) * 0.6
    return 1.0 + 0.03 * smooth((t - 0.25) / 1.05), 0.45, 0.55, 0, 0, 0

MOVES = {0: move_open, 1: move_slide, 2: move_push, 3: move_drop,
         4: push(1.00, 1.05, 0.4, 0.5), 5: push(1.04, 1.00, 0.5, 0.4), 6: push(1.12, 1.17, 0.45, 0.55),
         7: push(1.00, 1.05, 0.55, 0.5), 8: push(1.00, 1.04, 0.7, 0.35), 9: push(1.05, 1.00, 0.4, 0.6),
         10: push(1.06, 1.11, 0.45, 0.6),
         11: push(1.00, 1.10, 0.42, 0.28),               # breath: slow push on the wide
         12: push(1.00, 1.08, 0.4, 0.55),                # hands lift off
         13: push(1.00, 1.04, 0.5, 0.4),                 # stand up
         15: push(1.00, 1.08, 0.48, 0.30, ease_out)}     # empty chair

# ---------------------------------------------------------------- the look (moody, warm highlights)
LEVELS = {}   # per clip black/white point, measured once on a mid frame, applied half strength
def clip_levels(clip):
    if clip not in LEVELS:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "5", "-i", f"raw/{clip}.mp4", "-frames:v", "1",
                            "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           capture_output=True).stdout
        if len(r) < 270 * 480 * 3:
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", f"raw/{clip}.mp4", "-frames:v", "1",
                                "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               capture_output=True).stdout
        L = np.frombuffer(r, np.uint8).reshape(480, 270, 3).astype(float) @ [0.114, 0.587, 0.299]
        lo, hi = np.percentile(L, [1.5, 99.0])
        LEVELS[clip] = (lo * 0.5, 255 - (255 - hi) * 0.5)
    return LEVELS[clip]

def _curve(x, lo, hi):
    x = np.clip((x - lo) / (hi - lo), 0, 1)
    x = x ** 1.12                                            # a touch darker overall (moody)
    s = x + 0.22 * (x - 0.5) * (1 - np.abs(2 * x - 1))       # gentle S for contrast
    s = np.where(s > 0.82, 0.82 + (s - 0.82) * 0.55, s)      # roll off highlights (the window)
    return np.clip(0.035 + s * 0.94, 0, 1)                   # lifted, filmic blacks

LUTS = {}
def clip_lut(clip):
    if clip not in LUTS:
        lo, hi = clip_levels(clip); x = np.arange(256, dtype=np.float32)
        base = _curve(x, lo, hi)
        sh = np.clip(1 - base / 0.45, 0, 1) ** 1.5           # shadow weight
        hl = np.clip((base - 0.5) / 0.5, 0, 1) ** 1.2        # highlight weight
        b = base + 0.030 * sh - 0.045 * hl                   # BGR: teal-ish shadows, warm highlights
        g = base + 0.012 * sh + 0.004 * hl
        r = base - 0.012 * sh + 0.040 * hl
        lut = np.stack([b, g, r], -1)
        LUTS[clip] = np.round(np.clip(lut, 0, 1) * 255).astype(np.uint8).reshape(1, 256, 3)
    return LUTS[clip]

_L = np.array([0.114, 0.587, 0.299], np.float32)
SAT = (0.82 * np.eye(3, dtype=np.float32) + 0.18 * np.tile(_L, (3, 1)))
SAT_M = np.hstack([SAT, np.zeros((3, 1), np.float32)])
_VIG = {}
def look(img, clip, f):
    out = cv2.LUT(img, clip_lut(clip))
    out = cv2.transform(out, SAT_M)
    small = cv2.resize(out, (SW // 4, SH // 4), interpolation=cv2.INTER_AREA)   # halation on highlights
    hlm = cv2.GaussianBlur(np.clip(small.astype(np.int16) - 205, 0, 50).astype(np.uint8), (0, 0), 9)
    glow = cv2.resize(hlm, (SW, SH), interpolation=cv2.INTER_LINEAR)
    out = cv2.add(out, cv2.transform(glow, np.array([[0.3, 0, 0, 0], [0, 0.5, 0, 0], [0, 0, 0.75, 0]], np.float32)))
    if "v" not in _VIG:
        y, x = np.ogrid[-1:1:SH * 1j, -1:1:SW * 1j]
        v = 1 - 0.42 * np.clip(x * x * 0.9 + y * y * 0.55 - 0.18, 0, None)
        _VIG["v"] = np.repeat(np.round(np.clip(v, 0, 1) * 255).astype(np.uint8)[..., None], 3, axis=2)
    out = cv2.multiply(out, _VIG["v"], scale=1 / 255.0)
    return grain(out, f)

_GR = {}
def grain(img, f, amount=0.035, bank=16):
    if not _GR:
        rng = np.random.default_rng(4)
        for k in range(bank):
            n = cv2.GaussianBlur(rng.normal(0, 255 * amount, (SH, SW)).astype(np.float32), (0, 0), 0.7) * 1.6
            n = np.round(n).astype(np.int16)
            _GR[k] = (np.repeat(np.clip(n, 0, 255).astype(np.uint8)[..., None], 3, 2),
                      np.repeat(np.clip(-n, 0, 255).astype(np.uint8)[..., None], 3, 2))
    pos, neg = _GR[f % bank]
    return cv2.subtract(cv2.add(img, pos), neg)

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
    ap.add_argument("--raw", action="store_true", help="no grade (cut + moves only)")
    ap.add_argument("--no-ov", dest="no_ov", action="store_true", help="no overlays (v1/v2 picture)")
    ap.add_argument("--stills", default=None, help="comma list of edit times: save PNGs to out/stills/")
    a = ap.parse_args()
    end = a.end or T.length(); W = a.w; H = W * 16 // 9
    if a.stills:
        return stills([float(x) for x in a.stills.split(",")], a)
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
            if not a.raw: out = look(out, s["clip"], s["start_f"] + f)
            if not a.no_ov: out = OV.apply(out, (s["start_f"] + f) / T.FPS)
            if W != SW: out = cv2.resize(out, (W, H), interpolation=cv2.INTER_AREA)
            enc.stdin.write(out.tobytes())
        dec.kill()
        print(f"shot {i+1} done", flush=True)
    enc.stdin.close(); enc.wait()

def stills(times, a):
    os.makedirs("out/stills", exist_ok=True)
    sh = list(T.shots())
    for tm in times:
        fi = min(round(tm * T.FPS), round(T.length() * T.FPS) - 1)
        i, s = next((i, s) for i, s in enumerate(sh) if s["start_f"] <= fi < s["start_f"] + s["frames"])
        f = fi - s["start_f"]
        src_t = s["src_in"] + f / T.FPS * s["speed"]
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{src_t:.3f}", "-i", f"raw/{s['clip']}.mp4",
                            "-frames:v", "1", "-vf", f"scale={SW}:{SH}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           capture_output=True).stdout
        img = np.frombuffer(r, np.uint8).reshape(SH, SW, 3)
        mv = MOVES.get(i); n = s["frames"]
        out = frame_out(img, mv, f / max(1, n - 1), f / T.FPS, 1 / max(1, n - 1)) if mv else img
        if not a.raw: out = look(out, s["clip"], fi)
        if not a.no_ov: out = OV.apply(out, fi / T.FPS)
        cv2.imwrite(f"out/stills/t{tm:05.2f}.png", out)
        print("still", tm, s["clip"], flush=True)

if __name__ == "__main__":
    main()
