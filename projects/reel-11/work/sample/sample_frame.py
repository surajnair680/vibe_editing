"""reel-11 styled sample frame: Pixel RPG look (Lemo-Opuscar pixel-rpg grammar) + real face circle.

Beat: "...overthinking whether keto, intermittent fasting, or push-pull legs is the perfect plan" (edit ~21 s).
Pixel world drawn at native 216x384 and scaled x5 nearest-neighbour to 1080x1920. Real video (his frame) stays real,
inside a pixel-stepped circle; the head breaks out above the circle's centre line.
Run from the project folder: python3 work/sample/sample_frame.py -> work/sample/sample_frame.png
"""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

S = 5
W, H = 216, 384
FONT = ImageFont.truetype("fonts/PressStart2P-400.ttf", 8)

C = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in dict(
    ink="#181425", navy="#262b44", blue="#3a4466", blue2="#5a6988", silver="#8b9bb4", white="#ffffff",
    gold="#feae34", orange="#f77622", red="#e43b44", skin="#e8b796", skin2="#c28569", beard="#3e2731",
    shirt="#c0cbdc", purple="#68386c", pink="#b55088", brown="#733e39", brown2="#3e2731", sky="#124e89",
    green="#63c74d").items()}

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def dither_v(img, x0, y0, x1, y1, c_top, c_bot):
    """vertical two-colour gradient with 4x4 Bayer dither (no blends)"""
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        for x in range(x0, x1):
            img[y, x] = c_bot if t > BAYER[y % 4, x % 4] else c_top


def window(img, x0, y0, x1, y1):
    """16-bit blue RPG window: ink / white / silver border, dithered blue fill"""
    img[y0:y1, x0:x1] = C["ink"]
    img[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = C["white"]
    img[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = C["silver"]
    dither_v(img, x0 + 3, y0 + 3, x1 - 3, y1 - 3, C["sky"], C["navy"])
    for (x, y) in [(x0, y0), (x1 - 1, y0), (x0, y1 - 1), (x1 - 1, y1 - 1)]:   # rounded corners
        img[y, x] = (0, 0, 0, ) if False else img[y, x]


def text(pil, x, y, s, col, shadow=True):
    d = ImageDraw.Draw(pil)
    if shadow:
        d.text((x + 1, y + 1), s, font=FONT, fill=C["ink"])
    d.text((x, y), s, font=FONT, fill=col)


SPRITE = """
....HHHHH.....
...HHHHHHH....
..HHHHHHHHH...
..HSSSSSSHH...
..SWKSSWKSH...
..SSSSSSSS....
..BBSSSSBB....
..BBBRRBBB....
...BBBBBB.....
....SSSS......
..TTTTTTTT....
.TTTTTTTTTT...
.TTTTTTTTTT...
STTTTTTTTTTS..
STTTTTTTTTTS..
S.TTTTTTTT.S..
S.TTTTTTTT.S..
..TTTTTTTT....
..PPPPPPPP....
..PPP..PPP....
..PPP..PPP....
..PPP..PPP....
..PPP..PPP....
..KKK..KKK....
"""
SPAL = {"H": "ink", "S": "skin", "W": "white", "K": "ink", "B": "beard", "R": "skin2", "T": "shirt", "P": "navy"}


def sprite(img, x0, y0, scale=1):
    rows = [r for r in SPRITE.strip("\n").split("\n")]
    h, w = len(rows), len(rows[0])
    m = np.zeros((h + 2, w + 2), bool)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                m[y + 1, x + 1] = True
    outline = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m
    for y in range(h + 2):
        for x in range(w + 2):
            col = None
            if outline[y, x]:
                col = C["ink"]
            elif m[y, x]:
                col = C[SPAL[rows[y - 1][x - 1]]]
            if col:
                img[y0 + y * scale:y0 + (y + 1) * scale, x0 + x * scale:x0 + (x + 1) * scale] = col


def build():
    img = np.zeros((H, W, 3), np.uint8)
    # room: dithered wall, floor with tiles
    dither_v(img, 0, 0, W, 244, C["purple"], C["navy"])
    rng = np.random.default_rng(3)
    for _ in range(26):                                  # wall specks
        x, y = rng.integers(0, W), rng.integers(0, 230)
        img[y, x] = C["pink"]
    img[244:H] = C["brown"]
    img[244] = C["ink"]
    for y in range(254, H, 10):
        img[y, :] = C["brown2"]
    for y0 in range(244, H, 10):
        off = 0 if (y0 // 10) % 2 else 12
        for x in range(off, W, 24):
            img[y0:y0 + 10, x] = C["brown2"]
    # wall calendar (procrastination prop)
    cx, cy = 10, 100
    img[cy:cy + 34, cx:cx + 30] = C["ink"]
    img[cy + 1:cy + 33, cx + 1:cx + 29] = C["white"]
    img[cy + 1:cy + 9, cx + 1:cx + 29] = C["red"]
    for r in range(3):
        for c in range(4):
            img[cy + 12 + r * 7:cy + 16 + r * 7, cx + 3 + c * 7:cx + 7 + c * 7] = C["silver"]
    img[cy + 12:cy + 16, cx + 3:cx + 7] = C["gold"]       # Monday circled

    pil = Image.fromarray(img)
    # caption window (top, the dialog box is the subtitle), below the 250 px safe zone
    a = np.array(pil)
    window(a, 4, 52, W - 4, 88)
    # menu window
    window(a, 50, 94, W - 6, 160)
    # status window
    window(a, 4, 164, 92, 188)
    pil = Image.fromarray(a)
    text(pil, 12, 61, "whether ", C["white"])
    text(pil, 12 + 8 * 8, 61, "keto,", C["gold"])
    text(pil, 12, 74, "intermittent fasting,", C["white"])
    text(pil, 58, 102, "CHOOSE PLAN", C["gold"])
    opts = ["KETO", "FASTING (IF)", "PUSH PULL LEGS"]
    for i, o in enumerate(opts):
        text(pil, 70, 117 + i * 13, o, C["white"])
    # hand cursor on the first option (bobbing in motion)
    a = np.array(pil)
    hx, hy = 58, 117
    hand = ["XXXX....", "XWWWXXX.", "XWWWWWWX", "XWWWWWWX", "XWWWWWX.", "XXXXXX.."]
    for y, r in enumerate(hand):
        for x, ch in enumerate(r):
            if ch == "X":
                a[hy + y, hx + x] = C["ink"]
            elif ch == "W":
                a[hy + y, hx + x] = C["white"]
    pil = Image.fromarray(a)
    text(pil, 10, 172, "DAY 143", C["gold"])
    # hero sprite with thought bubble
    a = np.array(pil)
    sprite(a, 12, 192, 2)
    bx, by = 44, 190
    a[by:by + 10, bx:bx + 14] = C["ink"]
    a[by + 1:by + 9, bx + 1:bx + 13] = C["white"]
    a[by + 10, bx + 2] = C["ink"]
    pil = Image.fromarray(a)
    ImageDraw.Draw(pil).text((bx + 3, by + 1), "?", font=FONT, fill=C["ink"])

    big = np.array(pil.resize((W * S, H * S), Image.NEAREST))

    # ---- real face circle (pixel-stepped circle, head breaks out above centre line) ----
    ccx, ccy, rr = 148, 248, 60                       # native units
    yy, xx = np.mgrid[0:H, 0:W]
    circ_n = ((xx + 0.5 - ccx) ** 2 + (yy + 0.5 - ccy) ** 2) <= rr ** 2
    ring_n = (((xx + 0.5 - ccx) ** 2 + (yy + 0.5 - ccy) ** 2) <= (rr + 2) ** 2) & ~circ_n
    ring_o = (((xx + 0.5 - ccx) ** 2 + (yy + 0.5 - ccy) ** 2) <= (rr + 3) ** 2) & ~circ_n & ~ring_n
    up = lambda m: cv2.resize(m.astype(np.uint8), (W * S, H * S), interpolation=cv2.INTER_NEAREST).astype(bool)
    circ, ring, ringo = up(circ_n), up(ring_n), up(ring_o)
    big[ringo] = C["ink"]
    big[ring] = C["gold"]
    # inside fill: dithered gold-orange disc (warm, so the face pops off the cool world)
    fill = np.zeros((H, W, 3), np.uint8)
    dither_v(fill, 0, int(ccy - rr), W, int(ccy + rr), C["gold"], C["orange"])
    fill_big = cv2.resize(fill, (W * S, H * S), interpolation=cv2.INTER_NEAREST)
    big[circ] = fill_big[circ]

    me = cv2.cvtColor(cv2.imread("work/sample/me_frame.png"), cv2.COLOR_BGR2RGB).astype(float)
    al = cv2.imread("work/sample/me_alpha.png", 0)
    n, lab, st, _ = cv2.connectedComponentsWithStats((al > 128).astype(np.uint8))
    keep = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
    al = np.where(lab == keep, al, 0).astype(float) / 255
    al = cv2.GaussianBlur(al, (3, 3), 0)
    sc = 0.62
    me = cv2.resize(me, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    ox, oy = int(ccx * S - 540 * sc), int((ccy - rr) * S - 105 - 470 * sc)
    canvas_me = np.zeros_like(big, float)
    canvas_al = np.zeros(big.shape[:2], float)
    h, w = me.shape[:2]
    y0, x0 = max(0, oy), max(0, ox)
    y1, x1 = min(big.shape[0], oy + h), min(big.shape[1], ox + w)
    canvas_me[y0:y1, x0:x1] = me[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    canvas_al[y0:y1, x0:x1] = al[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    above = np.zeros(big.shape[:2], bool)
    above[:ccy * S] = True
    clip = circ | (above & ~ring & ~ringo) | (above)      # inside circle, or anywhere above the centre line
    a_final = canvas_al * clip
    out = big.astype(float) * (1 - a_final[..., None]) + canvas_me * a_final[..., None]
    out = out.clip(0, 255).astype(np.uint8)
    Image.fromarray(out).save("work/sample/sample_frame.png")
    Image.fromarray(out).resize((540, 960), Image.LANCZOS).save("work/sample/sample_frame_half.jpg", quality=90)
    print("person top-left", ox, oy, "size", w, h)


if __name__ == "__main__":
    build()
