"""reel-02 look: the reel-01 poster style (cream paper, black serif, one red, dry brush, grain).
Copied from reel-01/hook_scene.py (helpers only, no footage) so this project stands alone.
"""
import math
import sys

import numpy as np
import skia

sys.path.insert(0, "vibe")
from motion_kit import (clamp, ease_in_cubic, ease_out_back, ease_out_cubic, ease_out_expo, lerp, noise1, prog, text,
                        text_width, with_alpha)

W, H = 1080, 1920

# ---------------------------------------------------------------- palette (from reel-01's poster)
def col(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * clamp(a)))

PAPER = "#E9E3D4"
INK = "#141312"
RED = "#D3372B"
CREAM = "#EEE8DA"
SERIF = "Playfair Display:900"
SANS = "Inter Tight:800"

# ---------------------------------------------------------------- paper texture (built once, 3 variants that "boil")
def make_paper(seed):
    rng = np.random.default_rng(seed)
    import cv2
    base = np.array([int(PAPER[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
    img = np.ones((H, W, 3), np.float32) * base
    blot = cv2.GaussianBlur(rng.normal(0, 1, (H // 8, W // 8)).astype(np.float32), (0, 0), 6)
    blot = cv2.resize(blot, (W, H)) * 9
    img += blot[..., None] * np.array([1.0, 0.95, 0.85])
    img += rng.normal(0, 4.5, (H, W))[..., None]                       # fine tooth
    for _ in range(260):                                               # dust specks
        x, y, r = rng.integers(0, W), rng.integers(0, H), rng.uniform(0.6, 2.4)
        cv2.circle(img, (int(x), int(y)), int(max(1, r)), (base * rng.uniform(0.45, 0.8)).tolist(), -1, cv2.LINE_AA)
    for _ in range(14):                                                # soft stains
        x, y = rng.integers(0, W), rng.integers(0, H)
        st = np.zeros((H, W), np.float32)
        cv2.circle(st, (int(x), int(y)), int(rng.uniform(40, 160)), 1.0, -1)
        img -= cv2.GaussianBlur(st, (0, 0), 40)[..., None] * rng.uniform(6, 14)
    yy, xx = np.mgrid[-1:1:H * 1j, -1:1:W * 1j]
    img *= (1 - 0.10 * np.clip(xx ** 2 + yy ** 2 - 0.4, 0, None))[..., None]   # aged edges
    arr = np.clip(img, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr, np.full((H, W), 255, np.uint8)])
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)

PAPERS = [make_paper(s) for s in (11, 12, 13)]
CARD_PAPERS = [make_paper(s) for s in (21, 22)]

def paper(c, t, variants=PAPERS):
    c.drawImage(variants[int(t * 12) % len(variants)], 0, 0)          # changes 12x a second, like print grain

def grade_matrix(sat=0.86, contrast=1.07, warm=(1.03, 1.0, 0.94), gain=1.0, lift=0.0):
    """The grade is all linear (desaturate, contrast, warm tint, optional brighten), so it is one 3x4 colour matrix."""
    L = np.array([0.299, 0.587, 0.114], np.float32)
    D = sat * np.eye(3, dtype=np.float32) + (1 - sat) * np.tile(L, (3, 1))     # desaturate towards luma
    Wm = np.diag(np.array(warm, np.float32))
    M = gain * Wm @ (contrast * D)
    off = gain * Wm @ np.full(3, 128 * (1 - contrast), np.float32) + lift
    return np.hstack([M, off[:, None]]).astype(np.float32)

GRADE_M = grade_matrix()

def grade(rgb, m=None):
    """Warm, slightly muted, a touch more contrast. One saturating cv2.transform per frame."""
    import cv2
    return cv2.transform(np.ascontiguousarray(rgb[..., :3]), GRADE_M if m is None else m)

def fill_holes(m):
    """Close holes inside the silhouette (open mouth, gaps in the beard) so nothing shows through."""
    import cv2
    bg = (m < 128).astype(np.uint8)
    ff = bg.copy(); mask = np.zeros((H + 2, W + 2), np.uint8)
    for seed in ((0, 0), (W - 1, 0)):
        if ff[seed[1], seed[0]] == 1:
            cv2.floodFill(ff, mask, seed, 2)
    holes = (ff == 1).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(holes, connectivity=8)
    small = np.isin(lab, [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] < 9000])  # mouth-sized only
    holes = small.astype(np.uint8) * 255
    return np.maximum(m, cv2.GaussianBlur(holes, (0, 0), 1.5))

EDGE = np.minimum(np.clip(np.arange(W) / 70.0, 0, 1), np.clip((W - 1 - np.arange(W)) / 70.0, 0, 1))[None, :]

# ---------------------------------------------------------------- drawing helpers
def condensed(c, s, cx, cy, size, font, fill, max_w, squeeze=0.74, stroke=None, alpha=1.0):
    """Tall condensed headline (the poster's masthead): draw at `size`, squeeze horizontally to fit max_w."""
    w = text_width(s, size, font)
    sx = min(squeeze, max_w / w)
    c.save(); c.translate(cx, cy); c.scale(sx, 1.0)
    if stroke:
        text(c, s, 0, 0, size, font, fill=None, alpha=0, align="center")
        f = skia.Font(skia.Typeface.MakeFromFile("fonts/PlayfairDisplay-900.ttf"), size)
        m = f.getMetrics()
        p = skia.Paint(Color=fill, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=stroke / sx)
        c.drawString(s, -w / 2, -(m.fAscent + m.fDescent) / 2, f, p)
    else:
        text(c, s, 0, 0, size, font, fill=fill, align="center", alpha=alpha)
    c.restore()

def brush(c, x0, y0, x1, y1, width, colr, seed, head=1.0, tail=0.0, bristles=34, dry=0.35):
    """Dry brush stroke from (x0,y0) to (x1,y1). Draws the part between tail..head (0..1) of its length."""
    if head <= tail:
        return
    rng = np.random.default_rng(seed)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    for b in range(bristles):
        o = (b / (bristles - 1) - 0.5) * width
        edge = abs(o) / (width / 2)
        s0 = tail + rng.uniform(0, 0.06) * (1 + 2 * edge)              # ragged start and end
        s1 = head - rng.uniform(0, 0.08) * (1 + 3 * edge)
        if s1 <= s0:
            continue
        path = skia.Path()
        n = 18
        for i in range(n + 1):
            s = lerp(s0, s1, i / n)
            wob = (noise1(s * 6 + b * 3.1, seed) - 0.5) * width * 0.05
            px, py = x0 + dx * s + nx * (o + wob), y0 + dy * s + ny * (o + wob)
            path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
        p = skia.Paint(Color=colr, AntiAlias=True, Style=skia.Paint.kStroke_Style,
                       StrokeWidth=width / bristles * rng.uniform(1.6, 2.6), StrokeCap=skia.Paint.kRound_Cap)
        if edge > 1 - dry and rng.random() < 0.8:                      # broken, dry edges
            on, off = rng.uniform(20, 90), rng.uniform(6, 40)
            p.setPathEffect(skia.DashPathEffect.Make([on, off], rng.uniform(0, 50)))
        p.setAlphaf(rng.uniform(0.82, 1.0))
        c.drawPath(path, p)

def wipe(c, t, t_in, t_mid, t_out, colr, seed, direction=1):
    """Screen-covering brush wipe: strokes sweep across by t_mid, then slide off by t_out."""
    if not (t_in <= t <= t_out):
        return
    k_in = clamp((t - t_in) / (t_mid - t_in))
    k_out = clamp((t - t_mid) / (t_out - t_mid))
    for i in range(6):
        d = i * 0.06
        head = ease_out_cubic(clamp((k_in - d) / (1 - 0.3)))
        tail = ease_in_cubic(clamp((k_out - d) / (1 - 0.3)))
        y = -260 + i * 470
        x0, x1 = (-300, W + 300) if direction > 0 else (W + 300, -300)
        brush(c, x0, y + 420, x1, y - 420, 620, colr, seed + i, head=head, tail=tail, bristles=40, dry=0.22)

def star(c, x, y, r, colr, rot=0.0):
    p = skia.Path()
    for i in range(8):
        a = rot + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.16
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
    p.close()
    c.drawPath(p, skia.Paint(Color=colr, AntiAlias=True))

def torn_band(c, colr, seed):
    """Black torn paper across the bottom, rising at the sides (hides the cut edges of the shoulders)."""
    rng = np.random.default_rng(seed)
    p = skia.Path(); edge = []
    for x in np.arange(-20, W + 21, 10):
        u = x / W
        base = 1290 - 230 * (abs(u - 0.47) * 2) ** 2.2                  # low in the middle, high at the sides
        y = base + rng.normal(0, 4) + (rng.random() < 0.08) * rng.uniform(-14, 14)
        edge.append((x, y))
    p.moveTo(*edge[0])
    for e in edge[1:]:
        p.lineTo(*e)
    p.lineTo(W + 20, H + 20); p.lineTo(-20, H + 20); p.close()
    c.drawPath(p, skia.Paint(Color=colr, AntiAlias=True))
    rim = skia.Path(); rim.moveTo(edge[0][0], edge[0][1] - 3)
    for x, y in edge[1:]:
        rim.lineTo(x, y - 3 + rng.normal(0, 1.2))
    c.drawPath(rim, skia.Paint(Color=col(CREAM, 0.35), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5))

def red_sun(c, cx, cy, r, k):
    """The poster's red circle, with a rough printed edge."""
    if k <= 0:
        return
    rng = np.random.default_rng(7)
    p = skia.Path()
    n = 180
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        rr = r * k * (1 + (rng.random() - 0.5) * 0.012)
        px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
    p.close()
    c.drawPath(p, skia.Paint(Color=col(RED), AntiAlias=True))

def word(c, s, x, y, size, start, t, fill, font=SANS, tracking=0.02):
    k = ease_out_cubic(prog(t, start, 0.14))
    if k <= 0:
        return text_width(s, size, font, tracking)
    return text(c, s, x, y + (1 - k) * 18, size, font, fill=fill, align="left", alpha=k, tracking=tracking)

def scribble_ring(c, k, cx, cy, rx, ry, colr, seed=2):
    if k <= 0:
        return
    rng = np.random.default_rng(seed); path = skia.Path(); n = 140; turns = 1.25
    for i in range(int(n * k) + 1):
        u = i / n; a = -2.2 + u * turns * 2 * math.pi
        wob = 1 + 0.035 * math.sin(u * 23 + seed) + 0.02 * (noise1(u * 9, seed) - 0.5)
        x, y = cx + math.cos(a) * rx * wob * (1 + 0.06 * u), cy + math.sin(a) * ry * wob * (1 + 0.04 * u)
        path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
    c.drawPath(path, skia.Paint(Color=colr, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=9,
                                StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))

def arrow(c, k, x0, y0, x1, y1, bend, colr):
    if k <= 0:
        return
    mx, my = (x0 + x1) / 2 + bend, (y0 + y1) / 2
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1)
           for u in np.linspace(0, k, 40)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    pa = skia.Paint(Color=colr, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=8, StrokeCap=skia.Paint.kRound_Cap,
                    StrokeJoin=skia.Paint.kRound_Join)
    c.drawPath(p, pa)
    if k >= 0.98:
        (ax, ay), (bx, by) = pts[-4], pts[-1]
        ang = math.atan2(by - ay, bx - ax)
        h = skia.Path(); h.moveTo(bx + math.cos(ang + 2.5) * 34, by + math.sin(ang + 2.5) * 34); h.lineTo(bx, by)
        h.lineTo(bx + math.cos(ang - 2.5) * 34, by + math.sin(ang - 2.5) * 34)
        c.drawPath(h, pa)

def barcode(c, x, y, w, h, colr):
    rng = np.random.default_rng(5); cx = x
    while cx < x + w:
        bw = rng.choice([2, 2, 3, 5]); c.drawRect(skia.Rect.MakeXYWH(cx, y, bw, h), skia.Paint(Color=colr))
        cx += bw + rng.choice([2, 3, 4])

def shake(t, hit, amp=14):
    d = t - hit
    if d < 0 or d > 0.35:
        return 0.0, 0.0
    e = math.exp(-12 * d)
    return amp * e * (noise1(t * 40, 1) - 0.5) * 2, amp * e * (noise1(t * 40, 2) - 0.5) * 2

