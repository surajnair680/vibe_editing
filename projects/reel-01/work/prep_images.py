"""Turn the supplied images into "printed on the poster" pieces (RGBA PNGs in assets/print/).

    python3 work/prep_images.py

ink():      white paper becomes transparent, the lines stay as black ink (multiply-like), so the cream paper shows.
halftone(): photo -> black ink dot screen, like a newspaper print.
Red accents: the ship's yellow sun becomes the poster red; the dice's top pip turns red.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

OUT = Path("assets/print"); OUT.mkdir(parents=True, exist_ok=True)
RED = np.array([211, 55, 43], np.float32)
INK = np.array([20, 19, 18], np.float32)


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32)


def ink(rgb, gamma=1.0, lift=0.0):
    """Darkness becomes ink opacity: white -> transparent, black -> solid ink."""
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32) / 255
    a = np.clip((1 - lum - lift) / (1 - lift), 0, 1) ** gamma
    out = np.zeros(rgb.shape[:2] + (4,), np.float32)
    out[..., :3] = INK; out[..., 3] = a * 255
    return out


def put_colour(out, mask, colour):
    m = mask.astype(np.float32)
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + colour * m[..., None]
    out[..., 3] = np.maximum(out[..., 3], m * 255)
    return out


def halftone(rgb, cell=9, angle=45, gamma=1.1):
    """Black ink dot screen. Dot area follows darkness."""
    h, w = rgb.shape[:2]
    lum = cv2.GaussianBlur(rgb @ np.array([0.299, 0.587, 0.114], np.float32) / 255, (0, 0), cell * 0.3)
    dark = np.clip(1 - lum, 0, 1) ** gamma
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.deg2rad(angle)
    u, v = xx * np.cos(a) + yy * np.sin(a), -xx * np.sin(a) + yy * np.cos(a)
    du = (u % cell) / cell - 0.5; dv = (v % cell) / cell - 0.5
    dist = np.sqrt(du ** 2 + dv ** 2)                                   # 0 at cell centre .. ~0.7 at corner
    radius = np.sqrt(dark / np.pi)                                      # dot area = darkness
    alpha = np.clip((radius - dist) * cell * 1.5 + 0.5, 0, 1)            # soft-edged dots
    out = np.zeros((h, w, 4), np.float32); out[..., :3] = INK; out[..., 3] = alpha * 255
    return out


def upscale(rgb, f):
    return cv2.resize(rgb, None, fx=f, fy=f, interpolation=cv2.INTER_LANCZOS4)


def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").save(OUT / name)
    print("  ->", OUT / name)


# ship: ink, yellow sun -> red
ship = upscale(load("assets/ship-engraving.jpg"), 2)
hsv = cv2.cvtColor(ship.astype(np.uint8), cv2.COLOR_RGB2HSV)
sun = (hsv[..., 0] >= 15) & (hsv[..., 0] <= 40) & (hsv[..., 1] > 90)
sun = cv2.GaussianBlur(sun.astype(np.float32), (0, 0), 1.0)
s = ink(ship, gamma=0.9, lift=0.06)
s[..., 3] *= (1 - sun)                                                   # remove the yellow's grey ink
save(put_colour(s, sun, RED), "ship.png")

# dice: ink, the top pip red
dice = upscale(load("assets/dice.jpg"), 2)
d = ink(dice, gamma=0.8, lift=0.04)
h, w = dice.shape[:2]
hsv = cv2.cvtColor(dice.astype(np.uint8), cv2.COLOR_RGB2HSV)
dark = (hsv[..., 2] < 90).astype(np.uint8)
n, lab, st, cen = cv2.connectedComponentsWithStats(dark)
top = [i for i in range(1, n) if 400 < st[i, cv2.CC_STAT_AREA] < 20000 and cen[i][1] < h * 0.33 and abs(cen[i][0] - w / 2) < w * 0.12]
if top:
    pip = (lab == top[0]).astype(np.float32)
    d = put_colour(d, cv2.GaussianBlur(pip, (0, 0), 1.0), RED)
save(d, "dice.png")

# beer: halftone print on a soft-edged, cut-out shape (the white studio background drops out)
beer = upscale(load("assets/beer.jpg"), 2)
beer = beer[: int(beer.shape[0] * 0.86)]                                # drop the table reflection
lum = beer @ np.array([0.299, 0.587, 0.114], np.float32)
obj = (lum < 238).astype(np.uint8)
obj = cv2.morphologyEx(obj, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
blue = np.repeat(beer[..., 2:3], 3, axis=2)                             # golden beer is dark in blue, foam stays white
b = halftone(blue * 0.92, cell=10, gamma=1.25)
edge = ink(beer, gamma=1.6, lift=0.35)                                  # keep the glass edges as fine ink lines
b[..., 3] = np.maximum(b[..., 3], edge[..., 3]) * cv2.GaussianBlur(obj.astype(np.float32), (0, 0), 3)
save(b, "beer.png")

# mirror: keep the woodcut as is (it is already black ink), white -> transparent
m = ink(load("assets/mirror.png"), gamma=1.0, lift=0.0)
save(m, "mirror.png")

# pizza: cut the slice off the plate, halftone it, pepperoni in poster red
pz = load("assets/pizza.jpg")
hsv = cv2.cvtColor(pz.astype(np.uint8), cv2.COLOR_RGB2HSV)
H_, S_, V_ = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
plate = ((V_ > 200) & (S_ < 45)).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(plate)
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
pts = cv2.findNonZero((lab == big).astype(np.uint8))
hull = np.zeros_like(plate); cv2.fillConvexPoly(hull, cv2.convexHull(pts), 1)
slice_ = ((S_ > 70) & (hull == 1)).astype(np.uint8)
slice_ = cv2.morphologyEx(slice_, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
slice_ = cv2.morphologyEx(slice_, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(slice_)
slice_ = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.float32)
soft = cv2.GaussianBlur(slice_, (0, 0), 2)
# two-colour print: red dots where the slice is red (sauce, pepperoni), black dots for shadows on top
pz2 = pz.copy()
redness = np.clip((S_ / 255.0) * (((H_ <= 12) | (H_ >= 168)).astype(np.float32) * 1.0 + ((H_ > 12) & (H_ <= 22)) * 0.45), 0, 1)
redness = cv2.GaussianBlur(redness.astype(np.float32), (0, 0), 1.5)
red_l = halftone(np.repeat((255 * (1 - redness ** 0.8))[..., None], 3, axis=2), cell=7, angle=15, gamma=1.0)
red_l[..., :3] = RED
lum = pz @ np.array([0.299, 0.587, 0.114], np.float32)
shadow = np.clip((lum - 40) / 170, 0, 1)
blk = halftone(np.repeat((255 * shadow ** 0.7)[..., None], 3, axis=2), cell=7, angle=45, gamma=1.6)
p = red_l.copy()
k = blk[..., 3:4] / 255
p[..., :3] = p[..., :3] * (1 - k) + INK * k
p[..., 3] = np.maximum(red_l[..., 3], blk[..., 3])
edge = ink(pz, gamma=1.6, lift=0.3)
p[..., 3] = np.maximum(p[..., 3], edge[..., 3] * 0.5) * soft
ys, xs = np.where(slice_ > 0)
save(p[ys.min() - 10: ys.max() + 10, xs.min() - 10: xs.max() + 10], "pizza.png")

# lighthouse: colour photo -> ink print, the lamp in poster red
lh = load("assets/lighthouse.jpg")
lh2 = upscale(lh, 2)
lum = lh2 @ np.array([0.299, 0.587, 0.114], np.float32)
lum = np.clip((lum / 255 - 0.42) * 1.9 + 0.5, 0, 1) * 255                # strong contrast: white tower vs sky
l = halftone(np.repeat(lum[..., None], 3, axis=2), cell=7, gamma=1.15)
hsv = cv2.cvtColor(lh2.astype(np.uint8), cv2.COLOR_RGB2HSV)
lamp = np.zeros(lum.shape, np.float32)
cv2.circle(lamp, (int(0.502 * lh2.shape[1]), int(0.198 * lh2.shape[0])), int(0.03 * lh2.shape[1]), 1.0, -1)
save(put_colour(l, cv2.GaussianBlur(lamp, (0, 0), 3), RED), "lighthouse.png")

# Seneca bust: cut from its black background, halftone (shadows as ink dots, highlights are paper)
sb = np.clip(upscale(load("assets/seneca-bust-photo.jpg"), 3.2), 0, 255)       # lanczos can overshoot below 0
lum = sb @ np.array([0.299, 0.587, 0.114], np.float32)
obj = (cv2.GaussianBlur(lum, (0, 0), 2) > 28).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(obj)
obj = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
ff = 1 - obj; mask = np.zeros((obj.shape[0] + 2, obj.shape[1] + 2), np.uint8)
cv2.floodFill(ff, mask, (0, 0), 2); obj[ff == 1] = 1                       # fill holes inside the bust
obj = obj[: int(obj.shape[0] * 0.80)]; sb = sb[: obj.shape[0]]; lum = lum[: obj.shape[0]]   # drop the plinth
soft = cv2.GaussianBlur(obj.astype(np.float32), (0, 0), 2.5)
lift = np.clip((np.clip(lum, 0, 255) / 255) ** 0.55 * 1.2, 0, 1) * 255                     # lift midtones so the dark stone doesn't flood
b = halftone(np.repeat(lift[..., None], 3, axis=2), cell=8, angle=45, gamma=1.15)
b[..., 3] *= soft
ys, xs = np.where(obj > 0)
save(b[ys.min(): ys.max(), xs.min(): xs.max()], "seneca.png")
