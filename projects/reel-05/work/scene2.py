"""reel-05 v2: Automance intro after the user's 9-frame storyboard (refs/storyboard/frame_1..9.jpg).

1 night landscape (dark hill, skyline, snowy mountains, winding road)  2 pink glow behind the mountains
3 red sun peeks  4 bike rides in from the left  5 car comes in from the right  6 both close
7 they cross and lock into the logo while the camera pulls back and the world turns white
8 AUTOMANCE with an orange light streak  9 tagline, then the exact logo.

World coordinates = the final 1920x1080 logo canvas (work/layers/). Two cameras: the scenery
camera (big zoom at the start, identity at the end) and the vehicle camera (parallax, vehicles big
and low on screen, identity at the end).

python3 work/scene2.py still 0.0 0.1 ...           -> out/stills/t_<t>.png
python3 work/scene2.py render out/x.mp4 [--fps 60] [--scale 0.5] [--start a --end b]
"""
import json, os, subprocess, sys
import cv2
import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "layers")
W, H = 1920, 1080
DUR = 3.0
FPS = 60
UP = 2                     # layers are upsampled 2x (crisp when zoomed in)


# ------------------------------------------------------------------ easing / keyframes
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def sstep(u):
    return u * u * (3 - 2 * u)


def smoother(u):
    return u * u * u * (u * (u * 6 - 15) + 10)


def ease_out(u, p=3):
    return 1 - (1 - u) ** p


def back_out(u, s=1.4):
    u = u - 1
    return u * u * ((s + 1) * u + s) + 1


def keys(t, kf, ease=sstep):
    """piecewise interpolation of numbers or arrays over [(time, value), ...] with easing per segment."""
    if t <= kf[0][0]:
        return np.asarray(kf[0][1], np.float64)
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            u = ease((t - t0) / (t1 - t0))
            return np.asarray(v0, np.float64) * (1 - u) + np.asarray(v1, np.float64) * u
    return np.asarray(kf[-1][1], np.float64)


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float64) / 255  # BGR


# ------------------------------------------------------------------ timing
T_MERGE = (1.45, 1.95)          # cross, lock, pull back, world turns white
T_LOCK = 1.95
T_LETTERS = 2.00                # first letter
T_LSTEP, T_LDUR = 0.035, 0.20
T_REDA = (2.24, 2.42)
T_STREAK = (2.10, 2.50)
T_TAG = (2.40, 2.72)
T_FINAL = (2.72, 2.84)          # blend into the exact logo, then hold
STREAK_Y = 921

# scenery camera: world anchor -> screen anchor, zoom
CAM_S = [(0.0, (1040, 352, 1020, 540, 1.60)), (1.45, (1040, 362, 1020, 560, 1.80)),
         (T_MERGE[1], (1040, 362, 1040, 362, 1.0))]
# vehicle camera: zoom and the screen y of the ground line (world y 725)
CAM_V = [(0.0, (1.12, 952)), (1.45, (1.12, 952)), (T_MERGE[1], (1.0, 725.0))]
GROUND_W = 725.0
# left edge of each vehicle on screen (PCHIP: smooth speed, ends at rest)
BIKE_L = PchipInterpolator([0.78, 1.08, 1.30, 1.45, 1.95, 2.3], [-760, -20, 60, 120, 965, 965])
CAR_L = PchipInterpolator([0.98, 1.24, 1.45, 1.95, 2.3], [2010, 1060, 900, 377, 377])
BIKE_X0, CAR_X0 = 965.0, 377.0          # their left edges in the logo

# sky: (time, top colour, horizon colour, glow colour, glow strength, glow radius)
SKY = [(0.00, "#0e1322", "#262c44", "#6a6f96", 0.20, 260),
       (0.35, "#1a1f36", "#4a4660", "#e3786a", 0.55, 330),
       (0.65, "#2e3150", "#7a6474", "#f29a78", 0.85, 420),
       (1.05, "#5d6286", "#c9a094", "#ffc796", 1.00, 560),
       (1.45, "#7e8098", "#d9b2a2", "#ffd2a4", 1.00, 650),
       (1.95, "#f1f0f5", "#fdfbfa", "#ffe6cf", 0.45, 900),
       (2.40, "#f7f6f9", "#fefdfc", "#ffeedd", 0.25, 1000),
       (2.80, "#ffffff", "#ffffff", "#ffffff", 0.00, 1000)]
HILL = [(0.0, "#0c0e16", "#0a0b12"), (0.85, "#101219", "#0d0e14"), (1.20, "#2c2d35", "#9d9ca4"),
        (1.45, "#3a3b43", "#b7b5bb"), (T_MERGE[1] - 0.05, "#fdfbfa", "#ffffff"), (2.6, "#ffffff", "#ffffff")]
FACE = [(0.0, "#8a90ab", "#565c78"), (1.0, "#c7c8d4", "#8d90a6"), (1.45, "#d6d6de", "#a4a6b6"),
        (T_MERGE[1] - 0.05, "#ffffff", "#ffffff")]
ROADC = [(0.0, "#7d8199"), (1.2, "#c9c8cf"), (1.6, "#c9c8cf"), (T_MERGE[1] - 0.03, "#000000")]
SUN_C, SUN_R = (1147.5, 241.5), 61.5
SUN_RISE = [(0.40, 175.0), (0.66, 95.0), (1.15, 18.0), (1.6, 0.0)]       # px below its final place

# hill top edge in world px (left low, up to the skyline base, under the mountains, down to the right)
HILL_EDGE = [(-500, 560), (0, 492), (300, 450), (535, 404), (650, 374), (800, 359), (960, 350),
             (1100, 344), (1300, 358), (1530, 385), (1900, 430), (2500, 520)]


# ------------------------------------------------------------------ assets
def load():
    boxes = json.load(open(os.path.join(LAY, "boxes.json")))
    L = {}
    fills = {n: cv2.imread(os.path.join(LAY, f"{n}_fill.png"), 0).astype(np.float32) / 255 for n in ("car", "bike")}
    tyre = cv2.imread(os.path.join(LAY, "car_tyre.png"), 0).astype(np.float32) / 255
    for name, (x0, y0, x1, y1) in boxes.items():
        im = cv2.imread(os.path.join(LAY, f"{name}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
        if name in fills:
            ys, xs = np.where(fills[name] > 0.01)
            x0, y0, x1, y1 = min(x0, xs.min()), min(y0, ys.min()), max(x1, xs.max()), max(y1, ys.max())
        pad = 6
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        x1, y1 = min(W, x1 + pad + 1), min(H, y1 + pad + 1)
        c = im[y0:y1, x0:x1]
        up = lambda a: cv2.resize(a, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
        a = np.clip(up(c[..., 3]), 0, 1)
        a = np.clip((a - 0.5) * 1.35 + 0.5, 0, 1)            # crisper edges at 2x
        col = np.clip(up(c[..., :3]), 0, 1)
        r, g, b = col[..., 2], col[..., 1], col[..., 0]
        red = np.clip((r - (g + b) / 2 - 0.15) * 3, 0, 1)
        d = dict(x=x0, y=y0, a=a, col=col, red=red, box=boxes[name])
        if name in fills:
            d["fill"] = np.clip(up(fills[name][y0:y1, x0:x1]), 0, 1)
            if name == "car":
                d["tyre"] = np.clip(up(tyre[y0:y1, x0:x1]), 0, 1)
        L[name] = d
    rn = L["road_near"]
    k = np.ones((9, 9), np.uint8)
    rib = cv2.dilate(cv2.erode((rn["a"] > 0.5).astype(np.uint8), k), k).astype(np.float32)
    rib = cv2.GaussianBlur(rib, (0, 0), 1.0)
    rib = np.minimum(rib, rn["a"])
    L["road_ribbon"] = dict(rn, a=rib)
    L["road_thin"] = dict(rn, a=np.clip(rn["a"] - rib, 0, 1))
    ring = cv2.dilate(rib, np.ones((7, 7), np.uint8)) - cv2.erode(rib, np.ones((3, 3), np.uint8))
    L["road_edge"] = dict(rn, a=np.clip(cv2.GaussianBlur(ring, (0, 0), 1.2) * 1.2, 0, 1))
    ref = cv2.imread(os.path.join(LAY, "reference_1080.png")).astype(np.float32) / 255
    return L, ref


L, REF = load()
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RNG = np.random.default_rng(7)
STARS = np.c_[RNG.uniform(0, W, 170), RNG.uniform(0, 560, 170), RNG.uniform(0.25, 1, 170), RNG.uniform(0, 6.3, 170)]


def mountain_face_top():
    """per world column: top of the mountain face (ridge top, or the logo sun's bottom edge where the sun is)."""
    m, s = L["mountains"], L["sun"]
    top = {}
    a = m["a"]
    for cx in range(a.shape[1]):
        rows = np.where(a[:, cx] > 0.5)[0]
        if len(rows):
            top[(m["x"] * UP + cx) / UP] = (m["y"] * UP + rows[0]) / UP
    sa = s["a"]
    for cx in range(sa.shape[1]):
        rows = np.where(sa[:, cx] > 0.5)[0]
        if len(rows):
            wx = (s["x"] * UP + cx) / UP
            sb = (s["y"] * UP + rows[-1]) / UP + 1.5
            if wx in top:
                top[wx] = min(top[wx], sb)
    xs = np.array(sorted(top))
    ys = np.array([top[x] for x in xs])
    ys = cv2.GaussianBlur(ys.reshape(1, -1).astype(np.float32), (0, 0), 1.0).ravel()
    return xs, ys


FACE_X, FACE_Y = mountain_face_top()
HE = np.array(HILL_EDGE, np.float64)
HILL_X = np.arange(-600, 2600, 4.0)
HILL_Y = PchipInterpolator(HE[:, 0], HE[:, 1])(HILL_X)


# ------------------------------------------------------------------ cameras
def cam_s(t):
    wx, wy, sx, sy, z = keys(t, CAM_S, smoother)
    return wx, wy, sx, sy, z


def w2s(pts, cam):
    wx, wy, sx, sy, z = cam
    p = np.asarray(pts, np.float64)
    return np.c_[sx + (p[:, 0] - wx) * z, sy + (p[:, 1] - wy) * z]


def place(canvas, ly, M, ink=None, alpha=1.0, blur=0, fill_col=None, tyre=0.0, mask=None):
    """composite a 2x layer crop with affine M (crop px -> screen px).
    ink: colour for the neutral ink (None = original colours). fill_col: colour of the body fill."""
    if alpha <= 0.002:
        return
    a = ly["a"] * alpha
    col = ly["col"]
    if ink is not None:
        red = ly["red"][..., None]
        col = col * red + np.asarray(ink, np.float32) * (1 - red)
    layers = []
    if fill_col is not None and "fill" in ly:
        f = ly["fill"] * alpha
        fc = np.broadcast_to(np.asarray(fill_col, np.float32), f.shape + (3,))
        if tyre > 0 and "tyre" in ly:
            tm = (ly["tyre"] * tyre)[..., None]
            fc = fc * (1 - tm) + np.array([0.05, 0.05, 0.06], np.float32) * tm
        layers.append((fc, f))
    layers.append((col, a))
    for c, aa in layers:
        if mask is not None:
            aa = aa * mask
        pm = np.dstack([c * aa[..., None], aa]).astype(np.float32)
        big = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        if blur > 1.5:
            k = int(blur) | 1
            big = cv2.blur(big, (k, 1))
        canvas[:] = canvas * (1 - big[..., 3:4]) + big[..., :3]


def M_scenery(ly, cam):
    wx, wy, sx, sy, z = cam
    k = z / UP
    return np.array([[k, 0, sx + (ly["x"] - wx) * z], [0, k, sy + (ly["y"] - wy) * z]], np.float32)


def M_vehicle(ly, t, left_screen=None, x0=None):
    zv, gs = keys(t, CAM_V, smoother)
    k = zv / UP
    # world x -> screen: 960 + (x-960)*zv + dx ; dx puts the vehicle's left edge at left_screen
    dx = 0.0
    if left_screen is not None:
        dx = left_screen - (960 + (x0 - 960) * zv)
    tx = 960 + (ly["x"] - 960) * zv + dx
    ty = gs + (ly["y"] - GROUND_W) * zv
    return np.array([[k, 0, tx], [0, k, ty]], np.float32), zv


# ------------------------------------------------------------------ scenery
def sky(t, cam):
    top, hor, glc = [keys(t, [(k[0], rgb(k[i])) for k in SKY]) for i in (1, 2, 3)]
    gs, gr = [float(keys(t, [(k[0], k[i]) for k in SKY])) for i in (4, 5)]
    sun_screen = w2s([(SUN_C[0], SUN_C[1] + 40)], cam)[0]
    hy = float(w2s([(0, 360)], cam)[0, 1])
    v = np.clip(YY / max(hy, 50), 0, 1) ** 1.3
    bg = top * (1 - v[..., None]) + hor * v[..., None]
    if gs > 0:
        z = cam[4]
        d = np.sqrt((XX - sun_screen[0]) ** 2 + ((YY - sun_screen[1]) * 1.6) ** 2)
        g = np.exp(-(d / (gr * z / 1.4)) ** 2) * gs
        bg = bg * (1 - g[..., None]) + glc * g[..., None]
    sv = 1 - prog(t, 0.45, 0.95)
    if sv > 0:
        st = np.zeros((H, W), np.float32)
        for x, y, b, ph in STARS:
            cv2.circle(st, (int(x * 16), int(y * 16)), 12, float(b * (0.7 + 0.3 * np.sin(ph + t * 8))), -1, cv2.LINE_AA, shift=4)
        st = cv2.GaussianBlur(st, (0, 0), 0.7) * 1.4
        bg = bg + st[..., None] * sv * 0.8 * (1 - v[..., None])
    return bg.astype(np.float32)


def draw_poly(canvas, pts, col_top, col_bot=None, y_top=None, y_bot=None):
    m = np.zeros((H, W), np.uint8)
    p = np.round(np.asarray(pts) * 16).astype(np.int32)
    cv2.fillPoly(m, [p], 255, cv2.LINE_AA, shift=4)
    a = (m.astype(np.float32) / 255)[..., None]
    if col_bot is None:
        c = np.asarray(col_top, np.float32)
    else:
        v = np.clip((YY - y_top) / max(1, y_bot - y_top), 0, 1)[..., None]
        c = (np.asarray(col_top) * (1 - v) + np.asarray(col_bot) * v).astype(np.float32)
    canvas[:] = canvas * (1 - a) + c * a


def scenery(c, t, cam):
    # sun (a full disc, the mountain face hides its lower part)
    rise = float(keys(t, SUN_RISE, sstep))
    if t >= SUN_RISE[0][0]:
        sc = w2s([(SUN_C[0], SUN_C[1] + rise)], cam)[0]
        r = SUN_R * cam[4]
        m = np.zeros((H, W), np.uint8)
        cv2.circle(m, (int(sc[0] * 16), int(sc[1] * 16)), int(r * 16), 255, -1, cv2.LINE_AA, shift=4)
        a = (m.astype(np.float32) / 255)[..., None]
        red = rgb("#d81e14")
        glow = cv2.GaussianBlur(a, (0, 0), r * 0.35)[..., None] if a.ndim == 2 else cv2.GaussianBlur(a[..., 0], (0, 0), r * 0.35)[..., None]
        wht = 1 - prog(t, 1.5, T_MERGE[1])
        c[:] = c + glow * np.array([0.25, 0.45, 0.9], np.float32) * 0.45 * wht
        c[:] = c * (1 - a) + red.astype(np.float32) * a
    # mountain faces
    ft, fb = keys(t, [(k[0], rgb(k[1])) for k in FACE]), keys(t, [(k[0], rgb(k[2])) for k in FACE])
    top = np.c_[FACE_X, FACE_Y]
    bot = np.array([(FACE_X[-1] - 10, 410), (985, 410), (FACE_X[0] + 14, FACE_Y[0] + 26)])
    pts = w2s(np.r_[top, bot], cam)
    ys = w2s([(0, 230), (0, 380)], cam)[:, 1]
    draw_poly(c, pts, ft, fb, ys[0], ys[1])
    place(c, L["mountains"], M_scenery(L["mountains"], cam), ink=(0, 0, 0))
    place(c, L["skyline"], M_scenery(L["skyline"], cam), ink=(0, 0, 0))
    # hill
    ht, hb = keys(t, [(k[0], rgb(k[1])) for k in HILL]), keys(t, [(k[0], rgb(k[2])) for k in HILL])
    edge = np.c_[HILL_X, HILL_Y]
    pts = w2s(np.r_[edge, [(2600, 3000), (-600, 3000)]], cam)
    hy = w2s([(0, 350)], cam)[0, 1]
    draw_poly(c, pts, ht, hb, hy, H)
    # road lines
    rc = keys(t, [(k[0], rgb(k[1])) for k in ROADC])
    edge_a = 1 - prog(t, T_MERGE[0] + 0.1, T_MERGE[1] - 0.05)
    place(c, L["road_edge"], M_scenery(L["road_edge"], cam), ink=keys(t, [(0, rgb("#8e93ab")), (1.2, rgb("#d4d3da"))]), alpha=edge_a)
    place(c, L["road_ribbon"], M_scenery(L["road_ribbon"], cam), ink=keys(t, [(0, rgb("#0b0c12")), (0.9, rgb("#101118")), (1.25, rgb("#26272e")), (1.45, rgb("#2e2f36")), (T_MERGE[1] - 0.05, rgb("#000000"))]))
    place(c, L["road_thin"], M_scenery(L["road_thin"], cam), ink=rc)
    place(c, L["road_far"], M_scenery(L["road_far"], cam), ink=rc)


# ------------------------------------------------------------------ vehicles
def vehicles(c, t):
    dt = 1 / FPS
    tyre = 1 - prog(t, 1.70, T_MERGE[1])
    fill = (1.0, 1.0, 1.0)
    # ground line
    gu = prog(t, 0.80, 1.10)
    if gu > 0:
        g = L["ground"]
        M, _ = M_vehicle(g, t)
        h, w = g["a"].shape
        xs = np.arange(w, dtype=np.float32)
        pos = ease_out(gu, 2) * (w + 200) - 100
        mask = np.broadcast_to(np.clip((pos - xs) / 100 + 0.5, 0, 1)[None, :], (h, w))
        place(c, g, M, ink=(0, 0, 0), mask=mask)
    items = []
    for name, curve, x0, t0 in (("bike", BIKE_L, BIKE_X0, 0.78), ("car", CAR_L, CAR_X0, 0.98)):
        if t < t0:
            continue
        ly = L[name]
        left = float(curve(min(t, 2.3)))
        spd = abs(left - float(curve(min(max(t - dt, t0), 2.3))))
        M, zv = M_vehicle(ly, t, left, x0)
        items.append((name, ly, M, spd))
    trail = 1 - prog(t, 1.75, T_LOCK)
    if trail > 0:
        for name, ly, M, spd in items:
            streak(c, ly, M, -1 if name == "bike" else 1, trail * (0.55 + min(0.45, spd / 60)))
    for name, ly, M, spd in items:
        place(c, ly, M, ink=(0, 0, 0), fill_col=fill, tyre=tyre if name == "car" else 0, blur=spd * 0.55)


def streak(c, ly, M, direction, amount):
    """motion streak smeared out of the vehicle's back (direction -1 = to the left)."""
    body = np.maximum(ly["a"], ly["fill"])
    light = (1 - ly["a"]) * ly["fill"] * 0.9                     # white body -> light streak
    pm = np.dstack([np.repeat(light[..., None], 3, 2), body]).astype(np.float32)
    big = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_LINEAR)
    small = cv2.resize(big, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    acc = np.zeros_like(small)
    n = 60
    wsum = 0.0
    for i in range(1, n + 1):
        w8 = (1 - i / n) ** 2
        acc += cv2.warpAffine(small, np.float32([[1, 0, i * 3 * direction], [0, 1, 0]]), (W // 4, H // 4)) * w8
        wsum += w8
    acc /= wsum / 3.0
    acc = cv2.GaussianBlur(acc, (0, 0), 2.0, sigmaY=0.6)
    acc = cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)
    a2 = np.clip(acc[..., 3:4] * amount, 0, 1) * (1 - big[..., 3:4])   # only outside the vehicle itself
    col = np.clip(acc[..., :3] / np.maximum(acc[..., 3:4], 1e-3), 0, 1) * 0.5 + 0.5
    c[:] = c * (1 - a2 * 0.8) + col * a2 * 0.8


# ------------------------------------------------------------------ text
def text(c, t):
    order = [0, 1, 2, 3, 4, 6, 7, 8]
    for k, i in enumerate(order):
        u = clamp((t - (T_LETTERS + k * T_LSTEP)) / T_LDUR)
        if u <= 0:
            continue
        ly = L[f"letter_{i}"]
        e = back_out(u, 1.3)
        dy = 46 * (1 - e)
        M = np.array([[1 / UP, 0, ly["x"]], [0, 1 / UP, ly["y"] + dy]], np.float32)
        a = min(1, u * 2.5)
        place(c, ly, M, ink=(0, 0, 0), alpha=a)
    u = prog(t, *T_REDA)
    if u > 0:
        ly = L["letter_5"]
        e = back_out(u, 1.8)
        dy = -60 * (1 - e)
        M = np.array([[1 / UP, 0, ly["x"]], [0, 1 / UP, ly["y"] + dy]], np.float32)
        f = prog(t, T_REDA[1] - 0.05, T_REDA[1] + 0.25)
        if 0 < f < 1:
            cx, cy = (ly["box"][0] + ly["box"][2]) / 2, (ly["box"][1] + ly["box"][3]) / 2 + 10
            d = np.sqrt(((XX - cx) / 1.4) ** 2 + (YY - cy) ** 2)
            g = (np.exp(-(d / (55 + 40 * f)) ** 2) * np.sin(np.pi * f) * 0.35 * (YY < 895))[..., None]
            c[:] = c * (1 - g) + np.array([0.2, 0.25, 0.95], np.float32) * g
        place(c, ly, M, alpha=min(1, u * 2.5))
    # orange light streak (frame 8), then the tagline opens from it (frame 9)
    su = prog(t, *T_STREAK)
    if su > 0:
        fade = 1 - prog(t, 2.50, 2.78)
        half = 720 * ease_out(su, 3)
        dx = np.abs(XX - 960)
        along = np.clip(1 - dx / max(half, 1), 0, 1) ** 0.6
        across = np.exp(-((YY - STREAK_Y) / 3.2) ** 2) + 0.55 * np.exp(-((YY - STREAK_Y) / 16) ** 2)
        g = (along * across * fade * 0.95)[..., None]
        col = np.array([0.30, 0.62, 1.0], np.float32)       # warm orange (BGR)
        core = (along * np.exp(-((YY - STREAK_Y) / 1.6) ** 2) * fade)[..., None]
        c[:] = c * (1 - np.clip(g, 0, 1)) + col * np.clip(g, 0, 1)
        c[:] = c * (1 - core * 0.6) + np.array([0.85, 0.95, 1.0], np.float32) * core * 0.6
    tu = prog(t, *T_TAG)
    if tu > 0:
        e = ease_out(tu, 3)
        for n, d in (("tag_line_l", "rl"), ("tag_line_r", "lr")):
            ly = L[n]
            h, w = ly["a"].shape
            xs = np.arange(w, dtype=np.float32)
            pos = e * (w + 40)
            m = np.clip((pos - xs) / 40, 0, 1) if d == "lr" else np.clip((pos - (w - xs)) / 40, 0, 1)
            M = np.array([[1 / UP, 0, ly["x"]], [0, 1 / UP, ly["y"]]], np.float32)
            place(c, ly, M, ink=(0, 0, 0), mask=np.broadcast_to(m[None, :], (h, w)))
        for n in ("tag_letters", "tag_bar"):
            ly = L[n]
            h, w = ly["a"].shape
            xs = np.abs(np.arange(w, dtype=np.float32) - (960 - ly["x"]) * UP)
            pos = e * (w * 0.62 + 200)
            m = np.clip((pos - xs) / 200, 0, 1)
            sp = 1 + 0.06 * (1 - e)                          # letters settle from slightly wider
            cx = 960
            M = np.array([[sp / UP, 0, cx + (ly["x"] - cx) * sp], [0, 1 / UP, ly["y"]]], np.float32)
            place(c, ly, M, ink=(0, 0, 0), mask=np.broadcast_to(m[None, :], (h, w)), alpha=min(1, tu * 2))


# ------------------------------------------------------------------ frame
def frame(t):
    cam = cam_s(t)
    c = sky(t, cam)
    scenery(c, t, cam)
    vehicles(c, t)
    # soft light from the joint at the lock
    f = prog(t, T_LOCK - 0.06, T_LOCK + 0.30)
    if 0 < f < 1:
        d = np.sqrt((XX - 1012) ** 2 + ((YY - 560) * 1.3) ** 2)
        g = (np.exp(-(d / (120 + 500 * f)) ** 2) * np.sin(np.pi * f) * 0.12)[..., None]
        c[:] = c * (1 - g) + g
    text(c, t)
    fb = smoother(prog(t, *T_FINAL))
    if fb > 0:
        c = c * (1 - fb) + REF * fb
    return np.clip(c * 255 + 0.5, 0, 255).astype(np.uint8)


def main():
    cmd = sys.argv[1]
    root = os.path.join(HERE, "..")
    if cmd == "still":
        d = os.path.join(root, "out", "stills")
        os.makedirs(d, exist_ok=True)
        for a in sys.argv[2:]:
            cv2.imwrite(os.path.join(d, f"t_{float(a):05.2f}.png"), frame(float(a)))
    elif cmd == "render":
        out = sys.argv[2]
        arg = lambda k, dflt: type(dflt)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else dflt
        fps, scale = arg("--fps", FPS), arg("--scale", 1.0)
        a, b = arg("--start", 0.0), arg("--end", DUR)
        ow, oh = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                              "-s", f"{ow}x{oh}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "14",
                              "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for i in range(int(round(a * fps)), int(round(b * fps))):
            im = frame(i / fps)
            if scale != 1:
                im = cv2.resize(im, (ow, oh), interpolation=cv2.INTER_AREA)
            p.stdin.write(im.tobytes())
        p.stdin.close()
        p.wait()


if __name__ == "__main__":
    main()
