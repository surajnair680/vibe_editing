"""Effect test for the silhouette beat: back photo -> background snaps to light, body goes black.
python3 work/sil/test.py  -> work/sil/frames/*.png and out/test_silhouette.mp4"""
import numpy as np, cv2, os, subprocess
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

W, H, FPS, DUR = 1080, 1920, 30, 1.6
T_SNAP = 0.40                      # light switches on
rng = np.random.default_rng(3)
src = cv2.imread("raw/c07_back_photo.jpg")
h0, w0 = src.shape[:2]

# matte: MediaPipe person mask (smooth shape), phone removed so only the fist is left
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
    output_confidence_masks=True))
r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(cv2.cvtColor(src, cv2.COLOR_BGR2RGB))))
person = 1 - r.confidence_masks[0].numpy_view().copy()
m = (person > 0.5).astype(np.float32)
cv2.rectangle(m, (262, 455), (450, 760), 0, -1)          # the phone (and the fingers around it)
cv2.ellipse(m, (322, 760), (92, 46), -8, 0, 360, 1, -1)   # a closed fist in its place
for y in range(1450, h0):                                 # waistband: solid down to the frame edge
    xs = np.flatnonzero(m[y] > 0.5)
    if xs.size: m[y, xs[0]:xs[-1] + 1] = 1
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
alpha = cv2.GaussianBlur(m, (0, 0), 2.0)

# place: width 1180 (sides cropped 50 px), bottom on the frame bottom
S = 1180 / w0
ph, pw = int(h0 * S), 1180
img = cv2.resize(src, (pw, ph), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
al = cv2.resize(alpha, (pw, ph))
y0, x0 = H - ph, (W - pw) // 2

def place(a, fill=0.0):
    c = np.full((H, W) + a.shape[2:], fill, np.float32)
    c[y0:, :] = a[:, -x0:-x0 + W] if x0 < 0 else a
    return c
IMG, AL = place(img), place(al)
fade = np.clip((np.arange(H) - y0) / 260.0, 0, 1)[:, None, None]   # photo top melts into black

# the normal look: darker, cooler, crushed
norm = IMG ** 1.25 * np.array([0.92, 0.85, 0.80]) * 0.85 * fade

# the light: hot core behind the shoulders, falling off to cold blue-grey, with rays
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy = 600, 1010
d = np.hypot((xx - cx) / 1.0, (yy - cy) / 1.25)
core = np.exp(-(d / 520) ** 2)
ang = np.arctan2(yy - cy, xx - cx)
rays = (0.5 + 0.5 * np.cos(ang * 23 + 1.3)) * (0.5 + 0.5 * np.cos(ang * 9 - 0.4))
rays = cv2.GaussianBlur(rays.astype(np.float32), (0, 0), 6) * np.clip(d / 900, 0, 1) * 0.35
lum = np.clip(0.18 + 0.95 * core + rays * (0.3 + core), 0, 1.4)
tint = np.array([1.0, 0.97, 0.93])[None, None] * (1 - core[..., None]) * 0 + 1
light = lum[..., None] * (np.array([0.93, 0.95, 1.0]) * (1 - core[..., None]) + np.array([1.0, 0.99, 0.97]) * core[..., None])

# rim: light wraps over the edges of the body
edge = np.clip(cv2.GaussianBlur(AL, (0, 0), 7) - AL, 0, 1)
inner = np.clip(AL - cv2.erode(AL, np.ones((9, 9), np.uint8)), 0, 1)
sil_body = 0.015
grain_bank = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(8)]

def vignette(x, s=0.55):
    v = 1 - s * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.6, 0, 1) ** 2
    return x * v[..., None]

def frame(t):
    i = int(round(t * FPS))
    k = 1 + 0.035 * t / DUR                                 # slow push in
    M = cv2.getRotationMatrix2D((W / 2, H * 0.55), 0, k)
    if t < T_SNAP:
        f = norm.copy()
    else:
        u = t - T_SNAP
        flash = 1 + 1.6 * np.exp(-u / 0.06)                 # overexposed pop, then settles
        flick = 1 + 0.06 * np.sin(i * 2.7) * np.exp(-u / 0.5) + 0.03 * rng.normal()
        L = light * flash * flick
        bloom = cv2.GaussianBlur(L, (0, 0), 25) * 0.35
        bg = L + bloom
        a = AL[..., None]
        body = sil_body + inner[..., None] * 0.10 * L
        f = bg * (1 - a) + body * a
        f = f + edge[..., None] * 0.6 * L                   # glow spill over the outline
        if u < 1 / FPS:                                     # one frame of the old photo burning out
            f = 0.5 * f + 0.5 * np.clip(norm * 3, 0, 1)
    f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    f = vignette(f)
    g = cv2.resize(grain_bank[i % 8], (W, H), interpolation=cv2.INTER_LINEAR)
    f = f + g[..., None] * 0.035
    return np.clip(f, 0, 1)

os.makedirs("work/sil/frames", exist_ok=True); os.makedirs("out", exist_ok=True)
for t in (0.2, 0.43, 0.8):
    cv2.imwrite(f"work/sil/frames/t{t:.2f}.png", (frame(t) * 255).astype(np.uint8))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "out/test_silhouette.mp4"],
                     stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write((frame(i / FPS) * 255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
