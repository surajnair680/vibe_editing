"""reel-12 manga style test frames (stills only, nothing animated yet).

A  ~41.3 s  "...10 crore logon ko hai. Standard feature hai."   spec card + stamp, big face circle, caption box
B  ~49.0 s  "Faster muscle growth"   back pic panel (real colour), list item 01, smaller face circle
Run from the project folder: python3 work/mg/test_frames.py
"""
import sys
import numpy as np
import cv2
from PIL import Image
sys.path.insert(0, "work/mg")
from manga import *  # noqa


def load(t):
    me = cv2.cvtColor(cv2.imread(f"work/mg/src_{t}.png"), cv2.COLOR_BGR2RGB)
    al = cv2.imread(f"work/mg/alpha_{t}.png", 0)
    return me, al


def caption(img, words, hot, y, x0=60, x1=1020, size=62):
    """Hinglish caption in a narration box; the spoken word is inverted (paper on ink)"""
    f = inter(size, "ExtraBold")
    pil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(pil)
    sp = d.textlength(" ", font=f)
    ws = [d.textlength(w, font=f) for w in words]
    tw = sum(ws) + sp * (len(words) - 1)
    bx0 = int((W - tw) / 2 - 34); bx1 = int((W + tw) / 2 + 34)
    box(img, bx0, y, bx1, y + size + 50, border=5, shadow=9)
    x = (W - tw) / 2
    for i, (w, wl) in enumerate(zip(words, ws)):
        if i == hot:
            img[y + 14:y + size + 36, int(x - 8):int(x + wl + 8)] = INK
            d.text((x, y + 18), w, font=f, fill=PAPER + (255,))
        else:
            d.text((x, y + 18), w, font=f, fill=INK + (255,))
        x += wl + sp
    paste(img, pil, W / 2, H / 2)


def frame_a():
    img = paper(11)
    # ---- top panel: spec card on a focus-line burst, slanted bottom edge
    P = [(40, 130), (1040, 130), (1040, 610), (40, 670)]
    pm = poly_mask(P)
    cov = np.tile(np.linspace(0.22, 0.0, H)[:, None], (1, W)).astype(np.float32)
    tone = dot_tone(H, W, cov, cell=8)
    fl = focus_lines(H, W, 540, 390, r_clear=330, n=150, seed=5, width=(3, 12), length=(0.0, 0.45))
    img[pm] = PAPER
    img[pm & (tone | fl)] = INK
    # spec card
    card = Image.new("RGBA", (760, 400), (0, 0, 0, 0))
    cimg = np.zeros((400, 760, 3), np.float32)
    cimg[:] = PAPER
    ca = np.asarray(card).copy()
    lay = Image.new("RGBA", (800, 450), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([22, 22, 782, 432], fill=INK + (255,))                     # shadow
    d.rectangle([10, 10, 770, 420], fill=INK + (255,))
    d.rectangle([16, 16, 764, 414], fill=PAPER + (255,))
    d.rectangle([16, 16, 764, 92], fill=INK + (255,))
    d.text((40, 24), "INDIAN GHAR KA KHAANA  /  SPECS", font=font("anton", 46), fill=PAPER + (255,))
    rows = ["ROTI", "SABZI", "KABHI KABHI CHUTNEY", "TYPE 2 DIABETES"]
    for i, r in enumerate(rows):
        y = 112 + i * 74
        d.text((44, y), r, font=font("anton", 54), fill=INK + (255,))
        d.line([(30, y + 70), (750, y + 70)], fill=INK + (255,), width=2)
    cardnp = np.asarray(lay).astype(np.float32)
    # ticks on the first three rows, drawn on the card layer
    tl = Image.fromarray(cardnp.astype(np.uint8))
    td = ImageDraw.Draw(tl)
    for i in range(3):
        y = 112 + i * 74
        td.line([(690, y + 32), (708, y + 54), (742, y + 10)], fill=INK + (255,), width=9, joint="curve")
    tl = tl.rotate(3, resample=Image.BICUBIC, expand=True)
    paste(img, tl, 540, 380)
    # red stamp over the last row
    st = sfx("STANDARD\nFEATURE", font("dela", 50), rot=-12, fill=RED)
    paste(img, st, 820, 575)
    stroke_poly(img, P, 8)
    # burst badge: 10 crore users
    bd = sfx("10 CRORE USERS!", font("bangers", 64), rot=-8)
    paste(img, bd, 250, 640)
    # ---- caption
    caption(img, ["Standard", "feature", "hai."], 1, 730)
    # ---- face circle
    me, al = load("41.3")
    face_circle(img, me, al, cx=540, cy=1450, r=320, scale=0.72, head_top=880, seed=7)
    return img


def frame_b():
    img = paper(21)
    # ---- big panel with his back photo, real colour
    P = [(40, 130), (1040, 130), (1040, 1000), (40, 1070)]
    pm = poly_mask(P)
    pic = cv2.cvtColor(cv2.imread("raw/assets/pic_back_pose.jpg"), cv2.COLOR_BGR2RGB)
    M = cv2.getRotationMatrix2D((pic.shape[1] / 2, pic.shape[0] / 2), -9, 1.0)          # straighten the tilt
    pic = cv2.warpAffine(pic, M, (pic.shape[1], pic.shape[0]), borderMode=cv2.BORDER_REFLECT)
    crop = cover(pic, 1000, 940, fx=0.52, fy=0.5, zoom=1.12)
    full = np.zeros((H, W, 3), np.float32)
    full[130:1070, 40:1040] = crop
    img[pm] = full[pm]
    stroke_poly(img, P, 8)
    # ---- list header tab + item box (the list item is the caption during the lists)
    box(img, 60, 880, 420, 950, border=0, shadow=0, fill=INK)
    ImageDraw  # noqa
    hdr = layer_text("PROTEIN BENEFITS  1/10", font("anton", 40), fill=PAPER, pad=10)
    paste(img, hdr, 240, 915)
    box(img, 60, 950, 900, 1090, border=6, shadow=12)
    num = layer_text("01", font("dela", 70), fill=RED, pad=10)
    paste(img, num, 135, 1020)
    t = layer_text("FASTER MUSCLE GROWTH", font("anton", 66), fill=INK, pad=10)
    paste(img, t, 215 + t.size[0] / 2, 1020)
    tick(img, 820, 985, 56, col=RED)
    # small "next" boxes, dashed = still to come
    for i in range(3):
        y = 1150 + i * 92
        x0, x1 = 60, 470
        m = Image.new("L", (W, H), 0)
        dd = ImageDraw.Draw(m)
        for x in range(x0, x1, 28):
            dd.line([(x, y), (min(x + 16, x1), y)], fill=255, width=5)
            dd.line([(x, y + 70), (min(x + 16, x1), y + 70)], fill=255, width=5)
        for yy in range(y, y + 70, 28):
            dd.line([(x0, yy), (x0, min(yy + 16, y + 70))], fill=255, width=5)
            dd.line([(x1, yy), (x1, min(yy + 16, y + 70))], fill=255, width=5)
        img[np.array(m) > 0] = INK
        n = layer_text(f"0{i + 2}", font("dela", 44), fill=INK, pad=6)
        paste(img, n, 110, y + 35)
    # ---- smaller face circle, bottom right
    me, al = load("49.0")
    face_circle(img, me, al, cx=770, cy=1530, r=245, scale=0.55, head_top=1190, seed=9, tone_cell=8)
    return img


if __name__ == "__main__":
    import os
    os.makedirs("out/stills/mg_test", exist_ok=True)
    for name, fn in (("A_41.3", frame_a), ("B_49.0", frame_b)):
        im = np.clip(fn(), 0, 255).astype(np.uint8)
        Image.fromarray(im).save(f"out/stills/mg_test/{name}.png")
        print(name)
