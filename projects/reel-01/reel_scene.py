"""reel-01: the whole edit, in finished-video time (edit time). Beat sheet: brief.md section 6.

    python3 reel_scene.py stills 6.0 9.0 ...     # check frames -> out/stills/reel/
    python3 reel_scene.py draft                   # half size, half fps -> out/reel-01_draft.mp4
    python3 reel_scene.py render                  # full -> out/reel-01_silent.mp4 (audio is mixed by work/mix.py)

Footage: work/cut.mp4 (the take cut by work/cut_plan.json). Word times: work/words_cut.json.
The hook and card 01 come from hook_scene.py, which runs on source time (edit time + HOOK_OFF).
"""
import json
import math
import sys

import numpy as np
import skia

sys.path.insert(0, "vibe")
sys.path.insert(0, ".")
import hook_scene as hk
import illus as il
from hook_scene import (CARD_PAPERS, CREAM, INK, PAPERS, RED, SANS, SERIF, brush, col, condensed, grade, paper, red_sun,
                        scribble_ring, shake, star, wipe, word)
from motion_kit import Stage, clamp, ease_in_cubic, ease_in_out_cubic, ease_out_back, ease_out_cubic, ease_out_expo, \
    grain, lerp, noise1, prog, text, text_width, vignette
from vframes import StreamFrames

W, H, FPS = 1080, 1920, 30
PLAN = json.load(open("work/cut_plan.json"))
DUR = round(PLAN["length"] + 1.5, 3)                           # 1.5 s hold on the end card
HOOK_OFF = PLAN["segments"][0]["src_in"] - PLAN["segments"][0]["edit_in"]
WORDS = json.load(open("work/words_cut.json"))

def wt(word, after=-1.0):
    """Edit time of the first occurrence of a word starting after `after` (case and punctuation ignored)."""
    key = word.lower().strip(".,!?'\"")
    for x in WORDS:
        if x["s"] > after and x["w"].lower().strip(".,!?'\"") == key:
            return x["s"]
    raise KeyError(f"{word} after {after}")

# ---------------------------------------------------------------- scene windows (edit time), wipes centred on *_MID
W1 = 3.32                                   # red wipe: cover -> card 01   (matches hook_scene WIPE1_MID in source)
W2 = 4.42                                   # black wipe: card 01 -> room
C2_IN, C2_OUT = 14.60, 15.74                # card 02
PAY_IN = wt("this")                          # payoff print slams in on "this."
P1_IN, P1_OUT = 25.12, 30.42                # Seneca poster 1
C3_IN, C3_OUT = 37.08, 38.30                # card 03
P2_OUT = 45.12                              # Seneca poster 2 ends
END_IN = 54.58                              # end card
WIPES = [(W1, RED, 40, 1), (W2, INK, 60, -1), (C2_IN, RED, 41, 1), (C2_OUT, INK, 61, -1), (P1_IN, RED, 42, 1),
         (P1_OUT, INK, 62, -1), (C3_IN, RED, 43, 1), (C3_OUT, INK, 63, -1), (P2_OUT, INK, 64, 1), (END_IN, RED, 44, -1)]

# ---------------------------------------------------------------- footage
CUT = StreamFrames("work/cut.mp4", fps=FPS)
GLOW_SRC = StreamFrames("work/glow_src.mp4", fps=FPS, offset=11.6)
GLOW_MAT = StreamFrames("work/matte/glow_src_alpha_clean.mp4", fps=FPS, offset=11.6)
GYM = StreamFrames("work/gym_print.mp4", fps=FPS, offset=0.0)

def to_img(rgb):
    a = np.ascontiguousarray(np.dstack([rgb[..., :3], np.full(rgb.shape[:2], 255, np.uint8)]))
    return skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType)

def lighten(rgb):
    return np.clip(rgb.astype(np.float32) * 1.05 + 6, 0, 255).astype(np.uint8)

def zoom(t):
    """Slow push-ins on the key lines (scale around the face)."""
    z = 1.0
    for a, b, peak in ((wt("you", 12) - 0.05, wt("different") + 0.4, 0.10),        # "You, my friend, are different"
                       (wt("but"), wt("this") - 0.02, 0.08),                      # "...looking like this"
                       (wt("just"), wt("wind", 35) + 0.4, 0.06),                    # "Just pick a harbor"
                       (wt("you", 45) - 0.05, wt("it", 47) + 0.4, 0.06),            # "You can't fix your body..."
                       (wt("when", 52), wt("flaws") + 0.5, 0.07)):                  # "When you forgive yourself"
        if a <= t <= b + 0.6:
            k = ease_in_out_cubic(prog(t, a, b - a)) if t <= b else 1 - ease_in_out_cubic(prog(t, b, 0.6))
            z = max(z, 1 + peak * k)
    return z

def glow_alpha(t):
    """Red outline around him for 'You, my friend, are different'."""
    import cv2
    m = GLOW_MAT.array(t)[..., 0]
    big = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
    ring = cv2.GaussianBlur(np.clip(big.astype(np.int16) - m, 0, 255).astype(np.uint8), (0, 0), 9)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 0], rgba[..., 1], rgba[..., 2] = 211, 55, 43; rgba[..., 3] = ring
    return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)

def room(c, t):
    z = zoom(t)
    c.save(); c.translate(540, 900); c.scale(z, z); c.translate(-540, -900)
    c.drawImage(to_img(lighten(grade(CUT.array(t)))), 0, 0)
    g0, g1 = wt("you", 12) - 0.1, wt("different") + 0.45
    if g0 <= t <= g1 + 0.35:
        k = ease_out_cubic(prog(t, g0, 0.4)) * (1 - ease_in_cubic(prog(t, g1, 0.35)))
        k *= 0.8 + 0.2 * math.sin(t * 9)
        c.drawImage(glow_alpha(t), 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=k))
    c.restore()

# ---------------------------------------------------------------- printed images
def img(path):
    return skia.Image.open(path)

PRINT = {k: img(f"assets/print/{k}.png") for k in ("ship", "dice", "beer", "pizza", "mirror", "lighthouse", "seneca")}
PHYS = hk.PHOTO                                                    # the framed physique print from the hook

def draw_img(c, im, cx, cy, w, rot=0.0, alpha=1.0):
    h = w * im.height() / im.width()
    c.save(); c.translate(cx, cy); c.rotate(rot)
    c.drawImageRect(im, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(skia.FilterMode.kLinear),
                    skia.Paint(Alphaf=alpha))
    c.restore()
    return h

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

def scrap(c, cx, cy, w, h, rot, seed, k, content, alpha=1.0):
    """A torn piece of cream paper that pops on (k: 0..1), with content(c) drawn centred on it."""
    if k <= 0:
        return
    s = lerp(0.6, 1.0, ease_out_back(clamp(k)))
    c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    path = torn_rect(w, h, seed)
    sh = skia.Paint(Color=col(INK, 0.4 * alpha), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
    c.save(); c.translate(8, 14); c.drawPath(path, sh); c.restore()
    c.save(); c.clipPath(path, doAntiAlias=True)
    c.drawImageRect(SCRAP_PAPER, skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), skia.SamplingOptions(), skia.Paint(Alphaf=alpha))
    c.restore()
    content(c)
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

def strike(c, x0, y0, x1, y1, k, seed=1):
    if k > 0:
        brush(c, x0, y0, x1, y1, 26, col(RED), seed, head=ease_out_cubic(k), bristles=12, dry=0.2)

def tick(c, x, y, s, k):
    if k <= 0:
        return
    from toon_kit import draw_on
    p = skia.Path(); p.moveTo(x - s * 0.5, y); p.lineTo(x - s * 0.1, y + s * 0.4); p.lineTo(x + s * 0.6, y - s * 0.5)
    c.drawPath(draw_on(p, ease_out_cubic(k)), skia.Paint(Color=col(RED), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                         StrokeWidth=s * 0.16, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join))

def label(c, s, x, y, size=34, colr=None, align="center", alpha=1.0):
    text(c, s, x, y, size, SANS, fill=colr if colr is not None else col(INK), align=align, tracking=0.12, alpha=alpha)

# ---------------------------------------------------------------- beats on top of the room
def beat_90(c, t):
    """90% of people around you are out of shape: strip with 90% and the crowd."""
    a, b = W2 + 0.05, wt("saying") - 0.15
    if not (a <= t <= b + 0.4):
        return
    k = prog(t, a, 0.35) - prog(t, b, 0.35)
    def content(c):
        h = prog(t, wt("90%"), 0.2)
        if h > 0:
            sc = lerp(1.3, 1.0, ease_out_expo(h))
            c.save(); c.translate(205, 420); c.scale(sc, sc)
            condensed(c, "90%", 0, 0, 300, SERIF, col(RED), 330, squeeze=0.8)
            c.restore()
        n_on = int(clamp((t - wt("of", 5)) / (wt("shape") - wt("of", 5))) * 9.999)
        gap = 670 / 10
        for i in range(10):
            x = 385 + gap * (i + 0.5)
            if i == 9:
                il.figure(c, x, 560, 150, t, fit=True)
                ring = prog(t, wt("shape"), 0.35)
                if ring > 0:
                    from toon_kit import draw_on, smooth_path
                    pts = il.ellipse_pts(x, 487, 44, 100, 40, -1.4, -1.4 + 2.15 * math.pi)
                    c.drawPath(draw_on(smooth_path(pts, closed=False), ease_out_cubic(ring)),
                               skia.Paint(Color=col(RED), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6,
                                          StrokeCap=skia.Paint.kRound_Cap))
            elif i < n_on:
                il.figure(c, x, 560, 142 * (0.97 + 0.03 * math.sin(i * 1.7)), t, fit=False, alpha=0.55, wob=1)
        label(c, "OUT OF SHAPE", 735, 285, 30, alpha=clamp((t - wt("shape")) * 4))
    strip(c, k, content=content)

def beat_habits(c, t):
    """Pizza and beer pop in on 'their habits', ticks on 'yes', red X on 'Say no'."""
    a, b = wt("their"), C2_IN
    if not (a <= t <= b):
        return
    dim = 1.0
    xk = prog(t, wt("say"), 0.25)
    for (key, cx, cy, w, h, rot, seed, start, tick_t) in (("pizza", 165, 900, 290, 300, -8, 3, wt("their"), wt("yes", 7.3)),
                                                          ("beer", 918, 880, 270, 320, 7, 4, wt("habits"), wt("yes", 8.8))):
        def content(c, key=key, w=w, h=h, tick_t=tick_t, seed=seed):
            draw_img(c, PRINT[key], 0, 8, w * 0.82)
            tick(c, w * 0.28, -h * 0.34, 56, prog(t, tick_t, 0.2))
            if xk > 0:
                il.red_x(c, 0, 0, w * 0.9, xk, t)
        scrap(c, cx, cy, w, h, rot, seed, prog(t, start, 0.25), content, alpha=dim)
    s = prog(t, wt("no"), 0.12)
    if s > 0:
        sc = lerp(1.6, 1.0, ease_out_expo(s))
        c.save(); c.translate(540, 420); c.rotate(-8); c.scale(sc, sc)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-230, -120, 460, 240), 20, 20)
        c.drawRRect(rr, skia.Paint(Color=col(RED, 0.92), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=14))
        condensed(c, "NO.", 0, 6, 230, SERIF, col(RED, 0.92), 400, squeeze=0.9)
        c.restore()

def beat_luck(c, t):
    """genetics / family / circumstances on a strip, struck through."""
    a, b = wt("you", 15.5) - 0.1, wt("i") - 0.25
    if not (a <= t <= b + 0.4):
        return
    k = prog(t, a, 0.35) - prog(t, b, 0.35)
    def content(c):
        for name, start, x in (("genetics", wt("genetics"), 190), ("family", wt("family"), 540), ("circumstances", wt("circumstances"), 890)):
            p = prog(t, start, 0.22)
            if p <= 0:
                continue
            c.save(); c.translate(x, 400); s = lerp(0.5, 1.0, ease_out_back(p)); c.scale(s, s)
            if name == "genetics":
                il.dna(c, 0, -10, 250, t)
            elif name == "family":
                il.family_tree(c, 0, -20, 260, t)
            else:
                draw_img(c, PRINT["dice"], 0, -20, 230)
            label(c, name.upper(), 0, 150, 30)
            c.restore()
        strike(c, 60, 430, 1020, 380, prog(t, wt("circumstances") + 0.45, 0.35), seed=7)
    strip(c, k, y0=225, y1=600, seed=8, content=content)

def beat_diabetes(c, t):
    a, b = wt("i") - 0.1, wt("but") + 0.2
    if not (a <= t <= b + 0.4):
        return
    k = prog(t, a, 0.35) - prog(t, b, 0.35)
    def content(c):
        p = prog(t, wt("type"), 0.3)
        if p > 0:
            il.insulin_pen(c, 270, 420, 360 * ease_out_back(p), t)
            il.blood_drop(c, 420, 330, 100 * ease_out_back(prog(t, wt("diabetes"), 0.25)), t)
        q = prog(t, wt("diabetes"), 0.25)
        if q > 0:
            brush(c, 560, 360, 1000, 350, 86, col(RED), 21, head=ease_out_cubic(q))
            text(c, "TYPE 1 DIABETES", 580, 357, 52, SANS, fill=col(INK), align="left", tracking=0.02)
        label(c, "SINCE CHILDHOOD", 580, 455, 36, align="left", alpha=clamp((t - wt("child")) * 4))
    strip(c, k, y0=225, y1=560, seed=9, content=content)

def beat_dice(c, t):
    """Dice tumble in on 'luck' and land beside him."""
    a, b = wt("luck", 30), wt("just") - 0.1
    if not (a - 0.2 <= t <= b + 0.3):
        return
    p = ease_out_cubic(prog(t, a - 0.2, 0.7))
    out = ease_in_cubic(prog(t, b, 0.3))
    x = lerp(1250, 905, p) + out * 400; y = 880 - 140 * math.sin(p * math.pi) * (1 - p) * 2
    rot = (1 - p) * 540
    def content(c):
        draw_img(c, PRINT["dice"], 0, 0, 230, rot=rot * 0.1)
    scrap(c, x, y, 260, 280, 6 + rot * 0.05, 11, 1.0, content)

def beat_lighthouse(c, t):
    a, b = wt("just"), C3_IN
    if not (a <= t <= b):
        return
    p = ease_out_cubic(prog(t, a, 0.45))
    x = lerp(-250, 175, p)
    flash = math.exp(-6 * max(0.0, t - wt("harbor", 35))) if t >= wt("harbor", 35) else 0.0
    def content(c):
        hh = draw_img(c, PRINT["lighthouse"], 0, 0, 270)
        if flash > 0.02:
            g = skia.Paint(Color=col(RED, 0.7 * flash), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
            c.drawCircle(0, -hh / 2 + 0.198 * hh, 60 + 40 * flash, g)
    scrap(c, x, 880, 310, 520, -5, 12, 1.0, content)

MIRROR_GLASS = (0.392, 0.50, 0.236, 0.345, -11)          # mirror.png: glass centre x, y, radius x, y (fractions), tilt

def beat_mirror(c, t):
    a, b = P2_OUT + 0.15, wt("when", 47.5) - 0.1
    if not (a <= t <= b + 0.3):
        return
    p = prog(t, a, 0.3) - prog(t, b, 0.3)
    reveal = ease_in_out_cubic(prog(t, wt("look", 46) - 0.05, 0.5))
    def content(c):
        im = PRINT["mirror"]; w = 330; h = w * im.height() / im.width()
        draw_img(c, im, 0, 0, w)
        gx, gy, rx, ry, tilt = MIRROR_GLASS
        if reveal > 0:                                                   # the reflection: a generic ink face, not his
            c.save(); c.translate(-w / 2 + gx * w, -h / 2 + gy * h); c.rotate(tilt)
            glass = skia.Path(); glass.addOval(skia.Rect.MakeXYWH(-rx * w, -ry * h, 2 * rx * w, 2 * ry * h))
            c.clipPath(glass, doAntiAlias=True)
            c.saveLayer(skia.Rect.MakeXYWH(-rx * w, -ry * h, 2 * rx * w, 2 * ry * h), skia.Paint(Alphaf=reveal))
            c.drawRect(skia.Rect.MakeXYWH(-rx * w, -ry * h, 2 * rx * w, 2 * ry * h), skia.Paint(Color=col("#D9D2C2")))
            il.generic_face(c, 0, ry * h * 0.05, 2 * rx * w * 1.35, t)
            glare = skia.Paint(Color=skia.Color(255, 255, 255, 70), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                               StrokeWidth=rx * w * 0.35, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
            c.drawLine(-rx * w * 0.6, ry * h, rx * w * 0.2, -ry * h, glare)
            c.restore(); c.restore()
    scrap(c, 185, 880, 360, 400, -6, 13, p, content)

def beat_scale(c, t):
    a, b = wt("when", 47.5) - 0.1, wt("when", 52) - 0.2
    if not (a <= t <= b + 0.4):
        return
    k = prog(t, a, 0.35) - prog(t, b, 0.35)
    def content(c):
        p = prog(t, wt("stepping"), 0.25)
        if p > 0:
            c.save(); c.translate(290, 390); s = ease_out_back(p); c.scale(s, s)
            il.bathroom_scale(c, 0, 0, 320, t, needle=0.3 + 0.5 * ease_out_cubic(prog(t, wt("scale"), 0.6)))
            c.restore()
        q = prog(t, wt("tracking"), 0.25)
        if q > 0:
            c.save(); c.translate(790, 400); s = ease_out_back(q); c.scale(s, s)
            il.food_diary(c, 0, 0, 340, t)
            c.restore()
        strike(c, 110, 450, 480, 330, prog(t, wt("and", 50), 0.3), seed=3)
        strike(c, 600, 460, 990, 340, prog(t, wt("eat"), 0.3), seed=4)
    strip(c, k, y0=225, y1=590, seed=14, content=content)

def beat_flaws(c, t):
    a, b = wt("look", 53) - 0.1, END_IN
    if not (a <= t <= b):
        return
    p = prog(t, a, 0.3)
    m = ease_in_out_cubic(prog(t, wt("at", 53.7), 1.1))
    def content(c):
        pw = 300; ph = pw * PHYS.height() / PHYS.width()
        c.drawImageRect(PHYS, skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
        mx, my = lerp(-60, 50, m), lerp(-120, 60, m)
        def under(c, cx, cy, r):
            z = 1.9
            c.save(); c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)
            c.drawImageRect(PHYS, skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
            c.restore()
        il.magnifier(c, mx, my, 260, t, under=under)
    scrap(c, 885, 880, 330, 440, 6, 15, p, content)

# ---------------------------------------------------------------- full-screen designs
def card_n(c, t, num, small, big1, big2, t_small, t_big1, t_big2, t_start, seed):
    paper(c, t, CARD_PAPERS)
    sx, sy = shake(t, t_big1, 10)
    c.save(); c.translate(sx, sy)
    k = ease_out_cubic(prog(t, t_start, 0.25))
    brush(c, 380, 560, 700, 548, 120, col(RED), seed, head=k)
    condensed(c, num, 540, 552, 150, SERIF, col(INK), 400, squeeze=0.9)
    word(c, small, 540 - text_width(small, 78, SANS, 0.12) / 2, 760, 78, t_small, t, col(INK), tracking=0.12)
    for wd, start, cy in ((big1, t_big1, 980), (big2, t_big2, 1270)):
        h = prog(t, start, 0.2)
        if h > 0:
            s = lerp(1.25, 1.0, ease_out_expo(h))
            c.save(); c.translate(540, cy); c.scale(s, s)
            condensed(c, wd, 0, 0, 330, SERIF, col(INK), 900, squeeze=0.95, alpha=clamp(h * 3))
            c.restore()
    u = ease_out_cubic(prog(t, t_big2 + 0.12, 0.25))
    brush(c, 150, 1440, 930, 1424, 34, col(RED), seed + 1, head=u, bristles=16)
    star(c, 120, 400, 24, col(INK)); star(c, 960, 1480, 24, col(RED), rot=0.3)
    c.restore()

def payoff(c, t):
    """Gym clip as a big framed print, slammed in on 'this'."""
    paper(c, t, PAPERS)
    red_sun(c, 540, 900, 470, 1.0)
    h = prog(t, PAY_IN, 0.18)
    s = lerp(1.18, 1.0, ease_out_expo(h))
    sx, sy = shake(t, PAY_IN, 16)
    fr = GYM.array(t - PAY_IN)
    pw, ph = 860, 860 * fr.shape[0] / fr.shape[1]
    c.save(); c.translate(540 + sx, 900 + sy); c.rotate(-3 + 1.2 * math.sin(t * 1.4)); c.scale(s, s)
    sh = skia.Paint(Color=col(INK, 0.45), AntiAlias=True, MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawRect(skia.Rect.MakeXYWH(-pw / 2 - 6, -ph / 2 + 10, pw + 44, ph + 44), sh)
    c.drawRect(skia.Rect.MakeXYWH(-pw / 2 - 22, -ph / 2 - 22, pw + 44, ph + 44), skia.Paint(Color=col(CREAM)))
    c.drawImageRect(to_img(grade(fr)), skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
    br = skia.Paint(Color=col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=10)
    o, L = 46, 90
    for sxn, syn in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x, y = sxn * (pw / 2 + o), syn * (ph / 2 + o)
        p = skia.Path(); p.moveTo(x, y - syn * L); p.lineTo(x, y); p.lineTo(x - sxn * L, y); c.drawPath(p, br)
    c.restore()

QUOTE1 = [("IF YOU DON'T KNOW", "if"), ("WHICH HARBOR", "which"), ("YOU ARE SAILING FOR,", "sailing"),
          ("NO WIND IS", "no"), ("FAVORABLE.", "favorable")]
QUOTE2 = [("WHY WOULD I BE SCARED", "why"), ("OF MY MISTAKES", "mistakes"), ("WHEN I CAN JUST SAY:", "when"),
          ("I FORGIVE YOU THIS TIME.", "forgive"), ("DON'T DO IT AGAIN.", "don't")]
QSERIF = "Instrument Serif:400"

def quote_lines(c, t, lines, x, y0, size, step, red_last=True, align="left"):
    for i, (s, key) in enumerate(lines):
        st = wt(key, P1_IN - 0.5 if lines is QUOTE1 else C3_OUT - 0.5)
        p = ease_out_cubic(prog(t, st - 0.05, 0.25))
        if p <= 0:
            continue
        colr = col(RED) if (red_last and i == len(lines) - 1) else col(INK)
        text(c, s, x, y0 + i * step + (1 - p) * 20, size, QSERIF, fill=colr, align=align, alpha=p)

def poster1(c, t):
    paper(c, t, CARD_PAPERS)
    rock = 2.0 * math.sin(t * 1.6)
    draw_img(c, PRINT["ship"], 540, 610 + 8 * math.sin(t * 1.3), 760, rot=rock, alpha=ease_out_cubic(prog(t, P1_IN, 0.3)))
    bh = draw_img(c, PRINT["seneca"], 225, 1270, 330)
    brush(c, 80, 1190, 380, 1180, 60, col(RED), 31, head=ease_out_cubic(prog(t, wt("seneca"), 0.3)))
    label(c, "SENECA", 225, 1470, 36)
    quote_lines(c, t, QUOTE1, 420, 1110, 66, 78)
    star(c, 980, 230, 24, col(INK)); star(c, 100, 230, 24, col(INK))

CRACK = [(0.52, 0.02), (0.47, 0.16), (0.55, 0.27), (0.44, 0.40), (0.52, 0.52), (0.42, 0.66), (0.50, 0.80), (0.45, 0.98)]

def poster2(c, t):
    paper(c, t, CARD_PAPERS)
    red_sun(c, 540, 650, 380, ease_out_back(prog(t, C3_OUT, 0.4)))
    bw = 590; bh = bw * PRINT["seneca"].height() / PRINT["seneca"].width()
    bx, by = 540, 720
    draw_img(c, PRINT["seneca"], bx, by, bw)
    from toon_kit import draw_on, smooth_path
    pts = [(bx - bw / 2 + u * bw, by - bh / 2 + v * bh) for u, v in CRACK]
    path = smooth_path(pts, closed=False)
    ck = prog(t, wt("mistakes") - 0.05, 0.3)
    if ck > 0:
        c.drawPath(draw_on(path, ease_out_cubic(ck)), skia.Paint(Color=col(INK), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                                StrokeWidth=11, StrokeJoin=skia.Paint.kMiter_Join))
    hk_ = prog(t, wt("forgive", 1) - 0.05, 0.6)
    if hk_ > 0:
        c.drawPath(draw_on(path, ease_in_out_cubic(hk_)), skia.Paint(Color=col(RED), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                                    StrokeWidth=13, StrokeCap=skia.Paint.kRound_Cap))
    quote_lines(c, t, QUOTE2, 540, 1150, 62, 74, red_last=True, align="center")
    label(c, "SENECA", 540, 300, 36)

def end_card(c, t):
    paper(c, t, PAPERS)
    red_sun(c, 540, 880, 390, ease_out_back(prog(t, END_IN, 0.4)))
    pw = 420; ph = pw * PHYS.height() / PHYS.width()
    c.save(); c.translate(540, 900); c.rotate(-3)
    c.drawImageRect(PHYS, skia.Rect.MakeXYWH(-pw / 2, -ph / 2, pw, ph), skia.SamplingOptions(skia.FilterMode.kLinear))
    c.restore()
    for wd, start, cy in (("OWN IT.", wt("own"), 400), ("FIX IT.", wt("fix"), 1410)):
        h = prog(t, start, 0.2)
        if h > 0:
            s = lerp(1.25, 1.0, ease_out_expo(h))
            c.save(); c.translate(540, cy); c.scale(s, s)
            condensed(c, wd, 0, 0, 300, SERIF, col(RED if wd == "FIX IT." else INK), 960, squeeze=0.9)
            c.restore()
    star(c, 110, 230, 26, col(INK)); star(c, 970, 1560, 26, col(RED))

# ---------------------------------------------------------------- captions
EMPH = {"different.", "no.", "habits", "body.", "luck.", "genetics,", "harbor", "flaws,", "scale", "eat."}
CAPTION_OFF = [(0, W2 + 0.05), (W2, wt("saying") - 0.05), (C2_IN - 0.2, C2_OUT + 0.15), (P1_IN - 0.2, P1_OUT + 0.1),
               (C3_IN - 0.2, P2_OUT + 0.15), (END_IN - 0.2, DUR + 1)]

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
        words = []
        for x in g:
            s = x["w"].strip("\"'").upper()
            if s == "ONE" and g[0]["w"].lower() == "type":
                s = "1"
            words.append((s, x["w"].lower() in EMPH or x["w"].lower().strip("\"'") in EMPH))
        out.append((g[0]["s"], end, words))
    return out

GROUPS = make_groups()
ITALIC = (wt("and", 30), wt("just") - 0.05)          # still quoting Seneca: serif italic style

def captions(c, t):
    if any(a <= t < b for a, b in CAPTION_OFF):
        return
    for s0, s1, words in GROUPS:
        if s0 - 0.02 <= t < s1:
            quoting = ITALIC[0] - 0.05 <= s0 < ITALIC[1]
            font = SERIF if quoting else SANS
            size = 70 if quoting else 62
            gap = size * 0.28
            widths = [text_width(w_, size, font, 0.01) for w_, _ in words]
            x = 540 - (sum(widths) + gap * (len(words) - 1)) / 2
            pop = lerp(0.88, 1.0, ease_out_back(prog(t, s0, 0.14)))
            c.save(); c.translate(540, 1440); c.scale(pop, pop); c.translate(-540, -1440)
            for (w_, em), wd in zip(words, widths):
                if em:
                    brush(c, x - 10, 1446, x + wd + 10, 1440, size * 1.05, col(RED), int(s0 * 10) % 50, bristles=14, dry=0.15)
                text(c, w_, x, 1440, size, font, fill=col(CREAM), align="left", tracking=0.01, stroke=7, stroke_col=col(INK))
                x += wd + gap
            c.restore()
            break

# ---------------------------------------------------------------- frame
def draw(c, t):
    if t < W2:
        if t < W1:
            hk.cover(c, t + HOOK_OFF)
        else:
            hk.card(c, t + HOOK_OFF)
    elif C2_IN <= t < C2_OUT:
        card_n(c, t, "02", "BLAMING", "YOUR", "LUCK.", wt("blaming"), wt("your", 15), wt("luck"), C2_IN, 51)
    elif PAY_IN <= t < P1_IN:
        payoff(c, t)
    elif P1_IN <= t < P1_OUT:
        poster1(c, t)
    elif C3_IN <= t < C3_OUT:
        card_n(c, t, "03", "HATING", "YOUR-", "SELF.", wt("hating"), wt("yourself"), wt("yourself") + 0.16, C3_IN, 53)
    elif C3_OUT <= t < P2_OUT:
        poster2(c, t)
    elif t >= END_IN:
        end_card(c, t)
    else:
        room(c, t)
        for beat in (beat_90, beat_habits, beat_luck, beat_diabetes, beat_dice, beat_lighthouse, beat_mirror, beat_scale, beat_flaws):
            beat(c, t)
    captions(c, t)
    for mid, colr, seed, d in WIPES:
        wipe(c, t, mid - 0.2, mid, mid + 0.22, col(colr) if isinstance(colr, str) else colr, seed, direction=d)

def post(arr, t):
    return grain(vignette(arr, 0.14), 0.026, seed=int(t * FPS))

S = Stage(W, H, fps=FPS, duration=DUR)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stills"
    if cmd == "stills":
        ts = [float(x) for x in sys.argv[2:]] or [5.5, 9.0, 13.2, 14.2, 17.9, 20.5, 24.0, 28.5, 32.0, 35.8, 41.5, 47.0, 50.8, 54.0, 56.5]
        S.stills(draw, ts, out_dir="out/stills/reel", post=post)
    elif cmd == "draft":
        S.render(draw, "out/reel-01_draft.mp4", draft=True, post=post)
    elif cmd == "render":
        S.render(draw, "out/reel-01_silent.mp4", post=post)
