"""reel-03: shot-for-shot remake of raw/reference.mp4 with the user's footage. Audio = the reference's, untouched.

python3 work/build/edit.py stills 3.2 11.5 ...         -> out/stills/s_<t>.png
python3 work/build/edit.py draft A B [--half]           -> out/draft_A-B.mp4 (with the reference audio for that range)
python3 work/build/edit.py render [A B]                 -> out/master.mp4 (crf 14)
Run from projects/reel-03.
"""
import sys, os, subprocess, functools
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from fx import *

R = "raw/"
C01, C02, C03, C04 = R + "c01_man_walking_gym.mp4", R + "c02_man_in_gym.mp4", R + "c03_vid_164738.mp4", R + "c04_man_turning_head.mp4"
C05, C06, C07 = R + "c05_glow_figure_beach.jpg", R + "c06_dark_empty_gym.jpg", R + "c07_back_photo.jpg"
C08, C09, C10 = R + "c08_vid_185334.mp4", R + "c09_vid_201511.mp4", R + "c10_vid_180447.mp4"
END = 22.22

# colours (B,G,R)
WHITE = (1, 1, 1)
CAP_ON_PIC = (0.84, 0.92, 0.94)          # the reference's pale warm caption colour over footage
RED = (92 / 255, 88 / 255, 222 / 255)    # "breathe."
TEAL = (130 / 255, 140 / 255, 0.0)
MINT = (188 / 255, 212 / 255, 168 / 255)  # "okay?"
O_TEAL = (180 / 255, 165 / 255, 40 / 255)

# ---------- captions, timed to the reference frame by frame ----------
CAPS = [
    (0.00, 0.32, "you’ve"), (0.32, 0.56, "gotta"), (0.56, 0.72, "want"), (0.72, 1.60, "it"),
    (1.60, 2.00, "as bad"), (2.00, 2.16, "as"), (2.16, 2.32, "you"), (2.32, 2.48, "want"), (2.48, 2.64, "to"),
    (4.32, 4.72, "and if you want"), (4.72, 6.40, "want it that bad"), (6.96, 7.52, "if you're willing"),
    (7.52, 8.08, "to give it"), (8.08, 9.12, "that much,"), (9.12, 9.92, "you get a big"), (9.92, 10.40, "piece of"),
    (10.40, 10.80, "what you want."), (11.20, 11.28, "anything you want"), (11.36, 11.84, "anything you want"),
    (11.84, 12.64, "can happen and"), (12.64, 13.40, "become a reality."), (13.68, 14.32, "i believe that"),
    (14.32, 15.12, "sincerely and"), (15.12, 16.00, "i'll die on that"), (16.00, 16.24, "thought."),
    (17.60, 18.32, "i say that not"), (18.32, 18.40, "from"), (18.40, 19.12, "something i read,"),
    (19.84, 20.00, "it's from"), (20.00, 20.24, "something"), (20.24, 20.56, "i lived."), (21.20, 21.80, "okay?"),
]
CAP_SIZE = size_for_width("something i read,", 312)
BLACK_SPANS = [(0, 2.64), (18.0, END)]


def captions(f, t):
    on_black = any(a <= t < b for a, b in BLACK_SPANS)
    for a, b, s in CAPS:
        if a <= t < b:
            put_text(f, s, CAP_SIZE, WHITE if on_black else CAP_ON_PIC, glow=0 if on_black else 0.6)
    return f


def finish(f, i, g=0.035, vig=0.45, ca=3):
    f = chroma(f, ca)
    f = vignette(f, vig)
    return grain(f, i, g)


# ---------- beat 1 / 18: black ----------
def bar_h(t):
    return int(302 * (min(t, 2.64) / 2.64) ** 1.5)


def b_black_open(tl, i):
    f = np.zeros((H, W, 3), np.float32)
    h = bar_h(tl)
    if h > 0:
        wob = (3 * np.sin(np.arange(W) / 90 + i * 0.3)).astype(int)
        for x in range(0, W, 4):
            f[:max(h + wob[x], 0), x:x + 4] = 0.835
            f[H - max(h - wob[x], 0):, x:x + 4] = 0.835
    return f


def b_black(tl, i):
    return np.zeros((H, W, 3), np.float32)


# ---------- beat 2: "breathe." over the dark gym, light flickers on ----------
@functools.lru_cache(maxsize=1)
def gym_layers():
    src = still(C06)
    on = cover(src)
    on = grade(on, gain=(1.0, 0.98, 0.86), gamma=1.35, contrast=1.1)
    tube = np.clip((luma(cover(src)) - 0.55) / 0.3, 0, 1)
    tube = cv2.GaussianBlur(tube, (0, 0), 3)[..., None]
    off = on * (1 - tube) * 0.22
    return on, off


FLICK = [0, 1, 0, 0, 1, 1, 0, 1]   # first frames of the shot: 1 = light on


def b_breathe(tl, i):
    on, off = gym_layers()
    k = int(round(tl * FPS))
    lit = FLICK[k] if k < len(FLICK) else 1
    f = on * flicker(i, 0.04) if lit else off
    if lit:
        f = bloom(f, thr=0.45, sigma=60, amt=1.4)
    f = push(f, 1.0 + 0.05 * tl / 1.28, W * 0.45, H * 0.5)
    if k % 9 == 4:
        f = glitch(f, i, n=4, amp=30)
    f = finish(f, i)
    f[:302] = (0.12, 0.11, 0.12); f[1615:] = (0.12, 0.11, 0.12)
    put_text(f, "breathe.", size_for_width("breathe.", 750), RED, cy=H * 0.47)
    return f


# ---------- beat 3: back photo, light snaps on, body goes black ----------
@functools.lru_cache(maxsize=1)
def back_layers():
    import mediapipe as mp
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    src = still(C07); h0, w0 = src.shape[:2]
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
        output_confidence_masks=True))
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB))))
    m = ((1 - r.confidence_masks[0].numpy_view()) > 0.5).astype(np.float32)
    cv2.rectangle(m, (262, 455), (450, 760), 0, -1)          # the phone
    cv2.ellipse(m, (322, 760), (92, 46), -8, 0, 360, 1, -1)   # a fist in its place
    for y in range(1450, h0):
        xs = np.flatnonzero(m[y] > 0.5)
        if xs.size: m[y, xs[0]:xs[-1] + 1] = 1
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    S = 1180 / w0; ph = int(h0 * S)
    img = cv2.resize(src, (1180, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    al = cv2.resize(cv2.GaussianBlur(m, (0, 0), 2.0), (1180, ph))
    IMG = np.zeros((H, W, 3), np.float32); AL = np.zeros((H, W), np.float32)
    IMG[H - ph:] = img[:, 50:50 + W]; AL[H - ph:] = al[:, 50:50 + W]
    fade = np.clip((np.arange(H) - (H - ph)) / 260.0, 0, 1)[:, None, None]
    norm = grade(IMG, gain=(0.80, 0.85, 0.92), gamma=1.25) * 0.85 * fade
    cx, cy = 600, 1010
    d = np.hypot(XX - cx, (YY - cy) / 1.25)
    core = np.exp(-(d / 520) ** 2)
    ang = np.arctan2(YY - cy, XX - cx)
    rays = (0.5 + 0.5 * np.cos(ang * 23 + 1.3)) * (0.5 + 0.5 * np.cos(ang * 9 - 0.4))
    rays = cv2.GaussianBlur(rays.astype(np.float32), (0, 0), 6) * np.clip(d / 900, 0, 1) * 0.35
    lum = np.clip(0.18 + 0.95 * core + rays * (0.3 + core), 0, 1.4)
    light = lum[..., None] * (np.float32([1.0, 0.95, 0.93]) * (1 - core[..., None]) + np.float32([0.97, 0.99, 1.0]) * core[..., None])
    edge = np.clip(cv2.GaussianBlur(AL, (0, 0), 7) - AL, 0, 1)[..., None]
    inner = np.clip(AL - cv2.erode(AL, np.ones((9, 9), np.uint8)), 0, 1)[..., None]
    return norm, light, AL[..., None], edge, inner


SNAP = 0.16          # local time the light switches on
LIGHT_SEQ = [1, 1, 1, 0.25, 1, 1, 1, 1, 0.5, 1, 1, 1, 1, 1, 0.3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def sil_frame(tl, i, cool=0.0, white=False):
    norm, light, A, edge, inner = back_layers()
    u = tl - SNAP
    k = int(round(u * FPS))
    flash = 1 + 1.4 * np.exp(-max(u, 0) / 0.06)
    L = light * flash * (LIGHT_SEQ[k] if 0 <= k < len(LIGHT_SEQ) else 1) * flicker(i, 0.04)
    if cool > 0:
        L = L * (1 - cool) + L * np.float32([1.15, 0.85, 0.55]) * cool
    bg = bloom(L, thr=0.6, sigma=40, amt=0.4)
    body = (np.float32([1.0, 0.98, 0.95]) * 1.3 if white else 0.015 + inner * 0.10 * L)
    f = bg * (1 - A) + body * A + edge * 0.6 * L
    if white:
        f = bloom(f, thr=0.8, sigma=50, amt=0.8)
    return f


def b_snap(tl, i):
    norm = back_layers()[0]
    if tl < SNAP:
        f = norm.copy()
    else:
        f = sil_frame(tl, i, cool=ease((tl - 0.85) / 0.2))
        if tl - SNAP < 1 / FPS:
            f = 0.5 * f + 0.5 * np.clip(norm * 3, 0, 1)
    f = push(f, 1 + 0.035 * tl / 1.08, W / 2, H * 0.55)
    f = finish(f, i)
    if tl < 0.40:                                    # "breathe." carries over, breaking into teal
        m = text_mask("breathe.", size_for_width("breathe.", 750), cy=H * 0.47)[..., None]
        rng = np.random.default_rng(i)
        band = np.zeros((H, 1, 1), np.float32)
        for _ in range(3):
            y = int(rng.integers(780, 1020)); band[y:y + int(rng.integers(20, 90))] = 1
        side = (XX > rng.integers(200, 900))[..., None].astype(np.float32) * (tl > 0.08)
        col = np.float32(RED) * (1 - side) + np.float32(TEAL) * side
        col = col * (1 - band) + np.float32(TEAL if rng.random() < 0.5 else RED) * band
        f = f * (1 - m) + col * m
    return f


# ---------- beat 9: the flurry, cut to the reference's frames ----------
def fl_light(tl, i):      # 11.00-11.16 a hot round light
    on, _ = gym_layers()
    f = cover((np.clip(on, 0, 1) * 255).astype(np.uint8), zoom=3.2, cx=0.13, cy=0.31)
    f = grade(f, gain=(0.55, 0.85, 1.25), gamma=1.1) * 1.4
    return bloom(f, thr=0.35, sigma=80, amt=2.2)


def fl_face(tl, i):       # 11.16-11.24 strained face, warm
    fr = frame_at(C10, 0.05, 0.1, tl)
    f = cover(fr, zoom=2.4, cx=0.42, cy=0.34)
    return grade(f, gain=(0.35, 0.6, 1.05), gamma=1.45, contrast=1.2)


def fl_squeeze(tl, i):    # 11.24-11.28 back squeeze, green
    f = cover(frame_at(C08, 1.3, 0.1, tl), zoom=1.4, cx=0.5, cy=0.35)
    return tint_bw(f, (0.02, 0.05, 0.0), (0.45, 1.0, 0.35), 1.4)


def fl_white(tl, i):      # 11.28-11.36 white flash
    f = np.full((H, W, 3), 0.97, np.float32)
    return f - (np.random.default_rng(i).random((H, W, 1)) < 0.002) * 0.3


def fl_reach_green(tl, i):  # 11.36-11.44
    f = cover(frame_at(C08, 0.0, 0.1, tl), zoom=1.5, cx=0.5, cy=0.22)
    f = grade(f, gain=(0.3, 1.0, 0.25), gamma=1.5)
    return bloom(f, thr=0.5, sigma=50, amt=1.2)


@functools.lru_cache(maxsize=8)
def bolt(k):
    fr = clip(C03, 2.4, 0.2)[k]
    g = cv2.cvtColor(cv2.resize(fr, (W, H)), cv2.COLOR_BGR2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 1.5), 40, 110).astype(np.float32) / 255
    e = cv2.dilate(e, np.ones((2, 2), np.uint8))
    glow = cv2.GaussianBlur(e, (0, 0), 6) * 1.6 + e
    return np.clip(glow, 0, 1.5)[..., None] * np.float32([1.0, 0.85, 0.9])


def fl_bolt(tl, i):       # 11.44-11.60 the lockout as white electric lines
    return bolt(min(int(tl * FPS), 3)) + np.float32([0.03, 0.01, 0.02])


def fl_reach_blue(tl, i):  # 11.60-11.72
    f = cover(frame_at(C08, 0.1, 0.15, tl), zoom=1.3, cx=0.5, cy=0.25)
    f = grade(f, gain=(1.25, 0.45, 0.25), gamma=1.4)
    return bloom(f, thr=0.5, sigma=60, amt=1.5)


def fl_flex(tl, i):       # 11.72-11.84 the flex, dark green
    f = cover(frame_at(C09, 0.35, 0.15, tl), zoom=1.15, cx=0.45, cy=0.4)
    return tint_bw(f, (0.0, 0.02, 0.0), (0.5, 0.95, 0.3), 1.6)


FLURRY = [(11.00, 11.16, fl_light), (11.16, 11.24, fl_face), (11.24, 11.28, fl_squeeze), (11.28, 11.36, fl_white),
          (11.36, 11.44, fl_reach_green), (11.44, 11.60, fl_bolt), (11.60, 11.72, fl_reach_blue), (11.72, 11.84, fl_flex)]


def b_flurry(tl, i):
    t = 11.0 + tl
    for a, b, fn in FLURRY:
        if a <= t < b + 1e-6:
            f = fn(t - a, i)
            break
    f = glitch(f, i, n=3, amp=25) if i % 3 == 0 else f
    return finish(f, i, g=0.05, ca=6)


# ---------- beat 13: your face, pixelated resolving to clear ----------
def b_pixel(tl, i):
    fr = frame_at(C04, 0.55, 0.52, tl, speed=2.0)
    f = cover(fr, zoom=1.75, cx=0.47, cy=0.2)
    f = grade(f, sat=0.0, gamma=1.25, contrast=1.15) * 0.9
    k = ease(tl / 0.44)
    rng = np.random.default_rng(7)
    out = f.copy()
    if k < 1:
        bs = int(10 + 70 * (1 - k))                                   # blocks shrink as it resolves
        small = cv2.resize(f, (W // bs, H // bs), interpolation=cv2.INTER_AREA)
        pix = cv2.resize(small, (W, H), interpolation=cv2.INTER_NEAREST)
        cell = 90
        thr = rng.random((H // cell + 1, W // cell + 1)).astype(np.float32)
        thr = cv2.resize(thr, (W, H), interpolation=cv2.INTER_NEAREST)
        keep = (thr > k * 1.15 - 0.05).astype(np.float32)[..., None]   # cells pop to clear one by one
        out = pix * keep + f * (1 - keep)
    return finish(out, i, g=0.06, vig=0.6)


# ---------- beat 17: "okay?" on warm burnt film ----------
def b_okay(tl, i):
    fr = frame_at(C04, 2.3, 1.66, tl)
    f = cover(fr, zoom=1.4, cx=0.46, cy=0.43)
    f = grade(f, gain=(0.25, 0.55, 1.0), gamma=1.25, contrast=1.1, sat=0.6)
    f = f * flicker(i, 0.06, seed=9)
    f = soft_frame(f, scale=0.86, feather=110, bg=(0.012, 0.015, 0.03), y_off=-20)
    f = film_dirt(f, i)
    burn = ease((tl - 1.22) / 0.44)                                    # 17.56: burns out to warm, then black
    if burn > 0:
        hot = np.float32([0.12, 0.35, 0.95])
        f = f * (1 - burn) + soft_frame(np.full_like(f, 1) * hot * (1 - burn * 0.6), scale=0.86, feather=110,
                                        bg=(0.012, 0.015, 0.03)) * burn
    f = finish(f, i, g=0.05, vig=0.5)
    t = 16.34 + tl
    big = size_for_width("okay?", 305)
    if 16.72 <= t < 16.80:
        put_text(f, "o", big, O_TEAL)
    elif 16.80 <= t < 17.60:
        put_text(f, "okay?", big, MINT, glow=0.8)
        if 17.28 <= t < 17.44:
            put_text(f, "okay?", big, MINT, cy=H * 0.494 + big * 0.75)
    return f


# ---------- the other beats ----------
def src(path, t0, tl, dur=4.0, speed=1.0):
    return still(path) if path.endswith(".jpg") else frame_at(path, t0, dur, tl, speed)


@functools.lru_cache(maxsize=1)
def side_mask():
    m = np.ones((H, W), np.float32)
    m[:, :int(W * 0.10)] = 0.15; m[:, int(W * 0.90):] = 0.15
    return cv2.GaussianBlur(m, (0, 0), 45)[..., None]


def b_want(tl, i):        # 5.00-8.88: slow, purple-blue night, dark soft sides
    f = cover(src(C02, 0.0, tl), zoom=1.18 + 0.06 * tl / 3.88, cx=0.48, cy=0.42)
    f = grade(f, sat=0.55, gain=(1.08, 0.78, 0.92), lift=(0.05, 0.025, 0.04), gamma=1.35, contrast=1.05)
    f = bloom(f, thr=0.55, sigma=40, amt=0.7) * side_mask()
    if i % 23 == 5:
        f = glitch(f, i, n=3, amp=20)
    return finish(f, i, ca=7, vig=0.5)


def b_grip(tl, i):        # 8.88-9.24 "you get": hands gripping, hot orange-red
    f = cover(src(C10, 0.0, tl), zoom=3.0, cx=0.16, cy=0.4)
    f = tint_bw(f, (0.02, 0.02, 0.10), (0.30, 0.55, 1.0), 1.3)
    f = bloom(f, thr=0.5, sigma=50, amt=1.2)
    f = glitch(f, i, n=5, amp=35) if i % 2 == 0 else f
    return finish(f, i, ca=6)


GHOST_T0 = 1.9


@functools.lru_cache(maxsize=1)
def lifter_mattes():
    """rembg person matte of the deadlift pull, only the lifter (people behind on the left are cut off)."""
    from rembg import remove, new_session
    ses = new_session("u2net_human_seg")
    out = []
    for fr in clip(C03, GHOST_T0, 0.68):
        m = np.asarray(remove(np.ascontiguousarray(fr[..., ::-1]), session=ses, only_mask=True)).astype(np.float32) / 255
        m[:, :int(fr.shape[1] * 0.19)] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
        if n > 1:
            best = 1 + int(np.argmax(st[1:, 4]))
            m = m * cv2.dilate((lab == best).astype(np.uint8), np.ones((15, 15), np.uint8))
        out.append(m)
    return out


def b_ghost(tl, i):       # 9.24-9.92 "a big": the lifter as a glowing blue outline
    k = min(int(round(tl * FPS)), len(lifter_mattes()) - 1)
    Z = dict(zoom=1.15, cx=0.4, cy=0.5)
    bg = cover(src(C03, GHOST_T0, tl, 0.68), **Z)
    bg = tint_bw(bg, (0.08, 0.03, 0.01), (0.85, 0.45, 0.15), 1.5) * 0.75
    m = cover((lifter_mattes()[k] * 255).astype(np.uint8)[..., None].repeat(3, 2), **Z)[..., 0]
    m = cv2.GaussianBlur(m, (0, 0), 2)
    edge = np.clip(cv2.dilate(m, np.ones((9, 9), np.uint8)) - cv2.erode(m, np.ones((5, 5), np.uint8)), 0, 1)
    glow = cv2.GaussianBlur(edge, (0, 0), 10) * 1.5 + edge
    f = bg * (1 - 0.7 * m[..., None]) + glow[..., None] * np.float32([1.0, 0.85, 0.55])
    return finish(bloom(f, thr=0.6, sigma=40, amt=0.6), i, ca=5)


def b_plates(tl, i):      # 9.92-10.28 "piece of": plates close, green
    f = cover(src(C03, 3.0, tl, 0.4), zoom=3.2, cx=0.665, cy=0.37)
    f = tint_bw(f, (0.01, 0.03, 0.0), (0.35, 1.0, 0.45), 1.35)
    f = bloom(f, thr=0.5, sigma=50, amt=1.0)
    return finish(f, i, g=0.05, ca=6)


def b_reach(tl, i):       # 10.28-11.00 "what you want.": arms up, the window blown into light
    f = cover(src(C08, 0.0, tl, 0.8), zoom=1.45, cx=0.45, cy=0.22)
    f = grade(f, sat=0.3, gamma=1.5)
    f = tint_bw(f, (0.12, 0.01, 0.04), (1.0, 0.62, 0.55), 1.2) * 1.15
    f = bloom(f, thr=0.45, sigma=70, amt=1.8)
    return finish(f, i, ca=6)


def b_mirror(tl, i):      # 11.84-12.40 "can happen and": mirror pose, teal
    f = cover(src(C09, 0.0, tl, 0.6), zoom=1.5, cx=0.35, cy=0.42)
    f = tint_bw(f, (0.03, 0.025, 0.0), (0.95, 0.85, 0.35), 1.3)
    f = bloom(f, thr=0.6, sigma=40, amt=0.6)
    return finish(f, i, ca=5)


@functools.lru_cache(maxsize=1)
def glow_fig():
    f = cover(still(C05))
    hot = np.clip((luma(f) - 0.55) / 0.35, 0, 1)
    return f, cv2.GaussianBlur(hot, (0, 0), 4)[..., None]


def b_reality(tl, i):     # 12.40-13.78 "become a reality.": the glowing figure, breathing light, push in
    f, hot = glow_fig()
    f = cover((np.clip(f, 0, 1) * 255).astype(np.uint8), zoom=1.15, cx=0.5, cy=0.28)
    hot = cover((np.clip(hot, 0, 1) * 255).astype(np.uint8).repeat(3, 2), zoom=1.15, cx=0.5, cy=0.28)[..., :1]
    breathe = 1 + 0.18 * np.sin(tl * 2 * np.pi / 1.1) + 0.04 * np.random.default_rng(i).normal()
    f = f * (1 + hot * (breathe - 1) * 1.5)
    f = grade(f, gain=(1.05, 0.98, 0.9), gamma=1.1)
    f = bloom(f, thr=0.55, sigma=60, amt=0.9 * breathe)
    f = push(f, 1 + 0.07 * tl / 1.38, W * 0.48, H * 0.68)
    return finish(f, i, ca=4)


def warm_look(f, hot=False):
    f = grade(f, sat=0.5, gain=(0.30, 0.58, 1.05), gamma=1.5 if not hot else 1.2, contrast=1.1)
    return bloom(f, thr=0.5, sigma=50, amt=1.2 if hot else 0.6)


def cold_look(f):
    return grade(f, sat=0.4, gain=(1.05, 0.88, 0.78), gamma=1.45, lift=(0.02, 0.01, 0.0))


def leak(f, tl, side=1.0):
    """Orange light leak drifting in from one side."""
    x = W * (0.5 + 0.55 * side) + 120 * np.sin(tl * 3)
    d = np.hypot((XX - x) / 500, (YY - H * 0.4) / 900)
    return f + np.exp(-d ** 2)[..., None] * np.float32([0.05, 0.25, 0.7]) * 0.8


def b_quiet(tl, i):       # 14.46-15.30 "sincerely and": walking away, four warm/dark cuts like the reference
    t = 14.46 + tl
    fr = src(C01, 0.5, tl, 0.9)
    if t < 14.74:
        f = soft_frame(leak(warm_look(cover(fr, 1.2, 0.48, 0.45)), tl), scale=0.9, feather=120)
    elif t < 14.90:
        f = soft_frame(warm_look(cover(fr, 1.3, 0.5, 0.4)) * 0.25, scale=0.9, feather=120)
    elif t < 15.14:
        f = soft_frame(leak(warm_look(cover(fr, 1.7, 0.5, 0.35), hot=True), tl, -1), scale=0.88, feather=120)
    else:
        f = soft_frame(warm_look(cover(fr, 1.2, 0.5, 0.5)) * 0.5, scale=0.9, feather=120)
    return finish(film_dirt(f, i, 0.6), i, g=0.05)


def b_die(tl, i):         # 15.30-16.02 "i'll die on that": alone, cold, then a warm flash
    t = 15.30 + tl
    if t < 15.62:
        f = soft_frame(cold_look(cover(src(C02, 2.8, tl, 0.8), 1.25, 0.48, 0.42)), scale=0.84, feather=120)
        if 15.38 <= t < 15.46:
            f = bloom(f * 1.6, thr=0.4, sigma=60, amt=1.5)
    elif t < 15.78:
        f = soft_frame(warm_look(cover((np.clip(gym_layers()[0], 0, 1) * 255).astype(np.uint8), 1.8, 0.2, 0.33), hot=True),
                       scale=0.88, feather=120)
    else:
        f = soft_frame(leak(warm_look(cover(src(C02, 3.2, tl, 0.8), 1.6, 0.5, 0.3)), tl), scale=0.88, feather=120)
    return finish(film_dirt(f, i, 0.6), i, g=0.05)


def b_thought(tl, i):     # 16.02-16.34 "thought.": the empty gym, then you small in the frame
    t = 16.02 + tl
    if t < 16.18:
        f = soft_frame(warm_look(cover((np.clip(gym_layers()[0] * 2.2, 0, 1) * 255).astype(np.uint8), 1.1, 0.5, 0.55), hot=True),
                       scale=0.86, feather=120)
    else:
        f = soft_frame(cold_look(cover(src(C01, 3.6, tl, 0.4), 1.15, 0.5, 0.45)) * 1.2, scale=0.7, feather=90)
    return finish(film_dirt(f, i, 0.6), i, g=0.05)


# ---------- timeline (edit time = reference time) ----------
TIMELINE = [
    (0.00, 2.64, b_black_open),
    (2.64, 3.92, b_breathe),
    (3.92, 5.00, b_snap),
    (5.00, 8.88, b_want),
    (8.88, 9.24, b_grip),
    (9.24, 9.92, b_ghost),
    (9.92, 10.28, b_plates),
    (10.28, 11.00, b_reach),
    (11.00, 11.84, b_flurry),
    (11.84, 12.40, b_mirror),
    (12.40, 13.78, b_reality),
    (13.78, 13.94, lambda tl, i: finish(sil_frame(1.0, i, white=True), i)),
    (13.94, 14.46, b_pixel),
    (14.46, 15.30, b_quiet),
    (15.30, 16.02, b_die),
    (16.02, 16.34, b_thought),
    (16.34, 18.00, b_okay),
    (18.00, END, b_black),
]

def render_frame(n):
    t = n / FPS
    for a, b, fn in TIMELINE:
        if a - 1e-6 <= t < b - 1e-6:
            f = fn(t - a, n)
            break
    else:
        f = np.zeros((H, W, 3), np.float32)
    f = captions(f, t)
    return (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)


def ref_wav():
    p = "work/audio/reference.wav"
    if not os.path.exists(p):
        os.makedirs("work/audio", exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw/reference.mp4", "-vn", "-c:a", "pcm_s16le", p], check=True)
    return p


def encode(a, b, out, scale=1.0, crf=14):
    n0, n1 = int(round(a * FPS)), int(round(b * FPS))
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                          "-r", str(FPS), "-i", "-", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", ref_wav(),
                          "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", out], stdin=subprocess.PIPE)
    for n in range(n0, n1):
        fr = render_frame(n)
        if scale != 1.0:
            fr = cv2.resize(fr, (w, h), interpolation=cv2.INTER_AREA)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    os.makedirs("out/stills", exist_ok=True)
    if cmd == "stills":
        for s in sys.argv[2:]:
            cv2.imwrite(f"out/stills/s_{float(s):05.2f}.png", render_frame(int(round(float(s) * FPS))))
    elif cmd == "draft":
        a, b = float(sys.argv[2]), float(sys.argv[3])
        encode(a, b, f"out/draft_{a:g}-{b:g}.mp4", scale=0.5 if "--half" in sys.argv else 1.0, crf=20)
    elif cmd == "render":
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        encode(a, b, "out/master.mp4" if (a, b) == (0, END) else f"out/master_{a:g}-{b:g}.mp4")
