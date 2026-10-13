"""reel-01 hook + first section card (style sample for step 7).

    python3 hook_scene.py stills 0.0 1.2 3.0 4.3     # check frames -> out/stills/
    python3 hook_scene.py render                      # out/hook_sample_silent.mp4 (0 to 5.6 s, source timing)

Source timing for now: the hook has no pauses worth cutting, so this matches raw/take-01.mp4 seconds 0 to 5.6.
Look: poster on cream paper (refs/poster-echoes.jpg) + grunge brush transitions (refs/ref-video.mp4).
"""
import math
import sys

import numpy as np
import skia

sys.path.insert(0, "vibe")
from motion_kit import (Stage, VideoFrames, clamp, ease_in_cubic, ease_in_out_cubic, ease_out_back, ease_out_cubic,
                        ease_out_expo, grain, lerp, noise1, prog, text, text_width, vignette, with_alpha)

W, H, FPS, DUR = 1080, 1920, 30, 5.6

# ---------------------------------------------------------------- palette (from the poster)
def col(h, a=1.0):
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * clamp(a)))

PAPER = "#E9E3D4"
INK = "#141312"
RED = "#D3372B"
CREAM = "#EEE8DA"
SERIF = "Playfair Display:900"
SANS = "Inter Tight:800"

# ---------------------------------------------------------------- word times (source seconds, work/words.json)
T = dict(three=0.24, disgusting=0.48, addictions=1.04, stopping=1.52, you=1.88, frm=2.02, building=2.22,
         your=2.52, dream=2.62, physique=2.88, being=3.52, yes=3.92, man=4.18, ninety=5.00)
WIPE1_IN, WIPE1_MID, WIPE1_OUT = 3.30, 3.50, 3.72      # red brush: cover -> card
WIPE2_IN, WIPE2_MID, WIPE2_OUT = 4.55, 4.74, 4.95      # black ink brush: card -> real room

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

# ---------------------------------------------------------------- footage: cut-out and full frame, gently graded
from vframes import StreamFrames
SRC = StreamFrames("work/hook_src.mp4", fps=FPS)                         # streamed, not held in memory
MAT = StreamFrames("work/matte/hook_src_alpha_clean.mp4", fps=FPS)

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

def person(t):
    rgb = grade(SRC.array(t))
    m = fill_holes(MAT.array(t)[..., 0]).astype(np.float32) * EDGE     # soft fade at the source frame's sides
    return with_alpha(rgb, m.astype(np.uint8))

def full_frame(t):
    rgb = grade(SRC.array(t))
    return skia.Image.fromarray(np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)]),
                                colorType=skia.kRGBA_8888_ColorType)

def make_photo():
    from PIL import Image
    im = Image.open("assets/physique-photo.jpg").convert("RGB")
    im = im.crop((200, 0, 1072, 1350))                                  # drop the phone, keep head to waist
    a = grade(np.asarray(im)).astype(np.float32)
    a = np.clip((a - 128) * 1.05 + 128, 0, 255).astype(np.uint8)
    b = 22                                                              # printed white border
    framed = np.full((a.shape[0] + 2 * b, a.shape[1] + 2 * b, 3), (238, 233, 222), np.uint8)
    framed[b:-b, b:-b] = a
    rgba = np.dstack([framed, np.full(framed.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)

PHOTO = make_photo()
PH_CX, PH_CY, PH_W = 805, 965, 440                                     # where the print sits on the cover
PH_H = PH_W * PHOTO.height() / PHOTO.width()

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

def print_photo(c, t):
    rot = 4 + 0.6 * math.sin(t * 1.3)
    c.save(); c.translate(PH_CX, PH_CY + 4 * math.sin(t * 1.1)); c.rotate(rot)
    shadow_p = skia.Paint(Color=col(INK, 0.35), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    c.drawRect(skia.Rect.MakeXYWH(-PH_W / 2 + 10, -PH_H / 2 + 16, PH_W, PH_H), shadow_p)
    c.drawImageRect(PHOTO, skia.Rect.MakeXYWH(-PH_W / 2, -PH_H / 2, PH_W, PH_H), skia.SamplingOptions(skia.FilterMode.kLinear))
    br = skia.Paint(Color=col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=8)
    o, L = 22, 60
    for sxn, syn in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x, y = sxn * (PH_W / 2 + o), syn * (PH_H / 2 + o)
        path = skia.Path(); path.moveTo(x, y - syn * L); path.lineTo(x, y); path.lineTo(x - sxn * L, y)
        c.drawPath(path, br)
    c.save(); c.translate(-20, -PH_H / 2 - 4); c.rotate(-9)                # red tape across the top edge
    rng = np.random.default_rng(31); tp = skia.Path(); tw, th = 190, 46
    tp.moveTo(-tw / 2, -th / 2)
    for x in np.linspace(-tw / 2, tw / 2, 12): tp.lineTo(x, -th / 2 + rng.normal(0, 1.2))
    for y in np.linspace(-th / 2, th / 2, 6): tp.lineTo(tw / 2 + rng.normal(0, 3), y)
    for x in np.linspace(tw / 2, -tw / 2, 12): tp.lineTo(x, th / 2 + rng.normal(0, 1.2))
    for y in np.linspace(th / 2, -th / 2, 6): tp.lineTo(-tw / 2 + rng.normal(0, 3), y)
    c.drawPath(tp, skia.Paint(Color=col(RED, 0.88), AntiAlias=True))
    c.restore(); c.restore()

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

# ---------------------------------------------------------------- scenes
def shake(t, hit, amp=14):
    d = t - hit
    if d < 0 or d > 0.35:
        return 0.0, 0.0
    e = math.exp(-12 * d)
    return amp * e * (noise1(t * 40, 1) - 0.5) * 2, amp * e * (noise1(t * 40, 2) - 0.5) * 2

def cover(c, t):
    """0 to ~3.5 s: the poster cover."""
    paper(c, t)
    sx, sy = shake(t, T["addictions"])
    c.save(); c.translate(sx, sy)
    # red sun behind the head
    red_sun(c, 380, 790, 345, 0.9 + 0.1 * ease_out_back(prog(t, 0.0, 0.35)))
    # masthead: outline from the first frame, slams solid on "addictions"
    hit = prog(t, T["addictions"], 0.22)
    push = 1 + 0.015 * prog(t, 0, 3.5)
    c.save(); c.translate(540, 495); c.scale(push, push); c.translate(-540, -495)
    if hit <= 0:
        condensed(c, "ADDICTIONS", 540, 495, 330, SERIF, col(INK, 0.9), 1010, stroke=3)
    else:
        s = lerp(1.14, 1.0, ease_out_expo(hit))
        c.save(); c.translate(540, 495); c.scale(s, s); c.translate(-540, -495)
        flash = prog(t, T["addictions"], 0.10) < 1
        condensed(c, "ADDICTIONS", 540, 495, 330, SERIF, col(RED if flash else INK), 1010)
        c.restore()
    c.restore()
    # top line: THREE (on "three") + DISGUSTING on a red brush (on "disgusting")
    word(c, "THREE", 70, 285, 62, T["three"], t, col(INK), tracking=0.04)
    bx = 70 + text_width("THREE ", 62, SANS, 0.04) + 26
    k = ease_out_cubic(prog(t, T["disgusting"], 0.22))
    brush(c, bx - 18, 295, bx + 445, 277, 88, col(RED), 3, head=k)
    word(c, "DISGUSTING", bx, 285, 62, T["disgusting"] + 0.06, t, col(INK), tracking=0.04)
    c.restore()
    # him: the cut-out, slow push-in
    s = lerp(0.74, 0.78, ease_in_out_cubic(prog(t, 0, 3.5)))
    c.save(); c.translate(375 + sx * 0.4, 800 + sy * 0.4); c.scale(s, s)
    c.drawImage(person(t), -540, -960)
    c.restore()
    # torn black band + the rest of the line, word by word
    torn_band(c, col(INK), 4)
    print_photo(c, t)
    y1, y2, y3 = 1350, 1412, 1474
    x = 64
    x += word(c, "STOPPING ", x, y1, 56, T["stopping"], t, col(CREAM))
    x += word(c, "YOU ", x, y1, 56, T["you"], t, col(CREAM))
    word(c, "FROM", x, y1, 56, T["frm"], t, col(CREAM))
    x = 64
    x += word(c, "BUILDING ", x, y2, 56, T["building"], t, col(CREAM))
    word(c, "YOUR", x, y2, 56, T["your"], t, col(CREAM))
    x = 64
    x += word(c, "DREAM ", x, y3, 56, T["dream"], t, col(CREAM))
    pw = word(c, "PHYSIQUE.", x, y3, 56, T["physique"], t, col(RED))
    scribble_ring(c, ease_out_cubic(prog(t, T["physique"], 0.35)), PH_CX, PH_CY, PH_W * 0.66, PH_H * 0.6, col(RED))
    arrow(c, ease_out_cubic(prog(t, T["physique"] + 0.12, 0.25)), x + pw + 14, y3 - 6, PH_CX - 150, PH_CY + PH_H * 0.52, -60, col(RED))
    # ornaments
    tw = 1 + 0.25 * math.sin(t * 5)
    star(c, 1010, 175, 24 * (2 - tw), col(INK))
    star(c, 1010, 1470, 22, col(CREAM), rot=0.2)
    barcode(c, 840, 1440, 130, 40, col(CREAM, 0.85))

def card(c, t):
    """Section card: 01 BEING A YES MAN."""
    paper(c, t, CARD_PAPERS)
    sx, sy = shake(t, T["yes"], 10)
    c.save(); c.translate(sx, sy)
    k = ease_out_cubic(prog(t, WIPE1_MID, 0.25))
    brush(c, 380, 560, 700, 548, 120, col(RED), 9, head=k)
    condensed(c, "01", 540, 552, 150, SERIF, col(INK), 400, squeeze=0.9)
    word(c, "BEING A", 540 - text_width("BEING A", 78, SANS, 0.12) / 2, 760, 78, T["being"], t, col(INK), tracking=0.12)
    for wd, start, cy in (("YES", T["yes"], 980), ("MAN.", T["man"], 1270)):
        h = prog(t, start, 0.2)
        if h > 0:
            s = lerp(1.25, 1.0, ease_out_expo(h))
            c.save(); c.translate(540, cy); c.scale(s, s)
            condensed(c, wd, 0, 0, 330, SERIF, col(INK), 900, squeeze=0.95, alpha=clamp(h * 3))
            c.restore()
    u = ease_out_cubic(prog(t, T["man"] + 0.12, 0.25))
    brush(c, 150, 1440, 930, 1424, 34, col(RED), 12, head=u, bristles=16)
    star(c, 120, 400, 24, col(INK)); star(c, 960, 1480, 24, col(RED), rot=0.3)
    c.restore()

def room(c, t):
    """Back to the real footage, full frame."""
    c.drawImage(full_frame(t), 0, 0)

def draw(c, t):
    if t < WIPE1_MID:
        cover(c, t)
    elif t < WIPE2_MID:
        card(c, t)
    else:
        room(c, t)
    wipe(c, t, WIPE1_IN, WIPE1_MID, WIPE1_OUT, col(RED), 40, direction=1)
    wipe(c, t, WIPE2_IN, WIPE2_MID, WIPE2_OUT, col(INK), 60, direction=-1)

def post(arr, t):
    return grain(vignette(arr, 0.22), 0.028, seed=int(t * FPS))

S = Stage(W, H, fps=FPS, duration=DUR)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        ts = [float(x) for x in sys.argv[2:]] or [0.0, 1.2, 3.0, 4.3]
        S.stills(draw, ts, out_dir="out/stills/hook", post=post)
    elif cmd == "render":
        S.render(draw, "out/hook_sample_silent.mp4", post=post)
