"""reel-12 manga motion sample: two beats from rough cut v3, timed to the spoken words.

A  37.0-42.9  "Type 2 diabetes. Woh toh India mein 10 crore logon ko hai. Standard feature hai. Usme kya badi baat hai."
B  45.2-52.2  "Protein khaane se max to max kya hi benefits milenge. Faster muscle growth, reduced hunger, losing fat..."
Usage: python3 work/mg/sample.py [half]   -> work/mg/sample/frames, out/reel-12-mg-sample.mp4 (half = 540x960 draft)
Times are edit times of rough v3 (Scribe words, work/check + work/check3).
"""
import os, sys, subprocess
import numpy as np
import cv2
from PIL import Image, ImageDraw
sys.path.insert(0, "work/mg")
from manga import *  # noqa

FPS = 30
HALF = "half" in sys.argv
RANGES = [(37.0, 42.9), (45.2, 52.2)]

# ---------------- captions (Hinglish, Latin script), chunk = list of (word, start) ----------------
CAPS = [
    [("Type", 37.38), ("2", 37.72), ("diabetes.", 37.78)],
    [("Woh", 38.80), ("toh", 38.92), ("India", 39.04), ("mein", 39.34)],
    [("10", 39.48), ("crore", 39.76), ("logon", 40.06), ("ko", 40.32), ("hai.", 40.44)],
    [("Standard", 40.76), ("feature", 41.18), ("hai.", 41.52)],
    [("Usme", 41.82), ("kya", 42.10), ("badi", 42.24), ("baat", 42.46), ("hai.", 42.66)],
    [("Protein", 45.64), ("khaane", 46.04), ("se", 46.28)],
    [("max", 46.42), ("to", 46.64), ("max", 46.74), ("kya", 47.02), ("hi", 47.18)],
    [("benefits", 47.32), ("milenge.", 47.76)],
]
CAP_END = {4: 43.0, 7: 48.40}       # last chunk of each beat stays until here

# protein list (the list item is the caption while the list runs)
ITEMS = [("FASTER MUSCLE GROWTH", 48.46, 49.48, "back"),
         ("REDUCED HUNGER", 49.60, 50.38, "back"),
         ("LOSING FAT, NOT MUSCLE", 50.58, 52.00, "front")]


def ease_out_back(x, s=1.7):
    x = np.clip(x, 0, 1) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def shake(t, hits, amp=18, tau=0.07):
    dx = dy = 0.0
    for h in hits:
        if t >= h:
            e = np.exp(-(t - h) / tau) * amp
            dx += e * np.sin(97 * (t - h) + h)
            dy += e * np.cos(83 * (t - h) + 2 * h)
    return dx, dy


# ---------------- assets ----------------
PIC = {}


def pic(name):
    if name not in PIC:
        f = {"back": "raw/assets/pic_back_pose.jpg", "front": "raw/assets/pic_mirror_front.jpg"}[name]
        p = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
        if name == "back":
            M = cv2.getRotationMatrix2D((p.shape[1] / 2, p.shape[0] / 2), -9, 1.0)
            p = cv2.warpAffine(p, M, (p.shape[1], p.shape[0]), borderMode=cv2.BORDER_REFLECT)
        PIC[name] = p
    return PIC[name]


FOCUS = {}


def focus(key, *a, **k):
    if key not in FOCUS:
        FOCUS[key] = focus_lines(*a, **k)
    return FOCUS[key]


TONE_TOP = dot_tone(H, W, np.tile(np.linspace(0.22, 0.0, H)[:, None], (1, W)).astype(np.float32), cell=8)


def video_frame(t):
    n = int(round(t * FPS))
    cap = video_frame.cap
    if video_frame.pos != n:
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, f = cap.read()
    video_frame.pos = n + 1
    al = cv2.imread(f"work/matte_v3/{n:05d}.png", 0)
    return cv2.cvtColor(f, cv2.COLOR_BGR2RGB), al


video_frame.cap = cv2.VideoCapture("out/reel-12-rough-v3.mp4")
video_frame.pos = -1


# ---------------- pieces ----------------
def caption(img, t):
    for i, ch in enumerate(CAPS):
        start = ch[0][1]
        nxt = CAPS[i + 1][0][1] if i + 1 < len(CAPS) else 99
        end = CAP_END.get(i, nxt)
        if start - 0.05 <= t < end:
            hot = max(j for j, (_, s) in enumerate(ch) if s <= max(t, start))
            y = 730 if t < 44 else 940
            pop = ease_out_back((t - start + 0.05) / 0.16)
            draw_caption(img, [w for w, _ in ch], hot, y, scale=0.9 + 0.1 * pop)
            return


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


def panel_wipe(t, t0, dur=0.12):
    """manga panel ink-in, right to left: returns the x from which the panel is visible"""
    k = smooth((t - t0) / dur)
    return int(1040 - k * 1000)


def spec_card(img, t, P):
    t0 = 37.38
    if t < t0:
        return
    pm = poly_mask(P)
    xvis = panel_wipe(t, t0)
    vis = pm.copy()
    vis[:, :xvis] = False
    fl = focus(("A", int(t * 10) % 3), H, W, 540, 390, r_clear=330, n=150, seed=5 + int(t * 10) % 3, width=(3, 12),
               length=(0.0, 0.45))
    img[vis] = PAPER
    img[vis & (TONE_TOP | fl)] = INK
    # card slams in from the right
    k = ease_out_back((t - t0 - 0.05) / 0.22)
    if t > t0 + 0.05:
        lay = Image.new("RGBA", (800, 450), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle([22, 22, 782, 432], fill=INK + (255,))
        d.rectangle([10, 10, 770, 420], fill=INK + (255,))
        d.rectangle([16, 16, 764, 414], fill=PAPER + (255,))
        d.rectangle([16, 16, 764, 92], fill=INK + (255,))
        d.text((40, 24), "INDIAN GHAR KA KHAANA  /  SPECS", font=font("anton", 46), fill=PAPER + (255,))
        rows = ["ROTI", "SABZI", "KABHI KABHI CHUTNEY"]
        for i, r in enumerate(rows):
            y = 112 + i * 74
            d.text((44, y), r, font=font("anton", 54), fill=INK + (255,))
            d.line([(30, y + 70), (750, y + 70)], fill=INK + (255,), width=2)
            tt = t0 + 0.12 + 0.08 * i
            if t > tt:
                d.line([(690, y + 32), (708, y + 54), (742, y + 10)], fill=INK + (255,), width=9, joint="curve")
        # "TYPE 2 DIABETES" writes on (wipe) from "Type" to the end of "diabetes"
        y = 112 + 3 * 74
        txt = layer_text("TYPE 2 DIABETES", font("anton", 54), fill=INK, pad=0)
        kk = smooth((t - 37.40) / 0.85)
        cw = int(txt.size[0] * kk)
        if cw > 0:
            lay.alpha_composite(txt.crop((0, 0, cw, txt.size[1])), (44, y + 12))
        d.line([(30, y + 70), (750, y + 70)], fill=INK + (255,), width=2)
        lay = lay.rotate(3, resample=Image.BICUBIC, expand=True)
        paste(img, lay, 540 + (1 - k) * 90, 380)
    stroke_poly(img, P, 8)
    # 10 crore users: letters slam in on "10"
    if t >= 39.48:
        txt = "10 CRORE USERS!"
        n = min(len(txt), int((t - 39.48) / 0.035) + 1)
        k = ease_out_back((t - 39.48 - 0.035 * (n - 1)) / 0.12)
        bd = sfx(txt[:n] + " " * (len(txt) - n), font("bangers", 64), rot=-8)
        paste(img, bd, 250, 640)
    # stamp slams on "Standard"
    if t >= 40.76:
        k = ease_out_back((t - 40.76) / 0.15, 2.4)
        sc = 1.8 - 0.8 * k
        st = sfx("STANDARD\nFEATURE", font("dela", 50), rot=-12, fill=RED)
        st = st.resize((max(1, int(st.size[0] * sc)), max(1, int(st.size[1] * sc))), Image.BICUBIC)
        paste(img, st, 820, 575)


def protein_shout(img, t, P):
    t0 = 45.64
    if not (t0 <= t < 48.44):
        return
    pm = poly_mask(P)
    xvis = panel_wipe(t, t0)
    vis = pm.copy()
    vis[:, :xvis] = False
    fl = focus(("B", int(t * 10) % 3), H, W, 540, 470, r_clear=230, n=190, seed=11 + int(t * 10) % 3,
               width=(3, 13), length=(0.0, 0.55))
    img[vis] = PAPER
    img[vis & (TONE_TOP | fl)] = INK
    stroke_poly(img, P, 8)
    word = "PROTEIN?"
    n = min(len(word), int((t - t0 - 0.06) / 0.05) + 1)
    if t > t0 + 0.06:
        sh = sfx(word[:n] + " " * (len(word) - n), font("dela", 150), rot=-6)
        paste(img, sh, 540, 470)
    if t >= 47.32:          # "benefits" lands: small shout
        k = ease_out_back((t - 47.32) / 0.14)
        b = sfx("MAX TO MAX?", font("bangers", int(40 + 24 * k)), rot=5)
        paste(img, b, 760, 760)


def protein_list(img, t, P):
    if t < 48.44:
        return
    # photo panel: inks in on "Faster", swaps on "losing"
    cur = [it for it in ITEMS if it[1] <= t + 0.001][-1] if t >= ITEMS[0][1] else ITEMS[0]
    t_sw = max(it[1] for it in ITEMS if it[1] <= max(t, ITEMS[0][1]) and (it[3] != ITEMS[0][3] or it is ITEMS[0]))
    pm = poly_mask(P)
    xvis = panel_wipe(t, t_sw)
    zoom = 1.10 + 0.03 * (t - t_sw)
    crop = cover(pic(cur[3]), 1000, 760, fx=0.52, fy=0.45 if cur[3] == "back" else 0.62, zoom=zoom)
    full = np.zeros((H, W, 3), np.float32)
    full[130:890, 40:1040] = crop
    if t_sw != ITEMS[0][1] and t < t_sw + 0.12:          # previous photo still under the wipe
        prev = cover(pic(ITEMS[0][3]), 1000, 760, fx=0.52, fy=0.45, zoom=1.10 + 0.03 * (t_sw - ITEMS[0][1]))
        pf = np.zeros((H, W, 3), np.float32)
        pf[130:890, 40:1040] = prev
        img[pm] = pf[pm]
    vis = pm.copy()
    vis[:, :xvis] = False
    img[vis] = full[vis]
    stroke_poly(img, P, 8)
    # header tab
    done = sum(1 for it in ITEMS if it[1] <= t)
    box(img, 50, 820, 440, 886, border=0, shadow=0, fill=INK)
    hdr = layer_text(f"PROTEIN BENEFITS  {done}/10", font("anton", 40), fill=PAPER, pad=8)
    paste(img, hdr, 245, 853)
    # items stack below
    for i, (txt, ts, te, _) in enumerate(ITEMS):
        if t < ts:
            continue
        y0 = 920 + i * 112
        k = ease_out_back((t - ts) / 0.22)
        dx = int((1 - k) * 70)
        lay = Image.new("RGBA", (640, 120), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rectangle([10, 10, 620, 106], fill=INK + (255,))
        d.rectangle([0, 0, 610, 96], fill=INK + (255,))
        d.rectangle([5, 5, 605, 91], fill=PAPER + (255,))
        d.text((18, 14), f"0{i + 1}", font=font("dela", 52), fill=RED + (255,))
        d.text((118, 18), txt, font=font("anton", 48), fill=INK + (255,))
        if t >= te:
            kk = smooth((t - te) / 0.10)
            pts = [(556, 52), (571, 74), (598, 26)]
            seg = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * min(1, kk * 2), pts[0][1] + (pts[1][1] - pts[0][1]) * min(1, kk * 2))]
            if kk > 0.5:
                f2 = (kk - 0.5) * 2
                seg = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * f2, pts[1][1] + (pts[2][1] - pts[1][1]) * f2)]
            d.line(seg, fill=RED + (255,), width=10, joint="curve")
        paste(img, lay, 50 + 320 + dx, y0 + 60)


# ---------------- circle states ----------------
CA = dict(cx=540, cy=1450, r=320, scale=0.72, head_top=880)
CB = dict(cx=800, cy=1575, r=235, scale=0.53, head_top=1225)


def circle_state(t):
    k = smooth((t - 45.28) / 0.36)
    return {key: CA[key] + (CB[key] - CA[key]) * k for key in CA}


def frame(t):
    img = paper(11)
    P_A = [(40, 130), (1040, 130), (1040, 610), (40, 670)]
    P_B = [(40, 130), (1040, 130), (1040, 860), (40, 900)]
    if t < 44:
        spec_card(img, t, P_A)
    else:
        protein_shout(img, t, P_B)
        protein_list(img, t, [(40, 130), (1040, 130), (1040, 870), (40, 890)])
    caption(img, t)
    me, al = video_frame(t)
    s = circle_state(t)
    face_circle(img, me, al, int(s["cx"]), int(s["cy"]), int(s["r"]), s["scale"], s["head_top"],
                seed=7 + int(t * 10) % 3)
    dx, dy = shake(t, [40.76, 48.46, 50.58])
    if dx or dy:
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    return np.clip(img, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    os.makedirs("work/mg/sample", exist_ok=True)
    parts = []
    for k, (a, b) in enumerate(RANGES):
        n0, n1 = int(round(a * FPS)), int(round(b * FPS))
        size = "540x960" if HALF else "1080x1920"
        vid = f"work/mg/sample/part{k}.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920",
                                "-r", "30", "-i", "-", "-ss", f"{n0 / FPS:.4f}", "-t", f"{(n1 - n0) / FPS:.4f}", "-i",
                                "work/audio/rough_v3.wav", "-map", "0:v", "-map", "1:a", "-vf", f"scale={size}",
                                "-c:v", "libx264", "-crf", "24" if HALF else "16", "-preset", "veryfast",
                                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", vid],
                               stdin=subprocess.PIPE)
        for n in range(n0, n1):
            enc.stdin.write(frame(n / FPS).tobytes())
            if n % 30 == 0:
                print(k, n, flush=True)
        enc.stdin.close(); enc.wait()
        parts.append(vid)
    with open("work/mg/sample/list.txt", "w") as fh:
        fh.writelines(f"file '{os.path.basename(p)}'\n" for p in parts)
    out = "out/reel-12-mg-sample.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/mg/sample/list.txt",
                    "-c", "copy", out], check=True)
    print("->", out)
