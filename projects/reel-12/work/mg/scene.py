"""reel-12 full manga build over rough cut v3 (edit times, 30 fps).

0-24.70 her clip + his inset: untouched (rough v3 frames). 85.19-end: the meme, untouched.
24.70-85.19: manga page (work/mg/manga.py), his real head out of a manga circle, Hinglish captions, beats from brief.md.
Usage:
  python3 work/mg/scene.py stills <dir> [t1 t2 ...]     (default: every 2.5 s)
  python3 work/mg/scene.py render <a> <b> <out.mp4>     (edit frames a..b-1, video only, crf 14)
"""
import os, sys, json, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw
sys.path.insert(0, "work/mg")
from manga import *  # noqa

FPS = 30
T_ME, T_MEME = 24.70, 85.19
WORDS = [w for w in json.load(open("work/words_edit.json")) if T_ME <= w["s"] < T_MEME]

# ---------------------------------------------------------------- captions
TR = {"दीदी": "Didi", "ने": "ne", "घर": "ghar", "के": "ke", "खाने": "khaane", "को": "ko", "कर": "kar", "दिया।": "diya.",
      "यह": "yeh", "खुद": "khud", "क्या": "kya", "समझती": "samajhti", "है?": "hai?", "हमारे": "hamare", "मां": "maa",
      "हाथ": "haath", "में": "mein", "है।": "hai.", "जरूरत": "Zaroorat", "से": "se", "ज्यादा": "zyada",
      "हो": "ho", "जाएगा।": "jaayega?", "वह": "Woh", "तो": "toh", "करोड़": "crore", "लोगों": "logon", "उसमें": "Usme",
      "बड़ी": "badi", "बात": "baat", "और": "aur", "तुम": "tum", "को?": "ko?", "ही": "hi", "मिलेंगे।": "milenge?",
      "फिर": "Phir", "पता": "pata", "चला": "chala", "जाने": "jaane", "बोलेगी": "bolegi", "बारे": "baare",
      "एक": "ek", "शब्द": "shabd", "अगर": "agar", "बोला": "bola", "है": "hai", "flaws।": "flaws.", "These": "these",
      "Healthier": "healthier", "but": "But"}
FIX = {("और", 43.00): "Aur", ("तो", 84.84): "toh...", ("हमारे", 28.83): "Hamare", ("यह", 27.31): "Yeh",
       ("है।", 42.68): "hai?"}
LISTS = [(48.40, 60.70), (67.45, 78.55)]


def hing(w):
    return FIX.get((w["w"], round(w["s"], 2)), TR.get(w["w"], w["w"]))


def build_chunks():
    """sentences (punctuation or a pause > 0.28 s), each split into nearly equal chunks of at most 4 words"""
    sents, cur = [], []
    for w in WORDS:
        if any(a <= w["s"] < b for a, b in LISTS):
            if cur:
                sents.append(cur); cur = []
            continue
        if cur and w["s"] - cur[-1]["e"] > 0.28:
            sents.append(cur); cur = []
        cur.append(dict(t=hing(w), s=w["s"], e=w["e"]))
        if cur[-1]["t"][-1] in ".?!":
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    chunks = []
    for st in sents:
        k = -(-len(st) // 4)
        size = -(-len(st) // k)
        for i in range(0, len(st), size):
            chunks.append(st[i:i + size])
    return chunks


CHUNKS = build_chunks()


def ease_out_back(x, s=1.7):
    x = np.clip(x, 0, 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def draw_caption(img, words, hot, y, size=62, scale=1.0):
    f = inter(int(size * scale), "ExtraBold")
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    sp = d0.textlength(" ", font=f)
    ws = [d0.textlength(w, font=f) for w in words]
    tw = sum(ws) + sp * (len(words) - 1)
    hh = int(f.size + 50)
    lay = Image.new("RGBA", (int(tw + 90), hh + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([9, 9, lay.size[0] - 1, hh + 9], fill=INK + (255,))
    d.rectangle([0, 0, lay.size[0] - 10, hh], fill=INK + (255,))
    d.rectangle([5, 5, lay.size[0] - 15, hh - 5], fill=PAPER + (255,))
    x = 38
    for i, (w, wl) in enumerate(zip(words, ws)):
        if i == hot:
            d.rectangle([x - 8, 13, x + wl + 8, hh - 13], fill=INK + (255,))
            d.text((x, 17), w, font=f, fill=PAPER + (255,))
        else:
            d.text((x, 17), w, font=f, fill=INK + (255,))
        x += wl + sp
    paste(img, lay, W / 2, y + hh / 2)


def caption(img, t, y):
    for i, ch in enumerate(CHUNKS):
        start = ch[0]["s"]
        nxt = CHUNKS[i + 1][0]["s"] if i + 1 < len(CHUNKS) else T_MEME
        end = min(nxt, ch[-1]["e"] + 0.6)
        if start - 0.04 <= t < end:
            hot = max(j for j, w in enumerate(ch) if w["s"] <= max(t, start))
            pop = ease_out_back((t - start + 0.04) / 0.16)
            draw_caption(img, [w["t"] for w in ch], hot, y, scale=0.9 + 0.1 * pop)
            return


# ---------------------------------------------------------------- media
_PIC = {}


def pic(name):
    if name not in _PIC:
        f = {"back": "raw/assets/pic_back_pose.jpg", "front": "raw/assets/pic_mirror_front.jpg",
             "dumbbell": "raw/assets/pic_dumbbell_side.jpg", "thali": "assets/codex/thali.png",
             "protein": "assets/codex/protein.png", "roti": "assets/codex/roti_stack.png"}[name]
        p = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
        if name == "back":
            M = cv2.getRotationMatrix2D((p.shape[1] / 2, p.shape[0] / 2), -9, 1.0)
            p = cv2.warpAffine(p, M, (p.shape[1], p.shape[0]), borderMode=cv2.BORDER_REFLECT)
        _PIC[name] = p
    return _PIC[name]


class Clip:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.pos, self.cache = -1, {}

    def at(self, ct):
        n = int(np.clip(round(ct * self.fps), 0, self.n - 1))
        if n in self.cache:
            return self.cache[n]
        if self.pos != n:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ok, f = self.cap.read()
        self.pos = n + 1
        f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
        self.cache = {n: f}
        return f


CLIPS = {"flex": Clip("raw/assets/broll_01.mp4"), "fly": Clip("raw/assets/broll_02.mp4")}
ROUGH = Clip("out/reel-12-rough-v3.mp4")


def me_frame(t):
    n = int(round(t * FPS))
    f = ROUGH.at(n / FPS)
    al = cv2.imread(f"work/matte_v3/{n:05d}.png", 0)
    if al is None:
        al = np.zeros(f.shape[:2], np.uint8)
    return f, al


# ---------------------------------------------------------------- page elements
_FOCUS = {}


def focus(key, *a, **k):
    if key not in _FOCUS:
        _FOCUS[key] = focus_lines(*a, **k)
    return _FOCUS[key]


TONE_TOP = dot_tone(H, W, np.tile(np.linspace(0.22, 0.0, H)[:, None], (1, W)).astype(np.float32), cell=8)


def wipe_mask(pm, t, t0, dur=0.12):
    """panel ink-in, right to left"""
    k = smooth((t - t0) / dur)
    x = int(1040 - k * 1010)
    v = pm.copy()
    v[:, :x] = False
    return v


def tone_panel(img, P, t, t0, seed, cx=540, cy=400, r_clear=300, n=150):
    pm = poly_mask(P)
    vis = wipe_mask(pm, t, t0)
    b = int(t * 10) % 3
    fl = focus((seed, b, cx, cy), H, W, cx, cy, r_clear=r_clear, n=n, seed=seed + b, width=(3, 12), length=(0.0, 0.45))
    img[vis] = PAPER
    img[vis & (TONE_TOP | fl)] = INK
    if t >= t0 + 0.12:
        stroke_poly(img, P, 8)
    return vis


def image_panel(img, P, src, t, t0, fx=0.5, fy=0.5, z0=1.03, zr=0.02, t_ref=None):
    """photo or clip frame in a panel; slow push (zoom z0 + zr per second since t_ref)"""
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pm = poly_mask(P)
    vis = wipe_mask(pm, t, t0)
    c = cover(src, x1 - x0, y1 - y0, fx=fx, fy=fy, zoom=z0 + zr * max(0, t - (t_ref if t_ref else t0)))
    full = np.zeros((H, W, 3), np.float32)
    full[y0:y1, x0:x1] = c
    img[vis] = full[vis]
    if t >= t0 + 0.12:
        stroke_poly(img, P, 8)


def slam(img, layer, cx, cy, t, t0, s0=1.8, dur=0.15):
    if t < t0:
        return
    k = ease_out_back((t - t0) / dur, 2.4)
    sc = s0 - (s0 - 1) * k
    L = layer.resize((max(1, int(layer.size[0] * sc)), max(1, int(layer.size[1] * sc))), Image.BICUBIC)
    paste(img, L, cx, cy)


def letters(img, txt, fnt, cx, cy, t, t0, rot=0, fill=INK, step=0.04):
    """shout that lands letter by letter"""
    if t < t0:
        return
    n = min(len(txt), int((t - t0) / step) + 1)
    paste(img, sfx(txt[:n] + " " * (len(txt) - n), fnt, rot=rot, fill=fill), cx, cy)


def star(img, cx, cy, s):
    pts = [(cx, cy - s), (cx + s * 0.22, cy - s * 0.22), (cx + s, cy), (cx + s * 0.22, cy + s * 0.22), (cx, cy + s),
           (cx - s * 0.22, cy + s * 0.22), (cx - s, cy), (cx - s * 0.22, cy - s * 0.22)]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = np.array(m) > 0
    e = cv2.dilate(m.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    img[e] = INK
    img[m] = PAPER


def anger(img, cx, cy, s, t, t0):
    """manga anger mark: four bulging red brackets, pops in and throbs"""
    if t < t0:
        return
    k = ease_out_back((t - t0) / 0.14, 2.6) * (1 + 0.08 * np.sin((t - t0) * 18))
    s = s * k
    lay = Image.new("RGBA", (int(s * 2.6) + 20, int(s * 2.6) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = lay.size[0] / 2
    for ang in (45, 135, 225, 315):
        a = np.deg2rad(ang)
        bx, by = c + np.cos(a) * s * 0.75, c + np.sin(a) * s * 0.75
        box_ = [bx - s * 0.55, by - s * 0.55, bx + s * 0.55, by + s * 0.55]
        st_ = ang + 135
        d.arc(box_, st_, st_ + 90, fill=INK + (255,), width=max(4, int(s * 0.34)))
        d.arc(box_, st_ + 8, st_ + 82, fill=RED + (255,), width=max(2, int(s * 0.2)))
    paste(img, lay, cx, cy)


def sweat(img, cx, cy, s, t, t0):
    if t < t0:
        return
    yy = cy + min(60, (t - t0) * 40)
    lay = Image.new("RGBA", (int(s * 1.4) + 12, int(s * 2) + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    w, h = lay.size
    pts = [(w / 2, 4)] + [(w / 2 + np.sin(a) * s * 0.6, h - 6 - s * 0.6 + np.cos(a) * s * 0.6 * -1)
                          for a in np.linspace(-np.pi / 2, 3 * np.pi / 2, 24)]
    d.polygon(pts, fill=PAPER + (255,), outline=INK + (255,), width=5)
    d.arc([w / 2 - s * 0.3, h - s * 1.1, w / 2 + s * 0.1, h - s * 0.5], 180, 260, fill=INK + (255,), width=3)
    paste(img, lay, cx, yy)


def crosshair(img, cx, cy, r, t, t0):
    if t < t0:
        return
    k = ease_out_back((t - t0) / 0.2)
    rr = int(r * (2.2 - 1.2 * k))
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=255, width=12)
    d.ellipse([cx - rr * 0.55, cy - rr * 0.55, cx + rr * 0.55, cy + rr * 0.55], outline=255, width=8)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.line([(cx + dx * rr * 0.35, cy + dy * rr * 0.35), (cx + dx * rr * 1.3, cy + dy * rr * 1.3)], fill=255, width=10)
    mm = np.array(m) > 0
    img[cv2.dilate(mm.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0] = PAPER
    img[mm] = RED


def card(img, title, rows, ticks, cx, cy, t, t0, w=800, rot=3, write_last=None):
    """spec card / checklist card that slams in from the right; rows get ink ticks at their times"""
    if t < t0 + 0.05:
        return
    k = ease_out_back((t - t0 - 0.05) / 0.22)
    hgt = 116 + 74 * len(rows)
    lay = Image.new("RGBA", (w + 40, hgt + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([22, 22, w + 22, hgt + 22], fill=INK + (255,))
    d.rectangle([10, 10, w + 10, hgt + 10], fill=INK + (255,))
    d.rectangle([16, 16, w + 4, hgt + 4], fill=PAPER + (255,))
    d.rectangle([16, 16, w + 4, 92], fill=INK + (255,))
    d.text((40, 24), title, font=font("anton", 46), fill=PAPER + (255,))
    for i, r in enumerate(rows):
        y = 112 + i * 74
        if write_last is not None and i == len(rows) - 1:
            txt = layer_text(r, font("anton", 54), fill=INK, pad=0)
            kk = smooth((t - write_last[0]) / (write_last[1] - write_last[0]))
            cw = int(txt.size[0] * kk)
            if cw > 0:
                lay.alpha_composite(txt.crop((0, 0, cw, txt.size[1])), (44, y + 12))
        else:
            d.text((44, y), r, font=font("anton", 54), fill=INK + (255,))
        d.line([(30, y + 70), (w - 10, y + 70)], fill=INK + (255,), width=2)
        if i < len(ticks) and ticks[i] is not None and t >= ticks[i]:
            d.line([(w - 80, y + 32), (w - 62, y + 54), (w - 28, y + 10)], fill=INK + (255,), width=9, joint="curve")
    lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    paste(img, lay, cx + (1 - k) * 90, cy)


def item_box(img, header, i, total, txt, ts, te, t, y=1020):
    """the current list item: counter tab + one big box, slams in from the left, red tick drawn on its last word"""
    k = ease_out_back((t - ts) / 0.22)
    dx = int((1 - k) * -90)
    hdr = layer_text(f"{header}  {i:02d}/{total}", font("anton", 36), fill=PAPER, pad=6)
    box(img, 50 + dx, y, 50 + dx + hdr.size[0] + 20, y + 60, border=0, shadow=0, fill=INK)
    paste(img, hdr, 60 + dx + hdr.size[0] / 2, y + 30)
    bw = 720
    lay = Image.new("RGBA", (bw + 14, 132), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([12, 12, bw + 12, 124], fill=INK + (255,))
    d.rectangle([0, 0, bw, 112], fill=INK + (255,))
    d.rectangle([6, 6, bw - 6, 106], fill=PAPER + (255,))
    d.text((22, 18), f"{i:02d}", font=font("dela", 60), fill=RED + (255,))
    size = 56
    while size > 30 and d.textlength(txt, font=font("anton", size)) > bw - 150 - 80:
        size -= 2
    fy = 22 + (56 - size) * 0.55
    d.text((150, fy), txt, font=font("anton", size), fill=INK + (255,))
    if t >= te:
        kk = smooth((t - te) / 0.10)
        p = [(bw - 66, 58), (bw - 48, 84), (bw - 16, 28)]
        seg = [p[0], (p[0][0] + (p[1][0] - p[0][0]) * min(1, kk * 2), p[0][1] + (p[1][1] - p[0][1]) * min(1, kk * 2))]
        if kk > 0.5:
            f2 = (kk - 0.5) * 2
            seg = [p[0], p[1], (p[1][0] + (p[2][0] - p[1][0]) * f2, p[1][1] + (p[2][1] - p[1][1]) * f2)]
        d.line(seg, fill=RED + (255,), width=11, joint="curve")
    paste(img, lay, 50 + bw / 2 + 7 + dx, y + 60 + 66)


def vertical_word(img, word, x0, x1, y0, y1, t, t0, seed):
    """tall side panel: focus lines + a vertical stack of slammed letters (Dela)"""
    P = [(x0, y0), (x1, y0), (x1, y1 - 20), (x0, y1)]
    tone_panel(img, P, t, t0, seed, cx=(x0 + x1) // 2, cy=(y0 + y1) // 2, r_clear=60, n=90)
    if t < t0 + 0.08:
        return
    n = len(word)
    size = int(min((x1 - x0) * 0.75, (y1 - y0) / n * 0.82))
    for i, ch in enumerate(word):
        tt = t0 + 0.08 + 0.05 * i
        cy = y0 + (i + 0.5) * (y1 - y0) / n
        slam(img, sfx(ch, font("dela", size), rot=(-6 if i % 2 else 5)), (x0 + x1) / 2, cy, t, tt, s0=1.6, dur=0.12)


# ---------------------------------------------------------------- lists
PROTEIN = [("FASTER MUSCLE GROWTH", 48.44, 49.46), ("REDUCED HUNGER", 49.58, 50.36),
           ("LOSING FAT, NOT MUSCLE", 50.58, 51.96), ("LESS MUSCLE LOSS AS YOU AGE", 52.12, 53.06),
           ("QUICKER RECOVERY", 53.28, 54.46), ("MORE CALORIES BURNED", 54.58, 55.66),
           ("FEWER SUGAR SPIKES", 55.78, 57.02), ("STRONGER BONES", 57.13, 57.69),
           ("BETTER IMMUNITY, FASTER HEALING", 57.80, 58.96), ("HEALTHIER HAIR, SKIN, NAILS", 59.09, 60.62)]
GYM = [("MORE CONFIDENCE", 67.50, 68.46), ("BETTER LOOKS", 68.60, 69.30), ("MORE MUSCLE & STRENGTH", 69.53, 70.28),
       ("LONGER LIFESPAN", 70.40, 71.08), ("BETTER BLOOD SUGAR CONTROL", 71.22, 72.04), ("STRONGER BONES", 72.19, 72.72),
       ("FASTER METABOLISM", 72.84, 73.47), ("EASIER FAT LOSS", 73.56, 74.16), ("LESS BACK & JOINT PAIN", 74.27, 75.09),
       ("STRONG & INDEPENDENT AS YOU AGE", 75.36, 76.47), ("BETTER MOOD, LESS ANXIETY", 76.60, 77.52),
       ("DEEPER SLEEP", 77.80, 78.47)]
# photo per stretch of a list: (start, kind, name, panel right edge x1, fx, fy, clip mapping)
# every physique shot keeps his face in frame (user rule)
PH_Y0, PH_Y1 = 130, 1110
MEDIA = [
    (45.64, "img", "protein", 1040, 0.5, 0.5, None),
    (48.44, "img", "back", 1040, 0.5, 0.47, None),
    (50.58, "img", "front", 800, 0.5, 0.47, None),
    (54.58, "img", "dumbbell", 680, 0.5, 0.40, None),
    (57.13, "clip", "flex", 800, 0.5, 0.36, (0.0, 0.30, 0.95)),      # clip time = 0 + 0.30*(t-t0), capped at 0.95 s
    (60.70, None, None, None, 0, 0, None),
    (63.00, "clip", "fly", 800, 0.42, 0.45, (3.0, 1.0, 8.9)),
    (67.50, "clip", "flex", 800, 0.5, 0.36, (0.0, 0.85, 0.95)),
    (68.60, "img", "front", 800, 0.5, 0.47, None),
    (69.53, "img", "dumbbell", 680, 0.5, 0.40, None),
    (70.40, "clip", "fly", 800, 0.42, 0.45, (0.25, 1.0, 8.9)),
    (72.84, "img", "back", 1040, 0.5, 0.47, None),
    (75.36, "clip", "flex", 800, 0.5, 0.36, (0.0, 0.30, 0.95)),
    (78.55, None, None, None, 0, 0, None),
]


def media_at(t):
    cur = None
    for m in MEDIA:
        if m[0] <= t:
            cur = m
    return cur


def media_panel(img, t):
    m = media_at(t)
    if m is None or m[1] is None:
        return None
    t0, kind, name, x1, fx, fy, cm = m
    P = [(40, PH_Y0), (x1, PH_Y0), (x1, PH_Y1 - 10), (40, PH_Y1 + 10)]
    if kind == "img":
        src = pic(name)
    else:
        c0, rate, cap = cm
        src = CLIPS[name].at(min(cap, c0 + rate * (t - t0)))
    image_panel(img, P, src, t, t0, fx=fx, fy=fy, z0=1.02, zr=0.02)
    return x1, t0


# ---------------------------------------------------------------- circle states
SA = dict(cx=540, cy=1450, r=320, scale=0.72, head_top=880)     # big, bottom centre
SB = dict(cx=830, cy=1500, r=195, scale=0.45, head_top=1215)    # small, bottom right (lists, photos)
SD = dict(cx=540, cy=1330, r=400, scale=0.92, head_top=600)     # final push in
KEYS = [(24.70, SA), (45.30, SA), (45.62, SB), (60.72, SB), (61.00, SA), (62.80, SA), (62.98, SB), (78.55, SB),
        (78.80, SA), (81.70, SA), (84.80, SD)]


def circle_state(t):
    if t <= KEYS[0][0]:
        return dict(KEYS[0][1])
    for (ta, a), (tb, b) in zip(KEYS[:-1], KEYS[1:]):
        if ta <= t < tb:
            k = smooth((t - ta) / (tb - ta))
            return {key: a[key] + (b[key] - a[key]) * k for key in a}
    return dict(KEYS[-1][1])


# ---------------------------------------------------------------- the beats
P_TOP = [(40, 130), (1040, 130), (1040, 610), (40, 670)]


def beats(img, t):
    """everything above the circle; returns the caption y (or None to hide captions)"""
    cap_y = 730
    if t < 34.38:                                              # thali: target, maa ke haath, stamps
        P = [(40, 130), (1040, 130), (1040, 620), (40, 680)]
        if t >= 25.17:
            image_panel(img, P, pic("thali"), t, 25.17, z0=1.05, zr=0.015)
        crosshair(img, 520, 400, 120, t, 26.43) if 26.43 <= t < 28.83 else None
        if 28.83 <= t:
            for i, (x, y, s) in enumerate([(150, 220, 46), (930, 250, 38), (880, 600, 52), (210, 600, 30)]):
                if t >= 28.83 + 0.07 * i:
                    star(img, x, y, s * (1 + 0.12 * np.sin((t - 28.83) * 9 + i)))
        if 27.83 <= t < 28.83:
            letters(img, "KYA SAMAJHTI HAI?!", font("bangers", 92), 540, 560, t, 27.83, rot=-5)
        if 29.27 <= t < 31.49:
            slam(img, sfx("MAA KE HAATH KA KHAANA", font("anton", 64), rot=-3), 540, 600, t, 29.27, s0=1.4)
        slam(img, sfx("PERFECT", font("dela", 74), rot=-10, fill=RED), 300, 280, t, 31.73)
        slam(img, sfx("FLAWLESS", font("dela", 74), rot=8, fill=RED), 770, 400, t, 32.63)
        slam(img, sfx("ZERO FLAWS", font("dela", 96), rot=-5, fill=RED), 540, 580, t, 33.43)
    elif t < 37.38:                                            # zyada carbs: roti stack grows
        P = [(40, 130), (1040, 130), (1040, 620), (40, 680)]
        tone_panel(img, P, t, 34.38, 41, cx=540, cy=400, r_clear=200)
        if os.path.exists("assets/codex/roti_stack.png"):
            rs = pic("roti")[520:1480, 60:964]
            h = 470
            wdt = int(rs.shape[1] * h / rs.shape[0])
            r = cv2.resize(rs, (wdt, h), interpolation=cv2.INTER_AREA).astype(np.float32)
            k = smooth((t - 35.26) / 1.2)                    # grows from "carbs" to "jaayega"
            show = int(h * (0.45 + 0.55 * k))
            x0 = 540 - wdt // 2
            y1 = 655
            sub = r[h - show:]
            box(img, x0 - 8, y1 - show - 8, x0 + wdt + 8, y1 + 8, border=6, shadow=10)
            img[y1 - show:y1, x0:x0 + wdt] = sub
        letters(img, "CARBS!!", font("dela", 90), 840, 250, t, 35.26, rot=10)
    elif t < 43.00:                                            # spec card
        tone_panel(img, P_TOP, t, 37.38, 5, cx=540, cy=390, r_clear=330)
        card(img, "INDIAN GHAR KA KHAANA  /  SPECS", ["ROTI", "SABZI", "KABHI KABHI CHUTNEY", "TYPE 2 DIABETES"],
             [37.50, 37.58, 37.66, None], 540, 380, t, 37.38, w=760, write_last=(37.40, 38.25))
        if t >= 39.48:
            letters(img, "10 CRORE USERS!", font("bangers", 64), 250, 640, t, 39.48, rot=-8, step=0.035)
        slam(img, sfx("STANDARD\nFEATURE", font("dela", 50), rot=-12, fill=RED), 820, 575, t, 40.76)
    elif t < 45.62:                                            # balanced meal obsession
        P = [(40, 130), (1040, 130), (1040, 620), (40, 680)]
        tone_panel(img, P, t, 43.00, 61, cx=540, cy=400, r_clear=220)
        k = ease_out_back((t - 43.10) / 0.25)
        R = int(170 * k)
        if R > 5:
            cx, cy = 330, 400
            yy, xx = np.mgrid[0:H, 0:W]
            dd = np.hypot(xx - cx, yy - cy)
            ang = (np.degrees(np.arctan2(yy - cy, xx - cx)) + 360) % 360
            disc = dd <= R
            img[(dd <= R + 14) & ~disc] = INK
            img[disc] = PAPER
            tone_q = [dot_tone(H, W, np.full((H, W), c, np.float32), cell=8) for c in (0.15, 0.35, 0.55)]
            for qi, (a0, a1) in enumerate(((0, 90), (90, 180), (180, 270))):
                img[disc & (ang >= a0) & (ang < a1) & tone_q[qi]] = INK
            for a in (0, 90, 180, 270):
                ex, ey = cx + np.cos(np.deg2rad(a)) * R, cy + np.sin(np.deg2rad(a)) * R
                m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).line([(cx, cy), (ex, ey)], fill=255, width=7)
                img[np.array(m) > 0] = INK
            if t > 43.4:
                for txt, a in (("PROTEIN", 45), ("CARBS", 135), ("FIBRE", 225), ("FATS", 315)):
                    lx, ly = cx + np.cos(np.deg2rad(a)) * R * 0.55, cy + np.sin(np.deg2rad(a)) * R * 0.55
                    lt = layer_text(txt, font("anton", 30), fill=INK, stroke=5, stroke_fill=PAPER, pad=6)
                    paste(img, lt, lx, ly)
        letters(img, "OBSESSION?", font("dela", 66), 730, 470, t, 44.44, rot=-8)
    elif t < 48.44:                                            # protein? + protein spread
        media_panel(img, t)
        letters(img, "PROTEIN?", font("dela", 130), 540, 330, t, 45.70, rot=-6, step=0.05)
        if t >= 46.42:
            slam(img, sfx("MAX TO MAX?", font("bangers", 64), rot=5), 780, 900, t, 46.42)
        cap_y = 1150
    elif t < 60.70:                                            # protein list
        r = media_panel(img, t)
        cur = [it for it in PROTEIN if it[1] <= t][-1]
        i = PROTEIN.index(cur) + 1
        if r and r[0] <= 860:
            vertical_word(img, "PROTEIN", r[0] + 24, 1040, PH_Y0, 1000, t, r[1], 71)
        item_box(img, "PROTEIN BENEFITS", i, 10, cur[0], cur[1], cur[2], t)
        cap_y = None
    elif t < 63.00:                                            # worth it?
        tone_panel(img, P_TOP, t, 60.80, 81, cx=540, cy=380, r_clear=260)
        card(img, "PROTEIN BENEFITS", ["10 / 10 UNLOCKED"], [60.95], 540, 330, t, 60.80, w=640, rot=-2)
        letters(img, "WORTH IT?", font("dela", 110), 560, 540, t, 62.36, rot=-5, step=0.05)
        sweat(img, 790, 940, 34, t, 61.10)
    elif t < 67.45:                                            # gym bolegi
        r = media_panel(img, t)
        if r:
            vertical_word(img, "GYM?!", r[0] + 24, 1040, PH_Y0, 1000, t, 65.70, 91)
        cap_y = 1150
    elif t < 78.55:                                            # gym list
        r = media_panel(img, t)
        cur = [it for it in GYM if it[1] <= t][-1]
        i = GYM.index(cur) + 1
        if r and r[0] <= 860:
            vertical_word(img, "GYM", r[0] + 24, 1040, PH_Y0, 1000, t, max(67.50, r[1]), 93)
        item_box(img, "GYM BENEFITS", i, 12, cur[0], cur[1], cur[2], t)
        cap_y = None
    elif t < 81.70:                                            # not worth it
        tone_panel(img, P_TOP, t, 78.73, 101, cx=540, cy=380, r_clear=260)
        card(img, "GYM BENEFITS", ["12 / 12 UNLOCKED"], [78.90], 540, 330, t, 78.73, w=640, rot=-2)
        slam(img, sfx("NOT WORTH IT", font("dela", 92), rot=-8, fill=RED), 560, 540, t, 80.23)
    else:                                                      # ek aur shabd... toh
        P = [(40, 130), (1040, 130), (1040, 460), (40, 500)]
        image_panel(img, P, pic("thali"), t, 81.74, z0=1.05, zr=0.03)
        anger(img, 170, 760, 80, t, 83.56)
        anger(img, 150, 1150, 70, t, 84.16)
        cap_y = 520
    return cap_y


def page_darken(img, t):
    """the last line: screentone creeps over the paper (not over the photos)"""
    if t < 82.0:
        return
    k = smooth((t - 82.0) / 2.8)
    cov = np.full((H, W), 0.08 + 0.4 * k, np.float32)
    m = dot_tone(H, W, cov, cell=10)
    paper_px = (np.abs(img - np.array(PAPER, np.float32)).sum(2) < 40)
    img[m & paper_px] = INK


def shake(t):
    dx = dy = 0.0
    for h, amp in ((26.43, 14), (31.73, 10), (32.63, 10), (33.43, 22), (40.76, 18), (48.44, 10), (80.23, 20),
                   (84.84, 30)):
        if t >= h:
            e = np.exp(-(t - h) / 0.07) * amp
            dx += e * np.sin(97 * (t - h) + h)
            dy += e * np.cos(83 * (t - h) + 2 * h)
    return dx, dy


INVERT = [(33.43, 2), (84.84, 2)]       # impact frames: paper and ink flip


def frame(t):
    if t < T_ME or t >= T_MEME:
        return ROUGH.at(t)
    img = paper(11)
    cap_y = beats(img, t)
    page_darken(img, t)
    me, al = me_frame(t)
    s = circle_state(t)
    face_circle(img, me, al, int(s["cx"]), int(s["cy"]), int(s["r"]), s["scale"], s["head_top"],
                seed=7 + int(t * 10) % 3)
    if t >= 81.70:
        anger(img, s["cx"] + s["r"] * 0.62, s["head_top"] + 90, 85, t, 82.68)
    if cap_y is not None:
        caption(img, t, cap_y)
    dx, dy = shake(t)
    if dx or dy:
        img = cv2.warpAffine(img, np.float32([[1, 0, dx], [0, 1, dy]]), (W, H), borderMode=cv2.BORDER_REPLICATE)
    out = np.clip(img, 0, 255).astype(np.uint8)
    for t0, nf in INVERT:
        if t0 <= t < t0 + nf / FPS:
            out = 255 - out
    return out


def label(im, t):
    im = im.copy()
    cv2.rectangle(im, (0, 0), (300, 90), (0, 0, 0), -1)
    cv2.putText(im, f"{t:5.1f}s", (14, 66), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (255, 255, 0), 4)
    return im


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        d = sys.argv[2]
        os.makedirs(d, exist_ok=True)
        ts = [float(x) for x in sys.argv[3:]] or [i * 2.5 for i in range(int(92.0 / 2.5) + 1)]
        for t in ts:
            im = frame(t)
            Image.fromarray(im).save(f"{d}/t_{t:05.1f}.jpg", quality=90)
        print("stills", len(ts))
    elif mode == "render":
        a, b, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
                                "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                                "-pix_fmt", "yuv420p", "-g", "30", out], stdin=subprocess.PIPE)
        for n in range(a, b):
            enc.stdin.write(frame(n / FPS).tobytes())
            if n % 60 == 0:
                print(n, flush=True)
        enc.stdin.close()
        enc.wait()
        print("done", out)
