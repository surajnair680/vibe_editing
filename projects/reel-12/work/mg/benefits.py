"""reel-12 benefit-list visuals (v2): every spoken item gets a panel that SHOWS that benefit.
His physique / gym assets where they show it (face always in frame), code-drawn manga illustrations (ink, screentone,
one red) for the abstract ones. No drawn people. Called from scene.py: list_panel(img, t, which).
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw
from manga import *  # noqa

PH_Y0, PH_Y1 = 130, 1110


def _sm(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def _eob(x, s=1.7):
    x = np.clip(x, 0, 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


class Pen:
    """an RGBA overlay to draw on with PIL, composited once"""
    def __init__(self):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def done(self, img, clip=None):
        if clip is not None:                       # keep the drawing inside its panel
            a = np.array(self.im)
            a[..., 3] = (a[..., 3] * clip).astype(np.uint8)
            self.im = Image.fromarray(a)
        paste(img, self.im, W / 2, H / 2)


def lbl(pen, txt, x, y, size=54, fill=INK, box_=True, anchor="mm", fnt="anton"):
    f = font(fnt, size)
    x0, y0, x1, y1 = pen.d.textbbox((x, y), txt, font=f, anchor=anchor)
    if box_:
        pen.d.rectangle([x0 - 18 + 8, y0 - 12 + 8, x1 + 18 + 8, y1 + 12 + 8], fill=INK + (255,))
        pen.d.rectangle([x0 - 18, y0 - 12, x1 + 18, y1 + 12], fill=INK + (255,))
        pen.d.rectangle([x0 - 13, y0 - 7, x1 + 13, y1 + 7], fill=PAPER + (255,))
    pen.d.text((x, y), txt, font=f, fill=fill + (255,), anchor=anchor)
    return (x0, y0, x1, y1)


def arrow(pen, x0, y0, x1, y1, w=18, col=RED, k=1.0):
    x1 = x0 + (x1 - x0) * k
    y1 = y0 + (y1 - y0) * k
    a = np.arctan2(y1 - y0, x1 - x0)
    hl = w * 2.4
    bx, by = x1 - np.cos(a) * hl, y1 - np.sin(a) * hl
    px, py = -np.sin(a), np.cos(a)
    pen.d.line([(x0, y0), (bx, by)], fill=INK + (255,), width=w + 10)
    pen.d.polygon([(x1 + np.cos(a) * 6, y1 + np.sin(a) * 6), (bx + px * (w * 1.6 + 5), by + py * (w * 1.6 + 5)),
                   (bx - px * (w * 1.6 + 5), by - py * (w * 1.6 + 5))], fill=INK + (255,))
    pen.d.line([(x0, y0), (bx, by)], fill=col + (255,), width=w)
    pen.d.polygon([(x1, y1), (bx + px * w * 1.6, by + py * w * 1.6), (bx - px * w * 1.6, by - py * w * 1.6)],
                  fill=col + (255,))


# ------------------------------------------------------------------ illustrations (dt = seconds since item start)
def il_gauge(pen, cx, cy, dt, label="HUNGER"):
    R = 300
    v = 0.92 - 0.8 * _sm((dt - 0.15) / 0.45)            # needle falls from FULL to LOW
    box_ = [cx - R, cy - R, cx + R, cy + R]
    pen.d.arc(box_, 180, 360, fill=INK + (255,), width=34)
    pen.d.arc([cx - R + 6, cy - R + 6, cx + R - 6, cy + R - 6], 300, 354, fill=RED + (255,), width=22)
    for i in range(11):
        a = np.deg2rad(180 + i * 18)
        r0, r1 = R - 40, R - (75 if i % 5 == 0 else 58)
        pen.d.line([(cx + np.cos(a) * r0, cy + np.sin(a) * r0), (cx + np.cos(a) * r1, cy + np.sin(a) * r1)],
                   fill=INK + (255,), width=8)
    lbl(pen, "LOW", cx - R + 70, cy + 50, 44, box_=False)
    lbl(pen, "FULL ON", cx + R - 100, cy + 50, 44, box_=False)
    a = np.deg2rad(180 + v * 180)
    pen.d.line([(cx, cy), (cx + np.cos(a) * (R - 70), cy + np.sin(a) * (R - 70))], fill=INK + (255,), width=26)
    pen.d.line([(cx, cy), (cx + np.cos(a) * (R - 76), cy + np.sin(a) * (R - 76))], fill=RED + (255,), width=14)
    pen.d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=INK + (255,))
    lbl(pen, label, cx, cy - R - 70, 70)


def il_age_chart(pen, x0, y0, x1, y1, dt):
    pen.d.line([(x0, y0), (x0, y1), (x1, y1)], fill=INK + (255,), width=10)
    for i, a in enumerate(("30", "50", "70")):
        x = x0 + 60 + i * (x1 - x0 - 120) / 2
        lbl(pen, "AGE " + a, x, y1 + 42, 40, box_=False)
    lbl(pen, "MUSCLE", x0 + 10, y0 - 40, 40, box_=False, anchor="lm")
    k = _sm((dt - 0.1) / 0.6)
    n = 60
    xs = np.linspace(x0 + 20, x1 - 20, n)
    hi = y0 + 60 + 25 * np.linspace(0, 1, n) ** 2                  # with protein: stays up
    lo = y0 + 60 + (y1 - y0 - 120) * np.linspace(0, 1, n) ** 1.6     # without: drops
    m = max(2, int(n * k))
    for i in range(0, m - 1, 2):                                     # dashed grey "without"
        pen.d.line([(xs[i], lo[i]), (xs[i + 1], lo[i + 1])], fill=INK + (255,), width=8)
    pen.d.line(list(zip(xs[:m], hi[:m])), fill=INK + (255,), width=22)
    pen.d.line(list(zip(xs[:m], hi[:m])), fill=RED + (255,), width=12)
    if k > 0.9:
        lbl(pen, "WITH PROTEIN", x1 - 190, hi[-1] - 60, 38, fill=RED)
        lbl(pen, "WITHOUT", x1 - 140, lo[-1] - 50, 36)


def il_flame(pen, cx, cy, dt, speed=1.0, count_to=250):
    s = 1 + 0.06 * np.sin(dt * 28 * speed)
    pts = []
    for a in np.linspace(0, 2 * np.pi, 80):
        r = 150 * s
        y = -np.cos(a)
        wob = 1 + 0.25 * np.sin(a * 5 + dt * 20 * speed) * max(0, y)
        x = np.sin(a) * r * (0.75 - 0.45 * max(0, y)) * wob
        yy = -(y * r * (1.4 if y > 0 else 0.8)) * wob
        pts.append((cx + x, cy + yy))
    pen.d.polygon(pts, fill=RED + (255,), outline=INK + (255,), width=12)
    inner = [(cx + (px - cx) * 0.45, cy + 60 + (py - cy) * 0.45) for px, py in pts]
    pen.d.polygon(inner, fill=PAPER + (255,), outline=INK + (255,), width=7)
    n = int(count_to * _sm(dt / 0.8))
    lbl(pen, f"+{n} KCAL", cx, cy + 250, 76)
    lbl(pen, "BURNED DIGESTING" if speed == 1.0 else "METABOLISM: FAST", cx, cy - 300, 50)


def il_sugar(pen, x0, y0, x1, y1, dt):
    k = _sm((dt - 0.15) / 0.5)
    n = 120
    xs = np.linspace(x0, x1, n)
    mid = (y0 + y1) / 2
    spikes = np.where((np.arange(n) // 10) % 2 == 0, -1, 1) * (y1 - y0) * 0.38 * np.abs(np.sin(np.arange(n) / 3.2))
    ys = mid + spikes * (1 - k) + 18 * np.sin(np.arange(n) / 9) * k
    pen.d.line([(x0, y1), (x1, y1)], fill=INK + (255,), width=6)
    pen.d.line([(x0, mid), (x1, mid)], fill=INK + (120,), width=3)
    pen.d.line(list(zip(xs, ys)), fill=INK + (255,), width=24, joint="curve")
    pen.d.line(list(zip(xs, ys)), fill=RED + (255,), width=12, joint="curve")
    lbl(pen, "BLOOD SUGAR", (x0 + x1) / 2, y0 - 60, 64)
    if k > 0.85:
        lbl(pen, "NO SPIKES, NO CRASHES", (x0 + x1) / 2, y1 + 70, 46)


def il_bone(img, pen, cx, cy, dt, tone):
    L, Rr, th = 330, 78, 70
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([cx - L, cy - th, cx + L, cy + th], fill=255)
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.ellipse([cx + sx * L - Rr, cy + sy * 62 - Rr, cx + sx * L + Rr, cy + sy * 62 + Rr], fill=255)
    mm = np.array(m) > 0
    edge = cv2.dilate(mm.astype(np.uint8), np.ones((19, 19), np.uint8)) > 0
    img[edge] = INK
    img[mm] = PAPER
    img[mm & tone] = INK
    # cracks fade out (bones get stronger)
    k = _sm((dt - 0.2) / 0.4)
    if k < 1:
        rng = np.random.default_rng(4)
        for c in range(3):
            x = cx - 160 + c * 150
            pts = [(x + rng.integers(-20, 20), cy - th + 8)]
            for j in range(5):
                pts.append((x + rng.integers(-30, 30), cy - th + 8 + (j + 1) * (2 * th - 16) / 5))
            a = int(255 * (1 - k))
            pen.d.line(pts, fill=RED + (a,), width=10)
    if k >= 1:
        lbl(pen, "STRONGER BONES", cx, cy + 210, 60, fill=INK)
    lbl(pen, "X-RAY", cx - L + 20, cy - 200, 40, box_=False, anchor="lm")


def il_shield(pen, cx, cy, dt):
    k = _eob((dt - 0.05) / 0.25)
    s = 230 * k
    if s < 5:
        return
    pts = [(cx - s, cy - s * 0.9), (cx, cy - s * 1.15), (cx + s, cy - s * 0.9), (cx + s * 0.95, cy + s * 0.1),
           (cx, cy + s * 1.2), (cx - s * 0.95, cy + s * 0.1)]
    pen.d.polygon(pts, fill=PAPER + (255,), outline=INK + (255,), width=18)
    w = s * 0.22
    pen.d.rectangle([cx - w, cy - s * 0.6, cx + w, cy + s * 0.6], fill=RED + (255,), outline=INK + (255,), width=8)
    pen.d.rectangle([cx - s * 0.6, cy - w, cx + s * 0.6, cy + w], fill=RED + (255,), outline=INK + (255,), width=8)
    pen.d.rectangle([cx - w + 8, cy - w + 8, cx + w - 8, cy + w - 8], fill=RED + (255,))
    lbl(pen, "IMMUNITY", cx, cy - 400, 66)


def il_hourglass(img, pen, cx, cy, dt, tone):
    h, w = 320, 210
    k = _sm(dt / 0.8)
    top = [(cx - w, cy - h), (cx + w, cy - h), (cx + 22, cy), (cx - 22, cy)]
    bot = [(cx - 22, cy), (cx + 22, cy), (cx + w, cy + h), (cx - w, cy + h)]
    for P in (top, bot):
        pen.d.polygon(P, fill=PAPER + (255,), outline=INK + (255,), width=14)
    pen.done(img)
    # sand: screentone, top level falls, bottom pile rises
    yy, xx = np.mgrid[0:H, 0:W]
    lvl_top = cy - h * 0.15 - (h * 0.8) * (1 - k) * 0 + h * 0.75 * k - h * 0.75
    in_top = (yy > cy - h * (0.85 - 0.75 * k)) & (yy < cy) & (np.abs(xx - cx) < 22 + (cy - yy) / h * (w - 22) - 16)
    in_bot = (yy > cy + h * (0.95 - 0.7 * k)) & (yy < cy + h - 10) & (np.abs(xx - cx) < 22 + (yy - cy) / h * (w - 22) - 16)
    img[(in_top | in_bot) & tone] = INK
    pen.__init__()
    pen.d.rectangle([cx - w - 40, cy - h - 30, cx + w + 40, cy - h], fill=INK + (255,))
    pen.d.rectangle([cx - w - 40, cy + h, cx + w + 40, cy + h + 30], fill=INK + (255,))
    if dt > 0.3:
        slam_k = _eob((dt - 0.3) / 0.15, 2.4)
        lbl(pen, "+ YEARS", cx + 300, cy - 200, int(60 + 20 * slam_k), fill=RED)
    lbl(pen, "LIFESPAN", cx, cy - h - 100, 64)


def il_mood(pen, cx, cy, dt):
    k = _sm((dt - 0.2) / 0.4)
    # sun rises behind as the cloud slides away
    if k > 0:
        r = 150
        for i in range(12):
            a = np.deg2rad(i * 30 + dt * 40)
            pen.d.line([(cx + np.cos(a) * (r + 30), cy + np.sin(a) * (r + 30)),
                        (cx + np.cos(a) * (r + 30 + 80 * k), cy + np.sin(a) * (r + 30 + 80 * k))], fill=INK + (255,), width=16)
        pen.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED + (255,), outline=INK + (255,), width=14)
    ox = -260 * k
    if k > 0.65:
        ox = None
    for (dx, dy, r) in (((-120, 20, 110), (0, -40, 140), (130, 10, 110), (-40, 60, 100), (70, 60, 100)) if ox is not None else ()):
        pen.d.ellipse([cx + ox + dx - r, cy + dy - r, cx + ox + dx + r, cy + dy + r], fill=PAPER + (255,),
                      outline=INK + (255,), width=12)
    for dx in (-150, -60, 30, 120):
        if ox is not None and k < 0.6:
            pen.d.line([(cx + ox + dx, cy + 190), (cx + ox + dx - 30, cy + 290)], fill=INK + (255,), width=10)
    lbl(pen, "ANXIETY" if k < 0.5 else "BETTER MOOD", cx, cy - 330, 66)


def il_sleep(img, pen, cx, cy, dt, tone):
    """crescent moon (screentone, ink edge) + Zzz popping up"""
    r = 210
    yy, xx = np.mgrid[0:H, 0:W]
    m = (np.hypot(xx - cx, yy - cy) <= r) & (np.hypot(xx - cx - 95, yy - cy + 55) > r * 0.86)
    edge = cv2.dilate(m.astype(np.uint8), np.ones((17, 17), np.uint8)) > 0
    img[edge] = INK
    img[m] = PAPER
    img[m & tone] = INK
    for i, (dx, dy, s) in enumerate(((210, -120, 70), (300, -250, 95), (400, -400, 125))):
        if dt > 0.12 + 0.15 * i:
            k = _eob((dt - 0.12 - 0.15 * i) / 0.15, 2.2)
            lbl(pen, "Z", cx + dx, cy + dy, int(s * k) + 1, box_=False, fnt="dela")


# ------------------------------------------------------------------ photo overlays (screen coordinates checked on stills)
def ov_growth(pen, dt):
    k = _eob((dt - 0.1) / 0.25)
    arrow(pen, 300, 690, 120, 690, k=k)
    arrow(pen, 760, 640, 960, 620, k=k)
    arrow(pen, 610, 330, 650, 170, k=k)
    if dt > 0.35:
        lbl(pen, "GROWTH", 830, 880, 56, fill=RED)


def ov_fat_muscle(pen, dt):
    if dt > 0.12:
        b = lbl(pen, "MUSCLE KEPT", 210, 600, 48)
        pen.d.line([(b[2] + 20, 600), (430, 610)], fill=INK + (255,), width=8)
    if dt > 0.4:
        b = lbl(pen, "FAT ↓", 190, 860, 56, fill=RED)
        pen.d.line([(b[2] + 20, 860), (420, 840)], fill=INK + (255,), width=8)


def battery(pen, x, y, dt, label="RECOVERY"):
    w, h = 300, 130
    pen.d.rectangle([x, y, x + w, y + h], fill=PAPER + (255,), outline=INK + (255,), width=12)
    pen.d.rectangle([x + w, y + 38, x + w + 26, y + h - 38], fill=INK + (255,))
    n = min(5, int(_sm(dt / 0.7) * 5 + 0.999))
    for i in range(n):
        pen.d.rectangle([x + 20 + i * 54, y + 20, x + 20 + i * 54 + 42, y + h - 20], fill=RED + (255,))
    lbl(pen, label, x + w / 2, y - 50, 44)


def star(img, cx, cy, s):
    pts = [(cx, cy - s), (cx + s * 0.22, cy - s * 0.22), (cx + s, cy), (cx + s * 0.22, cy + s * 0.22), (cx, cy + s),
           (cx - s * 0.22, cy + s * 0.22), (cx - s, cy), (cx - s * 0.22, cy - s * 0.22)]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = np.array(m) > 0
    e = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    img[e] = INK
    img[m] = PAPER


def ov_sparkle(img, dt):
    for i, (x, y, s) in enumerate(((180, 260, 44), (640, 220, 56), (690, 560, 38), (150, 700, 34))):
        if dt > 0.06 * i:
            star(img, x, y, s * (1 + 0.15 * np.sin(dt * 12 + i)))


def ov_pain(pen, dt):
    k = _sm((dt - 0.45) / 0.15)
    for (x, y) in ((560, 950), (470, 870), (650, 860)):
        pts = [(x + np.cos(a) * (46 if j % 2 else 22), y + np.sin(a) * (46 if j % 2 else 22))
               for j, a in enumerate(np.linspace(0, 2 * np.pi, 16, endpoint=False))]
        pen.d.polygon(pts, fill=RED + (255,), outline=INK + (255,), width=6)
    if k > 0:
        for (x, y) in ((560, 950), (470, 870), (650, 860)):
            e = 50 * k
            pen.d.line([(x - e, y - e), (x + e, y + e)], fill=INK + (255,), width=14)
            pen.d.line([(x - e, y + e), (x + e, y - e)], fill=INK + (255,), width=14)
        lbl(pen, "PAIN GONE", 840, 760, 50)


def fat_meter(pen, x, y, dt):
    h, w = 520, 110
    v = 1 - 0.75 * _sm((dt - 0.1) / 0.5)
    pen.d.rectangle([x, y, x + w, y + h], fill=PAPER + (255,), outline=INK + (255,), width=12)
    pen.d.rectangle([x + 16, y + h - 16 - (h - 32) * v, x + w - 16, y + h - 16], fill=RED + (255,))
    lbl(pen, "FAT", x + w / 2, y - 50, 48)
    lbl(pen, "↓", x + w / 2, y + h + 50, 60, box_=False)


# ------------------------------------------------------------------ the item tables
# (kind, name, panel x1, fx, fy, zoom, clip mapping (c0, rate, cap), overlay)
PROTEIN_V = [
    ("photo", "back", 1040, 0.5, 0.47, 1.02, None, "growth"),
    ("illus", "gauge", 1040, 0, 0, 0, None, None),
    ("photo", "front", 800, 0.5, 0.47, 1.02, None, "fat_muscle"),
    ("illus", "age_chart", 1040, 0, 0, 0, None, None),
    ("photo", "dumbbell", 680, 0.5, 0.40, 1.02, None, "battery"),
    ("illus", "flame", 1040, 0, 0, 0, None, None),
    ("illus", "sugar", 1040, 0, 0, 0, None, None),
    ("illus", "bone", 1040, 0, 0, 0, None, None),
    ("illus", "shield", 1040, 0, 0, 0, None, None),
    ("photo", "front", 800, 0.53, 0.16, 1.9, None, "sparkle"),
]
GYM_V = [
    ("clip", "flex", 800, 0.5, 0.36, 1.02, (0.0, 0.85, 0.95), None),
    ("photo", "front", 800, 0.5, 0.47, 1.02, None, None),
    ("photo", "dumbbell", 680, 0.5, 0.40, 1.02, None, None),
    ("illus", "hourglass", 1040, 0, 0, 0, None, None),
    ("illus", "sugar", 1040, 0, 0, 0, None, None),
    ("illus", "bone", 1040, 0, 0, 0, None, None),
    ("illus", "flame_fast", 1040, 0, 0, 0, None, None),
    ("clip", "fly", 800, 0.42, 0.45, 1.02, (0.25, 1.0, 8.9), "fat_meter"),
    ("photo", "back", 1040, 0.5, 0.47, 1.02, None, "pain"),
    ("clip", "fly", 800, 0.42, 0.45, 1.02, (3.1, 1.0, 8.9), "age70"),
    ("illus", "mood", 1040, 0, 0, 0, None, None),
    ("illus", "sleep", 1040, 0, 0, 0, None, None),
]
