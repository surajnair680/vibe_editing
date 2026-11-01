"""reel-04 overlays (mini vlog pack style, kept small and sparse). apply(frame_bgr, t) -> frame.

Four moments only:
  0.00-3.87   V4 camcorder corners (WORKING, REC with red dot; centre icons/GRINDING, 25FPS and Q3 masked out)
              + "the quiet hours" flickering in low in the frame
  10.37-11.67 "locked in." flickers in on the drop
  18.40-20.70 "the world goes quiet" types on during the breath
  28.57-31.97 V12 REC iris over the empty chair, closing to black like the recording stopping,
              + "same time tomorrow." inside the iris
Deterministic (seeded flicker) so re-renders match.
"""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlog_overlays import screen, keyed, read_all

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
if not os.path.exists(FONT):
    FONT = os.path.join(HERE, "fonts", "InterTight-400.ttf")

_cache = {}
def _ov(n):
    if n not in _cache:
        _cache[n] = read_all(os.path.join(HERE, "assets", "overlays", f"video-overlay-{n}.mp4"))[0]
    return _cache[n]

def _ovf(n, t):
    fr = _ov(n); return fr[min(len(fr) - 1, max(0, int(t * 30)))]

_V4MASK = None
def v4_corners(t):
    global _V4MASK
    if _V4MASK is None:   # keep WORKING (top left) and REC (bottom right) only
        m = np.zeros((H, W), np.float32)
        m[220:320, 40:300] = 1; m[1270:1390, 840:1040] = 1
        _V4MASK = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    return (_ovf(4, t).astype(np.float32) * _V4MASK).astype(np.uint8)

_txt = {}
def text_layer(s, size, y, x=None, tracking=0):
    """White text with a faint soft shadow, as (rgb, alpha) full frames. x=None centres it."""
    key = (s, size, y, x, tracking)
    if key not in _txt:
        f = ImageFont.truetype(FONT, size)
        widths = [f.getlength(c) for c in s]; tw = sum(widths) + tracking * (len(s) - 1)
        x0 = (W - tw) / 2 if x is None else x
        a = Image.new("L", (W, H), 0); d = ImageDraw.Draw(a); cx = x0; boxes = []
        for c, w in zip(s, widths):
            d.text((cx, y), c, font=f, fill=255); boxes.append(cx); cx += w + tracking
        al = np.asarray(a, np.float32) / 255
        sh = cv2.GaussianBlur(np.roll(al, (3, 2), (0, 1)), (0, 0), 6) * 0.55
        _txt[key] = (al, sh, boxes, size)
    return _txt[key]

def put_text(img, s, size, y, alpha=1.0, x=None, chars=None, tracking=0):
    al, sh, boxes, sz = text_layer(s, size, y, x, tracking)
    if chars is not None and chars < len(s):            # type-on: only the first n letters
        cut = int(boxes[chars]) if chars > 0 else 0
        al = al.copy(); sh = sh.copy(); al[:, cut:] = 0; sh[:, cut:] = 0
    out = img.astype(np.float32)
    out *= 1 - (sh * alpha)[..., None]
    out = out * (1 - (al * alpha)[..., None]) + 245 * (al * alpha)[..., None]
    return out.astype(np.uint8)

def flicker(t, dur=0.35, seed=0):
    """0 before, 1 after; random 1-frame drops while it flickers in."""
    if t < 0: return 0.0
    if t >= dur: return 1.0
    rng = np.random.default_rng(seed + int(t * 30)); return float(rng.random() < 0.55) * (0.5 + 0.5 * t / dur)

def fade(t, start, end, fin=0.0, fout=0.3):
    if t < start or t > end: return 0.0
    a = 1.0
    if fin: a = min(a, (t - start) / fin)
    if fout: a = min(a, (end - t) / fout)
    return max(0.0, min(1.0, a))

_IRIS = {}
def iris_k(t):
    return 1.0 if t < 30.0 else max(0.0, 1 - ((t - 30.0) / 1.6) ** 1.6)

def iris_mask(t):
    """Oval mask (from V12's lavender area, eroded so no blue fringe) and its REC layer, scaled by the close."""
    if not _IRIS:
        fr = _ov(12)[0].astype(np.float32)
        d = np.linalg.norm(fr - np.array([165, 107, 91], np.float32), axis=2)
        m = (d < 90).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))   # fill the REC hole
        m = cv2.erode(m, np.ones((9, 9), np.uint8))
        _IRIS["m"] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 5)
        rec = ((fr.min(2) > 170) | ((fr[..., 2] > 170) & (fr[..., 1] < 80))).astype(np.float32)
        rec = cv2.GaussianBlur(rec, (0, 0), 0.8)
        _IRIS["rec"] = rec; _IRIS["rec_rgb"] = _ov(12)[0]
    k = iris_k(t); m, rec, rgb = _IRIS["m"], _IRIS["rec"], _IRIS["rec_rgb"]
    if k < 1:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, max(k, 1e-3))
        m = cv2.warpAffine(m, M, (W, H)); rec = cv2.warpAffine(rec, M, (W, H))
        rgb = cv2.warpAffine(rgb, M, (W, H))
    return m, rec, rgb

def iris(img, t):
    """V12 REC iris on the ending: open oval, then it closes to black from 30.0 s."""
    m, rec, rgb = iris_mask(t)
    out = img.astype(np.float32) * m[..., None]
    out = out * (1 - rec[..., None]) + rgb.astype(np.float32) * rec[..., None]
    return out.astype(np.uint8), m

def apply(img, t):
    if 0.0 <= t < 3.87:
        a = fade(t, 0.0, 3.87, 0.0, 0.35)
        img = screen(img, v4_corners(t), opacity=a)
        img = put_text(img, "the quiet hours", 46, 1440, flicker(t - 0.9, seed=1) * fade(t, 0.9, 3.75, 0, 0.4),
                       tracking=3)
    if 10.37 <= t < 11.67:
        img = put_text(img, "locked in.", 54, 1440, flicker(t - 10.40, 0.3, seed=2) * fade(t, 10.37, 11.62, 0, 0.12))
    if 18.40 <= t < 20.70:
        s = "the world goes quiet"
        n = int((t - 18.40) * 30 / 2) + 1                   # a letter every 2 frames
        img = put_text(img, s, 44, 1440, fade(t, 18.40, 20.70, 0, 0.4), chars=min(n, len(s)), tracking=2)
    if 28.57 <= t:
        txt = put_text(img, "same time tomorrow.", 42, 1180, flicker(t - 29.0, seed=3), tracking=2)
        img, m = iris(txt, t)        # the line sits inside the iris and closes with it
    return img
