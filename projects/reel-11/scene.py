"""reel-11 scene: Pixel RPG world (Lemo-Opuscar pixel-rpg grammar) + real footage, frame(t) -> 1080x1920 RGB.

Pixel world: native 216x384, scaled x5 nearest-neighbour. Real assets (Tiger photo, his face video, gym clips,
physique photos, her clip) are never pixelated or recoloured; pixel art only frames them.
His face: real video in a pixel-stepped circle, head breaking out above the circle's centre line (work/matte/).

  python3 scene.py stills 0 2.5 5 ...     -> out/stills/t_<t>.png
  python3 scene.py grid                   -> one still every 2.5 s + labelled contact sheet
  python3 scene.py render [a b]           -> out/reel-11-picture.mp4 (picture only; audio is mixed separately)
"""
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import timeline as TL

S, W, H = 5, 216, 384
FW, FH = W * S, H * S
FPS = 30
FONT = ImageFont.truetype("fonts/PressStart2P-400.ttf", 8)
C = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)], np.uint8) for k, v in dict(
    ink="#181425", navy="#262b44", blue="#3a4466", blue2="#5a6988", silver="#8b9bb4", white="#ffffff",
    gold="#feae34", orange="#f77622", red="#e43b44", skin="#e8b796", skin2="#c28569", beard="#3e2731",
    shirt="#c0cbdc", purple="#68386c", pink="#b55088", brown="#733e39", brown2="#3e2731", sky="#124e89",
    green="#63c74d", green2="#3e8948", yellow="#fee761", dgrey="#5a6988").items()}
T = lambda k: tuple(int(x) for x in C[k])
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
WORDS = TL.words()


# ---------------------------------------------------------------- video sources (sequential-friendly)
class Src:
    def __init__(self, path, w=1080, h=1920, fps=30):
        self.path, self.w, self.h, self.fps = path, w, h, fps
        self.p, self.n = None, None

    def get(self, n):
        n = max(0, n)
        if self.p is None or n != self.n + 1 or n < self.n:
            if self.p:
                self.p.kill()
            self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{n / self.fps:.4f}", "-i", self.path,
                                       "-vf", f"scale={self.w}:{self.h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self.n = n - 1
            self.last = None
        while self.n < n:
            buf = self.p.stdout.read(self.w * self.h * 3)
            if len(buf) < self.w * self.h * 3:
                break
            self.last = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.n += 1
        self.n = n
        return self.last


CUT = Src("work/cut_v2_14.mp4")
HER = Src("work/her_full.mp4", fps=60)
GYM = {k: Src(f"raw/{k}.mp4") for k in ("gym_01", "gym_02", "gym_03")}


def load_rgb(p):
    return cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)


TIGER = load_rgb("assets/photos/celebrity_tiger.jpg")
PH_GYM = load_rgb("assets/photos/me_gym_dumbbell.jpg")
PH_MIR = load_rgb("assets/photos/me_physique_mirror.jpg")


# ---------------------------------------------------------------- pixel helpers (native grid)
def dither_v(img, x0, y0, x1, y1, c_top, c_bot):
    ys = np.arange(y0, y1)[:, None]
    xs = np.arange(x0, x1)[None, :]
    t = (ys - y0) / max(1, y1 - y0 - 1)
    m = t > BAYER[ys % 4, xs % 4]
    img[y0:y1, x0:x1] = np.where(m[..., None], C[c_bot], C[c_top])


def window(img, x0, y0, x1, y1, fill=("sky", "navy")):
    img[y0:y1, x0:x1] = C["ink"]
    img[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = C["white"]
    img[y0 + 2:y1 - 2, x0 + 2:x1 - 2] = C["silver"]
    dither_v(img, x0 + 3, y0 + 3, x1 - 3, y1 - 3, *fill)


def text(pil, x, y, s, col="white", shadow=True):
    d = ImageDraw.Draw(pil)
    if shadow:
        d.text((x + 1, y + 1), s, font=FONT, fill=T("ink"))
    d.text((x, y), s, font=FONT, fill=T(col))


def paint(img, x0, y0, art, pal, scale=1, outline=True):
    rows = art.strip("\n").split("\n")
    h, w = len(rows), max(len(r) for r in rows)
    m = np.zeros((h + 2, w + 2), bool)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                m[y + 1, x + 1] = True
    ol = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & ~m if outline else np.zeros_like(m)
    for y in range(h + 2):
        for x in range(w + 2):
            col = None
            if ol[y, x]:
                col = C["ink"]
            elif m[y, x]:
                col = C[pal[rows[y - 1][x - 1]]]
            if col is not None:
                yy, xx = y0 + y * scale, x0 + x * scale
                if 0 <= yy < H and 0 <= xx < W:
                    img[yy:yy + scale, xx:xx + scale] = col


HERO = """
...H.HHH.H....
..HHHHHHHHH...
..HHHHHHHHH...
..HSSSSSSSH...
..SWKSSWKS....
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
HERO_PAL = {"H": "ink", "S": "skin", "W": "white", "K": "ink", "B": "beard", "R": "skin2", "T": "shirt", "P": "navy"}
FRIEND = """
...RRRRRR.....
..RRRRRRRR....
.RRRRRRRRRRR..
..HSSSSSSH....
..SWKSSWKS....
..SSSSSSSS....
..SSSSSSSS....
...SSKKSS.....
....SSSS......
....SSSS......
..GGGGGGGG....
.GGGGGGGGGG...
.GGGGGGGGGG...
SGGGGGGGGGGS..
SGGGGGGGGGGS..
S.GGGGGGGG.S..
S.GGGGGGGG.S..
..GGGGGGGG....
..PPPPPPPP....
..PPP..PPP....
..PPP..PPP....
..PPP..PPP....
..PPP..PPP....
..KKK..KKK....
"""
FRIEND_PAL = {"R": "red", "H": "ink", "S": "skin2", "W": "white", "K": "ink", "G": "green2", "P": "blue"}
HAND = """
XXXX....
XWWWXXX.
XWWWWWWX
XWWWWWWX
XWWWWWX.
XXXXXX..
"""
HAND_PAL = {"X": "ink", "W": "white"}
SHIELD = """
.SSSSSSSSSS.
SGGGGGGGGGGS
SGYYGGGGGGGS
SGYGGGGGGGGS
SGGGGGGGGGGS
SGGGGGGGGGGS
.SGGGGGGGGS.
.SGGGGGGGGS.
..SGGGGGGS..
...SGGGGS...
....SGGS....
.....SS.....
"""
SHIELD_PAL = {"S": "silver", "G": "gold", "Y": "white"}


def hand(img, x, y, t, stop=False):
    bob = 0 if stop else (1 if int(t * 4) % 2 else 0)
    paint(img, x - bob, y, HAND, HAND_PAL, outline=False)


def hero(img, x, y, t, scale=2):
    breath = 1 if int(t * 2) % 2 else 0
    paint(img, x, y - breath * 0, HERO, HERO_PAL, scale)
    if breath:
        img[y + 11 * scale - 1, x + 2 * scale:x + 12 * scale] = img[y + 11 * scale, x + 2 * scale:x + 12 * scale]


def room():
    img = np.zeros((H, W, 3), np.uint8)
    dither_v(img, 0, 0, W, 244, "purple", "navy")
    rng = np.random.default_rng(3)
    for _ in range(26):
        img[rng.integers(0, 240), rng.integers(0, W)] = C["pink"]
    img[244:H] = C["brown"]
    img[244] = C["ink"]
    for y in range(254, H, 10):
        img[y, :] = C["brown2"]
    for y0 in range(244, H, 10):
        off = 0 if (y0 // 10) % 2 else 12
        for x in range(off, W, 24):
            img[y0:y0 + 10, x] = C["brown2"]
    return img


ROOM = room()


def mosaic(img, b):
    if b <= 1:
        return img
    h, w = img.shape[:2]
    small = cv2.resize(img, (max(1, w // b), max(1, h // b)), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def up(a):
    return cv2.resize(a, (FW, FH), interpolation=cv2.INTER_NEAREST)


# ---------------------------------------------------------------- captions (the dialog box is the subtitle)
# hand-set caption lines (word counts per line), following the phrasing of the script; max 25 chars a line (text starts at x 9)
LINES = [[4, 5], [4, 4], [2], [3, 1], [3], [2, 2], [3, 1], [4], [5], [4, 2], [3, 4], [4, 2], [4, 3], [4, 4],
         [5, 4], [4, 3], [2, 2], [5, 5], [4]]


def chunks():
    assert sum(sum(l) for l in LINES) == len(WORDS), (sum(sum(l) for l in LINES), len(WORDS))
    out, i = [], 0
    for lines in LINES:
        ch = []
        for li, k in enumerate(lines):
            for j in range(k):
                ch.append(dict(WORDS[i], nl=(li > 0 and j == 0)))
                i += 1
        assert all(len(" ".join(w["w"] for w in ch[sum(lines[:q]):sum(lines[:q + 1])])) <= 25 for q in range(len(lines))), [w["w"] for w in ch]
        out.append(ch)
    return out


CHUNKS = chunks()


def caption(img, t):
    for k, ch in enumerate(CHUNKS):
        a = ch[0]["s"]
        b = CHUNKS[k + 1][0]["s"] if k + 1 < len(CHUNKS) else ch[-1]["e"] + 0.5
        b = min(b, ch[-1]["e"] + 0.9)
        if a <= t < b:
            window(img, 4, 52, W - 4, 88)
            pil = Image.fromarray(img)
            x, y = 9, 61
            for w in ch:
                if w["nl"]:
                    x, y = 9, 74
                if w["s"] > t:
                    break
                n = min(len(w["w"]), int((t - w["s"]) * 40) + 1)
                col = "gold" if w["s"] <= t < w["e"] + 0.12 else "white"
                text(pil, x, y, w["w"][:n], col)
                x += (len(w["w"]) + 1) * 8
            img[:] = np.array(pil)
            return


# ---------------------------------------------------------------- face circle (real video, head breaks out)
def face(big, n, cx, cy, r, src_frame=None):
    yy, xx = np.mgrid[0:H, 0:W]
    d2 = (xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2
    circ_n, ring_n, ringo_n = d2 <= r * r, (d2 <= (r + 2) ** 2) & (d2 > r * r), (d2 <= (r + 3) ** 2) & (d2 > (r + 2) ** 2)
    circ, ring, ringo = up(circ_n.astype(np.uint8)) > 0, up(ring_n.astype(np.uint8)) > 0, up(ringo_n.astype(np.uint8)) > 0
    big[ringo] = C["ink"]
    big[ring] = C["gold"]
    fill = np.zeros((H, W, 3), np.uint8)
    dither_v(fill, 0, max(0, int(cy - r)), W, min(H, int(cy + r)), "gold", "orange")
    big[circ] = up(fill)[circ]
    me = CUT.get(n) if src_frame is None else src_frame
    mp = f"work/matte/{n:05d}.png"
    if me is None or not os.path.exists(mp):
        return
    al = cv2.imread(mp, 0).astype(np.float32) / 255
    al = cv2.GaussianBlur(al, (3, 3), 0)
    sc = r * 0.62 / 60
    me_s = cv2.resize(me, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA).astype(np.float32)
    al_s = cv2.resize(al, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    ox = int(cx * S - 540 * sc)
    oy = int((cy - r) * S - 105 * r / 60 - 470 * sc)
    h, w = al_s.shape
    y0, x0, y1, x1 = max(0, oy), max(0, ox), min(FH, oy + h), min(FW, ox + w)
    if y1 <= y0 or x1 <= x0:
        return
    a = al_s[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    clip = circ[y0:y1, x0:x1].copy()
    clip[: max(0, cy * S - y0)] = True                    # above the centre line the head is free
    a = a * clip
    reg = big[y0:y1, x0:x1].astype(np.float32)
    big[y0:y1, x0:x1] = (reg * (1 - a[..., None]) + me_s[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * a[..., None]).astype(np.uint8)


def place(big, img, x, y, w, h):
    """paste a real image resized to w x h at screen x, y (cover-crop to the box)"""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (max(w, int(round(iw * s))), max(h, int(round(ih * s)))), interpolation=cv2.INTER_AREA)
    ox, oy = (r.shape[1] - w) // 2, (r.shape[0] - h) // 2
    big[y:y + h, x:x + w] = r[oy:oy + h, ox:ox + w]


def cover(img, zoom=1.0, ax=0.5, ay=0.5):
    """real image to full frame, cover-fit, optional zoom anchored at (ax, ay)"""
    ih, iw = img.shape[:2]
    s = max(FW / iw, FH / ih) * zoom
    r = cv2.resize(img, (int(round(iw * s)), int(round(ih * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    ox, oy = int((r.shape[1] - FW) * ax), int((r.shape[0] - FH) * ay)
    return r[oy:oy + FH, ox:ox + FW].copy()


# ---------------------------------------------------------------- beats
def beat_of(t):
    for k, (a, b) in TL.BEATS.items():
        if a <= t < b:
            return k, t - a
    return "breakout", t - TL.BEATS["breakout"][0]


def calendar(img, x, y, month, w=50, h=56):
    img[y:y + h, x:x + w] = C["ink"]
    img[y + 1:y + h - 1, x + 1:x + w - 1] = C["white"]
    img[y + 1:y + 15, x + 1:x + w - 1] = C["red"]
    for r in range(4):
        for c in range(5):
            img[y + 19 + r * 9:y + 25 + r * 9, x + 4 + c * 9:x + 10 + c * 9] = C["silver"]
    img[y + 19:y + 25, x + 4:x + 10] = C["gold"]
    pil = Image.fromarray(img)
    text(pil, x + (w - len(month) * 8) // 2, y + 4, month, "white")
    img[:] = np.array(pil)


def couch(img, x, y):
    img[y:y + 22, x:x + 86] = C["ink"]
    img[y + 1:y + 21, x + 1:x + 85] = C["purple"]
    img[y + 1:y + 3, x + 1:x + 85] = C["pink"]
    img[y + 18:y + 36, x - 6:x + 92] = C["ink"]
    img[y + 19:y + 35, x - 5:x + 91] = C["pink"]
    img[y + 19:y + 21, x - 5:x + 91] = C["purple"]
    img[y + 14:y + 36, x - 8:x + 2] = C["ink"]
    img[y + 15:y + 35, x - 7:x + 1] = C["purple"]
    img[y + 14:y + 36, x + 84:x + 94] = C["ink"]
    img[y + 15:y + 35, x + 85:x + 93] = C["purple"]


def hero_sitting(img, x, y, t):
    """upper body on the couch, legs forward"""
    rows = HERO.strip("\n").split("\n")
    paint(img, x, y, "\n".join(rows[:18]), HERO_PAL, 2)
    img[y + 36:y + 42, x + 4:x + 28] = C["ink"]
    img[y + 37:y + 41, x + 5:x + 27] = C["navy"]
    # chips bag
    img[y + 24:y + 38, x + 30:x + 40] = C["ink"]
    img[y + 25:y + 37, x + 31:x + 39] = C["red"]
    img[y + 28:y + 31, x + 32:x + 38] = C["yellow"]


def pixel_beat(name, lt, t, n):
    img = ROOM.copy()
    reals, circle, post = [], None, []
    if name == "quest":
        hero(img, 14, 196, t)
        if t < 17.31:
            if lt > 0.12:
                window(img, 4, 98, W - 4, 150)
                pil = Image.fromarray(img)
                text(pil, 12, 107, "NEW QUEST!", "gold")
                text(pil, 12, 122, "Look like your", "white")
                text(pil, 12, 135, "favorite celebrity", "white")
                img = np.array(pil)
        else:
            k = int((t - 17.31) * FPS)
            sc = [0.25, 0.55, 0.9, 1.08, 1.03, 1.0][min(k, 5)]
            reals.append(("tiger", sc))
            if k >= 5:
                img[92:269, 68:210] = C["ink"]
                img[93:268, 69:209] = C["gold"]
                img[94:267, 70:208] = C["orange"]
                window(img, 100, 270, 210, 292)
                pil = Image.fromarray(img)
                text(pil, 108, 278, "TARGET", "gold")
                img = np.array(pil)
        circle = (40, 300, 34)
    elif name == "calendar":
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN"]
        k = 0 if t < 19.15 else min(5, int((t - 19.15) / 0.26) + 1)
        calendar(img, 16, 100, months[min(k, 5)], 64, 70)
        if 19.15 <= t < 20.75 and int((t - 19.15) / 0.26) < 5:
            ph = ((t - 19.15) % 0.26) / 0.26           # a page flying off up-left
            px, py = int(16 - ph * 40), int(100 - ph * 60)
            if py >= 2 and px >= 2:
                img[py - 1:py + 21, px - 1:px + 41] = C["ink"]
                img[py:py + 20, px:px + 40] = C["white"]
                img[py:py + 6, px:px + 40] = C["red"]
        window(img, 92, 100, 210, 124)
        day = 1 if t < 19.15 else min(183, 1 + int((t - 19.15) / (20.65 - 19.15) * 182))
        if t > 20.65:
            day = 183 + int((t - 20.65) * 10)
        pil = Image.fromarray(img)
        text(pil, 100, 108, f"DAY {day}", "gold")
        img = np.array(pil)
        hero(img, 14, 196, t)
        circle = (150, 252, 56)
    elif name == "menu":
        calendar(img, 10, 100, "JUN", 30, 34) if False else None
        window(img, 50, 94, W - 6, 160)
        window(img, 4, 164, 92, 188)
        pil = Image.fromarray(img)
        text(pil, 58, 102, "CHOOSE PLAN", "gold")
        for i, o in enumerate(["KETO", "FASTING (IF)", "PUSH PULL LEGS"]):
            text(pil, 70, 117 + i * 13, o, "white")
        text(pil, 10, 172, f"DAY {183 + int((t - 20.65) * 10)}", "gold")
        img = np.array(pil)
        if t < 22.03:
            sel = 0
        elif t < 22.55:
            sel = 0
        elif t < 24.01:
            sel = 1
        elif t < 24.7:
            sel = 2
        else:
            sel = int(t * 7) % 3                           # indecision: cursor can't settle
        hand(img, 58, 117 + sel * 13, t, stop=t >= 24.7)
        hero(img, 14, 196, t)
        img[190:200, 44:58] = C["ink"]
        img[191:199, 45:57] = C["white"]
        img[200, 46] = C["ink"]
        pil = Image.fromarray(img)
        ImageDraw.Draw(pil).text((47, 191), "?", font=FONT, fill=T("ink"))
        img = np.array(pil)
        if t >= 25.17:
            window(img, 56, 128, 208, 160, fill=("ink", "navy"))
            pil = Image.fromarray(img)
            text(pil, 62, 135, "PERFECT PLAN...", "white")
            img = np.array(pil)
            pct = min(99, int((t - 25.17) / 0.4 * 99))
            img[147:153, 62:166] = C["ink"]
            img[148:152, 63:63 + int(102 * pct / 100)] = C["green"]
            if pct < 99 or int(t * 4) % 2:
                pil = Image.fromarray(img)
                text(pil, 170, 146, f"{pct}%", "gold" if pct == 99 else "white")
                img = np.array(pil)
        circle = (148, 248, 60)
    elif name == "save":
        window(img, 14, 96, W - 6, 150)
        pil = Image.fromarray(img)
        text(pil, 22, 104, "SAVE GAME?", "gold")
        text(pil, 34, 119, "START NOW", "white")
        text(pil, 34, 133, "WAIT: NEXT MONDAY", "white")
        img = np.array(pil)
        sel = 1 if t >= 28.29 else 0
        flash = 28.29 <= t < 28.42 and int(t * 30) % 2
        hand(img, 22, 119 + sel * 14, t, stop=sel == 1)
        if flash:
            img[131:142, 32:172] = C["white"]
        if t >= 28.5:
            window(img, 100, 156, W - 4, 194, fill=("ink", "navy"))
            pil = Image.fromarray(img)
            text(pil, 108, 164, "GAME SAVED", "green")
            text(pil, 108, 178, "GO: MONDAY", "white")
            img = np.array(pil)
        hero(img, 168, 196, t)
        circle = (64, 254, 56)
    elif name in ("couch", "item"):
        couch(img, 110, 208)
        hero_sitting(img, 130, 186, t)
        if name == "couch":
            window(img, 96, 96, W - 6, 124)
            pil = Image.fromarray(img)
            text(pil, 104, 104, "BODY FAT", "white")
            img = np.array(pil)
            fill = min(1.0, 0.35 + max(0, t - 29.4) / 1.4 * 0.6)
            img[114:120, 104:204] = C["ink"]
            img[115:119, 105:105 + int(98 * fill)] = C["red"]
            if t >= 30.18:
                k = t - 30.18
                pil = Image.fromarray(img)
                text(pil, 120, int(176 - k * 30), "+1", "red")
                img = np.array(pil)
            if 30.18 <= t < 30.45:                      # 3-2-1 px shake
                sh = [3, -3, 2, -2, 1, -1, 1, 0][min(7, int((t - 30.18) * FPS))]
                img = np.roll(img, sh, axis=1)
            circle = (52, 262, 46)
        else:
            if t >= 31.87:
                k = int((t - 31.87) * FPS)
                yy = 150 - min(k, 8) * 2
                paint(img, 140, yy, SHIELD, SHIELD_PAL, 2)
                if int(t * 6) % 2 and k < 30:
                    for dx, dy in ((-8, 4), (34, 2), (-4, 26), (32, 24)):
                        img[yy + dy:yy + dy + 2, 140 + dx:140 + dx + 2] = C["white"]
                window(img, 4, 96, 136, 140)
                pil = Image.fromarray(img)
                text(pil, 12, 104, "YOU OBTAINED", "white")
                text(pil, 12, 117, "COMFORT ZONE!", "gold")
                text(pil, 12, 129, "DEF +99", "green")
                img = np.array(pil)
            if t >= 33.89:
                window(img, 4, 146, 136, 172, fill=("ink", "navy"))
                pil = Image.fromarray(img)
                text(pil, 12, 155, "BODY: UNHAPPY", "red")
                img = np.array(pil)
            circle = (52, 262, 46)
    elif name == "lady":
        out_k = int((t - 36.95) * FPS) if t >= 36.95 else -1
        if out_k < 8:
            window(img, 10, 96, 114, 238)
            reals.append(("her", max(1, [1, 2, 4, 8, 12, 18, 24, 32][out_k]) if out_k >= 0 else 1))
        window(img, 120, 100, W - 6, 144)
        pil = Image.fromarray(img)
        text(pil, 136, 110, "LISTEN", "white")
        text(pil, 136, 126, "SKIP", "white")
        img = np.array(pil)
        sel = 1 if t >= 36.27 else 0
        hand(img, 126, 110 + sel * 16, t, stop=sel == 1)
        if 36.6 <= t < 36.75 and int(t * 30) % 2:
            img[124:135, 134:170] = C["white"]
        if out_k < 8:
            window(img, 10, 240, 114, 262, fill=("ink", "navy")) if False else None
        circle = (164, 266, 44)
    elif name == "share":
        window(img, 40, 96, W - 6, 148)
        pil = Image.fromarray(img)
        text(pil, 48, 104, "SHARE VIDEO?", "gold")
        text(pil, 62, 119, "YES", "white")
        text(pil, 62, 133, "NO!", "white")
        img = np.array(pil)
        hand(img, 50, 133, t, stop=True)
        if t >= 39.45:
            fx = int(W - (t - 39.45) * 60)
            fx = max(150, fx)
            step = int(t * 8) % 2 if fx > 150 else 0
            paint(img, fx, 196 - step, FRIEND, FRIEND_PAL, 2)
            if fx == 150:
                window(img, 120, 154, W - 6, 176, fill=("ink", "navy"))
                pil = Image.fromarray(img)
                text(pil, 128, 162, "FRIEND", "green")
                img = np.array(pil)
        circle = (52, 262, 46)
    elif name == "questlog":
        paint(img, 150, 196, FRIEND, FRIEND_PAL, 2)
        window(img, 40, 96, W - 6, 190)
        pil = Image.fromarray(img)
        text(pil, 48, 104, "QUEST LOG", "gold")
        text(pil, 48, 120, "FITNESS JOURNEY", "white")
        if t >= 42.81:
            text(pil, 48, 134, "START:NEXT MON", "white")
        if t >= 43.57:
            yr = 2020 + min(6, int(max(0, t - 43.9) / 0.13))
            text(pil, 48, 148, f"SINCE: {yr}", "gold")
        if t >= 44.75:
            if int(t * 4) % 2 or t > 45.0:
                text(pil, 48, 166, "NOT STARTED", "red")
        img = np.array(pil)
        circle = (52, 262, 46)
    return img, reals, circle


def frame(t):
    n = int(round(t * FPS))
    name, lt = beat_of(t)
    if name == "her":
        return CUT.get(n).copy()
    if name == "pause":
        if t < 12.867:
            b = [1, 2, 4, 8, 14][min(4, int((t - 12.70) * FPS))]
            return mosaic(CUT.get(n), b * 5)
        f = mosaic(CUT.get(385), 70)
        f = (f.astype(np.float32) * 0.55).astype(np.uint8)
        win = np.zeros((H, W, 3), np.uint8)
        window(win, 66, 176, 150, 200)
        pil = Image.fromarray(win)
        text(pil, 84, 184, "PAUSED", "white")
        win = np.array(pil)
        m = up((win.sum(2) > 0).astype(np.uint8)) > 0
        f[m] = up(win)[m]
        return f
    if name == "deadpan":
        f = CUT.get(n)
        z = 1.0 + 0.06 * lt / 2.53
        f = cover(f, z, 0.5, 0.35)
        cap = np.zeros((H, W, 3), np.uint8)
        caption(cap, t)
        m = up((cap.sum(2) > 0).astype(np.uint8)) > 0
        f[m] = up(cap)[m]
        return f
    if name == "breakout":
        return breakout(t, lt, n)
    img, reals, circle = pixel_beat(name, lt, t, n)
    caption(img, t)
    if name == "quest" and lt < 0.3:                     # mosaic in from his real frame
        k = int(lt * FPS)
        if k < 4:
            return mosaic(cover(CUT.get(n)), [12, 24, 40, 60][k])
        img = mosaic(img, [8, 6, 4, 2, 1][min(4, k - 4)])
    big = up(img)
    for kind, v in reals:
        if kind == "tiger":
            w, h = int(690 * v), int(865 * v)
            cx, cy = 139 * S, 180 * S
            x, y = cx - w // 2, cy - h // 2
            if v < 1.0 or True:
                big[y - 5:y + h + 5, x - 5:x + w + 5] = C["gold"]
            place(big, TIGER, x, y, w, h)
        if kind == "her":
            src = HER.get(int((2.2 + (t - 35.3667)) * 60))
            box = big[(96 + 3) * S:(238 - 3) * S, (10 + 3) * S:(114 - 3) * S]
            tmp = np.zeros_like(box)
            place(tmp, src[60:], 0, 0, box.shape[1], box.shape[0])
            box[:] = mosaic(tmp, v * 5) if v > 1 else tmp
    if circle:
        face(big, n, *circle)
    return big


def breakout(t, lt, n):
    if lt < 0.23:                                         # the pixel world glitches and tears away
        img, _, circle = pixel_beat("questlog", 0, 45.16, n)
        caption(img, t)
        k = int(lt * FPS)
        rng = np.random.default_rng(k + 7)
        for y0 in range(0, H, 8):
            if rng.random() < 0.5:
                img[y0:y0 + 8] = np.roll(img[y0:y0 + 8], int(rng.integers(-30, 30)), axis=1)
        big = up(img)
        face(big, n, *circle)
        if k >= 3:
            big = np.roll(big, 10, axis=1)
            big[..., 0] = np.roll(big[..., 0], 14, axis=1)
        if k == 5:
            big = 255 - big
        return big
    if t < 46.17:
        f = cover(GYM["gym_03"].get(int((4.2 + t - 45.40) * 30)), 1.18, 0.5, 1.0)
    elif t < 46.93:
        f = cover(GYM["gym_02"].get(int((1.6 + t - 46.17) * 30)), 1.2, 1.0, 1.0)
    elif t < 47.63:
        f = cover(GYM["gym_01"].get(int((0.8 + t - 46.93) * 30)), 1.0)
    elif t < 48.33:
        f = up(ROOM.copy())                              # photo sits 200 px lower so the caption clears his face
        ph = cover(PH_GYM, 1.0 + 0.04 * (t - 47.63) / 0.7, 0.5, 0.0)
        f[200:] = ph[:FH - 200]
        f[195:200] = C["gold"]
    elif t < 49.05:
        f = cover(PH_MIR, 1.0 + 0.02 * (t - 48.33) / 0.72, 0.5, 0.4)
    else:
        return end_card(t)
    cap = np.zeros((H, W, 3), np.uint8)
    caption(cap, t)
    m = up((cap.sum(2) > 0).astype(np.uint8)) > 0
    f[m] = up(cap)[m]
    if t < 47.63:
        face(f, n, 176, 268, 28)
    return f


def end_card(t):
    """the physique photo shrinks into a pixel-framed card (like the Tiger TARGET card) + FOLLOW button"""
    k = int((t - 49.05) * FPS)
    img = ROOM.copy()
    sc = [1.6, 1.3, 1.1, 0.97, 1.0][min(k, 4)]
    cw, ch = 140, 210                                   # native card inner size (aspect 2:3)
    if k >= 4:
        x0, y0 = (W - cw) // 2, 58
        img[y0 - 3:y0 + ch + 3, x0 - 3:x0 + cw + 3] = C["ink"]
        img[y0 - 2:y0 + ch + 2, x0 - 2:x0 + cw + 2] = C["gold"]
        img[y0 - 1:y0 + ch + 1, x0 - 1:x0 + cw + 1] = C["orange"]
        window(img, 62, 276, 154, 300)
        pil = Image.fromarray(img)
        text(pil, 84, 284, "FOLLOW", "gold")
        img = np.array(pil)
        hand(img, 70, 284, t)
    big = up(img)
    w, h = int(cw * S * sc), int(ch * S * sc)
    cx, cy = FW // 2, (58 + ch // 2) * S
    x, y = cx - w // 2, cy - h // 2
    xa, ya = max(0, x), max(0, y)
    tmp = np.zeros((h, w, 3), np.uint8)
    place(tmp, PH_MIR, 0, 0, w, h)
    big[ya:min(FH, y + h), xa:min(FW, x + w)] = tmp[ya - y:min(FH, y + h) - y, xa - x:min(FW, x + w) - x]
    return big


# ---------------------------------------------------------------- CLI
def save_still(t, folder="out/stills"):
    os.makedirs(folder, exist_ok=True)
    p = f"{folder}/t_{t:05.2f}.png"
    Image.fromarray(frame(t)).save(p)
    return p


def sheet(paths, times, out, cols=6, tw=270):
    tiles = []
    for p, t in zip(paths, times):
        im = cv2.resize(cv2.imread(p), (tw, int(tw * 16 / 9)), interpolation=cv2.INTER_AREA)
        cv2.rectangle(im, (0, 0), (92, 30), (0, 0, 0), -1)
        cv2.putText(im, f"{t:.1f}s", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 230, 255), 2)
        tiles.append(im)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        for a in sys.argv[2:]:
            print(save_still(float(a)))
    elif cmd == "grid":
        ts = [round(i * 2.5, 2) for i in range(int(TL.DUR / 2.5) + 1)]
        ps = [save_still(t, "out/stills/grid") for t in ts]
        sheet(ps, ts, "out/stills/contact_sheet.jpg")
    elif cmd == "sheet":
        ts = [float(a) for a in sys.argv[3:]]
        ps = [save_still(t, "out/stills/keys") for t in ts]
        sheet(ps, ts, sys.argv[2], cols=5, tw=320)
    elif cmd == "render":
        a = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
        b = float(sys.argv[3]) if len(sys.argv) > 3 else TL.DUR
        out = sys.argv[4] if len(sys.argv) > 4 else "out/reel-11-picture.mp4"
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{FW}x{FH}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                              "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        for k in range(int(round(a * FPS)), int(round(b * FPS))):
            p.stdin.write(frame(k / FPS).tobytes())
            if k % 60 == 0:
                print(k, flush=True)
        p.stdin.close()
        p.wait()
