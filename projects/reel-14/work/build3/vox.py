"""reel-14 v3: dark Vox collage primitives (numpy / cv2 / PIL), 1080x1920 RGB uint8 frames.

Look (docs/playbook/brand/MOTION.md + .claude/skills/vox-explainer): torn bone paper with a white fibre edge and a
soft shadow, halftone, red marker, title-red highlighter, stamps, motion stepped on twos. Codex cut-outs get a torn
white paper margin. His photos and clips are pinned as torn prints, never recoloured.
"""
import functools, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
ROOT = "/home/user/vibe_editing/projects/reel-14/"
BONE = (237, 231, 225)
CREAM = (226, 216, 196)
INK = (22, 18, 18)
RED = (158, 26, 43)       # title red
MARK = (190, 22, 30)      # marker red, a touch brighter so it reads on paper
F_TITLE = ROOT + "fonts/BebasNeue-400.ttf"
F_CAP = ROOT + "fonts/Inter-600.ttf"
F_MONO = ROOT + "fonts/JetBrainsMono-700.ttf"


@functools.lru_cache(maxsize=64)
def font(path, size):
    return ImageFont.truetype(path, size)


def twos(t):
    return math.floor(t * 12 + 1e-6) / 12


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def span(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0)


# ------------------------------------------------------------------ torn shapes
def torn_mask(w, h, seed, rough=8, pad=30):
    """alpha mask (h+2pad, w+2pad) of a torn rectangle; same seed = same paper every frame."""
    r = np.random.default_rng(seed)
    pts = []
    def edge(x0, y0, x1, y1, nx, ny):
        n = max(4, int(math.hypot(x1 - x0, y1 - y0) / 12))
        for i in range(n):
            f = i / n
            j = (r.random() - .5) * rough + ((r.random() - .5) * rough * 1.8 if r.random() < .12 else 0)
            pts.append((pad + x0 + (x1 - x0) * f + nx * j, pad + y0 + (y1 - y0) * f + ny * j))
    edge(0, 0, w, 0, 0, 1); edge(w, 0, w, h, -1, 0); edge(w, h, 0, h, 0, -1); edge(0, h, 0, 0, 1, 0)
    m = np.zeros((h + 2 * pad, w + 2 * pad), np.uint8)
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)
    return m


def paste(img, rgba, cx, cy, rot=0.0, scale=1.0, shadow=0.45):
    """alpha-composite an RGBA layer centred at (cx, cy) with rotation (degrees), scale and a soft drop shadow."""
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += cx - w / 2; M[1, 2] += cy - h / 2
    lay = cv2.warpAffine(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = lay[..., 3:4].astype(np.float32) / 255
    out = img.astype(np.float32)
    if shadow:
        sh = cv2.GaussianBlur(lay[..., 3], (0, 0), 14)
        sh = cv2.warpAffine(sh, np.float32([[1, 0, 10], [0, 1, 16]]), (W, H)).astype(np.float32) / 255
        out *= 1 - sh[..., None] * shadow
    out = out * (1 - a) + lay[..., :3].astype(np.float32) * a
    return np.clip(out, 0, 255).astype(np.uint8)


def halftone(w, h, cell=14, rad=3.0, alpha=60):
    t = np.zeros((h, w), np.uint8)
    for y in range(cell // 2, h, cell):
        for x in range(cell // 2 + (y // cell % 2) * cell // 2, w, cell):
            cv2.circle(t, (x, y), int(rad), alpha, -1, cv2.LINE_AA)
    return t


def paper_sheet(w, h, color, seed, rough=8, tone=True, draw=None):
    """torn paper RGBA: white fibre fringe, colour body, faint halftone and paper mottling; draw(pil, ox, oy) adds ink."""
    pad = 30
    outer = torn_mask(w + 12, h + 12, seed + 7, rough * 1.2, pad - 6)
    inner = torn_mask(w, h, seed, rough, pad)
    H2, W2 = inner.shape
    rgb = np.zeros((H2, W2, 3), np.float32)
    rgb[:] = (252, 249, 241)
    a_in = inner.astype(np.float32)[..., None] / 255
    rgb = rgb * (1 - a_in) + np.array(color, np.float32) * a_in
    if tone:
        r = np.random.default_rng(seed)
        mott = cv2.GaussianBlur(r.normal(0, 1, (H2 // 8 + 1, W2 // 8 + 1)).astype(np.float32), (0, 0), 2)
        mott = cv2.resize(mott, (W2, H2))[..., None] * 5
        rgb = rgb + mott * a_in
        ht = halftone(W2, H2).astype(np.float32)[..., None] / 255 * 0.35
        rgb = rgb * (1 - ht * a_in)
    pil = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    if draw:
        draw(pil, pad, pad)
    out = np.dstack([np.asarray(pil), np.maximum(outer, inner)])
    return out


@functools.lru_cache(maxsize=128)
def strip(text, size, bg=BONE, fg=INK, seed=1, font_path=F_TITLE, padx=34, pady=14):
    f = font(font_path, size)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + padx * 2, bb[3] - bb[1] + pady * 2
    def ink(pil, ox, oy):
        ImageDraw.Draw(pil).text((ox + padx - bb[0], oy + pady - bb[1]), text, font=f, fill=fg)
    return paper_sheet(w, h, bg, seed, rough=6, draw=ink)


# ------------------------------------------------------------------ cut-outs
@functools.lru_cache(maxsize=32)
def cutout(path, height, margin=16, seed=3):
    """Codex object on white -> RGBA with a torn white paper margin (rembg isnet when present, else white key)."""
    im = Image.open(path).convert("RGB")
    cache = path + ".alpha.png"
    if os.path.exists(cache):
        a = np.asarray(Image.open(cache).convert("L"))
    else:
        try:
            from rembg import remove, new_session
            a = np.asarray(remove(im, session=new_session("isnet-general-use"), only_mask=True).convert("L"))
        except Exception:
            g = np.asarray(im.convert("L")).astype(np.int16)
            a = np.where(g < 238, 255, 0).astype(np.uint8)
        Image.fromarray(a).save(cache)
    s = height / im.height
    w = int(im.width * s)
    rgb = cv2.resize(np.asarray(im), (w, height), interpolation=cv2.INTER_AREA)
    a = cv2.resize(a, (w, height), interpolation=cv2.INTER_AREA)
    pad = margin * 3
    rgb = cv2.copyMakeBorder(rgb, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    a = cv2.copyMakeBorder(a, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    # torn white margin: dilate, then roughen the edge with low-frequency noise
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (margin * 2 + 1, margin * 2 + 1))
    m = cv2.dilate((a > 100).astype(np.uint8) * 255, k)
    r = np.random.default_rng(seed)
    n = cv2.resize(r.random((m.shape[0] // 6 + 1, m.shape[1] // 6 + 1)).astype(np.float32), (m.shape[1], m.shape[0]))
    dist = cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 3)
    m = np.where(dist > n * 9, 255, 0).astype(np.uint8)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    paper = np.full_like(rgb, (250, 247, 240))
    af = a.astype(np.float32)[..., None] / 255
    out = (rgb.astype(np.float32) * af + paper * (1 - af)).astype(np.uint8)
    return np.dstack([out, m])


@functools.lru_cache(maxsize=16)
def _blank_print(w, h, seed):
    return paper_sheet(w, h, (250, 247, 240), seed, rough=6, tone=False)


def print_frame(rgb, width, seed=5, border=18):
    """his photo / clip frame as a torn print: the picture untouched inside a white torn border."""
    h = int(rgb.shape[0] * width / rgb.shape[1])
    pic = cv2.resize(rgb, (width, h), interpolation=cv2.INTER_AREA)
    sheet = _blank_print(width + border * 2, h + border * 2, seed).copy()
    pad = 30
    sheet[pad + border:pad + border + h, pad + border:pad + border + width, :3] = pic
    return sheet


# ------------------------------------------------------------------ ink marks
def marker_x(img, cx, cy, size, p, seed=1, width=16):
    """two marker strokes drawn on in order; p 0..1."""
    out = img.copy()
    r = np.random.default_rng(seed)
    for k, (a, b) in enumerate([((-1, -1), (1, 1)), ((1, -1), (-1, 1))]):
        q = min(max(p * 2 - k, 0), 1)
        if q <= 0: continue
        n = 24
        pts = []
        for i in range(int(n * q) + 1):
            f = i / n
            pts.append((cx + size * (a[0] + (b[0] - a[0]) * f) / 2 + r.normal(0, 1.5),
                        cy + size * (a[1] + (b[1] - a[1]) * f) / 2 + r.normal(0, 1.5) + 10 * math.sin(f * 3)))
        cv2.polylines(out, [np.array(pts, np.int32)], False, MARK, width, cv2.LINE_AA)
    return out


def marker_circle(img, cx, cy, rx, ry, p, seed=1, width=12):
    out = img.copy()
    r = np.random.default_rng(seed)
    n = 90
    pts = []
    for i in range(int(n * 1.08 * p) + 1):
        a = -math.pi * .62 + i / n * math.pi * 2
        j = r.normal(0, 2)
        pts.append((cx + math.cos(a) * (rx + j), cy + math.sin(a) * (ry + j)))
    if len(pts) > 1:
        cv2.polylines(out, [np.array(pts, np.int32)], False, MARK, width, cv2.LINE_AA)
    return out


@functools.lru_cache(maxsize=32)
def stamp(text, size, color=MARK, seed=2, rot=-8):
    """rubber stamp: rough-edged red letters in a box, slightly worn."""
    f = font(F_TITLE, size)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 40
    pil = Image.new("L", (w + 20, h + 20), 0)
    d = ImageDraw.Draw(pil)
    d.rectangle((10, 10, w + 10, h + 10), outline=255, width=10)
    d.text((40 - bb[0], 30 - bb[1]), text, font=f, fill=255)
    a = np.asarray(pil).astype(np.float32)
    r = np.random.default_rng(seed)
    wear = cv2.resize(r.random((a.shape[0] // 3 + 1, a.shape[1] // 3 + 1)).astype(np.float32), (a.shape[1], a.shape[0]))
    a = np.where(wear > 0.22, a * 0.92, a * 0.25).astype(np.uint8)
    rgb = np.zeros((*a.shape, 3), np.uint8); rgb[:] = color
    return np.dstack([rgb, a])
