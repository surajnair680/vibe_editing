"""His head breaking out of a torn paper circle (Vox version of reel-12's manga face_circle, copied and adapted from
projects/reel-12/work/mg/manga.py). Inside: cream paper with halftone (deep red in the cream section). Ring: title red
with a white fibre edge and a soft shadow. Where his head leaves the circle: a 12 px white paper rim and a shadow."""
import functools
import numpy as np, cv2

W, H = 1080, 1920
RED = (158, 26, 43)
PAPER = (250, 247, 240)

# states: centre, radius, scale of his take, where his hair top lands
BIG = dict(cx=540, cy=1450, r=320, scale=0.72, head_top=880)
SR = dict(cx=830, cy=1500, r=195, scale=0.45, head_top=1215)
SL = dict(cx=250, cy=1500, r=195, scale=0.45, head_top=1215)


@functools.lru_cache(maxsize=4)
def _dots(cell=12):
    yy, xx = np.mgrid[0:H, 0:W]
    gx = (xx % cell) - cell / 2
    gy = ((yy + (xx // cell % 2) * cell // 2) % cell) - cell / 2
    return np.hypot(gx, gy).astype(np.float32)


@functools.lru_cache(maxsize=2)
def _grid():
    yy, xx = np.mgrid[0:H, 0:W]
    return yy.astype(np.float32), xx.astype(np.float32)


def draw(img, me_rgb, alpha, st, inside=(226, 216, 196), ring=RED, seed=7):
    cx, cy, r, scale, head_top = st["cx"], st["cy"], st["r"], st["scale"], st["head_top"]
    yy, xx = _grid()
    dd = np.hypot(xx - cx, yy - cy)
    out = img.astype(np.float32)
    # shadow of the disc
    disc = (dd <= r + 18).astype(np.float32)
    sh = cv2.GaussianBlur(disc, (0, 0), 16)
    sh = cv2.warpAffine(sh, np.float32([[1, 0, 10], [0, 1, 16]]), (W, H))
    out *= 1 - sh[..., None] * 0.5
    # torn white fibre edge, then the red ring, then the paper inside
    ang = np.arctan2(yy - cy, xx - cx)
    jit = 4 * np.sin(ang * 23 + seed) + 3 * np.sin(ang * 57 + 2 * seed) + 2 * np.sin(ang * 131)
    out[dd <= r + 16 + jit] = PAPER
    out[dd <= r + 8] = ring
    ins = dd <= r
    lin = np.clip((yy - (cy - r)) / (2 * r), 0, 1)
    col = np.array(inside, np.float32)[None, None] * (1.04 - 0.16 * lin[..., None])
    dots = _dots()
    rad = 1.2 + 3.2 * lin
    dmask = (dots < rad).astype(np.float32)[..., None] * 0.22
    col = col * (1 - dmask)
    out[ins] = col[ins]
    # him, scaled, hair top at head_top
    al = alpha.astype(np.float32) / 255
    me = cv2.resize(me_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA).astype(np.float32)
    al = cv2.resize(al, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    rows = np.where(al.max(1) > 0.5)[0]
    if len(rows) == 0:
        return np.clip(out, 0, 255).astype(np.uint8)
    oy, ox = int(head_top - rows[0]), int(cx - me.shape[1] / 2)
    cm = np.zeros((H, W, 3), np.float32); ca = np.zeros((H, W), np.float32)
    h, w = me.shape[:2]
    ya, xa, yb, xb = max(0, oy), max(0, ox), min(H, oy + h), min(W, ox + w)
    if yb > ya and xb > xa:
        cm[ya:yb, xa:xb] = me[ya - oy:yb - oy, xa - ox:xb - ox]
        ca[ya:yb, xa:xb] = al[ya - oy:yb - oy, xa - ox:xb - ox]
    allowed = (ins | (yy < cy)).astype(np.float32)
    allowed = cv2.GaussianBlur(allowed, (3, 3), 0)
    a = ca * allowed
    # paper rim + shadow where his head leaves the circle
    outp = ((a > 0.5) & ~ins).astype(np.uint8)
    rim = cv2.dilate(outp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))).astype(bool) & ~ins
    rsh = cv2.GaussianBlur(rim.astype(np.float32), (0, 0), 10)
    rsh = cv2.warpAffine(rsh, np.float32([[1, 0, 8], [0, 1, 12]]), (W, H))
    out *= 1 - (rsh * (~ins))[..., None] * 0.45
    out[rim] = PAPER
    out = out * (1 - a[..., None]) + cm * a[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)
