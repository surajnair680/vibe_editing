"""reel-10 visual hook: red scribble head on black, his clip in a wide box, breakout on the drop.

Music: The Box guitar remix starts at SONG_IN = 13.0 s, so the 808 drop (17.45 s in the song)
lands at DROP = 4.45 s edit time. The box cuts pull-up -> flex one bar (2.23 s) before.

    python3 work/hook/hook.py stills          -> out/hook_test/stills/*.png
    python3 work/hook/hook.py draft           -> out/hook_test/hook_draft.mp4 (540x960 + music)
"""
import cv2, numpy as np, subprocess, sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOK = os.path.join(ROOT, "work", "hook")
OUT = os.path.join(ROOT, "out", "hook_test")
W, H, FPS = 1080, 1920, 30
SONG_IN = 13.0
DROP = 17.45 - SONG_IN                 # 4.45
BAR = 4 * 60 / 107.66
CUT = DROP - BAR                       # 2.22: pull-up -> flex inside the box
BREAK = 0.30                           # box -> full frame, seconds
END = DROP + 1.2                       # test length
BOX = (120, 729, 890, 1125)            # x0, y0, x1, y1 (reference layout scaled to 1080)
BEAT = 60 / 107.66
# flash band hits during the pose, on the beats before the drop (first 0.56 s of the pose stays clean)
FLASH_BEATS = [DROP - 3 * BEAT, DROP - 2 * BEAT, DROP - BEAT]
FLASH = os.environ.get("FLASH", "strobe")   # "sweep" (diagonal light band) or "strobe" (horizontal bands)
GRAIN = float(os.environ.get("GRAIN", "0.06"))

# (file, source start, crop x0, y0, x1, y1 in the decoded frame, or None = cover the target)
SEG_A = ("raw/c_part2.mp4", 4.25 - 0.0, (0, 560, 1080, 1115))       # close pull-up, back band
SEG_B = ("raw/d_part1.mp4", 9.85, (0, 0, 1920, 988))                # front flex (horizontal clip)
SEG_C = ("raw/c_part3.mp4", 2.30, None)                             # full-screen close pull-up


def read_frames(path, start, dur):
    """Decode dur seconds from start (picture seek is frame accurate enough), auto-rotated."""
    p = os.path.join(ROOT, path)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                            "stream=width,height:stream_side_data=rotation", "-of", "csv=p=0", p],
                           capture_output=True, text=True).stdout.split()
    vals = [v for v in ",".join(probe).split(",") if v]
    w, h = int(vals[0]), int(vals[1])
    rot = vals[2] if len(vals) > 2 else ""
    if rot in ("-90", "90", "270", "-270"):
        w, h = h, w
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", p, "-t", f"{dur:.3f}",
                          "-r", str(FPS), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, h, w, 3)


def cover(img, tw, th):
    h, w = img.shape[:2]
    s = max(tw / w, th / h)
    r = cv2.resize(img, (max(tw, round(w * s)), max(th, round(h * s))), interpolation=cv2.INTER_AREA)
    y0 = (r.shape[0] - th) // 2; x0 = (r.shape[1] - tw) // 2
    return r[y0:y0 + th, x0:x0 + tw]


def flash_band(img, t):
    """Flash band on the pose: on each beat in FLASH_BEATS.
    sweep: a warm white diagonal band crosses the box in 0.26 s, with a quick exposure pop.
    strobe: 3 to 5 bright horizontal bands flicker for 4 frames (on, off, on, fade)."""
    hit = [b for b in FLASH_BEATS if 0 <= t - b < 0.4]
    if not hit:
        return img
    dt = t - hit[0]
    h, w = img.shape[:2]
    f = img.astype(np.float32) / 255.0
    warm = np.float32([0.86, 0.95, 1.0])            # BGR, slightly warm white
    if FLASH == "sweep":
        pop = 0.30 * np.exp(-dt / 0.07)              # photo-flash exposure pop
        f = f * (1 + pop) + pop * 0.25
        k = dt / 0.26
        if k <= 1.15:
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            u = xx + (yy - h / 2) * np.tan(np.radians(22))     # distance across a tilted band
            c = -160 + (w + 320) * k
            band = np.exp(-((u - c) / 70.0) ** 2) * 0.85 + np.exp(-((u - c) / 22.0) ** 2) * 0.6
            f = f + band[..., None] * warm
    else:
        n = int(dt * FPS)
        if n in (0, 2, 3):
            rng = np.random.default_rng(int(hit[0] * 1000) + (n > 1))
            m = np.zeros((h, 1), np.float32)
            for _ in range(int(rng.integers(3, 6))):
                y = int(rng.integers(0, h)); bh = int(rng.integers(14, 70))
                m[max(0, y - bh // 2): y + bh // 2] = rng.uniform(0.55, 1.0)
            m = cv2.GaussianBlur(m, (1, 0), sigmaX=0.1, sigmaY=4)
            a = 1.0 if n != 3 else 0.45
            f = f * (1 + 0.22 * a) + m[..., None] * warm * a
    return np.clip(f * 255.0, 0, 255).astype(np.uint8)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


class Hook:
    def __init__(self):
        sys.path.insert(0, os.path.join(ROOT, "work"))
        from look import Grain
        self.grain = Grain(W, H, strength=GRAIN)
        self.bg = [cv2.imread(os.path.join(HOOK, f"bg_v{v}.png")) for v in range(3)]
        self.A = read_frames(SEG_A[0], SEG_A[1], CUT + 0.1)
        self.B = read_frames(SEG_B[0], SEG_B[1], DROP - CUT + 0.1)
        self.C = read_frames(SEG_C[0], SEG_C[1], END - DROP + 0.1)

    def clip(self, seg, frames, i):
        f = frames[min(i, len(frames) - 1)]
        c = seg[2]
        return f[c[1]:c[3], c[0]:c[2]] if c else f

    def frame(self, t):
        return self.grain(self._frame(t), int(round(t * FPS)))

    def _frame(self, t):
        n = int(round(t * FPS))
        if t < DROP:
            # whole composition drifts in slowly so it moves from frame 0
            img = self.bg[(n // 15) % 3].copy()
            x0, y0, x1, y1 = BOX
            if t < CUT:
                src = self.clip(SEG_A, self.A, n)
            else:
                src = self.clip(SEG_B, self.B, n - int(round(CUT * FPS)))
            box = cover(src, x1 - x0, y1 - y0)
            if t >= CUT:
                box = flash_band(box, t)
            img[y0:y1, x0:x1] = box
            z = 1.0 + 0.045 * (t / DROP)
            M = cv2.getRotationMatrix2D((W / 2, (y0 + y1) / 2), 0, z)
            return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR)
        # breakout: the box grows to the full frame, the scribble head falls away behind it
        k = ease_out((t - DROP) / BREAK)
        z0 = 1.045
        bx = [(v - W / 2) * z0 + W / 2 if i % 2 == 0 else (v - (BOX[1] + BOX[3]) / 2) * z0 + (BOX[1] + BOX[3]) / 2
              for i, v in enumerate(BOX)]
        x0 = bx[0] * (1 - k); y0 = bx[1] * (1 - k)
        x1 = bx[2] + (W - bx[2]) * k; y1 = bx[3] + (H - bx[3]) * k
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        bg = (self.bg[(n // 15) % 3] * (1 - k)).astype(np.uint8)
        src = self.C[min(n - int(round(DROP * FPS)), len(self.C) - 1)]
        # the full shot slightly over-zoomed while expanding, settling to 1.0
        full = cover(src, W, H)
        zz = 1.0 + 0.08 * (1 - k)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, zz)
        full = cv2.warpAffine(full, M, (W, H))
        img = bg.copy()
        img[y0:y1, x0:x1] = full[y0:y1, x0:x1]
        # 2-frame flash on the drop
        fl = max(0.0, 1 - (t - DROP) / (2 / FPS)) * 0.35
        if fl > 0:
            img = cv2.addWeighted(img, 1 - fl, np.full_like(img, 255), fl, 0)
        return img


def stills(h):
    d = os.path.join(OUT, "stills"); os.makedirs(d, exist_ok=True)
    for t in (0.0, 1.0, 2.0, 2.5, 2.85, 2.9, 3.0, 3.4, 3.5, 3.95, 4.3, 4.5, 4.6, 4.8, 5.5):
        cv2.imwrite(os.path.join(d, f"t_{t:04.2f}.png"), h.frame(t))


def draft(h, scale=0.5):
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "hook_pic.mp4")
    w, hh = int(W * scale), int(H * scale)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{hh}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", tmp],
                         stdin=subprocess.PIPE)
    for n in range(int(END * FPS)):
        p.stdin.write(cv2.resize(h.frame(n / FPS), (w, hh), interpolation=cv2.INTER_AREA).tobytes())
    p.stdin.close(); p.wait()
    wav = os.path.join(ROOT, "work", "audio", "thebox.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ss", f"{SONG_IN}", "-t", f"{END}", "-i", wav,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-af", f"afade=t=out:st={END - 0.4}:d=0.4", os.path.join(OUT, f"hook_draft_{FLASH}.mp4")], check=True)
    os.remove(tmp)


if __name__ == "__main__":
    h = Hook()
    for a in sys.argv[1:] or ["stills"]:
        {"stills": stills, "draft": draft}[a](h)
    print("ok")
