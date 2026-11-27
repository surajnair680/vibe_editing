"""reel-14 v2 scene: the reference look (reanimate/spec.md) on the approved rough cut.
  python3 work/build2/scene2.py still 27.5 46.5 ...        -> out/stills/v2/s_<t>.png
  python3 work/build2/scene2.py render <a> <b> <out.mp4>   -> picture only, frames [a, b)
His takes: cut out (work/matte/NNNNN.png, rembg u2net_human_seg) onto the dark red background (grey section for the
"balance / class / A" lines). Titles sit behind him, captions build word by word above him. Clips and photos are
real and full frame, held at least 0.8 s. Run from the project folder."""
import json, re, subprocess, sys, os, math
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, "work/build2"); sys.path.insert(0, "work/build")
import fx2
from fx2 import W, H, FPS
sys.path.insert(0, "/home/user/vibe_editing/projects/reel-14/vibe")
import motion_kit                     # brand grain (cached noise bank)
import fx as fx1                     # v1 clip loader (Clip.frame)

WORDS = json.load(open("work/words_edit.json"))
CUT_LEN = json.load(open("work/cut_plan.json"))["length"]
LEN = CUT_LEN + 0.9                  # hold the ending title a little longer
HIS = 27.30
LAST_F = int(round(CUT_LEN * FPS)) - 1


def wd(text, near):
    key = re.sub(r"[^a-z']", "", text.lower())
    c = [w for w in WORDS if re.sub(r"[^a-z']", "", w["w"].lower()) == key]
    return min(c, key=lambda w: abs(w["s"] - near))


def s(text, near): return wd(text, near)["s"]
def fr(t): return int(round(t * FPS))


# ---------------------------------------------------------------- scenes (later entries win)
INS = []      # (t0, t1, kind, params): full-frame inserts and celebrity scenes
def ins(t0, t1, kind, **p): INS.append((t0, t1, kind, p))

ins(s("a", 28.75), s("You", 30.07), "photo", path="assets/photos/me_physique_mirror.jpg")
ins(s("by", 44.0), s("Successful", 44.9), "cutout", path="assets/photos/celebrity_jobs.jpg", height=1250)
ins(s("outliers", 46.0), s("belong", 47.6), "frame", path="assets/photos/celebrity_arnold.jpg", width=1000, yc=0.55,
    title="OUTLIERS")
ins(s("belong", 47.6), s("Which", 48.95) - 0.1, "frame", path="assets/photos/celebrity_musk.jpg", width=700, yc=0.56)
ins(s("Pain", 52.8), s("discomfort", 53.4), "clip", path="raw/vid_1111c.mp4", src=4.3, zoom=1.2, cx=0.0, cy=1.0, title="PAIN")
ins(s("discomfort", 53.4), s("than", 54.9) + 0.6, "clip", path="raw/pullups.mp4", src=7.7, title="DISCOMFORT", title_until=54.3)
ins(s("need", 69.9) + 0.06, s("But", 71.0), "clip", path="raw/vid_1111b.mp4", src=0.7, zoom=1.04, zoom1=1.10)   # BALANCE holds 0.8 s
ins(s("exact", 74.9), s("That", 76.87), "clip", path="raw/vid_1111.mp4", src=5.0, zoom=1.15, zoom1=1.18, cx=0.62, cy=0.55,
    title="KEEP GOING", title_from=s("keep", 76.2))
ins(s("is", 77.75), s("grow", 78.6) + 0.25, "clip", path="raw/flex_p1.mp4", src=7.2, zoom=1.06, zoom1=1.10, cy=0.3)
ins(s("adapt", 82.2), s("And", 83.66), "photo", path="assets/photos/me_gym_dumbbell.jpg")
ins(s("Outliers", 87.9), s("and", 89.29), "clip", path="raw/flex_p1.mp4", src=10.9, zoom=1.04, zoom1=1.08, cy=0.3,
    title="OUTLIERS")
ins(s("were", 99.97), s("normal", 101.0), "photo", path="assets/photos/me_physique_front.jpg")

# titles behind him on his cut-out scenes: (text, t0, t1, color, y, size or None = fit)
TIT = [
    ("NORMAL", s("Normal", 27.4), s("a", 28.75), fx2.OFFWHITE, 400, None),
    ("OBSESSED", s("obsessed", 35.4), s("abnormal", 36.2), fx2.RED, 400, None),
    ("ABNORMAL", s("abnormal", 36.2), 37.9, fx2.OFFWHITE, 400, None),
    ("ABNORMAL", s("Success", 42.6) + 0.25, s("by", 44.0), fx2.RED, 400, None),
    ("PRICE", s("price", 51.1), s("Pain", 52.8), fx2.OFFWHITE, 400, None),
    ("BALANCE", s("balance", 57.4), s("Balance", 60.3) - 0.05, fx2.RED, 400, None),
    ("EVERYBODY", s("everybody", 61.4), s("no", 64.3), fx2.RED, 400, None),
    ("NO VALUE", s("no", 64.3), s("It's", 65.25), fx2.RED, 400, None),
    ("A", s("A", 67.3), s("Screw", 68.8), fx2.RED, 360, 470),
    ("PROBLEM", s("problem", 72.0), s("exact", 74.9), fx2.OFFWHITE, 400, None),
    ("NO OPTION", s("no", 81.0), s("adapt", 82.2), fx2.OFFWHITE, 400, None),
    ("COMFORT", s("comfort", 87.3), s("Outliers", 87.9), fx2.RED, 400, None),
    ("JUDGING", s("judging", 90.45), s("Normal", 91.4), fx2.OFFWHITE, 400, None),
    ("LOOK AT YOU", s("look", 93.55), s("Crazy", 94.24) - 0.2, fx2.RED, 400, None),
    ("MEDIOCRITY", s("mediocrity", 98.4), s("were", 99.97), fx2.OFFWHITE, 400, None),
    ("SCREW", s("Screw", 68.8), s("need", 69.9) + 0.06, fx2.OFFWHITE, 330, 300),
    ("BALANCE", s("balance", 69.15), s("need", 69.9) + 0.06, fx2.RED, 560, 300),
    ("CRAZY", s("Crazy", 94.24), 97.0, fx2.OFFWHITE, 330, 250),
    ("BORING", s("boring", 95.0), 97.0, fx2.OFFWHITE, 580, 250),
    ("OBSESSED", s("obsessed", 95.5), 97.0, fx2.RED, 830, 250),
    ("NORMAL", s("normal", 101.0), LEN + 1, fx2.OFFWHITE, 400, None),
]
STRIKE = {("A", 360): s("nothing", 68.3), ("BALANCE", 560): s("balance", 69.15) + 0.35}
GREY = (s("Balance", 60.3) - 0.05, s("Screw", 68.8))
# his cut-out moves for the stacked list (scale, dx) with 0.35 s eases
MOVES = [(0, 0.82, 0), (s("Crazy", 94.24) - 0.2, 0.70, 230), (97.0, 0.82, 0)]   # 0.82: titles read above his head


def his_xf(t):
    sc, dx = MOVES[0][1], MOVES[0][2]
    for i, (t0, s1, d1) in enumerate(MOVES):
        if t >= t0 and i:
            p0 = MOVES[i - 1]
            u = fx2.ease_out((t - t0) / 0.35)
            sc = p0[1] + (s1 - p0[1]) * u; dx = p0[2] + (d1 - p0[2]) * u
    return sc, dx


# ---------------------------------------------------------------- captions: sentence blocks up to 9 words
def blocks():
    his = [dict(w) for w in WORDS if w["s"] >= HIS]
    for w in his:
        if w["w"] == "Is" and abs(w["s"] - 37.27) < 0.2: w["w"] = "is"
    out, cur = [], []
    for i, w in enumerate(his):
        cur.append(w)
        nxt = his[i + 1] if i + 1 < len(his) else None
        if nxt is None or re.search(r"[.?!]$", w["w"]) or (re.search(r",$", w["w"]) and len(cur) >= 4) \
                or nxt["s"] - w["e"] > 0.5 or len(cur) >= 9:
            out.append(cur); cur = []
    return out


BL = blocks()


def block_at(t):
    for i, b in enumerate(BL):
        end = BL[i + 1][0]["s"] if i + 1 < len(BL) else LEN
        end = min(end, b[-1]["e"] + 0.8)
        if b[0]["s"] - 0.01 <= t < end:
            return b
    return None


# ---------------------------------------------------------------- frame
def matte(f):
    p = f"work/matte/{min(f, LAST_F):05d}.png"
    m = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    return m if m is not None else np.zeros((H, W), np.uint8)


def edge_fix(base, m):
    """reel-12 hair-edge recipe: inside the head area and within 40 px of the matte edge, drop bright wall pixels
    (luma > 95) and pull what remains of the soft edge toward the dark hair tone (despill of wall and pink sheet)."""
    inside = (m > 127).astype(np.uint8)
    dist = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
    band = (dist < 40) & (m > 0)
    rows = np.where(inside.any(1))[0]
    top = rows[0] if len(rows) else 0
    head = np.zeros_like(band); head[:top + 300] = True        # hair only: ears and cheeks start lower
    luma = base.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    kill = band & head & (luma > 95)
    m = m.copy(); m[kill] = (m[kill] * 0.15).astype(np.uint8)
    m = cv2.GaussianBlur(m, (0, 0), 1.0)
    w = np.clip(1 - dist / 40.0, 0, 1) * band * np.where(head, 0.6, 0.2)
    tone = np.array([34, 28, 26], np.float32)
    base = (base.astype(np.float32) * (1 - w[..., None]) + tone * w[..., None]).astype(np.uint8)
    return base, m


def his_layer(bg, base, f, t):
    m = matte(f)
    base, m = edge_fix(base, m)
    # the frame edge cuts his shoulders in a straight line once he is scaled down: fade the outer 170 px instead
    xs = np.arange(W, dtype=np.float32)
    ramp = np.clip(np.minimum(xs, W - 1 - xs) / 170.0, 0, 1); ramp = ramp * ramp * (3 - 2 * ramp)
    ys = np.arange(H, dtype=np.float32)
    rb = np.clip((H - 1 - ys) / 60.0, 0, 1)
    m = (m.astype(np.float32) * ramp[None, :] * np.maximum(rb[:, None], 0.0 + (ys[:, None] < H - 60))).astype(np.uint8)
    sc, dx = his_xf(t)
    if abs(sc - 1) > 1e-3 or dx:
        M = np.float32([[sc, 0, (1 - sc) * W / 2 + dx], [0, sc, (1 - sc) * H]])
        base = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR)
        m = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)
    sh = cv2.GaussianBlur(m, (0, 0), 22)
    sh = cv2.warpAffine(sh, np.float32([[1, 0, 12], [0, 1, 18]]), (W, H))
    bgd = (bg.astype(np.float32) * (1 - sh[..., None] / 255.0 * 0.45)).astype(np.uint8)
    return fx2.over(bgd, base, m)


def draw_titles(img, t, only=None):
    for text, t0, t1, col, y, size in TIT:
        if not (t0 <= t < t1) or (text in ("CRAZY", "BORING", "OBSESSED") and size == 250):
            continue
        if size is None:
            size = 400
            while fx2.font(fx2.F_TITLE, size).getlength(text) > W - 110: size -= 10
        img, tw, th = fx2.title(img, text, t, t0, 0, y, size, col, seed=hash(text) % 97, align="center" if size > 300 or text in ("NORMAL", "ABNORMAL", "OBSESSED", "SCREW", "BALANCE", "A") else "left")
        if text in ("CRAZY", "BORING", "OBSESSED") and size == 250:
            pass
        st = STRIKE.get((text, y))
        if st is not None and t >= st:
            u = fx2.ease_out((t - st) / 0.25)
            img = np.ascontiguousarray(img).copy()
            bb = fx2.font(fx2.F_TITLE, size).getbbox(text)
            x0 = (W - tw) // 2 - 20; x1 = x0 + int((tw + 40) * u); ym = y + (bb[1] + bb[3]) // 2
            cv2.rectangle(img, (x0, ym - 14), (x1, ym + 14), (20, 20, 22) if text == "A" else fx2.OFFWHITE, -1)
    return img


def stack_titles(img, t):
    """the Crazy / boring / obsessed list: left aligned, his cut-out moved right."""
    for text, t0, t1, col, y, size in TIT:
        if text in ("CRAZY", "BORING", "OBSESSED") and size == 250 and t0 <= t < t1:
            img, _, _ = fx2.title(img, text, t, t0, 70, y, size, col, seed=len(text))
    return img


def compose(f, base):
    t = f / FPS
    if t < HIS:
        return base
    cur = [x for x in INS if x[0] <= t < x[1]]
    if cur:
        t0, t1, kind, p = cur[-1]
        u = (t - t0) / max(1e-3, t1 - t0)
        if kind == "photo":
            return fx2.photo_cover(p["path"], u)            # physique photo: nothing on top of it
        if kind == "clip":
            z = p.get("zoom", 1.0) + (p.get("zoom1", p.get("zoom", 1.0)) - p.get("zoom", 1.0)) * u
            img = fx1.clip_frame(p["path"], p["src"] + (t - t0), z, p.get("cx", 0.5), p.get("cy", 0.5))
        else:
            img = fx2.vignette(fx2.bg_red(t), 0.40)
            if kind == "cutout":
                img = fx2.place_cutout(img, p["path"], u, p["height"])
            else:
                img = fx2.photo_frame(img, p["path"], u, p["width"], p["yc"])
        if p.get("title") and p.get("title_from", t0) <= t < p.get("title_until", t1):
            tx = p["title"]; size = 330
            while fx2.font(fx2.F_TITLE, size).getlength(tx) > W - 120: size -= 10
            if kind == "clip":
                g = np.linspace(0.45, 1.0, 900, dtype=np.float32)
                img = img.copy(); img[:900] = (img[:900] * g[:, None, None]).astype(np.uint8)
            img, _, _ = fx2.title(img, tx, t, p.get("title_from", t0), 0, 230, size, fx2.OFFWHITE, seed=len(tx), align="center")
        b = block_at(t)
        if b:
            if kind == "frame" and p.get("title"):
                img = fx2.caption(img, b, t, y0=1380)
            elif kind == "clip":
                img = fx2.caption(img, b, t, y0=1300, boxed=True)
            else:
                img = fx2.caption(img, b, t, y0=300)
        return img
    # his cut-out scene
    grey = GREY[0] <= t < GREY[1]
    bg = fx2.bg_grey(t) if grey else fx2.vignette(fx2.bg_red(t), 0.40)
    if f > LAST_F:
        base = base  # frozen last frame passed in
    bg = draw_titles(bg, t)
    img = his_layer(bg, base, f, t)
    img = stack_titles(img, t)
    b = block_at(t)
    if b:
        img = fx2.caption(img, b, t, y0=300, color=(40, 36, 34) if grey else fx2.CAPGREY)
    return img


GRAIN = 0.08   # brand: heavy grain, about 2x the house default (0.04), new field every frame


def final(f, base):
    """compose + the brand's film grain on our graphic frames (texture only, no colour change)."""
    img = np.ascontiguousarray(compose(f, base))
    t = f / FPS
    if t < HIS:
        return img                                   # her clip stays untouched
    cur = [x for x in INS if x[0] <= t < x[1]]
    if cur and cur[-1][2] in ("photo", "clip"):
        return img                                   # his physique photos and B-roll: no filter
    return motion_kit.grain(img, GRAIN, seed=f)


def base_frames(f0, n):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{min(f0, LAST_F) / FPS:.4f}", "-i", "work/base.mp4",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        b = p.stdout.read(W * H * 3)
        if len(b) == W * H * 3:
            last = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        yield last
    p.stdout.close(); p.wait()


def still(t, out):
    f = fr(t)
    b = next(base_frames(f, 1))
    Image.fromarray(final(f, b)).save(out)


def render(a, b, out, crf=14):
    f0, f1 = fr(a), min(fr(b), fr(LEN))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                            str(FPS), "-i", "-", "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast", "-g", "30",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i, bf in enumerate(base_frames(f0, f1 - f0)):
        enc.stdin.write(np.ascontiguousarray(final(f0 + i, bf)).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    if sys.argv[1] == "still":
        os.makedirs("out/stills/v2", exist_ok=True)
        for t in sys.argv[2:]:
            still(float(t), f"out/stills/v2/s_{float(t):06.2f}.png")
    elif sys.argv[1] == "render":
        render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
