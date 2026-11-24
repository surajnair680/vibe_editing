"""reel-14 v2 look, copied from refs/ref_klickpin.mp4 (spec: reanimate/spec.md).
Dark red backgrounds with drifting hairlines, light grey section with red circles, word-by-word blur-in captions
(Inter), condensed titles with a scattered letter reveal (Bebas Neue), frosted caption boxes, cut-outs.
Frames are RGB uint8 numpy arrays 1920x1080. Real footage and photos are never recoloured."""
import functools, math, random
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = "/home/user/vibe_editing/projects/reel-14/"
F_TITLE = ROOT + "fonts/BebasNeue-400.ttf"
F_CAP = ROOT + "fonts/Inter-500.ttf"
OFFWHITE = (237, 231, 225)
CAPGREY = (232, 226, 220)
RED = (200, 20, 27)
DEEP = (150, 12, 14)


@functools.lru_cache(maxsize=256)
def font(path, size):
    return ImageFont.truetype(path, size)


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


# ---------------------------------------------------------------- backgrounds
@functools.lru_cache(maxsize=2)
def _red_static():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.42) / H * 1.1) ** 2)
    k = np.clip(r / 0.75, 0, 1) ** 1.3
    # brand (docs/playbook/brand/MOTION.md): darker than the reference, #4A0005 centre to near black edges
    c0, c1 = np.array([74, 0, 5], np.float32), np.array([16, 1, 1], np.float32)
    img = c0[None, None] * (1 - k[..., None]) + c1[None, None] * k[..., None]
    return img


def bg_red(t):
    """deep red, darker vertical bars drifting, hairline circles and lines at low alpha, vignette."""
    img = _red_static().copy()
    bars = np.zeros(W, np.float32)
    for i, (x0, w, sp, a) in enumerate([(120, 140, 6, 0.22), (430, 90, -4, 0.16), (700, 180, 3, 0.20), (930, 70, -7, 0.14)]):
        xc = (x0 + sp * t) % (W + 200) - 100
        xs = np.arange(W)
        bars += a * np.exp(-((xs - xc) / (w * 0.5)) ** 2)
    img *= (1 - np.clip(bars, 0, 0.6))[None, :, None]
    lay = np.zeros((H, W), np.uint8)
    ang = t * 2.0
    cv2.circle(lay, (int(W * 0.78 + 20 * math.sin(t * 0.3)), int(H * 0.30)), 330, 255, 2, cv2.LINE_AA)
    cv2.ellipse(lay, (int(W * 0.15), int(H * 0.82)), (520, 520), ang, 200, 320, 255, 2, cv2.LINE_AA)
    cv2.line(lay, (0, int(H * 0.215 + 6 * math.sin(t * 0.4))), (W, int(H * 0.215 + 6 * math.sin(t * 0.4))), 255, 1, cv2.LINE_AA)
    cv2.line(lay, (int(W * 0.88 + 4 * t % 40), 0), (int(W * 0.88 + 4 * t % 40), H), 255, 1, cv2.LINE_AA)
    img += lay[..., None].astype(np.float32) * 0.10
    return np.clip(img, 0, 255).astype(np.uint8)


@functools.lru_cache(maxsize=2)
def _grey_static():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W * 0.45) / W) ** 2 + ((y - H * 0.4) / H) ** 2)
    k = np.clip(r / 0.9, 0, 1)
    c0, c1 = np.array([236, 234, 231], np.float32), np.array([204, 201, 197], np.float32)
    return c0[None, None] * (1 - k[..., None]) + c1[None, None] * k[..., None]


def bg_grey(t, circles=True):
    """light grey paper with big red circles joined by a rounded path line, soft shadows (reference 29-35 s)."""
    img = _grey_static().copy()
    # circles only below the title band (titles sit at y 400-760)
    pts = [(int(W * 0.04), int(H * 0.44)), (int(W * 0.97), int(H * 0.56)), (int(W * 0.05), int(H * 0.72)), (int(W * 0.93), int(H * 0.88))]
    path = np.zeros((H, W), np.uint8)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        ym = (y0 + y1) // 2
        cv2.line(path, (x0, ym), (x1, ym), 255, 3, cv2.LINE_AA)
        cv2.line(path, (x0, y0), (x0, ym), 255, 3, cv2.LINE_AA)
        cv2.line(path, (x1, ym), (x1, y1), 255, 3, cv2.LINE_AA)
    sh = cv2.GaussianBlur(path, (0, 0), 6)
    img -= sh[..., None].astype(np.float32) * 0.10
    img = img * (1 - path[..., None] / 255.0 * 0.0) + path[..., None] / 255.0 * 6
    if circles:
        for i, (x, y) in enumerate(pts):
            rr = 120 + 10 * math.sin(t * 0.8 + i)
            shadow = np.zeros((H, W), np.uint8)
            cv2.circle(shadow, (x + 14, y + 22), int(rr), 255, -1, cv2.LINE_AA)
            shadow = cv2.GaussianBlur(shadow, (0, 0), 18)
            img -= shadow[..., None].astype(np.float32) * 0.18
            disc = np.zeros((H, W), np.uint8)
            cv2.circle(disc, (x, y), int(rr), 255, -1, cv2.LINE_AA)
            a = disc[..., None].astype(np.float32) / 255
            img = img * (1 - a) + np.array([150, 8, 10], np.float32) * a
    return np.clip(img, 0, 255).astype(np.uint8)


def vignette(img, s=0.35):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    v = 1 - s * np.clip((r - 0.3) / 0.45, 0, 1) ** 2
    return (img * v[..., None]).astype(np.uint8)


# ---------------------------------------------------------------- compositing
def over(bg, fg, alpha):
    a = alpha.astype(np.float32)[..., None] / 255.0
    return (fg.astype(np.float32) * a + bg.astype(np.float32) * (1 - a)).astype(np.uint8)


def clean_matte(m):
    """his matte: soften the edge 1.5 px; hair-edge wall bits at the top are handled by the threshold."""
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    return m


# ---------------------------------------------------------------- titles (Bebas Neue, scattered letter reveal)
@functools.lru_cache(maxsize=128)
def title_letters(text, size, color):
    """list of (RGBA letter image, x, y) for a line, plus total width/height."""
    f = font(F_TITLE, size)
    asc, desc = f.getmetrics()
    x = 0; out = []
    for ch in text:
        l, t_, r, b = f.getbbox(ch)
        adv = f.getlength(ch)
        if ch != " ":
            im = Image.new("RGBA", (int(adv) + 20, asc + desc + 20), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((10, 10), ch, font=f, fill=color + (255,))
            out.append((im, x - 10, -10))
        x += adv + size * 0.01
    return out, int(x), asc + desc


def title(frame, text, t, t0, x, y, size, color=OFFWHITE, seed=1, fade_out=None, align="left", dur=0.6):
    """draw a title whose letters fade in in a random order over dur s (each letter 0.4 s, ease-out)."""
    letters, tw, th = title_letters(text, size, color)
    if align == "center":
        x = (W - tw) // 2
    rnd = random.Random(seed); order = list(range(len(letters))); rnd.shuffle(order)
    n = max(1, len(letters) - 1)
    im = Image.fromarray(frame).convert("RGBA")
    for rank, i in enumerate(order):
        st = t0 + dur * 0.55 * rank / n
        a = ease_out((t - st) / 0.4)
        if fade_out is not None:
            a *= 1 - min(max((t - fade_out) / 0.2, 0), 1)
        if a <= 0:
            continue
        L, lx, ly = letters[i]
        if a < 1:
            L = L.copy(); al = L.getchannel("A").point(lambda v, a=a: int(v * a)); L.putalpha(al)
            if a < 0.7:
                L = L.filter(ImageFilter.GaussianBlur(3 * (1 - a)))
        im.alpha_composite(L, (int(x + lx), int(y + ly)))
    return np.asarray(im.convert("RGB")), tw, th


# ---------------------------------------------------------------- captions (Inter, word-by-word blur-in)
def layout_words(words, size, maxw):
    f = font(F_CAP, size); sp = f.getlength(" ")
    lines, cur, cw = [], [], 0
    for w in words:
        ww = f.getlength(w["w"])
        if cur and cw + sp + ww > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, ww)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines, sp


def caption(frame, words, t, x0=86, y0=300, size=56, maxw=900, boxed=False, color=CAPGREY):
    """sentence block building word by word: each word fades in over 0.6 s (ease-out) with a 4 px blur, stays."""
    lines, sp = layout_words(words, size, maxw)
    f = font(F_CAP, size)
    lh = int(size * 1.18)
    asc, desc = f.getmetrics()
    if boxed:
        bw = max(sum(ww for _, ww in ln) + sp * (len(ln) - 1) for ln in lines)
        bx0, by0, bx1, by1 = x0 - 30, y0 - 22, int(x0 + bw + 30), y0 + lh * len(lines) + 10
        bx0, bx1 = max(0, bx0), min(W, bx1)
        roi = frame[by0:by1, bx0:bx1].astype(np.float32)
        roi = cv2.GaussianBlur(roi, (0, 0), 18) * 0.55 + np.array([60, 6, 8], np.float32) * 0.12
        frame = frame.copy()
        mask = np.zeros((by1 - by0, bx1 - bx0), np.uint8)
        cv2.rectangle(mask, (16, 0), (bx1 - bx0 - 17, by1 - by0 - 1), 255, -1)
        cv2.rectangle(mask, (0, 16), (bx1 - bx0 - 1, by1 - by0 - 17), 255, -1)
        for cx, cy in ((16, 16), (bx1 - bx0 - 17, 16), (16, by1 - by0 - 17), (bx1 - bx0 - 17, by1 - by0 - 17)):
            cv2.circle(mask, (cx, cy), 16, 255, -1, cv2.LINE_AA)
        a = mask[..., None] / 255.0
        frame[by0:by1, bx0:bx1] = (roi * a + frame[by0:by1, bx0:bx1] * (1 - a)).astype(np.uint8)
        edge = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
        e = edge[..., None] / 255.0 * 0.35
        frame[by0:by1, bx0:bx1] = (frame[by0:by1, bx0:bx1] * (1 - e) + 230 * e).astype(np.uint8)
    im = Image.fromarray(frame).convert("RGBA")
    y = y0
    for ln in lines:
        x = x0
        for w, ww in ln:
            # reference: a word lands at about 60 % in 0.15 s, then settles to full over about 0.8 s
            # (10-90 % in about 0.65 s, measured on the caption energy curve, reanimate/spec.md)
            dt = t - w["s"]
            u2 = min(max(dt / 0.8, 0), 1)
            a = 0.6 * ease_out(dt / 0.18) + 0.4 * (u2 * u2 * (3 - 2 * u2))
            if a > 0:
                L = Image.new("RGBA", (int(ww) + 24, lh + 24), (0, 0, 0, 0))
                ImageDraw.Draw(L).text((12, 12), w["w"], font=f, fill=color + (int(255 * a),))
                if a < 0.85:
                    L = L.filter(ImageFilter.GaussianBlur(4 * (1 - a)))
                if not boxed:
                    sh = Image.new("RGBA", L.size, (0, 0, 0, 0))
                    shm = L.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.55))
                    sh.putalpha(shm)
                    im.alpha_composite(sh, (int(x - 12), int(y - 10)))
                im.alpha_composite(L, (int(x - 12), int(y - 12)))
            x += ww + sp
        y += lh
    return np.asarray(im.convert("RGB"))


# ---------------------------------------------------------------- photos and clips (real, never recoloured)
@functools.lru_cache(maxsize=16)
def photo_src(path):
    return Image.open(ROOT + path).convert("RGB")


@functools.lru_cache(maxsize=16)
def cutout_src(path):
    """RGBA cut-out of a person photo (rembg isnet-general-use, cached to work/cutouts/)."""
    import os
    out = ROOT + "work/cutouts/" + os.path.basename(path).rsplit(".", 1)[0] + ".png"
    if not os.path.exists(out):
        from rembg import remove, new_session
        os.makedirs(ROOT + "work/cutouts", exist_ok=True)
        im = photo_src(path)
        res = remove(im, session=new_session("isnet-general-use"))
        res.save(out)
    return Image.open(out).convert("RGBA")


def place_cutout(frame, path, u, height, cx=0.5, bottom=1.0, z0=1.0, z1=1.04):
    im = cutout_src(path)
    z = z0 + (z1 - z0) * u
    s = height * z / im.height
    r = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = int(W * cx - r.width / 2); y = int(H * bottom - r.height)
    base = Image.fromarray(frame).convert("RGBA")
    sh = Image.new("RGBA", r.size, (0, 0, 0, 0)); sh.putalpha(r.getchannel("A").filter(ImageFilter.GaussianBlur(25)).point(lambda v: int(v * 0.6)))
    base.alpha_composite(sh, (x + 10, y + 20))
    base.alpha_composite(r, (x, y))
    return np.asarray(base.convert("RGB"))


def photo_cover(path, u, anchor_y=0.0, z0=1.0, z1=1.05):
    im = photo_src(path)
    z = z0 + (z1 - z0) * u
    s = max(W / im.width, H / im.height) * z
    w2, h2 = int(im.width * s), int(im.height * s)
    r = im.resize((w2, h2), Image.LANCZOS)
    x = (w2 - W) // 2; y = int((h2 - H) * anchor_y)
    return np.asarray(r.crop((x, y, x + W, y + H)))


def photo_frame(frame, path, u, width, yc=0.5, z0=1.0, z1=1.04):
    """photo whole on the background, thin light border, soft shadow (reference UI cards)."""
    im = photo_src(path)
    s = width / im.width; w2, h2 = int(im.width * s), int(im.height * s)
    z = z0 + (z1 - z0) * u
    r = im.resize((int(w2 * z), int(h2 * z)), Image.LANCZOS)
    r = r.crop(((r.width - w2) // 2, (r.height - h2) // 2, (r.width - w2) // 2 + w2, (r.height - h2) // 2 + h2))
    base = Image.fromarray(frame).convert("RGBA")
    x = (W - w2) // 2; y = int(H * yc - h2 / 2)
    sh = Image.new("RGBA", (w2 + 120, h2 + 120), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([60, 60, 60 + w2, 60 + h2], fill=(0, 0, 0, 170))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)), (x - 50, y - 40))
    base.paste(r, (x, y))
    d = ImageDraw.Draw(base); d.rectangle([x - 1, y - 1, x + w2, y + h2], outline=(240, 236, 232, 120), width=2)
    return np.asarray(base.convert("RGB"))
