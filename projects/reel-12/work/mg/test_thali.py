"""still: 'zero flaws' beat (~33.9 s) with the colour Codex thali in a manga panel + three stamps"""
import sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, "work/mg")
from manga import *  # noqa
t = 33.9
n = round(t * 30)
img = paper(31)
P = [(40, 130), (1040, 130), (1040, 760), (40, 820)]
pm = poly_mask(P)
th = cv2.cvtColor(cv2.imread("assets/codex/thali.png"), cv2.COLOR_BGR2RGB)
full = np.zeros((H, W, 3), np.float32)
full[130:820, 40:1040] = cover(th, 1000, 690, fx=0.5, fy=0.5, zoom=1.05)
img[pm] = full[pm]
# manga sparkles (white four-point stars with an ink edge) around the thali
def star(img, cx, cy, s):
    pts = [(cx, cy - s), (cx + s * 0.22, cy - s * 0.22), (cx + s, cy), (cx + s * 0.22, cy + s * 0.22), (cx, cy + s),
           (cx - s * 0.22, cy + s * 0.22), (cx - s, cy), (cx - s * 0.22, cy - s * 0.22)]
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    m = np.array(m) > 0
    e = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    img[e] = INK; img[m] = PAPER
for (x, y, s) in [(150, 220, 46), (930, 250, 38), (880, 690, 52), (210, 690, 30)]:
    star(img, x, y, s)
stroke_poly(img, P, 8)
for txt, x, y, r in [("PERFECT", 300, 300, -10), ("FLAWLESS", 780, 420, 8)]:
    paste(img, sfx(txt, font("dela", 74), rot=r, fill=RED), x, y)
paste(img, sfx("ZERO FLAWS", font("dela", 96), rot=-5, fill=RED), 540, 640)
# caption
from sample import draw_caption
draw_caption(img, ["it's", "flawless,", "zero", "flaws."], 3, 870)
me = cv2.cvtColor(cv2.imread("out/stills/_tmp.png") if False else cv2.imread("work/mg/src_41.3.png"), cv2.COLOR_BGR2RGB)
cap = cv2.VideoCapture("out/reel-12-rough-v3.mp4"); cap.set(cv2.CAP_PROP_POS_FRAMES, n); ok, f = cap.read()
me = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
al = cv2.imread(f"work/matte_v3/{n:05d}.png", 0)
face_circle(img, me, al, 540, 1480, 300, 0.66, 1010, seed=4)
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGB").save("out/stills/mg_test/D_33.9.jpg", quality=92)
