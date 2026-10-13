"""Ink illustrations for reel-01, drawn in code: wobbly double-pass ink outlines, engraving-style hatching,
one red accent. Every draw function takes (c, cx, cy, size, t) and draws centred on (cx, cy).

    python3 illus.py        # test sheet -> out/stills/illus_test.png
"""
import math
import sys

import numpy as np
import skia

sys.path.insert(0, "vibe")
from motion_kit import noise1
from toon_kit import doodle_line, hatch_fill, smooth_path, stepped

INK = skia.Color(20, 19, 18)
RED = skia.Color(211, 55, 43)
CREAM = skia.Color(238, 232, 218)


def _ts(t):
    return stepped(t, 8)                                   # outlines re-wobble 8x a second (hand-drawn boil)


def outline(c, pts, w, t, closed=True, colr=INK, seed=0, jitter=None, straight=False):
    if not straight:
        doodle_line(c, pts, colr, w, _ts(t), seed=seed, passes=2, closed=closed, jitter=jitter)
        return
    from toon_kit import wobble_points
    jit = jitter if jitter is not None else w * 0.35
    for k in range(2):                                     # same double-pass ink, but hard corners
        wp = wobble_points(pts, jit, _ts(t), seed + k * 17, closed)
        p = skia.Path(); p.moveTo(*wp[0])
        for q in wp[1:]:
            p.lineTo(*q)
        if closed:
            p.close()
        c.drawPath(p, skia.Paint(Color=colr, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w * (1 if k == 0 else 0.6),
                                 StrokeJoin=skia.Paint.kRound_Join, StrokeCap=skia.Paint.kRound_Cap, Alphaf=0.95 if k == 0 else 0.55))


def shade(c, path, t, spacing=9, angle=-0.8, width=2.2, colr=INK, alpha=0.55, seed=0):
    hatch_fill(c, path, colr, _ts(t), spacing=spacing, angle=angle, width=width, seed=seed, alpha=alpha)


def poly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close(); return p


def ellipse_pts(cx, cy, rx, ry, n=28, a0=0.0, a1=2 * math.pi):
    return [(cx + math.cos(a) * rx, cy + math.sin(a) * ry) for a in np.linspace(a0, a1, n, endpoint=a1 - a0 < 6.28)]


def fill(c, path, colr):
    c.drawPath(path, skia.Paint(Color=colr, AntiAlias=True))


# ---------------------------------------------------------------- people
def _stroke(c, pts, w, colr, alpha=1.0):
    path = smooth_path(pts, closed=False)
    c.drawPath(path, skia.Paint(Color=colr, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                                StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, Alphaf=alpha))


def figure(c, cx, foot_y, h, t, fit=True, colr=INK, alpha=1.0, wob=0.0):
    """Pictogram person. fit: broad shoulders, narrow waist. Not fit: sloped shoulders, round belly, slumped head."""
    X = lambda x: cx + x * h
    Y = lambda y: foot_y - h + y * h
    j = lambda i: wob * 0.01 * noise1(t * 6 + i, int(cx))                  # tiny hand-drawn wobble (fraction of h)
    if fit:
        torso = [(X(-.21), Y(.19)), (X(.21), Y(.19)), (X(.215), Y(.25)), (X(.115), Y(.47)), (X(.12), Y(.54)),
                 (X(-.12), Y(.54)), (X(-.115), Y(.47)), (X(-.215), Y(.25))]
        fill(c, smooth_path(torso, closed=True), colr)
        for sx in (-1, 1):
            _stroke(c, [(X(sx * .2), Y(.23)), (X(sx * .25 + j(1)), Y(.38)), (X(sx * .245), Y(.53))], h * .075, colr, alpha)
            _stroke(c, [(X(sx * .07), Y(.52)), (X(sx * .075), Y(.75)), (X(sx * .075), Y(.97))], h * .095, colr, alpha)
        head = (X(0), Y(.09), h * .075)
    else:
        sh = [(X(-.15), Y(.24)), (X(.15), Y(.24)), (X(.19), Y(.32)), (X(.23), Y(.43)), (X(.19), Y(.56)), (X(.10), Y(.6)),
              (X(-.10), Y(.6)), (X(-.19), Y(.56)), (X(-.23), Y(.43)), (X(-.19), Y(.32))]
        p = smooth_path(sh, closed=True); c.drawPath(p, skia.Paint(Color=colr, AntiAlias=True, Alphaf=alpha))
        for sx in (-1, 1):
            _stroke(c, [(X(sx * .15), Y(.27)), (X(sx * .235 + j(2)), Y(.42)), (X(sx * .22), Y(.57))], h * .07, colr, alpha)
            _stroke(c, [(X(sx * .08), Y(.58)), (X(sx * .085), Y(.78)), (X(sx * .08), Y(.97))], h * .1, colr, alpha)
        head = (X(.015), Y(.13), h * .072)
    hp = skia.Path(); hp.addCircle(*head); c.drawPath(hp, skia.Paint(Color=colr, AntiAlias=True, Alphaf=alpha))


def crowd(c, cx, cy, size, t, n=10, fit_index=9, ring=1.0, fade=0.0):
    """Row of n figures: all out of shape except one (you). ring: red circle drawn on (0..1). fade: others fade out."""
    gap = size / n; h = gap * 1.75
    for i in range(n):
        x = cx - size / 2 + gap * (i + 0.5)
        if i == fit_index:
            figure(c, x, cy, h * 1.04, t, fit=True)
            if ring > 0:
                from toon_kit import draw_on
                pts = ellipse_pts(x, cy - h * 0.5, gap * 0.62, h * 0.66, 40, -1.4, -1.4 + 2.15 * math.pi)
                path = draw_on(smooth_path(pts, closed=False), ring)
                c.drawPath(path, skia.Paint(Color=RED, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6,
                                            StrokeCap=skia.Paint.kRound_Cap))
        else:
            figure(c, x, cy, h * (0.97 + 0.03 * math.sin(i * 1.7)), t, fit=False, alpha=0.55 * (1 - fade), wob=1)


# ---------------------------------------------------------------- objects
def dice(c, cx, cy, size, t, seed=0, rot=0.0):
    """Two dice, isometric, pips, one face hatched."""
    for k, (ox, oy, s, r) in enumerate(((-0.24, 0.06, 0.42, -0.25), (0.22, -0.05, 0.36, 0.35))):
        x0, y0, a = cx + ox * size, cy + oy * size, s * size / 2
        c.save(); c.translate(x0, y0); c.rotate(math.degrees(r + rot))
        top = [(0, -a), (a * 0.87, -a * 0.5), (0, 0), (-a * 0.87, -a * 0.5)]
        left = [(-a * 0.87, -a * 0.5), (0, 0), (0, a), (-a * 0.87, a * 0.5)]
        right = [(0, 0), (a * 0.87, -a * 0.5), (a * 0.87, a * 0.5), (0, a)]
        fill(c, poly(top + []), CREAM); fill(c, poly(left), CREAM); fill(c, poly(right), CREAM)
        shade(c, poly(right), t, spacing=7, seed=seed + k)
        for f in (top, left, right):
            outline(c, f, 4, t, seed=seed + k * 3)
        pip = lambda px, py, rr=a * 0.09, colr=INK: fill(c, (lambda p: (p.addCircle(px, py, rr), p)[1])(skia.Path()), colr)
        pip(0, -a * 0.5, colr=RED, rr=a * 0.12)                                   # one on top, red
        L0, L1, L2 = (-a * 0.87, -a * 0.5), (0, 0), (0, a)                         # left face: u along top edge, v down
        lf = lambda u, v: (L0[0] + (L1[0] - L0[0]) * u, L0[1] + (L1[1] - L0[1]) * u + a * v)
        for u, v in ((0.25, 0.25), (0.5, 0.5), (0.75, 0.75)):                       # three on the left
            pip(*lf(u, v))
        rf = lambda u, v: (a * 0.87 * u, -a * 0.5 * u + a * v)                       # right face
        for u, v in ((0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)):        # four on the right
            pip(*rf(u, v))
        c.restore()


def bathroom_scale(c, cx, cy, size, t, needle=0.6):
    """Bathroom scale seen from above at an angle: a trapezoid top, a thick front edge, a dial, two footprints."""
    w, h, d = size * 0.86, size * 0.5, size * 0.08
    tl, tr = (cx - w * 0.40, cy - h / 2), (cx + w * 0.40, cy - h / 2)
    br, bl = (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)
    front = poly([bl, br, (br[0], br[1] + d), (bl[0], bl[1] + d)])
    fill(c, front, INK)
    fill(c, poly([tl, tr, br, bl]), CREAM); shade(c, poly([tl, tr, br, bl]), t, spacing=11, alpha=0.18)
    outline(c, [tl, tr, br, (br[0], br[1] + d), (bl[0], bl[1] + d), bl], 5, t, seed=4, straight=True)
    dx, dy, dr = cx, cy - h * 0.18, h * 0.24
    win = skia.Path(); win.addOval(skia.Rect.MakeXYWH(dx - dr * 1.25, dy - dr, dr * 2.5, dr * 2)); fill(c, win, CREAM)
    outline(c, ellipse_pts(dx, dy, dr * 1.25, dr, 30), 4, t, seed=5)
    for i in range(13):
        ang = math.pi * (1.12 + 0.76 * i / 12)
        r0 = 0.62 if i % 3 else 0.48
        c.drawLine(dx + math.cos(ang) * dr * 1.25 * r0, dy + math.sin(ang) * dr * r0,
                   dx + math.cos(ang) * dr * 1.25 * 0.9, dy + math.sin(ang) * dr * 0.9, skia.Paint(Color=INK, StrokeWidth=3, AntiAlias=True))
    ang = math.pi * (1.12 + 0.76 * needle)
    c.drawLine(dx, dy + dr * 0.3, dx + math.cos(ang) * dr * 1.1, dy + math.sin(ang) * dr * 0.85,
               skia.Paint(Color=RED, StrokeWidth=6, AntiAlias=True, StrokeCap=skia.Paint.kRound_Cap))
    for fx in (-1, 1):
        foot = ellipse_pts(cx + fx * w * 0.17, cy + h * 0.2, w * 0.075, h * 0.2)
        shade(c, poly(foot), t, spacing=5, alpha=0.45)


def insulin_pen(c, cx, cy, size, t, rot=-28):
    L, r = size * 0.95, size * 0.065
    c.save(); c.translate(cx, cy); c.rotate(rot)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-L / 2, -r, L * 0.78, 2 * r), r, r)
    cap = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-L / 2 + L * 0.78, -r * 0.9, L * 0.22, 1.8 * r), r * 0.9, r * 0.9)
    pb = skia.Path(); pb.addRRect(body); fill(c, pb, CREAM); shade(c, pb, t, spacing=6, angle=0.3, alpha=0.35)
    pc = skia.Path(); pc.addRRect(cap); shade(c, pc, t, spacing=4, alpha=0.8)
    win = skia.Path(); win.addRect(skia.Rect.MakeXYWH(-L * 0.05, -r * 0.55, L * 0.22, r * 1.1)); fill(c, win, RED)
    for x in np.linspace(-L * 0.04, L * 0.16, 7):
        c.drawLine(x, -r * 0.55, x, -r * 0.1, skia.Paint(Color=INK, StrokeWidth=2))
    dial = skia.Path(); dial.addRect(skia.Rect.MakeXYWH(-L / 2 - r * 0.9, -r * 0.8, r * 0.9, r * 1.6)); shade(c, dial, t, spacing=3, angle=1.57, alpha=0.9)
    for rr_ in (body, cap):
        b = rr_.rect()
        outline(c, [(b.left(), b.top()), (b.right(), b.top()), (b.right(), b.bottom()), (b.left(), b.bottom())], 4, t, seed=7)
    c.drawLine(L / 2, 0, L / 2 + r * 1.6, 0, skia.Paint(Color=INK, StrokeWidth=3, AntiAlias=True))   # needle
    c.restore()


def blood_drop(c, cx, cy, size, t):
    s = size
    pts = [(cx, cy - s * 0.55)] + [(cx + math.cos(a) * s * 0.3, cy + s * 0.12 + math.sin(a) * s * 0.3)
                                   for a in np.linspace(-0.5, math.pi + 0.5, 18)]
    p = smooth_path(pts, closed=True); fill(c, p, RED)
    outline(c, pts, 4, t, seed=9)
    hl = skia.Path(); hl.addOval(skia.Rect.MakeXYWH(cx - s * 0.17, cy + s * 0.0, s * 0.08, s * 0.16))
    fill(c, hl, skia.Color(255, 220, 210, 160))


def dna(c, cx, cy, size, t, turns=2.2):
    h = size; w = size * 0.32; n = 60
    a_pts, b_pts = [], []
    for i in range(n + 1):
        u = i / n; y = cy - h / 2 + u * h; ph = u * turns * 2 * math.pi + t * 1.5
        a_pts.append((cx + math.sin(ph) * w / 2, y)); b_pts.append((cx + math.sin(ph + math.pi) * w / 2, y))
    for i in range(0, n + 1, 3):
        c.drawLine(*a_pts[i], *b_pts[i], skia.Paint(Color=INK, StrokeWidth=3, AntiAlias=True, Alphaf=0.6))
    outline(c, a_pts, 6, t, closed=False, seed=11)
    outline(c, b_pts, 6, t, closed=False, colr=RED, seed=12)


def pizza_slice(c, cx, cy, size, t):
    s = size
    tip, l, r = (cx, cy + s * 0.5), (cx - s * 0.36, cy - s * 0.38), (cx + s * 0.36, cy - s * 0.38)
    crust = ellipse_pts(cx, cy - s * 0.38, s * 0.36, s * 0.09, 16, math.pi, 2 * math.pi)
    tri = [tip, l] + crust + [r]
    p = smooth_path(tri, closed=True); fill(c, p, CREAM); shade(c, p, t, spacing=10, alpha=0.3)
    for px, py, pr in ((0, -0.18, 0.08), (-0.12, -0.05, 0.065), (0.1, 0.02, 0.06), (0, 0.22, 0.05)):
        q = skia.Path(); q.addCircle(cx + px * s, cy + py * s, pr * s); fill(c, q, RED)
    outline(c, tri, 5, t, seed=13)
    outline(c, ellipse_pts(cx, cy - s * 0.32, s * 0.33, s * 0.07, 14, math.pi, 2 * math.pi), 4, t, closed=False, seed=14)


def beer_glass(c, cx, cy, size, t):
    s = size; top, bot = s * 0.3, s * 0.22
    body = [(cx - top, cy - s * 0.4), (cx + top, cy - s * 0.4), (cx + bot, cy + s * 0.5), (cx - bot, cy + s * 0.5)]
    p = poly(body); fill(c, p, CREAM)
    liquid = poly([(cx - top * 0.95, cy - s * 0.22), (cx + top * 0.95, cy - s * 0.22), (cx + bot, cy + s * 0.48), (cx - bot, cy + s * 0.48)])
    shade(c, liquid, t, spacing=6, alpha=0.6)
    for i in range(7):                                                          # foam
        q = skia.Path(); q.addCircle(cx - top + i * top / 3, cy - s * 0.42 + (i % 2) * 6, s * 0.075); fill(c, q, CREAM)
        outline(c, ellipse_pts(cx - top + i * top / 3, cy - s * 0.42 + (i % 2) * 6, s * 0.075, s * 0.075, 14), 3, t, seed=20 + i)
    outline(c, body, 5, t, seed=15, straight=True)


def red_x(c, cx, cy, size, k, t):
    """Two red slashes, drawn on with k (0..1)."""
    from toon_kit import draw_on
    for i, (a, b) in enumerate((((-1, -1), (1, 1)), ((1, -1), (-1, 1)))):
        kk = max(0.0, min(1.0, k * 2 - i))
        if kk <= 0:
            continue
        pts = [(cx + a[0] * size / 2 + j * (b[0] - a[0]) * size / 16 + noise1(j, i) * 6,
                cy + a[1] * size / 2 + j * (b[1] - a[1]) * size / 16) for j in range(9)]
        path = draw_on(smooth_path(pts, closed=False), kk)
        c.drawPath(path, skia.Paint(Color=RED, AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=size * 0.07,
                                    StrokeCap=skia.Paint.kRound_Cap))


def family_tree(c, cx, cy, size, t):
    """Two parents and a child: circles joined by ink lines, one child figure filled."""
    s = size
    nodes = [(-0.28, -0.3), (0.28, -0.3), (0.0, 0.32)]
    c.drawLine(cx - s * 0.28, cy - s * 0.3, cx + s * 0.28, cy - s * 0.3, skia.Paint(Color=INK, StrokeWidth=5, AntiAlias=True))
    outline(c, [(cx, cy - s * 0.3), (cx, cy + s * 0.32)], 5, t, closed=False, seed=31)
    for i, (x, y) in enumerate(nodes):
        figure(c, cx + x * s, cy + y * s + s * 0.2, s * 0.38, t, fit=(i == 2), alpha=0.6 if i < 2 else 1.0)


def food_diary(c, cx, cy, size, t):
    """An open notebook with ruled lines and a fork + knife on the left page."""
    w, h = size, size * 0.66
    left = [(cx - w / 2, cy - h / 2 + 10), (cx, cy - h / 2), (cx, cy + h / 2), (cx - w / 2, cy + h / 2 + 10)]
    right = [(cx, cy - h / 2), (cx + w / 2, cy - h / 2 + 10), (cx + w / 2, cy + h / 2 + 10), (cx, cy + h / 2)]
    for pg in (left, right):
        fill(c, poly(pg), CREAM)
        outline(c, pg, 5, t, seed=33, straight=True)
    for i in range(6):
        y = cy - h / 2 + h * (0.22 + i * 0.13)
        c.drawLine(cx + w * 0.06, y, cx + w * 0.44, y + 4, skia.Paint(Color=INK, StrokeWidth=3, AntiAlias=True, Alphaf=0.6))
    fx = cx - w * 0.3
    for dx in (-10, 0, 10):
        c.drawLine(fx + dx, cy - h * 0.3, fx + dx, cy - h * 0.12, skia.Paint(Color=INK, StrokeWidth=4, AntiAlias=True))
    c.drawLine(fx, cy - h * 0.12, fx, cy + h * 0.32, skia.Paint(Color=INK, StrokeWidth=8, AntiAlias=True, StrokeCap=skia.Paint.kRound_Cap))
    kx = cx - w * 0.16
    kn = [(kx, cy - h * 0.3), (kx + 14, cy - h * 0.2), (kx + 12, cy + h * 0.05), (kx, cy + h * 0.05)]
    fill(c, poly(kn), INK)
    c.drawLine(kx + 4, cy + h * 0.05, kx + 4, cy + h * 0.32, skia.Paint(Color=INK, StrokeWidth=8, AntiAlias=True, StrokeCap=skia.Paint.kRound_Cap))


def magnifier(c, cx, cy, size, t, under=None):
    """Magnifying glass. under(c, cx, cy, r) draws what is seen (zoomed) inside the lens."""
    r = size * 0.32
    if under is not None:
        c.save(); clip = skia.Path(); clip.addCircle(cx, cy, r); c.clipPath(clip, doAntiAlias=True)
        under(c, cx, cy, r); c.restore()
    lens = skia.Path(); lens.addCircle(cx, cy, r)
    c.drawPath(lens, skia.Paint(Color=skia.Color(255, 255, 255, 40), AntiAlias=True))
    outline(c, ellipse_pts(cx, cy, r, r, 40), 12, t, seed=35)
    a = math.radians(45)
    x0, y0 = cx + math.cos(a) * r, cy + math.sin(a) * r
    _stroke(c, [(x0, y0), (x0 + size * 0.36, y0 + size * 0.36)], size * 0.09, INK)


def generic_face(c, cx, cy, size, t):
    """An anonymous ink head and shoulders (front view), simple features, engraving-style shading."""
    s = size
    head = ellipse_pts(cx, cy - s * 0.12, s * 0.2, s * 0.26, 40)
    neck = [(cx - s * 0.08, cy + s * 0.08), (cx - s * 0.08, cy + s * 0.2), (cx + s * 0.08, cy + s * 0.2), (cx + s * 0.08, cy + s * 0.08)]
    shoulders = [(cx - s * 0.48, cy + s * 0.62), (cx - s * 0.44, cy + s * 0.34), (cx - s * 0.24, cy + s * 0.22),
                 (cx - s * 0.08, cy + s * 0.2), (cx + s * 0.08, cy + s * 0.2), (cx + s * 0.24, cy + s * 0.22),
                 (cx + s * 0.44, cy + s * 0.34), (cx + s * 0.48, cy + s * 0.62)]
    fill(c, smooth_path(shoulders, closed=True), CREAM); shade(c, smooth_path(shoulders, closed=True), t, spacing=7, alpha=0.45)
    outline(c, shoulders, 5, t, closed=False, seed=41)
    fill(c, poly(neck), CREAM); shade(c, poly(neck), t, spacing=5, alpha=0.5)
    hp = smooth_path(head, closed=True); fill(c, hp, CREAM)
    c.save(); c.clipPath(hp, doAntiAlias=True)
    shade(c, poly([(cx + s * 0.05, cy - s * 0.4), (cx + s * 0.3, cy - s * 0.4), (cx + s * 0.3, cy + s * 0.2), (cx + s * 0.05, cy + s * 0.2)]),
          t, spacing=5, alpha=0.45)                                                       # shadow side
    hair = ellipse_pts(cx, cy - s * 0.3, s * 0.22, s * 0.13, 30, math.pi, 2 * math.pi) + [(cx + s * 0.2, cy - s * 0.2), (cx - s * 0.2, cy - s * 0.2)]
    shade(c, poly(hair), t, spacing=3, alpha=0.95)
    c.restore()
    outline(c, head, 5, t, seed=42)
    for ex in (-1, 1):                                                                     # brows, eyes
        _stroke(c, [(cx + ex * s * 0.13, cy - s * 0.17), (cx + ex * s * 0.08, cy - s * 0.185), (cx + ex * s * 0.03, cy - s * 0.17)], 4, INK)
        e = skia.Path(); e.addCircle(cx + ex * s * 0.08, cy - s * 0.12, s * 0.014); fill(c, e, INK)
    _stroke(c, [(cx + s * 0.005, cy - s * 0.1), (cx - s * 0.02, cy - s * 0.01), (cx + s * 0.025, cy + 0.0)], 4, INK)   # nose
    _stroke(c, [(cx - s * 0.06, cy + s * 0.06), (cx, cy + s * 0.07), (cx + s * 0.06, cy + s * 0.06)], 4, INK)          # mouth


if __name__ == "__main__":
    from hook_scene import PAPERS
    from PIL import Image
    surf = skia.Surface(1080, 1920)
    with surf as c:
        c.drawImage(PAPERS[0], 0, 0)
        t = 1.0
        crowd(c, 540, 470, 900, t)
        dice(c, 290, 760, 360, t)
        bathroom_scale(c, 790, 780, 380, t)
        insulin_pen(c, 300, 1130, 380, t); blood_drop(c, 470, 1040, 110, t)
        dna(c, 790, 1150, 380, t)
        pizza_slice(c, 290, 1560, 340, t); beer_glass(c, 560, 1560, 300, t); red_x(c, 560, 1560, 300, 1.0, t)
        figure(c, 840, 1720, 320, t, fit=True)
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    Image.fromarray(arr).save("out/stills/illus_test.png")
    print("test sheet -> out/stills/illus_test.png")