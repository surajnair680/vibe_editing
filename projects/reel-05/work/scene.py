"""reel-05: Automance logo reveal intro, 1920x1080, 2.5 s.

Night sky -> car drives in from the right going left, bike from the left going right,
they lock together -> flash, sky turns white, scenery draws in -> AUTOMANCE letters slam in,
red A last -> tagline -> hold on the exact reference.

python3 work/scene.py still 0.6 1.3 ...      -> out/stills/t_<t>.png
python3 work/scene.py render out/draft.mp4 [--fps 30] [--scale 0.5]
"""
import json, os, subprocess, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "layers")
W, H = 1920, 1080
DUR = 2.5
FPS = 30

# ---------------------------------------------------------------- timing (seconds)
T_DRIVE = (0.10, 0.95)     # car + bike travel, lock at the end
T_LOCK = 0.95
T_GROUND = (0.20, 0.75)
T_SUN = (0.30, 0.95)
T_MOUNT = (0.40, 0.90)
T_FLASH = (0.95, 1.04)     # sky goes to white
T_SKY = (1.00, 1.32)       # skyline rises
T_ROAD = (1.02, 1.38)
T_LET0, T_LETSTEP, T_LETDUR = 1.08, 0.05, 0.16
T_REDA = (1.42, 1.62)
T_TAGLINE = (1.55, 1.95)
T_SHEEN = (1.98, 2.30)
T_FINAL = (2.22, 2.32)     # blend into the exact reference
T_PUSH = (0.0, 2.25)       # camera push 1.06 -> 1.0


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, rng):
    return clamp((t - rng[0]) / (rng[1] - rng[0]))


def ease_out(u, p=3):
    return 1 - (1 - u) ** p


def ease_io(u):
    return u * u * (3 - 2 * u)


def back_out(u, s=1.7):
    u = u - 1
    return u * u * ((s + 1) * u + s) + 1


# ---------------------------------------------------------------- assets
def load_layers():
    boxes = json.load(open(os.path.join(LAY, "boxes.json")))
    L = {}
    for name, (x0, y0, x1, y1) in boxes.items():
        im = cv2.imread(os.path.join(LAY, f"{name}.png"), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
        pad = 4
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        x1, y1 = min(W, x1 + pad + 1), min(H, y1 + pad + 1)
        c = im[y0:y1, x0:x1]
        rgb, a = c[..., :3], c[..., 3]
        r, g, b = rgb[..., 2], rgb[..., 1], rgb[..., 0]
        red = np.clip((r - (g + b) / 2 - 0.15) * 3, 0, 1)   # 1 on the red parts
        L[name] = dict(x=x0, y=y0, rgb=rgb, a=a, red=red, box=boxes[name])
    ref = cv2.imread(os.path.join(LAY, "reference_1080.png")).astype(np.float32) / 255
    return L, ref


L, REF = load_layers()
RNG = np.random.default_rng(5)
STARS = np.c_[RNG.uniform(0, W, 160), RNG.uniform(0, 640, 160), RNG.uniform(0.3, 1, 160), RNG.uniform(0, 6.28, 160)]
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------------------------------------------------------------- drawing helpers
def layer_color(ly, ink):
    """premultiplied colour of a layer: neutral ink gets colour `ink`, red parts keep red."""
    rgb = ly["rgb"] * ly["red"][..., None] + np.array(ink, np.float32) * (1 - ly["red"][..., None])
    return rgb


def place(canvas, ly, ink, dx=0.0, dy=0.0, scale=1.0, alpha=1.0, blur_x=0, blur_y=0,
          mask=None, glow=0.0, origin=None):
    """composite a layer over the canvas (float BGR) with a transform."""
    if alpha <= 0.002:
        return
    rgb = layer_color(ly, ink)
    a = ly["a"] * alpha
    if mask is not None:
        a = a * mask
    h, w = a.shape
    if origin is None:
        origin = (ly["x"] + w / 2, ly["y"] + h / 2)
    ox, oy = origin
    # affine: local crop px -> canvas px
    M = np.array([[scale, 0, ox + (ly["x"] - ox) * scale + dx],
                  [0, scale, oy + (ly["y"] - oy) * scale + dy]], np.float32)
    pm = np.dstack([rgb * a[..., None], a])
    big = cv2.warpAffine(pm, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    if blur_x > 1 or blur_y > 1:
        big = cv2.blur(big, (max(1, int(blur_x)), max(1, int(blur_y))))
    if glow > 0:
        gl = cv2.GaussianBlur(big, (0, 0), 9) * glow
        canvas[:] = canvas + gl[..., :3]                      # additive light
    canvas[:] = canvas * (1 - big[..., 3:4]) + big[..., :3]


def sky(t):
    """background: night gradient -> red sunrise glow -> white."""
    top = np.array([0.075, 0.035, 0.020])       # BGR deep navy
    hor = np.array([0.19, 0.10, 0.09])
    v = np.clip(YY / 760, 0, 1)[..., None]
    bg = top * (1 - v) + hor * v
    bg = np.broadcast_to(bg, (H, W, 3)).copy()
    # stars
    sv = (1 - prog(t, (0.5, 0.95))) * 0.9
    if sv > 0:
        layer = np.zeros((H, W), np.float32)
        for x, y, b, ph in STARS:
            tw = 0.65 + 0.35 * np.sin(ph + t * 9)
            cv2.circle(layer, (int(x), int(y)), 1, float(b * tw), -1, cv2.LINE_AA)
        layer = cv2.GaussianBlur(layer, (0, 0), 0.8) * 1.6
        bg += layer[..., None] * sv
    # sunrise glow around the sun
    s = ease_io(prog(t, (0.30, 1.0)))
    if s > 0:
        sx, sy = 1148, 225
        d = np.sqrt((XX - sx) ** 2 + ((YY - sy) * 1.5) ** 2)
        rad = 250 + 650 * s
        g = np.exp(-(d / rad) ** 2)[..., None]
        warm = np.array([0.12, 0.22, 0.85])        # orange-red (BGR)
        bg = bg + warm * g * 0.75 * s
        bg += np.array([0.10, 0.12, 0.25]) * s * 0.6 * v    # horizon warms
    return bg


def flash_amount(t):
    """0 = night, 1 = white sky. A bloom from the lock point."""
    return ease_out(prog(t, T_FLASH), 2)


def bloom(canvas, t):
    """white light expanding from the lock point, then everything white."""
    f = prog(t, (T_LOCK - 0.02, T_FLASH[1] + 0.06))
    if f <= 0 or f >= 1:
        return
    cx, cy = 1010, 560
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    r = 80 + 2600 * ease_out(f, 2.5)
    m = np.clip(np.exp(-(d / (r + 1)) ** 2) * (0.6 + 3 * f), 0, 1)[..., None] * (1 - prog(f, (0.7, 1.0)))
    canvas[:] = canvas * (1 - m) + 1.0 * m


def wipe_mask(ly, u, direction="lr", soft=40):
    """reveal mask over a layer crop. u 0..1."""
    h, w = ly["a"].shape
    if direction in ("lr", "rl"):
        xs = np.arange(w, dtype=np.float32)
        pos = u * (w + soft) - soft
        m = np.clip((pos - xs) / soft + 1, 0, 1) if direction == "lr" else np.clip(((w - xs) - pos) / soft, 0, 1)
        if direction == "rl":
            m = np.clip((xs - (w - pos - soft)) / soft, 0, 1)
        return np.broadcast_to(m[None, :], (h, w))
    if direction == "co":   # centre out
        xs = np.abs(np.arange(w, dtype=np.float32) - w / 2)
        pos = u * (w / 2 + soft)
        m = np.clip((pos - xs) / soft, 0, 1)
        return np.broadcast_to(m[None, :], (h, w))
    raise ValueError(direction)


def sun_clip():
    """per column, hide the sun below its final bottom edge (it rises from behind the mountains)."""
    ly = L["sun"]
    a = ly["a"]
    h, w = a.shape
    bottom = np.array([np.max(np.where(a[:, x] > 0.3)[0]) if (a[:, x] > 0.3).any() else -1 for x in range(w)])
    return bottom


SUN_BOTTOM = sun_clip()


# ---------------------------------------------------------------- the frame
def frame(t):
    fl = flash_amount(t)
    night_ink = (0.93, 0.93, 0.93)
    ink = tuple(np.array(night_ink) * (1 - fl))           # white lines at night -> black
    glow = 0.55 * (1 - fl)

    c = sky(t) * (1 - fl) + 1.0 * fl

    # sun rising behind the mountains
    s = prog(t, T_SUN)
    if s > 0:
        ly = L["sun"]
        h, w = ly["a"].shape
        dy = 70 * (1 - ease_out(s, 2))
        rows = np.arange(h)[:, None] + dy               # row in final position
        m = (rows <= SUN_BOTTOM[None, :] + 0.5).astype(np.float32)
        place(c, ly, ink, dy=dy, alpha=min(1, s * 3), mask=m, glow=0.5 * (1 - fl))

    # mountains draw in left to right
    u = prog(t, T_MOUNT)
    if u > 0:
        place(c, L["mountains"], ink, mask=wipe_mask(L["mountains"], ease_io(u), "lr", 80), glow=glow)

    # ground line from the centre out
    u = prog(t, T_GROUND)
    if u > 0:
        place(c, L["ground"], ink, mask=wipe_mask(L["ground"], ease_out(u, 2), "co", 120), glow=glow * 1.4)

    # scenery after the flash
    u = prog(t, T_SKY)
    if u > 0:
        ly = L["skyline"]
        h, w = ly["a"].shape
        dy = 60 * (1 - ease_out(u, 3))
        base = 357 - ly["y"]                           # skyline base row in crop (final)
        rows = np.arange(h)[:, None] + dy
        m = np.broadcast_to((rows <= base + 6).astype(np.float32), (h, w))
        place(c, ly, ink, dy=dy, mask=m, alpha=min(1, u * 2.5))
    u = prog(t, T_ROAD)
    if u > 0:
        place(c, L["road_near"], ink, mask=wipe_mask(L["road_near"], ease_io(u), "rl", 90))
        place(c, L["road_far"], ink, mask=wipe_mask(L["road_far"], ease_io(u), "lr", 90))

    # car (from the right, going left) and bike (from the left, going right)
    u = prog(t, T_DRIVE)
    if u > 0:
        p = ease_out(u, 3)
        dt = 1 / FPS
        u2 = prog(t - dt * 0.5, T_DRIVE)
        speed = abs(ease_out(u, 3) - ease_out(u2, 3)) * 1700      # px per half frame
        car_dx = 1700 * (1 - p)
        bike_dx = -1700 * (1 - p)
        place(c, L["car"], ink, dx=car_dx, blur_x=speed, glow=glow)
        place(c, L["bike"], ink, dx=bike_dx, blur_x=speed, glow=glow)

    bloom(c, t)

    # AUTOMANCE letters slam in, left to right, red A last
    order = [0, 1, 2, 3, 4, 6, 7, 8]
    for k, i in enumerate(order):
        t0 = T_LET0 + k * T_LETSTEP
        u = clamp((t - t0) / T_LETDUR)
        if u <= 0:
            continue
        sc = 1 + 0.9 * (1 - back_out(u, 1.4))
        bl = int(30 * (1 - u))
        place(c, L[f"letter_{i}"], (0, 0, 0), scale=sc, alpha=min(1, u * 3), blur_y=bl)
    u = prog(t, T_REDA)
    if u > 0:
        ly = L["letter_5"]
        sc = 1 + 1.4 * (1 - back_out(u, 2.0))
        dy = -40 * (1 - ease_out(u, 3))
        place(c, ly, (0, 0, 0), scale=sc, dy=dy, alpha=min(1, u * 3), blur_y=int(40 * (1 - u)))
        # red glow pulse behind the A when it lands (stays above the tagline)
        f = prog(t, (T_REDA[1] - 0.03, T_REDA[1] + 0.20))
        if 0 < f < 1:
            cx, cy = (ly["box"][0] + ly["box"][2]) / 2, (ly["box"][1] + ly["box"][3]) / 2
            d = np.sqrt(((XX - cx) / 1.3) ** 2 + (YY - cy) ** 2)
            g = np.exp(-(d / (60 + 50 * f)) ** 2) * np.sin(np.pi * f) * 0.45
            g = g * (YY < 895)
            red = np.array([0.15, 0.12, 0.85])
            c[:] = c * (1 - g[..., None]) + red * g[..., None]
            place(c, ly, (0, 0, 0))            # keep the letter crisp on top

    # tagline: side lines grow outward, words open from the centre
    u = prog(t, T_TAGLINE)
    if u > 0:
        e = ease_out(u, 3)
        place(c, L["tag_line_l"], (0, 0, 0), mask=wipe_mask(L["tag_line_l"], e, "rl", 30))
        place(c, L["tag_line_r"], (0, 0, 0), mask=wipe_mask(L["tag_line_r"], e, "lr", 30))
        place(c, L["tag_letters"], (0, 0, 0), mask=wipe_mask(L["tag_letters"], e, "co", 140), alpha=min(1, u * 2))
        place(c, L["tag_bar"], (0, 0, 0), alpha=min(1, u * 2), scale=1 + 0.3 * (1 - e))

    # sheen across the wordmark
    u = prog(t, T_SHEEN)
    if 0 < u < 1:
        x0 = 150 + u * 1800
        band = np.exp(-(((XX - x0) + (YY - 820) * 0.45) / 14) ** 2)
        m = (YY > 760) & (YY < 880)
        lum = c.mean(axis=2)
        dark = (lum < 0.5) & m
        c[dark] = c[dark] + (band[dark] * 0.55)[:, None]

    # blend into the exact reference
    f = ease_io(prog(t, T_FINAL))
    if f > 0:
        c = c * (1 - f) + REF * f

    # camera: slow push and a hit shake at the lock and the red A
    z = 1.0 + 0.06 * (1 - ease_io(prog(t, T_PUSH)))
    sh = 0.0
    for th, amp in ((T_LOCK, 9), (T_REDA[1], 4)):
        if th <= t < th + 0.16:
            k = (t - th) / 0.16
            sh += amp * (1 - k) * np.sin(k * 40)
    if z != 1.0 or sh != 0:
        M = np.array([[z, 0, (1 - z) * W / 2 + sh], [0, z, (1 - z) * H / 2 + sh * 0.6]], np.float32)
        c = cv2.warpAffine(c, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return np.clip(c * 255 + 0.5, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- CLI
def main():
    cmd = sys.argv[1]
    root = os.path.join(HERE, "..")
    if cmd == "still":
        os.makedirs(os.path.join(root, "out", "stills"), exist_ok=True)
        for a in sys.argv[2:]:
            t = float(a)
            cv2.imwrite(os.path.join(root, "out", "stills", f"t_{t:05.2f}.png"), frame(t))
    elif cmd == "render":
        out = sys.argv[2]
        fps = FPS
        scale = 1.0
        if "--fps" in sys.argv:
            fps = int(sys.argv[sys.argv.index("--fps") + 1])
        if "--scale" in sys.argv:
            scale = float(sys.argv[sys.argv.index("--scale") + 1])
        ow, oh = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                              "-s", f"{ow}x{oh}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "14",
                              "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n = int(round(DUR * fps))
        for i in range(n):
            im = frame(i / fps)
            if scale != 1:
                im = cv2.resize(im, (ow, oh), interpolation=cv2.INTER_AREA)
            p.stdin.write(im.tobytes())
        p.stdin.close()
        p.wait()


if __name__ == "__main__":
    main()
