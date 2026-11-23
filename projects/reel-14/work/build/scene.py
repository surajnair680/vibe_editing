"""reel-14 scene: the approved beat sheet (work/beats.md) as events on the rough v1 cut, and the renderer.
  python3 work/build/scene.py still 27.5 46.5 ...        -> out/stills/s_<t>.png
  python3 work/build/scene.py render <a> <b> <out.mp4>   -> picture only, frames [a, b) of the edit
Base picture = work/base.mp4 (the cut pieces, stream copy). Run from the project folder."""
import json, re, subprocess, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "work/build")
import fx
from fx import W, H, FPS

WORDS = json.load(open("work/words_edit.json"))
LEN = json.load(open("work/cut_plan.json"))["length"]
HIS = 27.30            # his take starts here (her clip before)


def wd(text, near):
    """the spoken word matching text closest to time near (edit time) -> dict."""
    key = re.sub(r"[^a-z']", "", text.lower())
    c = [w for w in WORDS if re.sub(r"[^a-z']", "", w["w"].lower()) == key]
    return min(c, key=lambda w: abs(w["s"] - near))


def s(text, near): return wd(text, near)["s"]
def fr(t): return int(round(t * FPS))


EV = []   # (kind, f0, f1, params); later events win where they overlap
def card(t, n, word, layout, field, strike=False):
    EV.append(("card", fr(t), fr(t) + n, dict(word=word, layout=layout, field=field, strike=strike)))
def photo(t0, t1, **k): EV.append(("photo", fr(t0), fr(t1), k))
def clip(t0, t1, path, src, **k): EV.append(("clip", fr(t0), fr(t1), dict(path=path, src=src, **k)))
def special(t, n, name): EV.append((name, fr(t), fr(t) + n, {}))


# ---------------------------------------------------------------- beats (work/beats.md)
special(HIS, 5, "slit")
card(s("Normal", 27.4), 5, "NORMAL", "vert", "red")
photo(s("a", 28.75), s("You", 30.07), kind="cover", path="assets/photos/me_physique_mirror.jpg", anchor=0.0)
card(s("drinks", 30.6), 5, "DRINKS", "corner", "black")
card(s("pizza", 32.2), 6, "PIZZA", "stack", "paper", strike=True)
card(s("obsessed", 35.4), 5, "OBSES|SED", "stack", "black")
clip(s("obsessed", 35.4) + 5 / FPS, s("abnormal", 36.2), "raw/flex_p1.mp4", 7.6)
card(s("abnormal", 36.2), 6, "AB|NOR|MAL", "stack", "red")
card(s("yes", 39.6), 6, "YES", "giant", "red")
card(s("normal", 40.7), 6, "NORMAL", "rail", "red", strike=True)
card(s("abnormal", 43.3), 7, "ABNOR|MAL", "stack", "paperred")
photo(s("by", 44.0), s("Successful", 44.9), kind="card", path="assets/photos/celebrity_jobs.jpg", width=1040,
      field=fx.PAPER, yc=0.43)
EV.append(("outliers", fr(s("outliers", 46.0)), fr(s("outliers", 46.0)) + 6, {}))
photo(s("outliers", 46.0) + 6 / FPS, s("belong", 47.6), kind="card", path="assets/photos/celebrity_arnold.jpg",
      width=1080, field=fx.BLACK, yc=0.46)
photo(s("belong", 47.6), s("Which", 48.95) - 0.12, kind="card", path="assets/photos/celebrity_musk.jpg", width=720,
      field=fx.BLACK, yc=0.40, border=fx.RED)
card(s("price", 51.1), 5, "PRICE", "corner", "red")
card(s("Pain", 52.8), 5, "PAIN", "vert", "black")
clip(s("Pain", 52.8) + 5 / FPS, s("discomfort", 53.4), "raw/vid_1111c.mp4", 4.3, zoom=1.2, cx=0.0, cy=1.0)
card(s("discomfort", 53.4), 5, "DIS|COM|FORT", "stack", "red")
clip(s("discomfort", 53.4) + 5 / FPS, s("than", 54.9) + 0.6, "raw/pullups.mp4", 7.9)
card(s("balance", 57.4), 5, "BALANCE", "rail", "red")
card(s("everybody", 61.4), 4, "EVERYBODY", "corner", "paper")
card(s("everybody", 62.8), 4, "EVERY|BODY", "stack", "black")
card(s("no", 64.3), 6, "NO|VALUE", "stack", "red")
card(s("A", 67.3), 8, "A", "giant", "red")
card(s("nothing", 68.3), 8, "A", "giant", "red", strike=True)
# the big hit: Screw balance
t = s("Screw", 68.8)
card(t, 5, "SCR|EW", "stack", "inv")
clip(t + 5 / FPS, s("balance", 69.15), "raw/vid_1111c.mp4", 4.4, zoom=1.2, cx=0.0, cy=1.0)
t2 = s("balance", 69.15)
card(t2, 5, "BALANCE", "vert", "red")
clip(t2 + 5 / FPS, t2 + 8 / FPS, "raw/vid_1111c.mp4", 4.9, zoom=1.2, cx=0.0, cy=1.0)
card(t2 + 8 / FPS, 4, "BALANCE", "vert", "inv", strike=True)
clip(t2 + 12 / FPS, s("You", 69.8), "raw/vid_1111c.mp4", 5.1, zoom=1.2, cx=0.0, cy=1.0)
clip(s("You", 69.8), s("But", 71.0), "raw/vid_1111b.mp4", 0.7, zoom=1.04, zoom1=1.10)
clip(s("exact", 74.9), s("keep", 76.2), "raw/vid_1111.mp4", 5.0, zoom=1.15, zoom1=1.18, cx=0.62, cy=0.55)
card(s("keep", 76.2), 5, "KEEP|GOING", "stack", "red")
clip(s("is", 77.75), s("grow", 78.6), "raw/flex_p1.mp4", 7.2, zoom=1.06, zoom1=1.10, cy=0.3)
card(s("grow", 78.6), 5, "GROW", "corner", "paper")
card(s("no", 81.0), 5, "NO OPTION", "rail", "black")
photo(s("adapt", 82.2), s("And", 83.66), kind="cover", path="assets/photos/me_gym_dumbbell.jpg", anchor=0.0)
card(s("comfort", 87.3), 5, "COM|FORT", "stack", "paper")
card(s("Outliers", 87.9), 5, "OUT|LIERS", "stack", "red")
clip(s("Outliers", 87.9) + 5 / FPS, s("and", 89.29), "raw/flex_p1.mp4", 10.9, zoom=1.04, zoom1=1.08, cy=0.3)
card(s("judging", 90.45), 5, "JUDG|ING", "stack", "black")
t = s("Crazy", 94.24)
card(t, 4, "CRAZY", "vert", "red")
photo(t + 4 / FPS, s("boring", 95.0), kind="card", path="assets/photos/celebrity_musk.jpg", width=720,
      field=fx.BLACK, yc=0.40, border=fx.RED)
t = s("boring", 95.0)
card(t, 3, "BORING", "corner", "paper")
photo(t + 3 / FPS, s("obsessed", 95.5), kind="card", path="assets/photos/celebrity_jobs.jpg", width=1040,
      field=fx.PAPER, yc=0.43)
t = s("obsessed", 95.5)
card(t, 3, "OBSES|SED", "stack", "black")
photo(t + 3 / FPS, s("whatever", 96.1) - 0.05, kind="card", path="assets/photos/celebrity_arnold.jpg", width=1080,
      field=fx.BLACK, yc=0.46)
card(s("mediocrity", 98.4), 6, "MEDI|OCRI|TY", "stack", "black")
photo(s("were", 99.97), s("normal", 101.0), kind="cover", path="assets/photos/me_physique_front.jpg", anchor=0.0)
card(s("normal", 101.0), 99, "NOR|MAL", "stack", "red")


# ---------------------------------------------------------------- captions: chunks of up to 4 words
def chunks():
    his = [w for w in WORDS if w["s"] >= HIS]
    sent, cur = [], []
    for i, w in enumerate(his):
        cur.append(w)
        nxt = his[i + 1] if i + 1 < len(his) else None
        if nxt is None or re.search(r"[.,?!]$", w["w"]) or nxt["s"] - w["e"] > 0.28:
            sent.append(cur); cur = []
    out = []
    for se in sent:
        n = -(-len(se) // 4); k = -(-len(se) // n)
        for i in range(0, len(se), k):
            out.append(se[i:i + k])
    return out


CH = chunks()


def chunk_at(t):
    for i, c in enumerate(CH):
        end = CH[i + 1][0]["s"] if i + 1 < len(CH) else LEN
        end = min(end, c[-1]["e"] + 0.6)
        if c[0]["s"] <= t < end:
            return c
    return None


# ---------------------------------------------------------------- compose one frame
def compose(f, base):
    t = f / FPS
    act = [e for e in EV if e[1] <= f < e[2]]
    kind, img, cap_y = "base", base, 372
    for e in act:
        k, f0, f1, p = e
        u = (f - f0) / max(1, f1 - f0 - 1)
        if k == "photo":
            if p["kind"] == "cover":
                img = fx.photo_cover(p["path"], u, p.get("anchor", 0.0))
            else:
                img = fx.photo_card(p["path"], u, p["width"], p["field"], p["yc"], border=p.get("border"))
            kind, cap_y = "insert", 1420
            if "me_" in p["path"]:
                kind = "physique"      # no caption over his physique photos (never let anything eat the money shot)
        elif k == "clip":
            z = p.get("zoom", 1.0) + (p.get("zoom1", p.get("zoom", 1.0)) - p.get("zoom", 1.0)) * u
            img = fx.clip_frame(p["path"], p["src"] + (f - f0) / FPS, z, p.get("cx", 0.5), p.get("cy", 0.5))
            kind, cap_y = "insert", 1420
    for e in act:
        k, f0, f1, p = e
        if k == "card":
            img = fx.slam(fx.card(p["word"], p["layout"], p["field"], p["strike"]), f - f0, f0); kind = "card"
        elif k == "outliers":
            img = fx.slam(fx.outliers_card(), f - f0, f0); kind = "card"
        elif k == "slit":
            img = fx.red_slit(base, f - f0); kind = "card"
    if kind not in ("card", "physique") and t >= HIS:
        c = chunk_at(t)
        if c:
            img = fx.caption(np.ascontiguousarray(img), c, t, cap_y)
    return img


def base_frames(f0, n):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{f0 / FPS:.4f}", "-i", "work/base.mp4", "-frames:v", str(n),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    for _ in range(n):
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.stdout.close(); p.wait()


def still(t, out):
    f = fr(t)
    b = next(base_frames(f, 1))
    Image.fromarray(compose(f, b)).save(out)


def render(a, b, out, crf=14):
    f0, f1 = fr(a), min(fr(b), fr(LEN))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                            str(FPS), "-i", "-", "-c:v", "libx264", "-crf", str(crf), "-preset", "veryfast", "-g", "30",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i, bf in enumerate(base_frames(f0, f1 - f0)):
        enc.stdin.write(np.ascontiguousarray(compose(f0 + i, bf)).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    if sys.argv[1] == "still":
        for t in sys.argv[2:]:
            still(float(t), f"out/stills/s_{float(t):06.2f}.png")
    elif sys.argv[1] == "render":
        render(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
