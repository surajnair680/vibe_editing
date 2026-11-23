"""reel-14 graphics kit: Text Flash Cuts (Lemo-Opuscar #42) adapted for a talking-head reel.
Cards, captions, photo and clip inserts, red slit. All frames are RGB uint8 numpy arrays 1920x1080.
Deterministic (seeded per frame). Real photos and clips are never recoloured."""
import functools, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
RED, BLACK, PAPER, GREY = (212, 22, 43), (10, 10, 12), (242, 239, 232), (141, 138, 132)
ROOT = "/home/user/vibe_editing/projects/reel-14/"
F_CARD = ROOT + "fonts/NotoSerifDisplay-900.ttf"
F_CAP = ROOT + "fonts/NotoSerif-800.ttf"


@functools.lru_cache(maxsize=64)
def font(path, size):
    return ImageFont.truetype(path, size)


def text_img(word, size, ink, path=F_CARD):
    """tight RGBA image of a word (ink colour) at a given pixel size."""
    f = font(path, size)
    l, t, r, b = f.getbbox(word)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), word, font=f, fill=ink + (255,))
    return im


def fit_size(word, box_w, box_h, path=F_CARD, start=1400):
    """largest size whose tight box fits (box_w, box_h)."""
    s = start
    while s > 20:
        l, t, r, b = font(path, s).getbbox(word)
        if r - l <= box_w and b - t <= box_h:
            return s
        s = int(s * 0.94)
    return s


def slam(img, k, seed):
    """card slam: frame 0 at 1.08x, frame 1 at 1.02x, then 1.0; jitter 12 px on the first two frames, 2 px after."""
    sc = 1.08 if k == 0 else 1.02 if k == 1 else 1.0
    rnd = random.Random(seed * 131 + k)
    j = 12 if k < 2 else 2
    dx, dy = rnd.randint(-j, j), rnd.randint(-j, j)
    im = Image.fromarray(img)
    if sc != 1.0:
        w2, h2 = int(W * sc), int(H * sc)
        im = im.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    out = Image.new("RGB", (W, H), tuple(int(v) for v in img[5, 5]))
    out.paste(im, (dx, dy))
    return np.asarray(out)


@functools.lru_cache(maxsize=128)
def card(word, layout="vert", field="red", strike=False, sub=None):
    """one flash card, static (slam applied per frame by the caller). Layouts never centre the word:
    vert   word turned 90 deg reading upward, filling the height, bleeding off the left edge
    stack  word broken into short lines, huge, bleeding off the right edge
    giant  one glyph (A, YES) about 1300 px, bleeding off the bottom right
    rail   full-height column in the field colour at the left edge, black/paper page beside it
    corner word set big in the top left corner area, bleeding off the top
    field: red (black type), black (paper type), paper (black type), inv (red type on black)."""
    bg, ink = {"red": (RED, BLACK), "black": (BLACK, PAPER), "paper": (PAPER, BLACK), "inv": (BLACK, RED),
               "paperred": (PAPER, RED)}[field]
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    if layout == "vert":
        # cap height about 0.62 of the width; long words run off the top and bottom (bleed)
        s = fit_size(word, int(H * 1.0), int(W * 0.66))
        t = text_img(word, s, ink).rotate(90, expand=True)
        x = -int(t.width * 0.08); y = (H - t.height) // 2 + 30
        im.paste(t, (x, y), t)
        box = (x, y, x + t.width, y + t.height); horiz = False
    elif layout == "stack":
        if "|" in word or " " in word:
            parts = word.replace(" ", "|").split("|")      # hand-set line breaks
        else:
            n = 2 if len(word) <= 8 else 3
            k = -(-len(word) // n); parts = [word[i:i + k] for i in range(0, len(word), k)]
        s = min(fit_size(p, W - 90, int(H / len(parts) * 0.82)) for p in parts)
        th = sum(text_img(p, s, ink).height * 1.08 for p in parts)
        y = max(60, int((H - th) * 0.42))
        for p in parts:
            t = text_img(p, s, ink); im.paste(t, (W - t.width - 45, y), t); y += int(t.height * 1.08)
        box = (0, 120, W, y); horiz = True
    elif layout == "giant" and len(word) > 3:
        # a whole word as wide as the frame, low in the frame
        s = fit_size(word, W - 60, int(H * 0.5))
        t = text_img(word, s, ink); x = 30; y = int(H * 0.60) - t.height // 2
        im.paste(t, (x, y), t); box = (x, y, x + t.width, y + t.height); horiz = True
    elif layout == "giant":
        s = fit_size(word, int(W * 1.25), int(H * 0.80))
        t = text_img(word, s, ink); x = W - int(t.width * 0.86); y = H - int(t.height * 0.92)
        im.paste(t, (x, y), t); box = (x, y, x + t.width, y + t.height); horiz = True
    elif layout == "rail":
        rw = 300
        page = PAPER if field != "paper" else BLACK
        im = Image.new("RGB", (W, H), page); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, rw, H], fill=bg)
        s = fit_size(word, int(H * 0.86), rw - 40)
        t = text_img(word, s, ink).rotate(-90, expand=True)
        im.paste(t, ((rw - t.width) // 2, 140), t)
        d.rectangle([rw, 0, rw + 14, H], fill=BLACK if page == PAPER else RED)
        box = ((rw - t.width) // 2, 140, (rw + t.width) // 2, 140 + t.height); horiz = False
    elif layout == "corner":
        s = fit_size(word, int(W * 1.12), int(H * 0.36))
        t = text_img(word, s, ink); x = -int(t.width * 0.04); y = -int(t.height * 0.10)
        im.paste(t, (x, y), t)
        d.rectangle([0, y + t.height + 40, int(W * 0.62), y + t.height + 64], fill=ink)
        box = (x, y, x + t.width, y + t.height); horiz = True
    if strike:
        sc = BLACK if field == "red" else RED
        x0, y0, x1, y1 = box
        if horiz:
            hh = max(10, int((y1 - y0) * 0.09)); ym = (y0 + y1) // 2 + 10
            d.rectangle([max(0, x0 - 30), ym - hh, min(W, x1 + 30), ym + hh], fill=sc)
        else:
            hh = max(10, int((x1 - x0) * 0.09)); xm = (x0 + x1) // 2
            d.rectangle([xm - hh, max(0, y0 - 30), xm + hh, min(H, y1 + 30)], fill=sc)
    if sub:
        t = text_img(sub, 64, GREY if field in ("black", "inv") else BLACK, ROOT + "fonts/CormorantGaramond-600.ttf")
        im.paste(t, (W - t.width - 60, H - 470), t)
    return np.asarray(im)


@functools.lru_cache(maxsize=4)
def outliers_card(seed=7):
    """rows of black tally marks on paper, one red mark standing taller and out of line."""
    im = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    cols, rows = 9, 13; x0, y0, dx, dy = 92, 300, 112, 104
    rr, rc = 6, 6
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * dx; y = y0 + r * dy
            if (r, c) == (rr, rc):
                continue
            d.rectangle([x - 9, y, x + 9, y + 70], fill=BLACK)
    x = x0 + rc * dx + 30; y = y0 + rr * dy - 150
    d.rectangle([x - 26, y, x + 26, y + 300], fill=RED)
    return np.asarray(im)


def red_slit(base, k, n=5):
    """transition: black frame, a red slit opens from the centre line and reveals the picture."""
    out = np.full_like(base, BLACK)
    h = int(H * ((k + 1) / n) ** 2)
    y0, y1 = (H - h) // 2, (H + h) // 2
    out[y0:y1] = base[y0:y1]
    e = 10
    out[max(0, y0 - e):y0] = RED; out[y1:min(H, y1 + e)] = RED
    return out


# ---------------------------------------------------------------- captions
def caption(frame, words, t, y_center=372):
    """held caption chunk: black rail box, paper serif type, the word being spoken on a red box. words: list of
    dicts (w, s, e) of the current chunk."""
    size = 60
    f = font(F_CAP, size)
    txt = [w["w"] for w in words]
    gap = int(size * 0.28)
    widths = [f.getbbox(x)[2] - f.getbbox(x)[0] for x in txt]
    while sum(widths) + gap * (len(txt) - 1) > W - 140 and size > 40:
        size -= 2; f = font(F_CAP, size); gap = int(size * 0.28)
        widths = [f.getbbox(x)[2] - f.getbbox(x)[0] for x in txt]
    tw = sum(widths) + gap * (len(txt) - 1)
    padx, pady = 26, 18
    asc = f.getbbox("Hgy")
    th = asc[3] - asc[1]
    bx0 = (W - tw) // 2 - padx; by0 = y_center - th // 2 - pady
    im = Image.fromarray(frame); d = ImageDraw.Draw(im)
    d.rectangle([bx0, by0, bx0 + tw + 2 * padx, by0 + th + 2 * pady], fill=BLACK)
    x = bx0 + padx
    cur = max([i for i, w in enumerate(words) if w["s"] <= t + 0.01] or [0])
    for i, (w, ww) in enumerate(zip(txt, widths)):
        l = f.getbbox(w)[0]
        if i == cur:
            d.rectangle([x - 10, by0 + 6, x + ww + 10, by0 + th + 2 * pady - 6], fill=RED)
        d.text((x - l, by0 + pady - asc[1]), w, font=f, fill=PAPER)
        x += ww + gap
    return np.asarray(im)


# ---------------------------------------------------------------- inserts
@functools.lru_cache(maxsize=16)
def photo_src(path):
    return Image.open(ROOT + path).convert("RGB")


def photo_cover(path, u, anchor_y=0.0, z0=1.0, z1=1.05):
    """photo filling the frame (crop the sides), slow push z0 -> z1 over u in 0..1. anchor_y 0 = keep the top."""
    im = photo_src(path)
    z = z0 + (z1 - z0) * u
    s = max(W / im.width, H / im.height) * z
    w2, h2 = int(im.width * s), int(im.height * s)
    r = im.resize((w2, h2), Image.LANCZOS)
    x = (w2 - W) // 2; y = int((h2 - H) * anchor_y)
    return np.asarray(r.crop((x, y, x + W, y + H)))


def photo_card(path, u, width, field=BLACK, yc=0.5, z0=1.0, z1=1.04, border=None):
    """photo shown whole on a solid field (never stretched), slow push inside its frame."""
    im = photo_src(path)
    s = width / im.width
    w2, h2 = int(im.width * s), int(im.height * s)
    z = z0 + (z1 - z0) * u
    r = im.resize((int(w2 * z), int(h2 * z)), Image.LANCZOS)
    r = r.crop(((r.width - w2) // 2, (r.height - h2) // 2, (r.width - w2) // 2 + w2, (r.height - h2) // 2 + h2))
    out = Image.new("RGB", (W, H), field)
    x = (W - w2) // 2; y = int(H * yc - h2 / 2)
    if border:
        ImageDraw.Draw(out).rectangle([x - 10, y - 10, x + w2 + 10, y + h2 + 10], fill=border)
    out.paste(r, (x, y))
    return np.asarray(out)


class Clip:
    """frames of a raw clip at 30 fps (autorotated), decoded once per range and cached."""
    cache = {}

    @classmethod
    def frame(cls, path, t):
        key = (path, round(t * FPS))
        if key not in cls.cache:
            if len(cls.cache) > 400:
                cls.cache.clear()
            t0 = round(t * FPS) / FPS
            n = 45
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", ROOT + path, "-frames:v", str(n),
                                  "-vf", f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                                  "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
            for i in range(len(fr)):
                cls.cache[(path, round(t * FPS) + i)] = fr[i]
        return cls.cache[key]


def clip_frame(path, t, zoom=1.0, cx=0.5, cy=0.5):
    f = Clip.frame(path, t)
    if zoom <= 1.0001:
        return f
    w2, h2 = int(W / zoom), int(H / zoom)
    x = int((W - w2) * cx); y = int((H - h2) * cy)
    return np.asarray(Image.fromarray(f[y:y + h2, x:x + w2]).resize((W, H), Image.LANCZOS))
