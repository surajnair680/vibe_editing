"""reel-14 v3: dark Vox collage, one visual per line (work/beats_vox.md, approved 2026-11-24).

python3 work/build3/scene3.py still <t> [<t> ...]       -> out/stills/v3/s_<t>.png
python3 work/build3/scene3.py render <a> <b> <out.mp4>   -> picture only (30 fps, crf 14)

Layers per frame: collage ground (dark red, or cream in the balance section) -> grain on the ground -> beat visuals
behind him -> his cut-out (scale 0.72, bottom) -> front visuals (name tags) -> full-scene prints (his photos and
clips, never filtered) -> caption strip at the top -> paper wipes. Her clip (before 27.30) is untouched.
"""
import functools, math, os, subprocess, sys
ROOT = "/home/user/vibe_editing/projects/reel-14/"
os.chdir(ROOT)
for p in ("work/build3", "work/build2", "work/build", "vibe"):
    sys.path.insert(0, ROOT + p)
import numpy as np, cv2
from PIL import Image, ImageDraw
import scene2, fx2, motion_kit
import fx as fx1
import vox
from vox import W, H, BONE, CREAM, INK, RED, MARK, ease, span, twos, paste, font

s, fr, LEN, HIS = scene2.s, scene2.fr, scene2.LEN, scene2.HIS
scene2.MOVES[:] = [(0, 0.72, 0)]            # smaller him: visuals live above his head (y 380 to 900)
C = "assets/codex/"
GRAIN = 0.08
SFX = []                                    # (time, sound, dB) collected for mix3.py


def sfx(t, name, db=0):
    SFX.append((round(t, 3), name, db))


def land(t, t0, d=0.33):
    """0 -> 1 as an element lands at t0 (stepped on twos)."""
    return ease(span(twos(t), t0 - d, t0))


def drop(img, rgba, cx, cy, t, t0, rot=0.0, dy=-420, scale=1.0, shadow=0.45):
    p = land(t, t0)
    if p <= 0:
        return img
    return paste(img, rgba, cx, cy + dy * (1 - p), rot=rot * (0.4 + 0.6 * p), scale=scale, shadow=shadow)


# ------------------------------------------------------------------ paper pieces made in code (cached)
@functools.lru_cache(maxsize=8)
def figure(color=BONE, h=150, seed=1):
    """a paper person pictogram (no face), cut out with a white fibre margin."""
    w = int(h * 0.5)
    pil = Image.new("L", (w + 40, h + 40), 0)
    d = ImageDraw.Draw(pil)
    cx = (w + 40) // 2
    d.ellipse((cx - h * .14, 20, cx + h * .14, 20 + h * .28), fill=255)
    d.rounded_rectangle((cx - h * .22, 20 + h * .33, cx + h * .22, 20 + h * .78), radius=int(h * .1), fill=255)
    d.rectangle((cx - h * .16, 20 + h * .7, cx - h * .03, 20 + h), fill=255)
    d.rectangle((cx + h * .03, 20 + h * .7, cx + h * .16, 20 + h), fill=255)
    a = np.asarray(pil)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    m = cv2.dilate(a, k)
    rgb = np.zeros((*a.shape, 3), np.uint8); rgb[:] = (250, 247, 240)
    rgb[a > 128] = color
    return np.dstack([rgb, m])


def card(w, h, seed, draw, color=CREAM):
    return vox.paper_sheet(w, h, color, seed, rough=7, draw=draw)


@functools.lru_cache(maxsize=4)
def phone():
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.rounded_rectangle((ox + 20, oy + 20, ox + 520, oy + 600), radius=46, outline=INK, width=8)
        d.text((ox + 270, oy + 70), "group chat", font=font(vox.F_CAP, 30), fill=(90, 80, 76), anchor="mm")
    return card(540, 620, 31, ink, color=(232, 225, 212))


@functools.lru_cache(maxsize=8)
def bubble(text, red=False, seed=0):
    f = font(vox.F_CAP, 40)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 52, 76
    pil = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pil)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=MARK + (255,) if red else (60, 54, 54, 255))
    d.text((26 - bb[0], (h - (bb[3] - bb[1])) // 2 - bb[1]), text, font=f, fill=BONE)
    return np.asarray(pil)


@functools.lru_cache(maxsize=4)
def diagnosis():
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.text((ox + 40, oy + 34), "DIAGNOSIS", font=font(vox.F_MONO, 44), fill=INK)
        d.line((ox + 40, oy + 100, ox + 560, oy + 100), fill=INK, width=4)
        d.text((ox + 40, oy + 130), "Is something wrong", font=font(vox.F_CAP, 44), fill=INK)
        d.text((ox + 40, oy + 186), "with you?", font=font(vox.F_CAP, 44), fill=INK)
        for i, lab in enumerate(("YES", "NO")):
            x = ox + 60 + i * 260
            d.rectangle((x, oy + 270, x + 64, oy + 334), outline=INK, width=6)
            d.text((x + 90, oy + 274), lab, font=font(vox.F_TITLE, 66), fill=INK)
    return card(600, 380, 41, ink)


def curve_card(t, t_draw, dot_t, show_avg=None, labels=True):
    """bell curve inked on cream; red YOU dot on the far right tail."""
    w, h = 860, 500
    p = span(twos(t), t_draw, t_draw + 0.7)
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        base = oy + h - 70
        d.line((ox + 30, base, ox + w - 30, base), fill=INK, width=4)
        pts = []
        n = int(120 * p)
        for i in range(n + 1):
            x = -3.2 + 6.4 * i / 120
            pts.append((ox + 50 + (x + 3.2) / 6.4 * (w - 100), base - 330 * math.exp(-x * x / 2)))
        if len(pts) > 1:
            d.line(pts, fill=INK, width=8, joint="curve")
        if show_avg is not None and show_avg > 0:
            d.text((ox + w / 2, base + 34), "THE AVERAGE", font=font(vox.F_TITLE, 52), fill=(70, 60, 58), anchor="mm")
    sheet = card(w, h, 51, ink)
    return sheet


def curve(img, t, t_draw, dot_t, cy=690, avg_t=None):
    sheet = curve_card(t, t_draw, dot_t, show_avg=(None if avg_t is None else span(t, avg_t, avg_t + .1)))
    img = paste(img, sheet, W / 2, cy, rot=-1.5)
    if avg_t is not None and t >= avg_t:          # grey figures crowd the middle
        for i in range(7):
            ti = avg_t + i * 0.06
            img = drop(img, figure((150, 146, 140), 120, 2), W / 2 - 20 + (i - 3) * 62, cy + 120, t, ti, dy=-120, shadow=.3)
    if dot_t is not None and t >= dot_t - 0.2:
        q = land(t, dot_t, .2)
        x, y = W / 2 - 20 + 355, cy + 180
        cv2.circle(img, (int(x), int(y)), int(26 * q), MARK, -1, cv2.LINE_AA)
        if q >= 1:
            img = paste(img, vox.strip("YOU", 70, bg=MARK, fg=BONE, seed=61), x - 10, y - 90, rot=4, shadow=.3)
    return img


@functools.lru_cache(maxsize=4)
def clipping(word, pos, definition):
    w, h = 820, 300
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.text((ox + 40, oy + 30), word, font=font(ROOT + "fonts/NotoSerif-800.ttf", 92), fill=INK)
        d.text((ox + 44, oy + 152), pos, font=font(ROOT + "fonts/InstrumentSerif-400.ttf", 44), fill=(90, 80, 76))
        d.text((ox + 44, oy + 210), definition, font=font(ROOT + "fonts/InstrumentSerif-400.ttf", 48), fill=INK)
    return card(w, h, hash(word) % 97, ink, color=(236, 230, 214))


def highlight(img, x0, y0, x1, y1, p):
    if p <= 0: return img
    out = img.astype(np.float32)
    xe = int(x0 + (x1 - x0) * ease(p))
    reg = out[y0:y1, x0:xe]
    out[y0:y1, x0:xe] = reg * np.array([1.0, 0.62, 0.62]) * 0.9 + np.array([60, 0, 0])
    return np.clip(out, 0, 255).astype(np.uint8)


def receipt(t, lines):
    w = 520
    shown = [ln for ln in lines if t >= ln[0]]
    h = 140 + 70 * len(shown)
    pil = Image.new("RGBA", (w, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(pil)
    zig = [(x, h + (14 if (x // 20) % 2 else 0)) for x in range(0, w + 1, 20)]
    d.polygon([(0, 0), (w, 0)] + zig[::-1], fill=(246, 243, 236, 255))
    d.text((w / 2, 50), "RECEIPT", font=font(vox.F_MONO, 44), fill=INK, anchor="mm")
    d.line((30, 90, w - 30, 90), fill=INK, width=3)
    for i, (t0, left, right, red) in enumerate(shown):
        y = 120 + i * 70
        col = MARK if red else INK
        d.text((30, y), left, font=font(vox.F_MONO, 36), fill=col)
        d.text((w - 30, y), right, font=font(vox.F_MONO, 36), fill=col, anchor="ra")
    return np.asarray(pil)


def gauge(t, t0, t_pass, t_end):
    w, h = 760, 470
    p = ease(span(twos(t), t0, t_end))
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        cx, cy, r = ox + w / 2, oy + h - 70, 300
        d.arc((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=INK, width=10)
        d.arc((cx - r, cy - r, cx + r, cy + r), 180 + 0.7 * 180, 360, fill=MARK, width=22)
        a = math.pi + 0.7 * math.pi
        d.line((cx + math.cos(a) * (r - 40), cy + math.sin(a) * (r - 40), cx + math.cos(a) * (r + 30), cy + math.sin(a) * (r + 30)), fill=MARK, width=8)
        d.text((cx + math.cos(a) * (r + 10) - 210, cy + math.sin(a) * (r + 10) - 70), "MOST PEOPLE", font=font(vox.F_TITLE, 50), fill=MARK)
        na = math.pi + (0.12 + 0.83 * p) * math.pi
        d.line((cx, cy, cx + math.cos(na) * (r - 30), cy + math.sin(na) * (r - 30)), fill=INK, width=12)
        d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=INK)
    return card(w, h, 71, ink)


@functools.lru_cache(maxsize=4)
def report(seed):
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.text((ox + 30, oy + 26), "REPORT CARD", font=font(vox.F_MONO, 34), fill=INK)
        for i in range(4):
            d.line((ox + 30, oy + 100 + i * 46, ox + 200, oy + 100 + i * 46), fill=(150, 140, 130), width=4)
        d.text((ox + 300, oy + 150), "A", font=font(vox.F_TITLE, 210), fill=MARK, anchor="mm")
        d.ellipse((ox + 225, oy + 60, ox + 375, oy + 240), outline=MARK, width=7)
    return card(400, 300, seed, ink)


def progress(t, t0, t_red, t_end):
    w, h = 820, 260
    p = ease(span(twos(t), t0, t_end))
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        x0, x1, y0, y1 = ox + 40, ox + w - 40, oy + 110, oy + 190
        xr = x0 + (x1 - x0) * 0.55
        d.rectangle((xr, y0, x1, y1), fill=(222, 196, 190))
        d.rectangle((x0, y0, x0 + (x1 - x0) * p, y1), fill=INK)
        d.rectangle((x0, y0, x1, y1), outline=INK, width=5)
        d.text((x0, oy + 40), "COMFORT", font=font(vox.F_TITLE, 54), fill=INK)
        d.text((xr + 10, oy + 40), "UNCOMFORTABLE", font=font(vox.F_TITLE, 54), fill=MARK)
    return card(w, h, 81, ink)


def fibres(t, t_tear, t_grow, w=440, h=300):
    torn = t >= t_tear; thick = ease(span(twos(t), t_grow, t_grow + .4))
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.text((ox + 24, oy + 18), "MUSCLE FIBRES", font=font(vox.F_MONO, 28), fill=INK)
        for i in range(4):
            y = oy + 90 + i * 52
            hh = 16 + 12 * thick
            d.rounded_rectangle((ox + 30, y - hh / 2, ox + w - 30, y + hh / 2), radius=int(hh / 2), fill=(176, 60, 66))
            if torn and thick < 1:
                for k in range(3):
                    x = ox + 80 + k * 120 + i * 17
                    d.line((x, y - hh / 2 - 4, x + 14, y + hh / 2 + 4), fill=(236, 230, 214), width=6)
    return card(w, h, 91, ink)


@functools.lru_cache(maxsize=4)
def name_tag(word, seed):
    w, h = 300, 200
    def ink(pil, ox, oy):
        d = ImageDraw.Draw(pil)
        d.rectangle((ox, oy, ox + w, oy + 64), fill=MARK)
        d.text((ox + w / 2, oy + 32), "HELLO I AM", font=font(vox.F_TITLE, 46), fill=BONE, anchor="mm")
        d.text((ox + w / 2, oy + 135), word, font=font(vox.F_TITLE, 84), fill=INK, anchor="mm")
    return vox.paper_sheet(w, h, (246, 243, 236), seed, rough=4, tone=False, draw=ink)


def arrow(img, x0, y0, x1, y1, p, width=12):
    if p <= 0: return img
    img = img.copy()
    n = 30
    pts = [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n - 80 * math.sin(math.pi * i / n)) for i in range(int(n * p) + 1)]
    cv2.polylines(img, [np.array(pts, np.int32)], False, MARK, width, cv2.LINE_AA)
    if p >= 1:
        a = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
        for da in (2.6, -2.6):
            cv2.line(img, (int(x1), int(y1)), (int(x1 + 50 * math.cos(a + da)), int(y1 + 50 * math.sin(a + da))), MARK, width, cv2.LINE_AA)
    return img


def tick(img, x, y, p):
    if p <= 0: return img
    img = img.copy()
    pts = [(x - 30, y), (x - 6, y + 30), (x + 50, y - 50)]
    n = 20; seg = []
    for i in range(int(n * p) + 1):
        f = i / n
        if f < .35: q = f / .35; seg.append((pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q))
        else: q = (f - .35) / .65; seg.append((pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q))
    cv2.polylines(img, [np.array(seg, np.int32)], False, MARK, 14, cv2.LINE_AA)
    return img


def torn_half(rgba, side, seed=9):
    """left or right half of an image with a jagged vertical tear."""
    h, w = rgba.shape[:2]
    r = np.random.default_rng(seed)
    xs = (w / 2 + np.cumsum(r.normal(0, 4, h)).clip(-30, 30)).astype(int)
    m = np.zeros((h, w), np.uint8)
    for y in range(h):
        if side == "L": m[y, :xs[y]] = 255
        else: m[y, xs[y]:] = 255
    out = rgba.copy(); out[..., 3] = np.minimum(out[..., 3], m)
    return out


# ------------------------------------------------------------------ the beats
SEC_CREAM = (s("Balance", 60.32) - 0.05, s("Screw", 68.83))


def ground(t):
    if SEC_CREAM[0] <= t < SEC_CREAM[1]:
        g = vox.paper_sheet(W + 40, H + 40, (226, 218, 202), 7, rough=2)[30:30 + H, 30:30 + W, :3]
        return fx2.vignette(np.ascontiguousarray(g), 0.35)
    return fx2.vignette(fx2.bg_red(t), 0.40)


def behind(img, t):
    """visuals behind him, by beat."""
    # 1. Normal people: rows of identical figures
    if HIS <= t < s("a", 28.75):
        t0 = s("Normal", 27.4)
        for i in range(10):
            r_, c_ = divmod(i, 5)
            img = drop(img, figure(), 220 + c_ * 150, 520 + r_ * 210, t, t0 + 0.05 + i * 0.05, dy=-200, shadow=.35)
        if i == 0: pass
    # 2. drinks, pizza
    if s("You", 30.07) <= t < s("and", 33.63):
        td, tp = s("drinks", 30.63), s("pizza", 32.17)
        img = drop(img, vox.cutout(C + "drinks.png", 400, seed=11), 350, 640, t, td, rot=3, dy=-500)
        if t >= td + .27: img = vox.marker_x(img, 350, 640, 340, span(t, td + .27, td + .77), seed=4)
        img = drop(img, vox.cutout(C + "pizza.png", 540, seed=12), 750, 620, t, tp, rot=-5, dy=-560)
        if t >= tp + .28:
            q = ease(span(twos(t), tp + .28, tp + .45))
            img = paste(img, vox.stamp("NO", 210, seed=5), 770, 650, rot=-12, scale=1.6 - .6 * q, shadow=0)
    # 3. group chat
    if s("and", 33.63) <= t < s("So", 36.91):
        img = drop(img, phone(), 540, 720, t, s("tonight", 33.79), rot=-2, dy=-300)
        for k, (word, near, txt, red, x, y) in enumerate([("tonight", 33.79, "come out tonight?", False, 450, 560),
                                                           ("obsessed", 35.37, "bro you're obsessed", True, 600, 680),
                                                           ("abnormal", 36.23, "that's abnormal man", True, 470, 800)]):
            tb = s(word, near) + .05
            if twos(t) >= tb:
                q = ease(span(twos(t), tb, tb + .17))
                img = paste(img, bubble(txt, red, k), x, y, scale=0.6 + 0.4 * q, shadow=.25)
    # 4-5. diagnosis + magnifier, then YES ticked
    if s("So", 36.91) <= t < s("You", 40.25):
        img = drop(img, diagnosis(), 520, 620, t, s("Is", 37.27), rot=-2, dy=-350)
        if t >= s("wrong", 38.25) - .3 and os.path.exists(C + "magnifier.png"):
            img = drop(img, vox.cutout(C + "magnifier.png", 380, seed=13), 760, 560, t, s("wrong", 38.25), rot=-20, dy=0)
        ty = s("yes", 39.64)
        img = tick(img, 520 - 300 + 60 + 32 + 4, 620 - 190 + 302 - 6, span(twos(t), ty, ty + .25))
    # 6. bell curve with YOU
    if s("You", 40.25) <= t < s("Success", 42.62):
        img = curve(img, t, s("You", 40.25), s("normal", 40.73) + .3)
    # 7. dictionary + Jobs
    if s("Success", 42.62) <= t < s("Successful", 44.89):
        img = drop(img, clipping("ab·nor·mal", "adjective", "not normal; unusual."), 500, 560, t, s("Success", 42.62) + .1, rot=-2, dy=-300)
        hp = span(twos(t), s("abnormal", 43.34), s("abnormal", 43.34) + .45)
        img = highlight(img, 130, 700, 600, 760, hp)
        img = drop(img, vox.print_frame(_photo("assets/photos/celebrity_jobs.jpg"), 330, seed=21), 820, 700, t, s("by", 43.98), rot=5, dy=-500)
    # 8. outliers on the curve, the average
    if s("Successful", 44.89) <= t < s("Which", 48.95):
        img = curve(img, t, s("Successful", 44.89) - .5, None, avg_t=s("average", 48.27) - .4)
        img = drop(img, vox.print_frame(_photo("assets/photos/celebrity_arnold.jpg"), 320, seed=22), 805, 560, t, s("outliers", 46.03), rot=6, dy=-500)
        img = drop(img, vox.print_frame(_photo("assets/photos/celebrity_musk.jpg"), 190, seed=23), 230, 560, t, s("belong", 47.61), rot=-6, dy=-500)
    # 9. receipt
    if s("Which", 48.95) <= t < s("Pain", 52.76):
        lines = [(s("except", 50.01), "DRINKS", "SKIPPED", False), (s("comes", 50.63), "PIZZA", "SKIPPED", False),
                 (s("price", 51.11), "NIGHTS OUT", "SKIPPED", False), (s("won't", 52.19), "TOTAL", "THE PRICE", True)]
        rc = receipt(twos(t), lines)
        img = drop(img, rc, 540, 470 + rc.shape[0] / 2, t, s("Which", 48.95) + .25, rot=-1.5, dy=-300)
    # 10b. gauge
    if s("going", 54.27) <= t < s("That's", 56.82):
        img = drop(img, gauge(t, s("going", 54.27), s("people", 55.35), s("tolerate", 56.15)), 540, 640, t, s("going", 54.27), rot=-1.5, dy=-300)
    # 11. balance scale wobbles
    if s("That's", 56.82) <= t < SEC_CREAM[0] and os.path.exists(C + "scale.png"):
        tt = twos(t)
        rot = 7 * math.sin((tt - 56.8) * 5) * (1 + span(tt, 57.4, 58.4)) + 14 * ease(span(tt, s("hold", 58.16), s("hold", 58.16) + .5))
        img = drop(img, vox.cutout(C + "scale.png", 560, seed=14), 540, 640, t, s("balance", 57.42) - .1, rot=rot, dy=-400)
    # 12. everybody can do it: grid of figures with little scales, NO VALUE
    if SEC_CREAM[0] <= t < s("It's", 65.25):
        t0 = s("everybody", 61.36)
        for i in range(12):
            r_, c_ = divmod(i, 6)
            x, y = 130 + c_ * 165, 470 + r_ * 260
            img = drop(img, figure(INK, 170, 3), x, y, t, t0 + i * .05, dy=-160, shadow=.3)
            if os.path.exists(C + "scale.png") and t >= t0 + i * .05:
                img = paste(img, vox.cutout(C + "scale.png", 80, margin=6, seed=15), x, y - 10, shadow=0.2)
        tn = s("no", 64.28)
        if twos(t) >= tn:
            q = ease(span(twos(t), tn, tn + .17))
            img = paste(img, vox.stamp("NO VALUE", 170, seed=6), 540, 600, rot=-8, scale=1.5 - .5 * q, shadow=0)
    # 13. report cards, the A crossed out
    if s("It's", 65.25) <= t < SEC_CREAM[1]:
        for k, (word, near, x, rot) in enumerate([("class", 65.71, 260, -8), ("everybody", 66.49, 540, 3), ("A", 67.33, 820, 9)]):
            img = drop(img, report(101 + k), x, 600, t, s(word, near), rot=rot, dy=-400)
        tn = s("nothing", 68.34)
        if t >= tn:
            for k, x in enumerate((260, 540, 820)):
                img = vox.marker_x(img, x + 60, 590, 190, span(t, tn + k * .08, tn + .3 + k * .08), seed=7 + k, width=14)
    # 14. scale torn in half
    if s("Screw", 68.83) <= t < s("need", 69.91) + .06 and os.path.exists(C + "scale.png"):
        sc = vox.cutout(C + "scale.png", 560, seed=14)
        q = ease(span(twos(t), s("balance", 69.15), s("balance", 69.15) + .4))
        img = paste(img, torn_half(sc, "L"), 540 - 220 * q, 640 + 60 * q, rot=-18 * q)
        img = paste(img, torn_half(sc, "R"), 540 + 220 * q, 640 + 80 * q, rot=22 * q)
    # 15. warning tape: THE PROBLEM
    if s("But", 71.01) <= t < s("The", 72.65):
        tp = s("problem", 71.99)
        for k, (y, rot) in enumerate([(520, -9), (700, 7)]):
            q = ease(span(twos(t), tp - .25 + k * .1, tp + k * .1))
            if q > 0:
                img = paste(img, vox.strip("THE PROBLEM   THE PROBLEM   THE PROBLEM", 80, bg=MARK, fg=BONE, seed=111 + k),
                            540 + (1 - q) * (1400 if k else -1400), y, rot=rot, shadow=.4)
    # 16a. progress bar into uncomfortable
    if s("The", 72.65) <= t < s("exact", 74.93):
        img = drop(img, progress(t, s("moment", 72.81), s("uncomfortable", 73.61), s("is", 74.59)), 540, 640, t, s("moment", 72.81), rot=-1.5, dy=-300)
    # 17a. muscle fibres tear
    if s("That", 76.87) <= t < s("is", 77.75):
        img = drop(img, fibres(t, s("discomfort", 77.07), 99), 540, 640, t, s("That", 76.87) + .1, rot=-2, dy=-300, scale=1.4)
    # 18a. brain -> muscle
    if s("It", 78.99) <= t < s("adapt", 82.21):
        if os.path.exists(C + "brain.png"):
            img = drop(img, vox.cutout(C + "brain.png", 330, seed=16), 280, 560, t, s("mind", 80.17), rot=-6, dy=-400)
        if os.path.exists(C + "muscle.png"):
            img = drop(img, vox.cutout(C + "muscle.png", 360, seed=17), 800, 600, t, s("body", 79.57), rot=6, dy=-400)
        img = arrow(img, 400, 470, 660, 520, span(twos(t), s("there's", 80.75), s("there's", 80.75) + .45))
        tn = s("no", 81.01)
        if twos(t) >= tn:
            q = ease(span(twos(t), tn, tn + .17))
            img = paste(img, vox.stamp("NO OPTION", 130, seed=8), 540, 820, rot=-6, scale=1.5 - .5 * q, shadow=0)
    # 19. sofa, figures crawl to it
    if s("And", 83.66) <= t < s("Outliers", 87.89):
        if os.path.exists(C + "sofa.png"):
            img = drop(img, vox.cutout(C + "sofa.png", 420, seed=18), 720, 640, t, s("comfort", 87.28) - 2.2, rot=-2, dy=-400)
        tc = s("crawl", 86.40)
        for i in range(3):
            x = 110 + i * 110 + 170 * ease(span(twos(t), tc, tc + 1.0))
            img = drop(img, figure((150, 146, 140), 130, 2), x, 760, t, s("people", 85.12) + i * .08, dy=-160, rot=-20, shadow=.3)
    # 21. judging eyes
    if s("and", 89.29) <= t < s("Normal", 91.37) and os.path.exists(C + "eyes.png"):
        tj = s("that", 89.55)                       # eyes start on "that" so the frame is never empty, one every 0.22 s
        for k, (x, y, sc_, rot) in enumerate([(200, 560, 250, -8), (870, 540, 230, 7), (540, 500, 210, 2), (150, 800, 200, 10), (930, 790, 220, -9)]):
            ti = tj + k * .22
            if twos(t) >= ti:
                q = ease(span(twos(t), ti, ti + .17))
                img = paste(img, vox.cutout(C + "eyes.png", sc_, margin=10, seed=30 + k), x, y, rot=rot, scale=.5 + .5 * q, shadow=.35)
    # 22. mirror turned away, pointing hands
    if s("Normal", 91.37) <= t < s("Crazy", 94.24):
        if os.path.exists(C + "mirror.png"):
            img = drop(img, vox.cutout(C + "mirror.png", 560, seed=19), 230, 700, t, s("people", 91.73), rot=-4, dy=-500)
        if os.path.exists(C + "hand.png"):
            th = s("They", 93.41)
            hand = vox.cutout(C + "hand.png", 170, margin=10, seed=40)
            for k, (x, y, flip, rot) in enumerate([(-60, 960, False, -6), (1140, 960, True, 6), (-60, 1200, False, 8), (1140, 1200, True, -8)]):
                q = ease(span(twos(t), th + k * .08, th + .25 + k * .08))
                if q > 0:
                    hh = hand[:, ::-1] if flip else hand
                    dx = (1 - q) * (-300 if not flip else 300)
                    img = paste(img, np.ascontiguousarray(hh), x + (150 if not flip else -150) + dx, y, rot=rot, shadow=.35)
    # 24. mediocrity
    if s("whatever", 96.09) <= t < s("You", 99.05):
        img = drop(img, clipping("me·di·o·cri·ty", "noun", "being average. Not very good."), 520, 560, t, s("whatever", 96.09) + .1, rot=-2, dy=-300)
        hp = span(twos(t), s("mediocrity", 98.41), s("mediocrity", 98.41) + .4)
        img = highlight(img, 110, 700, 650, 760, hp)
        for i in range(6):
            img = drop(img, figure((150, 146, 140), 110, 2), 250 + i * 110, 870, t, s("better", 97.27) + i * .05, dy=-100, shadow=.3)
    # 25a. YOU on the curve before the last photo
    if s("You", 99.05) <= t < s("were", 99.97):
        img = curve(img, t, s("You", 99.05) - 1.0, s("You", 99.05))
    return img


def front(img, t, st):
    """in front of him: name tags on the paper circle around him."""
    if s("Crazy", 94.24) <= t < s("whatever", 96.09):
        cx, cy, r = st["cx"], st["cy"], st["r"]
        for k, (word, near, x, y, rot) in enumerate([("Crazy", 94.24, cx - r * .95, cy + r * .05, -12), ("boring", 95.02, cx, cy + r * .55, 4),
                                                      ("obsessed", 95.50, cx + r * .95, cy + r * .05, 12)]):
            ti = s(word, near) + .05
            if twos(t) >= ti:
                q = ease(span(twos(t), ti, ti + .17))
                img = paste(img, name_tag(word.upper(), 120 + k), x, y, rot=rot, scale=1.35 - .35 * q, shadow=.4)
    return img


@functools.lru_cache(maxsize=16)
def _photo(path):
    return np.asarray(Image.open(path).convert("RGB"))


# full-scene prints of his photos and clips: (t0, t1, kind, path, src, zoom, cx, cy, width, label, label_t)
PRINTS = [
    (s("a", 28.75), s("You", 30.07), "photo", "assets/photos/me_physique_mirror.jpg", 0, 1, .5, .5, 720, None, None),
    (s("Pain", 52.76), s("discomfort", 53.44), "clip", "raw/vid_1111c.mp4", 4.3, 1.2, 0.0, 1.0, 700, "PAIN", s("Pain", 52.76)),
    (s("discomfort", 53.44), s("going", 54.27), "clip", "raw/pullups.mp4", 7.7, 1.0, .5, .5, 700, "DISCOMFORT", s("discomfort", 53.44)),
    (s("exact", 74.93), s("That", 76.87), "clip", "raw/vid_1111.mp4", 5.0, 1.15, .62, .55, 720, "KEEP GOING", s("keep", 76.19)),
    (s("is", 77.75), s("It", 78.99), "clip", "raw/flex_p1.mp4", 7.2, 1.06, .5, .3, 560, None, None),
    (s("adapt", 82.21), s("And", 83.66), "photo", "assets/photos/me_gym_dumbbell.jpg", 0, 1, .5, .5, 720, None, None),
    (s("Outliers", 87.89), s("and", 89.29), "clip", "raw/flex_p1.mp4", 10.9, 1.04, .5, .3, 720, "OUTLIERS", s("Outliers", 87.89)),
    (s("were", 99.97), LEN + 1, "photo", "assets/photos/me_physique_front.jpg", 0, 1, .5, .5, 720, "YOU.", s("normal", 101.01)),
]
FULLCLIP = (s("need", 69.91) + .06, s("But", 71.01))      # close press full frame, as v2


def print_scene(t):
    for t0, t1, kind, path, src, z, cx, cy, width, label, lt in PRINTS:
        if t0 <= t < t1:
            return (t0, t1, kind, path, src, z, cx, cy, width, label, lt)
    return None


def caption(img, t):
    b = scene2.block_at(t)
    if not b: return img
    text = " ".join(w["w"] for w in b)
    f = font(vox.F_CAP, 46)
    lines, cur = [], ""
    for w in text.split():
        if f.getlength((cur + " " + w).strip()) > 860 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    p = ease(span(twos(t), b[0]["s"] - .05, b[0]["s"] + .17))
    for i, ln in enumerate(lines):
        st = vox.strip(ln, 46, bg=(20, 16, 16), fg=BONE, seed=hash(ln) % 997, font_path=vox.F_CAP, padx=22, pady=11)
        img = paste(img, st, W / 2 - 40, 270 + i * 70 - (1 - p) * 30, rot=-0.8 + 0.6 * i, shadow=.3)
    return img


WIPES = [s("You", 40.25), s("That's", 56.82), s("But", 71.01), s("You", 99.05)]


def wipe(img, t):
    for k, tw in enumerate(WIPES):
        p = span(twos(t), tw - .25, tw + .25)
        if 0 < p < 1:
            sheet = _wipe_sheet(k)
            x = -W * .9 + (p * p * (3 - 2 * p)) * W * 2.8
            img = paste(img, sheet, x, H / 2, rot=5, shadow=.5)
    return img


@functools.lru_cache(maxsize=4)
def _wipe_sheet(k):
    return vox.paper_sheet(int(W * 1.1), int(H * 1.25), (226, 216, 196) if k % 2 == 0 else (58, 6, 10), 300 + k, rough=22)


import circle as circ
# where he sits (time, state): BIG for punchy lines, small left / right when the visual does the work
_K = [("Normal", 27.40, "BIG"), ("You", 30.07, "SR"), ("and", 33.63, "SL"), ("So", 36.91, "SR"), ("Actually", 38.96, "BIG"),
      ("Success", 42.62, "SL"), ("Successful", 44.89, "SR"), ("Which", 48.95, "SL"), ("going", 54.27, "SR"),
      ("That's", 56.82, "SL"), ("Balance", 60.32, "SR"), ("It's", 65.25, "SL"), ("Screw", 68.83, "BIG"),
      ("The", 72.65, "SR"), ("That", 76.87, "SL"), ("It", 78.99, "SR"), ("And", 83.66, "SL"), ("and", 89.29, "BIG"),
      ("whatever", 96.09, "SR"), ("You", 99.05, "BIG")]
STATES = [(HIS if i == 0 else s(w, n) - 0.12, n_) for i, (w, n, n_) in enumerate(_K)]
ZOOM = {"BIG": (1.0, 0.0), "SR": (1.1, 150.0), "SL": (1.1, 150.0)}     # visual layer zoom about (540, 380), push down
MOVE = 0.25                                                             # jump time, stepped on twos


def state_at(t):
    """circle state and visual zoom; jumps between states in MOVE seconds on twos."""
    tt = twos(t)
    cur, prev, t0 = STATES[0][1], STATES[0][1], STATES[0][0]
    for ts, name in STATES:
        if tt >= ts:
            prev, cur, t0 = cur, name, ts
    u = ease(span(tt, t0, t0 + MOVE)) if prev != cur else 1.0
    A, B = getattr(circ, prev), getattr(circ, cur)
    st = {k: A[k] + (B[k] - A[k]) * u for k in A}
    za, zb = ZOOM[prev], ZOOM[cur]
    return st, (za[0] + (zb[0] - za[0]) * u, za[1] + (zb[1] - za[1]) * u)


for ts, _ in STATES[1:]:
    sfx(ts + MOVE * .6, "paper-02", -14)


def visual_layer(t):
    """behind() drawn on black and on white -> colour + alpha, so the whole layer can be zoomed."""
    kb = behind(np.zeros((H, W, 3), np.uint8), t).astype(np.float32)
    kw = behind(np.full((H, W, 3), 255, np.uint8), t).astype(np.float32)
    a = np.clip(1 - (kw - kb).mean(2) / 255, 0, 1)
    rgb = np.where(a[..., None] > 1e-3, kb / np.maximum(a[..., None], 1e-3), 0)
    return np.clip(rgb, 0, 255), a


def place_layer(g, t, zoom):
    z, dy = zoom
    rgb, a = visual_layer(t)
    if abs(z - 1) > 1e-3 or dy:
        M = np.float32([[z, 0, 540 - 540 * z], [0, z, 380 - 380 * z + dy]])
        rgb = cv2.warpAffine(rgb.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
        a = cv2.warpAffine(a.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR)
    out = g.astype(np.float32) * (1 - a[..., None]) + rgb * a[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def him(img, base, f, t, st):
    m = scene2.matte(f)
    b2, m2 = scene2.edge_fix(base, m)
    cream = SEC_CREAM[0] <= t < SEC_CREAM[1]
    return circ.draw(img, b2, m2, st, inside=(74, 0, 5) if cream else (226, 216, 196),
                     ring=BONE if cream else (158, 26, 43), seed=7)


def compose(f, base):
    t = f / 30
    if t < HIS:
        return base                                    # her clip untouched
    if FULLCLIP[0] <= t < FULLCLIP[1]:
        u = (t - FULLCLIP[0]) / (FULLCLIP[1] - FULLCLIP[0])
        img = fx1.clip_frame("raw/vid_1111b.mp4", 0.7 + (t - FULLCLIP[0]), 1.04 + .06 * u, .5, .5)
        return caption(np.ascontiguousarray(img), t)
    g = ground(t)
    g = motion_kit.grain(np.ascontiguousarray(g), GRAIN, seed=f)
    pr = print_scene(t)
    if pr:
        t0, t1, kind, path, src, z, cx, cy, width, label, lt = pr
        pic = _photo(path) if kind == "photo" else fx1.clip_frame(path, src + (t - t0), z, cx, cy)
        img = behind(g, t)
        pf = vox.print_frame(np.ascontiguousarray(pic), width, seed=hash(path) % 50)
        x = 760 if width < 600 else W / 2
        q = land(t, t0 + .17, .17)
        img = paste(img, pf, x, 1010 + (1 - q) * 300, rot=-1.5 if width >= 600 else 3, shadow=.5)
        if path.endswith("mirror.jpg"):
            img = vox.marker_circle(img, int(W / 2), 1010, 430, 640, span(twos(t), t0 + .5, t0 + 1.0), seed=3)
        if label and t >= lt:
            ql = ease(span(twos(t), lt, lt + .17))
            img = paste(img, vox.strip(label, 96, bg=MARK, fg=BONE, seed=hash(label) % 99), 300, 470 + (1 - ql) * -60, rot=-4, shadow=.4)
        if width < 600:                                 # side-by-side: fibres grow back next to the print
            img = drop(img, fibres(t, 0, s("makes", 78.27)), 280, 700, t, t0, rot=-3, dy=0, scale=1.0)
        img = caption(img, t)
        return wipe(img, t)
    st, zoom = state_at(t)
    img = place_layer(g, t, zoom)
    img = him(img, base, f, t, st)
    img = front(img, t, st)
    img = caption(img, t)
    return wipe(img, t)


def still(t, out):
    f = fr(t)
    b = next(scene2.base_frames(f, 1))
    Image.fromarray(compose(f, b)).save(out)


def render(a, b, out, crf=14):
    f0, f1 = fr(a), min(fr(b), fr(LEN))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                            "-i", "-", "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast", "-g", "30",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i, bf in enumerate(scene2.base_frames(f0, f1 - f0)):
        enc.stdin.write(np.ascontiguousarray(compose(f0 + i, bf)).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    if sys.argv[1] == "still":
        os.makedirs("out/stills/v3", exist_ok=True)
        for t in sys.argv[2:]:
            still(float(t), f"out/stills/v3/s_{float(t):06.2f}.png")
    elif sys.argv[1] == "render":
        render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
