"""reel-02: the whole edit, in finished-video time (edit time). Beat sheet: brief.md section 6.

    python3 reel_scene.py stills 6.0 9.0 ...     # check frames -> out/stills/reel/
    python3 reel_scene.py sheet                   # one frame every 2.5 s -> out/stills/contact.png (+ singles)
    python3 reel_scene.py draft                   # half size, half fps -> out/reel-02_draft.mp4
    python3 reel_scene.py render                  # full -> out/reel-02_silent.mp4 (audio is mixed by work/mix.py)

Footage: work/cut.mp4 (both clips cut by work/cut_plan.json). Word times: work/words_cut.json (edit time).
Look: reel-01's poster style (style.py). Drawings: illus.py. Wipes sit on music B's beat grid (work/music_beats.json).
"""
import json
import math
import sys

import numpy as np
import skia

sys.path.insert(0, "vibe")
sys.path.insert(0, ".")
import illus as il
from motion_kit import Stage, clamp, ease_in_cubic, ease_in_out_cubic, ease_out_back, ease_out_cubic, ease_out_expo, \
    grain, lerp, prog, text, text_width, vignette, with_alpha
from style import (CARD_PAPERS, CREAM, INK, PAPERS, RED, SANS, SERIF, arrow, barcode, brush, col, condensed, fill_holes,
                   grade, paper, red_sun, scribble_ring, shake, star, torn_band, wipe, word)
from vframes import StreamFrames

W, H, FPS = 1080, 1920, 30
PLAN = json.load(open("work/cut_plan.json"))
DUR = round(PLAN["length"] + 1.5, 3)                           # 1.5 s hold on the end card
WORDS = json.load(open("work/words_cut.json"))
QSERIF = "Instrument Serif:400"

def wt(word, after=-1.0):
    """Edit time of the first occurrence of a word starting after `after` (case and punctuation ignored)."""
    key = word.lower().strip(".,!?'\"")
    for x in WORDS:
        if x["s"] > after and x["w"].lower().strip(".,!?'\"") == key:
            return x["s"]
    raise KeyError(f"{word} after {after}")

# ---------------------------------------------------------------- music grid and scene windows (edit time)
BEAT = json.load(open("work/music_beats.json"))
def beat(t):
    """Nearest beat of music B to t (150 BPM grid)."""
    k = round((t - BEAT["phase"]) / BEAT["beat"])
    return round(BEAT["phase"] + k * BEAT["beat"], 3)

W_DIAG = beat(3.2)            # red: cover -> diagnosis card (the track's drop lands here)
W_ROOM1 = beat(6.4)           # black: card -> room
W_POSTER = beat(24.0)         # red: room -> poster
W_ROOM2 = beat(27.2)          # black: poster -> room
W_CARD = beat(34.8)           # red: room -> exist/perfect card
W_ROOM3 = beat(40.0)          # black: card -> room
W_END = beat(42.0)            # red: room -> end card
FLIP = beat(25.6)             # poster print flips gym-1 -> gym-3 lat spread
WIPES = [(W_DIAG, RED, 40, 1), (W_ROOM1, INK, 60, -1), (W_POSTER, RED, 41, 1), (W_ROOM2, INK, 61, -1),
         (W_CARD, RED, 42, 1), (W_ROOM3, INK, 62, -1), (W_END, RED, 43, 1)]

# ---------------------------------------------------------------- footage
CUT = StreamFrames("work/cut.mp4", fps=FPS)
HOOK = StreamFrames("work/hook_src.mp4", fps=FPS)
HOOK_MAT = StreamFrames("work/matte/hook_src_alpha_clean.mp4", fps=FPS)
GYM1 = StreamFrames("work/gym1_print.mp4", fps=FPS, offset=W_POSTER - 0.2)
GYM3 = StreamFrames("work/gym3_lat.mp4", fps=FPS, offset=FLIP)
SIDE = StreamFrames("work/gym3_side.mp4", fps=FPS, offset=W_END - 0.2)

def to_img(rgb):
    a = np.ascontiguousarray(np.dstack([rgb[..., :3], np.full(rgb.shape[:2], 255, np.uint8)]))
    return skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType)

def lighten(rgb):
    import cv2
    return cv2.convertScaleAbs(rgb, alpha=1.05, beta=6)

EDGE = np.minimum(np.clip(np.arange(W) / 70.0, 0, 1), np.clip((W - 1 - np.arange(W)) / 70.0, 0, 1))[None, :]

def person(t):
    rgb = grade(HOOK.array(t))
    m = fill_holes(HOOK_MAT.array(t)[..., 0]).astype(np.float32) * EDGE
    return with_alpha(rgb, m.astype(np.uint8))

def img(path):
    return skia.Image.open(path)

PRINT = {k: img(f"assets/print/{k}.png") for k in ("front", "back_photo", "back_sketch")}

def draw_img(c, im, cx, cy, w, rot=0.0, alpha=1.0):
    h = w * im.height() / im.width()
    c.save(); c.translate(cx, cy); c.rotate(rot)
    c.drawImageRect(im, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear),
                    skia.Paint(Alphaf=alpha))
    c.restore()
    return h

def brackets(c, pw, ph, o=46, L=90, width=10, colr=None):
    br = skia.Paint(Color=colr if colr is not None else col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width)
    for sxn, syn in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x, y = sxn * (pw / 2 + o), syn * (ph / 2 + o)
        p = skia.Path(); p.moveTo(x, y - syn * L); p.lineTo(x, y); p.lineTo(x - sxn * L, y); c.drawPath(p, br)

def framed_print(c, im, cx, cy, pw, rot=0.0, scale=1.0, border=22, tape=False):
    """A photo (skia image) as a print: cream border, soft shadow, corner brackets, optional red tape."""
    ph = pw * im.height() / im.width()
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(scale, scale)
    sh = skia.Paint(Color=col(INK, 0.45), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawRect(skia.Rect.MakeXYWH(-pw / 2 + 16, -ph / 2 + 26, pw + 2 * border, ph + 2 * border), sh)
    c.drawRect(skia.Rect.MakeXYWH(-pw / 2 - border, -ph / 2 - border, pw + 2 * border, ph + 2 * border), skia.Paint(Color=col(CREAM)))
    c.drawImageRect(im, skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
    brackets(c, pw, ph)
    if tape:
        red_tape(c, -20, -ph / 2 - 4, -9)
    c.restore()
    return ph

def red_tape(c, x, y, rot, tw=190, th=46, seed=31):
    c.save(); c.translate(x, y); c.rotate(rot)
    rng = np.random.default_rng(seed); tp = skia.Path()
    tp.moveTo(-tw / 2, -th / 2)
    for xx in np.linspace(-tw / 2, tw / 2, 12): tp.lineTo(xx, -th / 2 + rng.normal(0, 1.2))
    for yy in np.linspace(-th / 2, th / 2, 6): tp.lineTo(tw / 2 + rng.normal(0, 3), yy)
    for xx in np.linspace(tw / 2, -tw / 2, 12): tp.lineTo(xx, th / 2 + rng.normal(0, 1.2))
    for yy in np.linspace(th / 2, -th / 2, 6): tp.lineTo(-tw / 2 + rng.normal(0, 3), yy)
    c.drawPath(tp, skia.Paint(Color=col(RED, 0.88), AntiAlias=True))
    c.restore()

def torn_rect(w, h, seed, amp=5):
    rng = np.random.default_rng(seed); p = skia.Path(); pts = []
    for x in np.linspace(-w / 2, w / 2, 24): pts.append((x, -h / 2 + rng.normal(0, amp)))
    for y in np.linspace(-h / 2, h / 2, 30): pts.append((w / 2 + rng.normal(0, amp), y))
    for x in np.linspace(w / 2, -w / 2, 24): pts.append((x, h / 2 + rng.normal(0, amp)))
    for y in np.linspace(h / 2, -h / 2, 30): pts.append((-w / 2 + rng.normal(0, amp), y))
    p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p

SCRAP_PAPER = PAPERS[2]

def scrap(c, cx, cy, w, h, rot, seed, k, content, alpha=1.0, veil=0.0, scale=1.0):
    """A torn piece of cream paper that pops on (k: 0..1), with content(c) drawn centred on it."""
    if k <= 0:
        return
    s = lerp(0.6, 1.0, ease_out_back(clamp(k))) * scale
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    if alpha < 1:
        c.saveLayer(None, skia.Paint(Alphaf=alpha))
    path = torn_rect(w, h, seed)
    sh = skia.Paint(Color=col(INK, 0.4), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
    c.save(); c.translate(8, 14); c.drawPath(path, sh); c.restore()
    c.save(); c.clipPath(path, doAntiAlias=True)
    c.drawImageRect(SCRAP_PAPER, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions())
    c.restore()
    content(c)
    if veil > 0:                                                        # greyed out: a paper veil over the content
        c.drawPath(path, skia.Paint(Color=col("#E6E0D2", veil), AntiAlias=True))
    if alpha < 1:
        c.restore()
    c.restore()

def strip(c, k, y0=235, y1=600, seed=5, content=None):
    """Torn paper strip across the top of the frame (above the head). Slides down with k."""
    if k <= 0:
        return
    off = (1 - ease_out_cubic(clamp(k))) * -(y1 + 40)
    c.save(); c.translate(0, off)
    path = torn_rect(W + 60, y1 - y0, seed, amp=7); c.save(); c.translate(W / 2, (y0 + y1) / 2)
    sh = skia.Paint(Color=col(INK, 0.4), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    c.save(); c.translate(0, 12); c.drawPath(path, sh); c.restore()
    c.clipPath(path, doAntiAlias=True); c.translate(-W / 2, -(y0 + y1) / 2); c.drawImage(SCRAP_PAPER, 0, 0); c.restore()
    if content:
        content(c)
    c.restore()

def strike(c, x0, y0, x1, y1, k, seed=1, width=26):
    if k > 0:
        brush(c, x0, y0, x1, y1, width, col(RED), seed, head=ease_out_cubic(k), bristles=12, dry=0.2)

def label(c, s, x, y, size=34, colr=None, align="center", alpha=1.0, font=SANS):
    text(c, s, x, y, size, font, fill=colr if colr is not None else col(INK), align=align, tracking=0.12, alpha=alpha)

def stamp(c, s, x, y, k, rot=-8, size=120, w=None):
    """Red ink stamp: slams in from big (k: 0..1), rough rounded frame."""
    if k <= 0:
        return
    sc = lerp(1.6, 1.0, ease_out_expo(k))
    tw = w or text_width(s, size, SERIF) * 0.9 + 70
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(sc, sc)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-tw / 2, -size * 0.62, tw, size * 1.24), 18, 18)
    c.drawRRect(rr, skia.Paint(Color=col(RED, 0.92), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.09))
    condensed(c, s, 0, 4, size, SERIF, col(RED, 0.92), tw - 50, squeeze=0.9)
    c.restore()

def slam(c, s, cx, cy, size, start, t, colr, max_w=960, squeeze=0.9):
    h = prog(t, start, 0.2)
    if h <= 0:
        return
    sc = lerp(1.25, 1.0, ease_out_expo(h))
    c.save(); c.translate(cx, cy); c.scale(sc, sc)
    condensed(c, s, 0, 0, size, SERIF, colr, max_w, squeeze=squeeze, alpha=clamp(h * 3))
    c.restore()

# ---------------------------------------------------------------- 1. hook cover (0 to W_DIAG)
PH_CX, PH_CY, PH_W = 805, 965, 420
PH_H = PH_W * PRINT["front"].height() / PRINT["front"].width()

def print_photo(c, t):
    rot = 4 + 0.6 * math.sin(t * 1.3)
    c.save(); c.translate(PH_CX, PH_CY + 4 * math.sin(t * 1.1)); c.rotate(rot)
    sh = skia.Paint(Color=col(INK, 0.35), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    c.drawRect(skia.Rect.MakeXYWH(-PH_W / 2 + 10, -PH_H / 2 + 16, PH_W, PH_H), sh)
    c.drawImageRect(PRINT["front"], skia.Rect.MakeXYWH(-PH_W / 2, -PH_H / 2, PH_W, PH_H), skia.SamplingOptions(skia.FilterMode.kLinear))
    brackets(c, PH_W, PH_H, o=22, L=60, width=8)
    red_tape(c, -20, -PH_H / 2 - 4, -9)
    c.restore()

def cover(c, t):
    paper(c, t)
    sx, sy = shake(t, wt("you"))
    c.save(); c.translate(sx, sy)
    red_sun(c, 380, 790, 345, 0.9 + 0.1 * ease_out_back(prog(t, 0.0, 0.35)))
    # top line: INTELLIGENT on a red brush, then PEOPLE
    k = ease_out_cubic(prog(t, wt("intelligent") - 0.05, 0.22))
    iw = text_width("INTELLIGENT", 62, SANS, 0.04)
    brush(c, 52, 295, 70 + iw + 22, 279, 88, col(RED), 3, head=k)
    word(c, "INTELLIGENT", 70, 285, 62, wt("intelligent"), t, col(INK), tracking=0.04)
    word(c, "PEOPLE", 70 + iw + 36, 285, 62, wt("people"), t, col(INK), tracking=0.04)
    # masthead LIKE YOU: outline from the first frame, slams solid on "you"
    hit = prog(t, wt("you"), 0.22)
    push = 1 + 0.015 * prog(t, 0, 3.2)
    MY = 440
    c.save(); c.translate(540, MY); c.scale(push, push); c.translate(-540, -MY)
    if hit <= 0:
        condensed(c, "LIKE YOU", 540, MY, 330, SERIF, col(INK, 0.9), 1000, stroke=3)
    else:
        s = lerp(1.14, 1.0, ease_out_expo(hit))
        c.save(); c.translate(540, MY); c.scale(s, s); c.translate(-540, -MY)
        flash = prog(t, wt("you"), 0.10) < 1
        condensed(c, "LIKE YOU", 540, MY, 330, SERIF, col(RED if flash else INK), 1000)
        c.restore()
    c.restore()
    c.restore()
    # him: the cut-out, slow push-in
    s = lerp(0.74, 0.78, ease_in_out_cubic(prog(t, 0, 3.2)))
    c.save(); c.translate(375 + sx * 0.4, 800 + sy * 0.4); c.scale(s, s)
    c.drawImage(person(t), -540, -960)
    c.restore()
    torn_band(c, col(INK), 4)
    print_photo(c, t)
    y1, y2, y3 = 1350, 1412, 1474
    x = 64
    x += word(c, "CANNOT ", x, y1, 56, wt("cannot"), t, col(CREAM))
    word(c, "BUILD", x, y1, 56, wt("build"), t, col(CREAM))
    x = 64
    x += word(c, "THEIR ", x, y2, 56, wt("their"), t, col(CREAM))
    word(c, "DREAM", x, y2, 56, wt("dream"), t, col(CREAM))
    pw = word(c, "PHYSIQUE.", 64, y3, 56, wt("physique"), t, col(RED))
    scribble_ring(c, ease_out_cubic(prog(t, wt("physique"), 0.35)), PH_CX, PH_CY, PH_W * 0.66, PH_H * 0.6, col(RED))
    arrow(c, ease_out_cubic(prog(t, wt("physique") + 0.12, 0.25)), 64 + pw + 14, y3 - 6, PH_CX - 150, PH_CY + PH_H * 0.52, -60, col(RED))
    tw_ = 1 + 0.25 * math.sin(t * 5)
    star(c, 1010, 175, 24 * (2 - tw_), col(INK))
    star(c, 1010, 1470, 22, col(CREAM), rot=0.2)

# ---------------------------------------------------------------- 2. diagnosis card (W_DIAG to W_ROOM1)
def diagnosis(c, t):
    paper(c, t, CARD_PAPERS)
    sx, sy = shake(t, wt("paralysis"), 12)
    c.save(); c.translate(sx, sy)
    label(c, "DIAGNOSIS:", 540, 300, 44)
    brush(c, 330, 340, 750, 334, 14, col(RED), 71, head=ease_out_cubic(prog(t, W_DIAG, 0.3)), bristles=8)
    bz = ease_out_back(prog(t, W_DIAG - 0.05, 0.35))
    if bz > 0:
        c.save(); c.translate(540, 700); c.scale(bz, bz)
        il.brain(c, 0, 0, 560, t)
        il.tangle(c, -10, -40, 250, 130, ease_in_out_cubic(prog(t, wt("my"), wt("disease") - wt("my"))), t, width=7)
        c.restore()
    slam(c, "ANALYSIS", 540, 1120, 300, wt("analysis"), t, col(INK))
    slam(c, "PARALYSIS.", 540, 1370, 300, wt("paralysis"), t, col(RED))
    brush(c, 150, 1490, 930, 1476, 30, col(RED), 72, head=ease_out_cubic(prog(t, wt("paralysis") + 0.3, 0.25)), bristles=16)
    star(c, 120, 230, 24, col(INK)); star(c, 960, 1560, 24, col(RED), rot=0.3)
    c.restore()

# ---------------------------------------------------------------- 3 to 7. the class story, over the room
def zoom(t):
    """Slow push-ins on the key lines (scale around the face)."""
    z = 1.0
    for a, b, peak in ((wt("at", 15.5), wt("photos", 19.0) + 0.3, 0.06),          # "At the end, the best photos..."
                       (wt("no", 27), wt("are", 28.3) + 0.3, 0.10),               # "no matter how intelligent you are"
                       (wt("with", 39.5), wt("now") + 0.3, 0.08)):                # "With whatever knowledge..."
        if a <= t <= b + 0.6:
            k = ease_in_out_cubic(prog(t, a, b - a)) if t <= b else 1 - ease_in_out_cubic(prog(t, b, 0.6))
            z = max(z, 1 + peak * k)
    return z

def room(c, t):
    z = zoom(t)
    c.save(); c.translate(540, 900); c.scale(z, z); c.translate(-540, -900)
    c.drawImage(to_img(lighten(grade(CUT.array(t)))), 0, 0)
    c.restore()

def beat_class(c, t):
    """A photography professor split his class in two: camera + a row of students split by a red line."""
    a, b = W_ROOM1 + 0.05, wt("one", 9.0) - 0.1
    if not (a <= t <= b + 0.4):
        return
    k = prog(t, a, 0.35) - prog(t, b, 0.35)
    def content(c):
        il.camera(c, 165, 430, 210, t, flash=math.exp(-5 * (t - wt("photography"))) if t >= wt("photography") else 0)
        label(c, "PHOTOGRAPHY CLASS", 690, 292, 30, alpha=clamp((t - wt("photography")) * 4))
        n_on = int(clamp((t - wt("professor")) / 0.5) * 10)
        sep = ease_out_cubic(prog(t, wt("two"), 0.3)) * 26
        for i in range(n_on):
            x = 335 + 70 * i + (-sep if i < 5 else sep)
            il.figure(c, x, 560, 150, t, fit=True, alpha=0.9)
        sk = prog(t, wt("split"), 0.25)
        if sk > 0:
            brush(c, 685, 330, 680, 580, 16, col(RED), 81, head=ease_out_cubic(sk), bristles=8)
        g = clamp((t - wt("two")) * 4)
        if g > 0:
            label(c, "A", 510 - sep, 345, 40, colr=col(RED), alpha=g)
            label(c, "B", 860 + sep, 345, 40, colr=col(RED), alpha=g)
    strip(c, k, content=content)

PILE = [(np.random.default_rng(i).uniform(-70, 70), np.random.default_rng(i + 50).uniform(-60, 90),
         np.random.default_rng(i + 99).uniform(-24, 24)) for i in range(16)]

def group_a(c, t):
    """Scrap left of the head: GROUP A / QUANTITY, photos pile up, counter runs."""
    a = wt("one", 9.0)
    out = wt("the", 20.0) - 0.1
    if not (a <= t <= out + 0.35):
        return
    k = prog(t, a, 0.25)
    leave = ease_in_cubic(prog(t, out, 0.35))
    def content(c):
        label(c, "GROUP A", 0, -168, 34)
        q = prog(t, wt("graded"), 0.25)
        if q > 0:
            brush(c, -118, -110, 118, -116, 52, col(RED), 91, head=ease_out_cubic(q), bristles=14)
            label(c, "QUANTITY", 0, -114, 30, colr=col(CREAM))
        p0, p1 = wt("graded"), wt("took") + 0.4
        n = int(clamp((t - p0) / (p1 - p0)) * len(PILE))
        for i in range(n):
            dx, dy, r = PILE[i]
            il.photo_print(c, dx, 40 + dy * 0.8, 120, t, rot=r, seed=i)
        if t >= p0:
            cnt = int(clamp((t - p0) / (p1 + 0.8 - p0)) ** 0.7 * 100)
            label(c, f"x{cnt}", 0, 178, 40, colr=col(RED))
        win = prog(t, wt("best"), 0.35)
        if win > 0:
            scribble_ring(c, ease_out_cubic(win), 0, 40, 165, 200, col(RED), seed=5)
        stamp(c, "WINNER", 0, 95, prog(t, wt("photos", 16.8), 0.12), rot=-12, size=84, w=270)
    x = lerp(158, -260, leave) - 400 * (zoom(t) - 1)                   # step aside while the face pushes in
    scrap(c, x, 880, 300, 420, -4, 21, k, content, scale=0.92)

def group_b(c, t):
    """Scrap right of the head: GROUP B / QUALITY, one empty frame, a big red 1. Fades when A wins."""
    a = wt("the", 12.0)
    out = wt("the", 20.0) - 0.1
    if not (a <= t <= out + 0.35):
        return
    k = prog(t, a, 0.25)
    leave = ease_in_cubic(prog(t, out, 0.35))
    veil = 0.6 * ease_out_cubic(prog(t, wt("all", 17.0), 0.4))
    def content(c):
        label(c, "GROUP B", 0, -168, 34)
        q = prog(t, wt("perfect", 14.5), 0.25)
        if q > 0:
            brush(c, -108, -110, 108, -116, 52, col(INK), 92, head=ease_out_cubic(q), bristles=14)
            label(c, "QUALITY", 0, -114, 30, colr=col(CREAM))
        il.photo_print(c, 0, 40, 170, t, rot=3, empty=True)
        one = prog(t, wt("one", 13.4), 0.18)
        if one > 0:
            s = lerp(1.5, 1.0, ease_out_expo(one))
            c.save(); c.translate(0, 30); c.scale(s, s)
            condensed(c, "1", 0, 0, 200, SERIF, col(RED), 200, squeeze=1.0)
            c.restore()
        label(c, "ONE SHOT", 0, 178, 30, colr=col(RED), alpha=clamp((t - wt("chance")) * 4))
    x = lerp(922, 1340, leave) + 400 * (zoom(t) - 1)
    scrap(c, x, 880, 300, 420, 5, 22, k, content, veil=veil, scale=0.92)

def beat_thinking(c, t):
    """The perfect photo group just sat around thinking: sitting figure, empty frame in a thought bubble, 0 PHOTOS."""
    a, b = wt("the", 20.0), W_POSTER
    if not (a <= t <= b):
        return
    k = prog(t, a, 0.35)
    def content(c):
        label(c, "GROUP B", 150, 292, 30, colr=col(RED))
        il.sitting_figure(c, 200, 585, 270, t)
        tb = ease_out_back(prog(t, wt("thinking"), 0.35))
        il.thought_bubble(c, 500, 395, 330, 230, t, k=tb)
        if tb > 0.5:
            il.photo_print(c, 500, 400, 120 * tb, t, rot=-4, empty=True)
            c.save(); c.translate(500, 335)
            text(c, "?", 0, 0, 52, SERIF, fill=col(RED), align="center", alpha=clamp((tb - 0.5) * 2))
            c.restore()
        z = prog(t, wt("perfection"), 0.18)
        if z > 0:
            s = lerp(1.4, 1.0, ease_out_expo(z))
            c.save(); c.translate(860, 420); c.scale(s, s)
            condensed(c, "0", 0, -20, 230, SERIF, col(RED), 200, squeeze=1.0)
            label(c, "PHOTOS", 0, 120, 34, colr=col(RED))
            c.restore()
    strip(c, k, y0=235, y1=620, seed=6, content=content)

# ---------------------------------------------------------------- 8. poster: repeated actions (W_POSTER to W_ROOM2)
QUOTE = [("REPEATED ACTIONS", "repeated"), ("WILL TEACH YOU THINGS", "will"), ("YOUR THOUGHTS", "your"),
         ("NEVER CAN,", "never")]

def poster(c, t):
    paper(c, t, CARD_PAPERS)
    red_sun(c, 540, 720, 400, ease_out_back(prog(t, W_POSTER, 0.4)))
    flip = t >= FLIP
    fr = (GYM3 if flip else GYM1).array(t)[..., :3]
    h0 = prog(t, FLIP if flip else W_POSTER, 0.18)
    s = lerp(1.18, 1.0, ease_out_expo(h0))
    sx, sy = shake(t, FLIP if flip else W_POSTER + 0.05, 14)
    pw = 640
    c.save(); c.translate(sx, sy)
    framed_print(c, to_img(fr), 540, 730, pw, rot=(3 if flip else -3) + 1.0 * math.sin(t * 1.4), scale=s)
    c.restore()
    label(c, "THE LESSON", 540, 270, 34, colr=col(RED))
    for i, (s_, key) in enumerate(QUOTE):
        st = wt(key, W_POSTER - 0.5)
        p = ease_out_cubic(prog(t, st - 0.05, 0.25))
        if p <= 0:
            continue
        colr = col(RED) if i == len(QUOTE) - 1 else col(INK)
        text(c, s_, 540, 1265 + i * 72 + (1 - p) * 20, 64, QSERIF, fill=colr, align="center", alpha=p)
    star(c, 110, 230, 24, col(INK)); star(c, 970, 230, 24, col(INK))

# ---------------------------------------------------------------- 10. stop chasing perfect (strip over the room)
def beat_stop(c, t):
    a, b = wt("stop"), W_CARD
    if not (a <= t <= b):
        return
    k = prog(t, a - 0.05, 0.35)
    def content(c):
        items = ((il.dumbbell, 190, 410, 250, "EXERCISE", wt("exercise"), wt("perfect", 30.4)),
                 (il.plate, 540, 420, 270, "DIET", wt("diet"), wt("perfect", 31.6)),
                 (il.clipboard, 890, 415, 190, "PROGRAM", wt("program"), wt("perfect", 32.7)))
        for fn, x, y, size, name, t_item, t_perf in items:
            p = prog(t, t_perf - 0.05, 0.25)
            if p > 0:
                c.save(); c.translate(x, y); sc = ease_out_back(p); c.scale(sc, sc)
                fn(c, 0, 0, size, t)
                c.restore()
                label(c, name, x, 568, 30)
            q = clamp((t - t_perf) * 5)
            if q > 0:
                label(c, "PERFECT", x, 282, 28, colr=col(RED), alpha=q)
        strike(c, 70, 470, 1010, 380, prog(t, wt("program") + 0.35, 0.35), seed=7, width=30)
    strip(c, k, y0=235, y1=610, seed=8, content=content)

# ---------------------------------------------------------------- 11. exist first, then perfect (W_CARD to W_ROOM3)
SK_CX, SK_CY, SK_W = 540, 820, 600

def reveal_mask(c, k, seed, w, h, direction=1):
    """Brush strokes covering the print area from top to bottom as k goes 0..1 (drawn into the current layer)."""
    for i in range(5):
        d = i * 0.12
        head = ease_out_cubic(clamp((k - d) / 0.5))
        y = -h / 2 + (i + 0.5) * h / 5
        brush(c, -w / 2 - 80, y + 40 * direction, w / 2 + 80, y - 40 * direction, h / 5 * 1.7, col(INK), seed + i,
              head=head, bristles=26, dry=0.1)

def exist_card(c, t):
    paper(c, t, CARD_PAPERS)
    sk, ph = PRINT["back_sketch"], PRINT["back_photo"]
    w = SK_W; h = w * sk.height() / sk.width()
    c.save(); c.translate(SK_CX, SK_CY); c.rotate(-2 + 0.6 * math.sin(t * 1.2))
    sh = skia.Paint(Color=col(INK, 0.35), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, -h / 2 + 22, w, h), sh)
    c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.Paint(Color=col(CREAM)))
    rect = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    # the sketch draws itself on "bring it into existence", top to bottom
    e = prog(t, wt("bring") - 0.1, wt("first", 35.8) - wt("bring") + 0.2)
    if e > 0:
        c.saveLayer(rect, None)
        reveal_mask(c, e, 101, w, h)
        c.drawImageRect(sk, rect, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(BlendMode=skia.BlendMode.kSrcIn))
        c.restore()
    # then the real photo paints in on "make it perfect"
    f = prog(t, wt("make", 37.0) - 0.1, wt("perfect", 37.3) - wt("make", 37.0) + 0.45)
    if f > 0:
        c.saveLayer(rect, None)
        reveal_mask(c, f, 111, w, h, direction=-1)
        c.drawImageRect(ph, rect, skia.SamplingOptions(skia.FilterMode.kLinear), skia.Paint(BlendMode=skia.BlendMode.kSrcIn))
        c.restore()
    brackets(c, w, h, o=30, L=70, width=9)
    c.restore()
    # the two steps
    for num, name, start, x, colr in (("1", "EXIST", wt("existence"), 270, INK), ("2", "PERFECT", wt("perfect", 37.3), 790, RED)):
        p = prog(t, start, 0.2)
        if p <= 0:
            continue
        s = lerp(1.4, 1.0, ease_out_expo(p))
        bw = text_width(f"{num}. {name}", 56, SANS, 0.06) / 2 + 26
        c.save(); c.translate(x, 300); c.scale(s, s)
        brush(c, -bw, 6, bw, -4, 92, col(colr), 120 + int(x), head=ease_out_cubic(p))
        text(c, f"{num}. {name}", 0, 0, 56, SANS, fill=col(CREAM), align="center", tracking=0.06)
        c.restore()
    arrow(c, ease_out_cubic(prog(t, wt("then", 36.8), 0.25)), 445, 300, 575, 300, 0, col(INK))
    # not the other way around: PERFECT FIRST? crossed out
    n = prog(t, wt("not", 38.2), 0.2)
    if n > 0:
        s = lerp(1.3, 1.0, ease_out_expo(n))
        c.save(); c.translate(540, 1370); c.scale(s, s)
        condensed(c, "PERFECT FIRST?", 0, 0, 150, SERIF, col(INK), 900, squeeze=0.85, alpha=clamp(n * 3))
        c.restore()
        il.red_x(c, 540, 1365, 330, prog(t, wt("way", 38.9), 0.4), t)
    star(c, 110, 1560, 24, col(INK)); star(c, 970, 230, 24, col(RED), rot=0.3)

# ---------------------------------------------------------------- 13. end card (W_END to the end)
def end_card(c, t):
    paper(c, t, PAPERS)
    red_sun(c, 540, 850, 400, ease_out_back(prog(t, W_END, 0.4)))
    fr = SIDE.array(t)[..., :3]
    sx, sy = shake(t, wt("start", 42.3), 16)
    c.save(); c.translate(sx, sy)
    framed_print(c, to_img(fr), 540, 860, 520, rot=-3 + 0.8 * math.sin(t * 1.3), tape=True)
    slam(c, "JUST", 540, 330, 300, wt("just", 42.0), t, col(INK))
    slam(c, "START.", 540, 1410, 330, wt("start", 42.3), t, col(RED))
    c.restore()
    star(c, 110, 230, 26, col(INK)); star(c, 970, 1580, 26, col(RED))

# ---------------------------------------------------------------- captions (reel-01 style)
EMPH = {"many", "perfect", "best", "intelligent", "now,", "start.", "stop", "most"}
EMPH_AT = {("perfect", 14.8), ("intelligent", 28.0), ("best", 16.6), ("many", 10.9), ("now,", 41.4), ("stop", 29.7)}
CAPTION_OFF = [(0, W_ROOM1 + 0.05), (W_POSTER - 0.2, W_ROOM2 + 0.05), (W_CARD - 0.2, W_ROOM3 + 0.05), (W_END - 0.2, DUR + 1)]
CAP_Y = 1440

def make_groups():
    groups, cur = [], []
    for w_ in WORDS:
        cur.append(w_)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= 3 or w_["w"][-1] in ".,?!\"'" or len(txt) > 16:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        end = groups[i + 1][0]["s"] if i + 1 < len(groups) else g[-1]["e"] + 0.4
        end = min(end, g[-1]["e"] + 0.6)
        words = [(x["w"].strip("\"'").upper(),
                  any(x["w"].lower() == k and abs(x["s"] - ts) < 0.6 for k, ts in EMPH_AT)) for x in g]
        out.append((g[0]["s"], end, words))
    return out

GROUPS = make_groups()

def captions(c, t):
    if any(a <= t < b for a, b in CAPTION_OFF):
        return
    for s0, s1, words in GROUPS:
        if s0 - 0.02 <= t < s1:
            size = 62
            gap = size * 0.28
            widths = [text_width(w_, size, SANS, 0.01) for w_, _ in words]
            x = 540 - (sum(widths) + gap * (len(words) - 1)) / 2
            pop = lerp(0.88, 1.0, ease_out_back(prog(t, s0, 0.14)))
            c.save(); c.translate(540, CAP_Y); c.scale(pop, pop); c.translate(-540, -CAP_Y)
            for (w_, em), wd in zip(words, widths):
                if em:
                    brush(c, x - 10, CAP_Y + 6, x + wd + 10, CAP_Y, size * 1.05, col(RED), int(s0 * 10) % 50, bristles=14, dry=0.15)
                text(c, w_, x, CAP_Y, size, SANS, fill=col(CREAM), align="left", tracking=0.01, stroke=7, stroke_col=col(INK))
                x += wd + gap
            c.restore()
            break

# ---------------------------------------------------------------- frame
def draw(c, t):
    if t < W_DIAG:
        cover(c, t)
    elif t < W_ROOM1:
        diagnosis(c, t)
    elif W_POSTER <= t < W_ROOM2:
        poster(c, t)
    elif W_CARD <= t < W_ROOM3:
        exist_card(c, t)
    elif t >= W_END:
        end_card(c, t)
    else:
        room(c, t)
        for b in (beat_class, group_a, group_b, beat_thinking, beat_stop):
            b(c, t)
    captions(c, t)
    for mid, colr, seed, d in WIPES:
        wipe(c, t, mid - 0.2, mid, mid + 0.22, col(colr) if isinstance(colr, str) else colr, seed, direction=d)

def post(arr, t):
    return grain(vignette(arr, 0.14), 0.026, seed=int(t * FPS))

S = Stage(W, H, fps=FPS, duration=DUR)

def sheet(step=2.5, out="out/stills/contact.png"):
    """Contact sheet: one frame every `step` s of the finished video, each labelled with its time."""
    from PIL import Image, ImageDraw, ImageFont
    ts = [round(i * step, 2) for i in range(int(DUR / step) + 1) if i * step < DUR]
    paths = S.stills(draw, ts, out_dir="out/stills/sheet", post=post)
    cols = 6; tw, th = 270, 480
    rows = math.ceil(len(paths) / cols)
    im = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * (th + 44) + 10), (24, 24, 24))
    f = ImageFont.truetype("fonts/InterTight-800.ttf", 26)
    d = ImageDraw.Draw(im)
    for i, (t_, p) in enumerate(zip(ts, paths)):
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 44)
        im.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y + 34))
        d.text((x, y), f"{int(t_ // 60)}:{t_ % 60:04.1f}", fill=(240, 235, 220), font=f)
    im.save(out); print("sheet ->", out, len(ts), "frames")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        ts = [float(x) for x in sys.argv[2:]]
        S.stills(draw, ts, out_dir="out/stills/reel", post=post)
    elif cmd == "sheet":
        sheet()
    elif cmd == "draft":
        S.render(draw, "out/reel-02_draft.mp4", draft=True, post=post)
    elif cmd == "render":
        S.render(draw, "out/reel-02_silent.mp4", post=post, crf=14, preset="veryfast")    # master only; delivery is re-encoded
