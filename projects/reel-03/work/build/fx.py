"""reel-03 effects: frames are float32 BGR 0..1 at 1080x1920. Everything seeded so re-renders match."""
import functools, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 25
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------- sources ----------
@functools.lru_cache(maxsize=64)
def clip(path, t0, dur, speed=1.0):
    """Frames of path from t0 for dur seconds of EDIT time (source plays at `speed`), resampled to 25 fps."""
    src_dur = dur * speed + 0.2
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{src_dur:.3f}", "-i", path,
           "-vf", f"setpts=PTS/{speed},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    w, h = probe(path)
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)


@functools.lru_cache(maxsize=32)
def probe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.split(",")
    return int(o[0]), int(o[1])


def frame_at(path, t0, dur, tl, speed=1.0):
    fr = clip(path, t0, dur, speed)
    return fr[min(int(round(tl * FPS)), len(fr) - 1)]


@functools.lru_cache(maxsize=32)
def still(path):
    return cv2.imread(path)


def cover(img, zoom=1.0, cx=0.5, cy=0.5, w=W, h=H):
    """Cover-fit img into w x h, zoomed, centred on (cx, cy) of the source. Returns float32 0..1."""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * zoom
    x0 = np.clip(cx * iw * s - w / 2, 0, iw * s - w)
    y0 = np.clip(cy * ih * s - h / 2, 0, ih * s - h)
    M = np.float32([[s, 0, -x0], [0, s, -y0]])
    out = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR if s > 1 else cv2.INTER_AREA,
                         borderMode=cv2.BORDER_REFLECT)
    return out.astype(np.float32) / 255


# ---------- colour ----------
def grade(f, gain=(1, 1, 1), lift=(0, 0, 0), gamma=1.0, sat=1.0, contrast=1.0):
    """gain/lift are B,G,R. sat via luma mix, contrast around 0.5."""
    f = np.maximum(f, 0)
    if sat != 1.0:
        l = f @ np.float32([0.114, 0.587, 0.299])
        f = l[..., None] + (f - l[..., None]) * sat
    if contrast != 1.0:
        f = (f - 0.5) * contrast + 0.5
    f = np.maximum(f, 0) ** gamma
    return f * np.float32(gain) + np.float32(lift)


def luma(f):
    return f @ np.float32([0.114, 0.587, 0.299])


def tint_bw(f, dark, light, gamma=1.0):
    """Map luma to a two-colour ramp (B,G,R)."""
    l = np.clip(luma(f), 0, 1)[..., None] ** gamma
    return np.float32(dark) * (1 - l) + np.float32(light) * l


# ---------- optics ----------
def bloom(f, thr=0.7, sigma=30, amt=0.6):
    hi = np.maximum(f - thr, 0)
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), sigma / 4)
    return f + cv2.resize(small, (W, H)) * amt


def chroma(f, px=4):
    """Lateral chromatic aberration, growing towards the edges."""
    if px <= 0:
        return f
    out = f.copy()
    for c, k in ((2, 1), (0, -1)):
        s = 1 + k * px / W
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
        out[..., c] = cv2.warpAffine(f[..., c], M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out


@functools.lru_cache(maxsize=1)
def _grain_bank():
    rng = np.random.default_rng(11)
    return [cv2.GaussianBlur(rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32), (0, 0), 0.6) for _ in range(12)]


def grain(f, i, amt=0.04):
    g = cv2.resize(_grain_bank()[i % 12], (W, H), interpolation=cv2.INTER_LINEAR)
    return f + g[..., None] * amt


@functools.lru_cache(maxsize=8)
def _vig(strength, power):
    d = np.hypot((XX - W / 2) / (W / 2), (YY - H / 2) / (H / 2)) / np.sqrt(2)
    return (1 - strength * np.clip(d, 0, 1) ** power)[..., None].astype(np.float32)


def vignette(f, strength=0.5, power=2.0):
    return f * _vig(strength, power)


def push(f, k, cx=W / 2, cy=H / 2):
    """Zoom an already-composed frame by k around (cx, cy)."""
    if abs(k - 1) < 1e-4:
        return f
    M = cv2.getRotationMatrix2D((cx, cy), 0, k)
    return cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def glitch(f, i, n=6, amp=40, seed=0):
    """Horizontal slice offsets with a little channel split."""
    rng = np.random.default_rng(seed * 1000 + i)
    out = f.copy()
    for _ in range(n):
        y = rng.integers(0, H - 20); h = int(rng.integers(6, 60)); dx = int(rng.integers(-amp, amp))
        out[y:y + h] = np.roll(f[y:y + h], dx, axis=1)
        out[y:y + h, :, 2] = np.roll(f[y:y + h, :, 2], dx + 8, axis=1)
    return out


def soft_frame(f, inset=0.08, feather=60, bg=(0.02, 0.02, 0.025), scale=None, y_off=0):
    """Picture shrunk into the middle with soft blurred edges on a dark ground (the reference's framed shots)."""
    s = scale if scale else 1 - 2 * inset
    w, h = int(W * s), int(H * s)
    small = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA)
    out = np.empty_like(f); out[:] = np.float32(bg)
    m = np.zeros((H, W), np.float32)
    x0, y0 = (W - w) // 2, (H - h) // 2 + y_off
    out[y0:y0 + h, x0:x0 + w] = small
    m[y0 + feather // 2:y0 + h - feather // 2, x0 + feather // 2:x0 + w - feather // 2] = 1
    m = cv2.GaussianBlur(m, (0, 0), feather / 2.2)[..., None]
    return out * m + np.float32(bg) * (1 - m)


def film_dirt(f, i, amt=1.0, seed=5):
    """Dust specks and a couple of vertical scratches, new every frame."""
    rng = np.random.default_rng(seed * 7919 + i)
    m = np.zeros((H, W), np.float32)
    for _ in range(int(14 * amt)):
        cv2.circle(m, (int(rng.integers(0, W)), int(rng.integers(0, H))), int(rng.integers(1, 4)), 1, -1)
    for _ in range(int(rng.integers(0, 3))):
        x = int(rng.integers(0, W)); cv2.line(m, (x, 0), (x + int(rng.integers(-8, 8)), H), 0.6, 1)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)[..., None]
    return f * (1 - 0.6 * m) + 0.04 * m


def flicker(i, amt=0.05, seed=3):
    return 1 + amt * np.random.default_rng(seed * 31 + i).normal()


# ---------- text ----------
@functools.lru_cache(maxsize=256)
def text_img(s, size):
    font = ImageFont.truetype(FONT, size)
    l, t, r, b = font.getbbox(s)
    pad = 8
    im = Image.new("L", (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), s, font=font, fill=255)
    return np.asarray(im, np.float32) / 255


def size_for_width(s, width):
    font = ImageFont.truetype(FONT, 100)
    l, _, r, _ = font.getbbox(s)
    return int(100 * width / (r - l))


def put_text(f, s, size, color, cy=H * 0.494, cx=W / 2, alpha=1.0, glow=0.0, top_of_x=None):
    """Draw s centred on (cx, cy). color is B,G,R 0..1. Optional soft glow behind."""
    a = text_img(s, size)
    h, w = a.shape
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya:
        return f
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0][..., None] * alpha
    if glow > 0:
        g = cv2.GaussianBlur(sub[..., 0], (0, 0), size * 0.12)[..., None] * glow
        f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - g * 0.5)
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - sub) + np.float32(color) * sub
    return f


def text_mask(s, size, cx=W / 2, cy=H * 0.494):
    a = text_img(s, size)
    h, w = a.shape
    m = np.zeros((H, W), np.float32)
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    m[y0:y0 + h, x0:x0 + w] = a
    return m


def ease(k):
    k = np.clip(k, 0, 1)
    return k * k * (3 - 2 * k)
