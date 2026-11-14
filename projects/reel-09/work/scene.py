"""reel-09 scenes: Bicep curl elbow check. frame(t) -> RGB uint8 1080x1920.

0-2 title, 2-6 CURRENT (elbow pinned, stiff), 6-11 CORRECT (elbow free, smooth), 11-15 top/bottom in sync.
"""
import math
import sys
import os
import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig import Figure, Cam, Pose, new_surface, to_rgb, col, paint, arm_points, hand_point, torso_halfwidth

W, H, FPS, DUR = 1080, 1920, 30, 15.0
YAW = 55
BG = (246, 243, 236)
INK = (28, 31, 38)
RED = (222, 52, 52)
GREEN = (30, 160, 84)
RED_BG = (252, 236, 234)
GREEN_BG = (234, 246, 236)

FONT_DIR = "/usr/share/fonts/opentype/inter/"
TF_XB = skia.Typeface.MakeFromFile(FONT_DIR + "Inter-ExtraBold.otf")
TF_B = skia.Typeface.MakeFromFile(FONT_DIR + "Inter-Bold.otf")


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):  # smoothstep
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def back_out(x, k=1.7):
    x = clamp(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


# ---------------------------------------------------------------- motion
FLEX_LO, FLEX_HI = 12.0, 138.0


def smooth_flex(u):
    """u: time since rep start (s). 2 s up, 2 s down, even speed feel (cosine)."""
    if u <= 0:
        return FLEX_LO
    if u < 2.0:
        k = 0.5 - 0.5 * math.cos(math.pi * u / 2.0)
    elif u < 4.0:
        k = 0.5 + 0.5 * math.cos(math.pi * (u - 2.0) / 2.0)
    else:
        k = 0.0
    return FLEX_LO + (FLEX_HI - FLEX_LO) * k


def jerky_profile(u, up, down, steps_up=3, steps_down=2):
    """0..1 lift in hitches: each step is a fast push then a stall, with a small recoil."""
    if u <= 0:
        return 0.0
    if u < up:
        x = u / up * steps_up
        i = min(int(x), steps_up - 1)
        f = x - i
        move = ease_out(clamp(f / 0.55))  # pushes in the first 55% of each step, then stalls
        recoil = -0.035 * math.sin(math.pi * clamp((f - 0.55) / 0.3)) if f > 0.55 else 0.0
        return clamp((i + move) / steps_up + recoil / steps_up * 3, 0, 1)
    u2 = u - up
    if u2 < 0.25:
        return 1.0
    u2 -= 0.25
    if u2 < down:
        x = u2 / down * steps_down
        i = min(int(x), steps_down - 1)
        f = x - i
        move = ease(clamp(f / 0.6))
        return 1.0 - (i + move) / steps_down
    return 0.0


def tremor(t, amp):
    return amp * (math.sin(t * 2 * math.pi * 8.3) * 0.6 + math.sin(t * 2 * math.pi * 13.1 + 1.3) * 0.4)


def pose_current(t, rep_start, up=1.6, down=1.3):
    k = jerky_profile(t - rep_start, up, down)
    flex = FLEX_LO + (FLEX_HI - FLEX_LO) * k
    active = 0.0 < t - rep_start < up + down + 0.25
    flex += tremor(t, 1.4 if active else 0.0)
    # elbow jammed into the ribs (pulled in), slightly back, shoulder tense and raised
    return Pose(flex=flex, swing=-4.0, abd=-4.0, shrug=2.4 + (0.6 * k), squeeze=1.0)


def pose_correct(t, rep_start):
    flex = smooth_flex(t - rep_start)
    k = (flex - FLEX_LO) / (FLEX_HI - FLEX_LO)
    # relaxed: a small natural gap, the elbow drifts a little forward and out as the weight comes up
    return Pose(flex=flex, swing=3.0 + 6.0 * k, abd=8.5 + 1.5 * k, shrug=0.0)


def pose_neutral():
    return Pose(flex=FLEX_LO, swing=3.0, abd=8.5, shrug=0.0)


# ---------------------------------------------------------------- drawing helpers
def text_w(s, size, tf=TF_XB):
    return skia.Font(tf, size).measureText(s)


def draw_text(cv, s, x, y, size, c, a=255, tf=TF_XB, align="center"):
    f = skia.Font(tf, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    w = f.measureText(s)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    cv.drawString(s, x, y, f, paint(c, a))
    return w


def draw_mark(cv, kind, cx, cy, r, fg, bg, a=255):
    """kind 'x' or 'check' in a filled circle."""
    cv.drawCircle(cx, cy, r, paint(bg, a))
    p = skia.Paint(AntiAlias=True, Color=col(fg, a), Style=skia.Paint.kStroke_Style, StrokeWidth=r * 0.24,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    path = skia.Path()
    if kind == "x":
        d = r * 0.4
        path.moveTo(cx - d, cy - d); path.lineTo(cx + d, cy + d)
        path.moveTo(cx + d, cy - d); path.lineTo(cx - d, cy + d)
    else:
        path.moveTo(cx - r * 0.45, cy + r * 0.02)
        path.lineTo(cx - r * 0.12, cy + r * 0.36)
        path.lineTo(cx + r * 0.48, cy - r * 0.34)
    cv.drawPath(path, p)


def label_pill(cv, word, kind, color, cx, cy, size, a=255, scale=1.0):
    """Coloured pill: WORD + mark. Centred at cx, cy."""
    cv.save()
    cv.translate(cx, cy)
    cv.scale(scale, scale)
    tw = text_w(word, size)
    mr = size * 0.42
    gap = size * 0.32
    padx, h = size * 0.62, size * 1.42
    w = padx * 2 + tw + gap + mr * 2
    rect = skia.RRect.MakeRectXY(skia.Rect(-w / 2, -h / 2, w / 2, h / 2), h / 2, h / 2)
    cv.drawRRect(rect, paint(color, a))
    x0 = -w / 2 + padx
    draw_text(cv, word, x0, size * 0.36, size, (255, 255, 255), a, align="left")
    draw_mark(cv, kind, x0 + tw + gap + mr, 0, mr, color, (255, 255, 255), a)
    cv.restore()


def glow(cv, cx, cy, r, c, a):
    if a <= 0:
        return
    sh = skia.GradientShader.MakeRadial(skia.Point(cx, cy), r,
                                        [col(c, int(150 * a)), col(c, int(70 * a)), col(c, 0)], [0.0, 0.45, 1.0])
    p = skia.Paint(AntiAlias=True)
    p.setShader(sh)
    cv.drawCircle(cx, cy, r, p)


def ring(cv, cx, cy, r, c, a, w):
    if a <= 0:
        return
    p = skia.Paint(AntiAlias=True, Color=col(c, int(255 * a)), Style=skia.Paint.kStroke_Style, StrokeWidth=w)
    cv.drawCircle(cx, cy, r, p)


def contact_point(cam, pose):
    """Where the (far, curling) elbow meets the ribs, in screen space."""
    sh, el, wr = arm_points(pose, -1)
    # inner side of the elbow, toward the body
    inner = el + np.array([0, 0, 4.0])
    return cam.p(inner)


def trail_path(cam, pts):
    path = skia.Path()
    for i, q in enumerate(pts):
        x, y = cam.p(q)
        path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
    return path


def dumbbell_centre(pose):
    return hand_point(pose, -1)


# ---------------------------------------------------------------- panels
def figure_cam(px, py, scale):
    """Camera that puts the figure's chest point (0, 120, 0) at screen (px, py)."""
    cam = Cam(YAW, scale, 0, 0)
    x, y = cam.p((0, 120, 0))
    cam.ox, cam.oy = px - x, py - y
    return cam


def draw_current(cv, t, rep_start, cam, show_glow=1.0, up=1.6, down=1.3):
    pose = pose_current(t, rep_start, up, down)
    fig = Figure(cam)

    def extra(c):
        pass

    fig.draw(cv, pose, rest=Pose(flex=8, swing=0, abd=2, shrug=pose.shrug))
    if show_glow > 0:
        cx, cy = contact_point(cam, pose)
        pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.6)
        glow(cv, cx, cy, cam.s * (11 + 2 * pulse), RED, show_glow * (0.75 + 0.25 * pulse))
        ring(cv, cx, cy, cam.s * (7.5 + 0.8 * pulse), RED, show_glow, cam.s * 0.75)
    return pose


def draw_correct(cv, t, rep_start, cam, show_trail=1.0):
    pose = pose_correct(t, rep_start)
    fig = Figure(cam)
    # trail of the dumbbell from rep start to now (drawn behind the figure's arm)
    u = clamp(t - rep_start, 0, 4.0)
    if show_trail > 0 and u > 0:
        ts = np.linspace(0, u, max(2, int(u * 40)))
        pts = [dumbbell_centre(pose_correct(rep_start + s, rep_start)) for s in ts]
        # full arc for reference once the top is passed
        top = min(u, 2.0)
        arc = [dumbbell_centre(pose_correct(rep_start + s, rep_start)) for s in np.linspace(0, top, 60)]
        p = skia.Paint(AntiAlias=True, Color=col(GREEN, int(70 * show_trail)), Style=skia.Paint.kStroke_Style,
                       StrokeWidth=cam.s * 4.2, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
        cv.drawPath(trail_path(cam, arc), p)
        p2 = skia.Paint(AntiAlias=True, Color=col(GREEN, int(230 * show_trail)), Style=skia.Paint.kStroke_Style,
                        StrokeWidth=cam.s * 1.2, StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
        p2.setPathEffect(skia.DashPathEffect.Make([cam.s * 2.6, cam.s * 2.2], 0))
        cv.drawPath(trail_path(cam, arc), p2)
    fig.draw(cv, pose, rest=Pose(flex=8, swing=0, abd=3, shrug=0))
    return pose


def caption(cv, lines, y, size, a=255, colors=None):
    lh = size * 1.18
    for i, s in enumerate(lines):
        c = colors[i] if colors else INK
        draw_text(cv, s, W / 2, y + i * lh, size, c, a)


def floor_fade(cv, y0, y1):
    sh = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(BG, 0), col(BG, 255)])
    p = skia.Paint()
    p.setShader(sh)
    cv.drawRect(skia.Rect(0, y0, W, y1), p)
    cv.drawRect(skia.Rect(0, y1, W, H), paint(BG))


def dumbbell_icon(cv, cx, cy, s, a):
    c = (52, 64, 84)
    cv.save()
    cv.translate(cx, cy)
    cv.scale(s, s)
    cv.rotate(-18)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-95, -11, 95, 11), 8, 8), paint(INK, a))
    for sx in (-1, 1):
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(sx * 60 - 15, -58, sx * 60 + 15, 58), 12, 12), paint(c, a))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(sx * 92 - 12, -40, sx * 92 + 12, 40), 10, 10), paint(c, a))
    cv.restore()


# ---------------------------------------------------------------- the timeline
T_CUR, T_COR, T_SPLIT = 2.0, 6.0, 11.0
CUR_REP = 2.45  # rep start inside the current scene
COR_REP = 6.55
SPLIT_REP = 11.0

MAIN_SCALE = 9.4
MAIN_CAM_POS = (470, 1000)


def frame(t):
    surf, cv = new_surface(W, H, BG)

    if t < T_CUR:  # ------------------------------------------------ title
        a_in = 1.0  # visible from the first frame (thumbnail)
        out = ease(clamp((t - 1.75) / 0.25))
        a = int(255 * a_in * (1 - out))
        y = 900 - 24 * ease_out(t / 1.7) - 50 * out
        dumbbell_icon(cv, W / 2, y - 250, 1.0 + 0.04 * math.sin(t * 3), a)
        draw_text(cv, "Bicep curl:", W / 2, y, 120, INK, a)
        draw_text(cv, "elbow check", W / 2, y + 150, 120, INK, a)
        bw = 220 * ease_out((t - 0.25) / 0.5)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect(W / 2 - bw / 2, y + 200, W / 2 + bw / 2, y + 216), 8, 8),
                     paint(INK, a))

    elif t < T_SPLIT:
        is_cur = t < T_COR
        t0 = T_CUR if is_cur else T_COR
        lt = t - t0
        cam = figure_cam(*MAIN_CAM_POS, MAIN_SCALE)
        if is_cur:
            g = ease(clamp((t - (CUR_REP + 0.2)) / 0.3))
            draw_current(cv, t, CUR_REP, cam, show_glow=g)
        else:
            draw_correct(cv, t, COR_REP, cam, show_trail=1.0)
        floor_fade(cv, 1465, 1545)
        # scene change: quick fade from background
        fade_in = ease(lt / 0.22)
        if fade_in < 1:
            cv.drawRect(skia.Rect(0, 0, W, H), paint(BG, int(255 * (1 - fade_in))))
        # top label
        pop = back_out(clamp(lt / 0.35))
        if is_cur:
            label_pill(cv, "CURRENT", "x", RED, W / 2, 205, 84, scale=max(0.01, pop))
        else:
            label_pill(cv, "CORRECT", "check", GREEN, W / 2, 205, 84, scale=max(0.01, pop))
        # caption (bottom)
        ca = ease((lt - 0.3) / 0.3)
        cy = 1625 + 24 * (1 - ca)
        a = int(255 * ca)
        if is_cur:
            caption(cv, ["Elbow locked", "to the side"], cy, 92, a, [RED, INK])
        else:
            caption(cv, ["Elbow free,", "smooth and natural"], cy, 92, a, [GREEN, INK])

    else:  # ----------------------------------------------------- side by side
        lt = t - T_SPLIT
        app = ease(lt / 0.3)
        PH = 790
        top_rect = skia.Rect(0, 0, W, PH)
        bot_rect = skia.Rect(0, PH, W, 2 * PH)
        cv.drawRect(top_rect, paint(RED_BG, int(255 * app)))
        cv.drawRect(bot_rect, paint(GREEN_BG, int(255 * app)))
        sc = 6.6
        for rect, is_cur in ((top_rect, True), (bot_rect, False)):
            cv.save()
            cv.clipRect(rect)
            cam = figure_cam(560, rect.top() + 470, sc)
            if is_cur:
                draw_current(cv, t, SPLIT_REP, cam, show_glow=1.0, up=1.75, down=1.75)
            else:
                draw_correct(cv, t, SPLIT_REP, cam, show_trail=1.0)
            cv.restore()
            lab = "CURRENT" if is_cur else "CORRECT"
            label_pill(cv, lab, "x" if is_cur else "check", RED if is_cur else GREEN, 238, rect.top() + 78, 50,
                       scale=max(0.01, back_out(clamp((lt - (0 if is_cur else 0.08)) / 0.35))))
        # divider
        cv.drawRect(skia.Rect(0, PH - 3, W, PH + 3), paint((255, 255, 255)))
        # bottom text band
        ca = ease((lt - 0.25) / 0.3)
        caption(cv, ["Don't lock the elbow.", "Let it move naturally."], 1720 + 20 * (1 - ca), 74, int(255 * ca),
                [RED, GREEN])
        if app < 1:
            cv.drawRect(skia.Rect(0, 0, W, H), paint(BG, int(255 * (1 - app))))

    return to_rgb(surf)


if __name__ == "__main__":
    import cv2
    out = sys.argv[1]
    for tt in sys.argv[2:]:
        im = frame(float(tt))
        cv2.imwrite(os.path.join(out, f"t_{float(tt):05.2f}.png"), cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
