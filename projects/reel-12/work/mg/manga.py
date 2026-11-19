"""reel-12 manga kit (Lemo-Opuscar "Manga Panels" grammar, built in Python for a hybrid with real footage).

Paper #F3F0E8, ink #121212, one spot red #F03C1E. Every grey is screentone (dots or lines), never a gradient.
His face, footage and photos stay real and in colour (user rule from reel-11); the manga lives around them.
The face circle: real head breaking out above the circle's centre line, with a manga paper rim + ink outline.
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
PAPER = (243, 240, 232)
INK = (18, 18, 18)
RED = (240, 60, 30)
F = "fonts/"


def font(name, size):
    return ImageFont.truetype(F + {"anton": "Anton-400.ttf", "dela": "DelaGothicOne-400.ttf",
                                   "bangers": "Bangers-400.ttf"}[name], size)


def inter(size, w="ExtraBold"):
    return ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{w}.otf", size)


def paper(seed=1):
    """warm paper with a fixed grain multiplied at about 10 %"""
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_CUBIC)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    img = np.empty((H, W, 3), np.float32)
    img[:] = PAPER
    img *= (1 - 0.05 * np.clip(g, -2, 2))[..., None]
    return img


def dot_tone(h, w, cov, cell=8.0, angle=45):
    """AM dot screen. cov: (h, w) coverage 0..1 -> bool mask of ink dots. Coverage capped at 0.62, solid above 0.84."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle)
    u = (xx * np.cos(a) + yy * np.sin(a)) / cell
    v = (-xx * np.sin(a) + yy * np.cos(a)) / cell
    du, dv = u - np.round(u), v - np.round(v)
    d = np.sqrt(du * du + dv * dv)
    c = np.clip(cov, 0, 0.62)
    r = np.sqrt(c / np.pi)
    m = d < r
    m |= cov > 0.84
    return m


def focus_lines(h, w, cx, cy, r_clear, n=180, seed=3, width=(2, 9), length=(0.25, 0.75)):
    """manga focus lines: tapered black wedges from beyond the frame edge toward (cx, cy), stopping at r_clear+"""
    rng = np.random.default_rng(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    R = np.hypot(max(cx, w - cx), max(cy, h - cy)) + 40
    for i in range(n):
        th = rng.uniform(0, 2 * np.pi)
        r0 = r_clear + (R - r_clear) * rng.uniform(*length) * 0.6
        hw = rng.uniform(*width) / 2
        ox, oy = cx + R * np.cos(th), cy + R * np.sin(th)
        tx, ty = cx + r0 * np.cos(th), cy + r0 * np.sin(th)
        px, py = -np.sin(th) * hw, np.cos(th) * hw
        d.polygon([(ox + px, oy + py), (ox - px, oy - py), (tx, ty)], fill=255)
    return np.array(im) > 0


def poly_mask(pts, h=H, w=W):
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
    return np.array(im) > 0


def stroke_poly(img, pts, width=7, col=INK):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).line([tuple(p) for p in pts] + [tuple(pts[0])], fill=255, width=width, joint="curve")
    img[np.array(m) > 0] = col


def put(img, mask, col):
    img[mask] = col


def layer_text(txt, fnt, fill=INK, stroke=0, stroke_fill=PAPER, pad=40):
    """text rendered on its own RGBA layer (so it can be rotated and slammed)"""
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    x0, y0, x1, y1 = tmp.textbbox((0, 0), txt, font=fnt, stroke_width=stroke)
    im = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), txt, font=fnt, fill=fill + (255,), stroke_width=stroke,
                            stroke_fill=stroke_fill + (255,))
    return im


def sfx(txt, fnt, rot=0, fill=INK):
    """manga sound effect / shout: wide ink stroke, paper stroke, ink (or red) fill"""
    s = fnt.size
    a = layer_text(txt, fnt, fill=INK, stroke=int(s * 0.17), stroke_fill=INK)
    b = layer_text(txt, fnt, fill=PAPER, stroke=int(s * 0.10), stroke_fill=PAPER)
    c = layer_text(txt, fnt, fill=fill)
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    for L in (a, b, c):
        out.alpha_composite(L, ((a.size[0] - L.size[0]) // 2, (a.size[1] - L.size[1]) // 2))
    return out.rotate(rot, resample=Image.BICUBIC, expand=True)


def paste(img, layer, cx, cy):
    """alpha-composite an RGBA PIL layer centred at (cx, cy) onto float img"""
    L = np.asarray(layer).astype(np.float32)
    h, w = L.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xb <= xa or yb <= ya:
        return
    sub = L[ya - y0:yb - y0, xa - x0:xb - x0]
    al = sub[..., 3:4] / 255
    img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - al) + sub[..., :3] * al


def box(img, x0, y0, x1, y1, border=5, shadow=10, fill=PAPER):
    """narration box: paper box, ink border, offset solid ink shadow"""
    img[y0 + shadow:y1 + shadow, x0 + shadow:x1 + shadow] = INK
    img[y0:y1, x0:x1] = INK
    img[y0 + border:y1 - border, x0 + border:x1 - border] = fill


def tick(img, x, y, s, col=INK, w=None):
    """hand-inked check mark, top-left at (x, y), size s"""
    m = Image.new("L", (W, H), 0)
    w = w or max(6, int(s * 0.16))
    ImageDraw.Draw(m).line([(x, y + s * 0.55), (x + s * 0.38, y + s * 0.92), (x + s, y + s * 0.05)], fill=255,
                           width=w, joint="curve")
    img[np.array(m) > 0] = col


def cover(src, w, h, fx=0.5, fy=0.5, zoom=1.0):
    """crop-to-fill src (H, W, 3) into (h, w), focus point fx, fy in 0..1"""
    sh, sw = src.shape[:2]
    s = max(w / sw, h / sh) * zoom
    r = cv2.resize(src, (int(sw * s + 0.5), int(sh * s + 0.5)), interpolation=cv2.INTER_AREA)
    x0 = int(np.clip(fx * r.shape[1] - w / 2, 0, r.shape[1] - w))
    y0 = int(np.clip(fy * r.shape[0] - h / 2, 0, r.shape[0] - h))
    return r[y0:y0 + h, x0:x0 + w]


def face_circle(img, me_rgb, alpha, cx, cy, r, scale, head_top, seed=7, ring=10, tone_cell=9.0):
    """his real head breaking out of a manga circle.
    Inside the circle: paper + dot gradient + focus lines (intense manga background). Ring: ink, paper rim, thin ink.
    The person (matte) is drawn inside the circle and anywhere above its centre line, with a manga paper rim (12 px)
    + ink outline (3 px) where the head breaks out of the circle."""
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.hypot(xx - cx, yy - cy)
    circ = dd <= r
    # background inside the circle
    ys, ye = max(0, cy - r), min(H, cy + r)
    sub_h = ye - ys
    cov = np.zeros((sub_h, W), np.float32)
    lin = np.clip((np.arange(sub_h)[:, None] + ys - (cy - r)) / (2 * r), 0, 1)
    cov[:] = 0.04 + 0.22 * lin
    tone = np.zeros((H, W), bool)
    tone[ys:ye] = dot_tone(sub_h, W, cov, cell=tone_cell)
    fl = focus_lines(H, W, cx, cy - int(r * 0.25), r_clear=int(r * 0.55), n=110, seed=seed, width=(3, 10), length=(0.0, 0.5))
    bg = circ & (tone | fl)
    img[circ] = PAPER
    img[bg] = INK
    # ring
    img[(dd > r) & (dd <= r + ring)] = INK
    img[(dd > r + ring) & (dd <= r + ring + 9)] = PAPER
    img[(dd > r + ring + 9) & (dd <= r + ring + 12)] = INK
    # person
    al = alpha.astype(np.float32) / 255
    rows0 = np.where(al.max(1) > 0.5)[0]
    top = rows0[0]
    band = slice(max(0, top - 5), top + int(0.22 * (rows0[-1] - top)))          # hair zone
    luma = cv2.cvtColor(me_rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    wall = (luma > 82).astype(np.uint8)
    wall = cv2.morphologyEx(wall, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    hz = np.zeros_like(al); hz[band] = 1
    # only near the matte's outer edge (wall bits stuck to the hair), never the forehead inside the head
    inside = cv2.distanceTransform((al > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    hz *= (inside < 60)
    al = al * (1 - hz * wall)
    # despill: the soft hair edge still mixes in wall colour; darken bright pixels there toward the hair tone
    k = np.clip(55.0 / np.maximum(luma, 1), 0.25, 1.0)
    me_rgb = (me_rgb.astype(np.float32) * (1 - hz[..., None] + hz[..., None] * k[..., None])).astype(np.float32)
    al = cv2.morphologyEx(al, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    al = cv2.erode(al, np.ones((3, 3), np.uint8))
    al = cv2.GaussianBlur(al, (5, 5), 0)
    me = cv2.resize(me_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA).astype(np.float32)
    al = cv2.resize(al, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    # person's own top row (hair top) in source -> place at head_top
    rows = np.where(al.max(1) > 0.5)[0]
    oy = int(head_top - rows[0])
    ox = int(cx - me.shape[1] / 2)
    cm = np.zeros((H, W, 3), np.float32)
    ca = np.zeros((H, W), np.float32)
    h, w = me.shape[:2]
    ya, xa, yb, xb = max(0, oy), max(0, ox), min(H, oy + h), min(W, ox + w)
    cm[ya:yb, xa:xb] = me[ya - oy:yb - oy, xa - ox:xb - ox]
    ca[ya:yb, xa:xb] = al[ya - oy:yb - oy, xa - ox:xb - ox]
    allowed = circ | (yy < cy)
    allowed = cv2.GaussianBlur(allowed.astype(np.float32), (3, 3), 0)
    a = ca * allowed
    # paper rim + ink outline only where the person is outside the circle (breaking out)
    out_part = ((a > 0.5) & ~circ).astype(np.uint8)
    rim = cv2.dilate(out_part, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))) & ~circ
    edge = cv2.dilate(rim, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) & ~circ
    img[(edge > 0) & (rim == 0)] = INK
    img[rim > 0] = PAPER
    img[:] = img * (1 - a[..., None]) + cm * a[..., None]
    return dict(ox=ox, oy=oy, w=w, h=h)
