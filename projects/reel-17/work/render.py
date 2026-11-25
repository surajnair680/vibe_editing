"""reel-17 v1 render: Berserk panel fixed on screen behind his body, HDR 1.0 on his body only.

    python3 work/render.py                       # full 33 s -> out/reel-17-v1.mp4
    python3 work/render.py --start 4 --end 7     # a range (whole seconds) for revisions

Layers: gym (bar included) -> panel (solid 540 px square, fixed, top left) -> him (cut out).
Matte: rembg u2net_human_seg x MediaPipe hair/skin/clothes classes (class 5 "others" grabs the rings, left out),
holes inside the body filled, edge pulled in 1 px, edge band colour pushed out from the body (no wall fringe).
The alpha is cached to work/cache/alpha/ so a revision does not re-run the matte.
Source: work/cache/src.mp4 = raw/part1..3 joined with the concat demuxer (-c copy), 992 frames at 30 fps.
"""
import argparse, os, subprocess
import numpy as np, cv2
from rembg import new_session, remove
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
PX, PY, PS = 53, 42, 540          # his 2nd mockup, refs/mockup2_position.jpg
HDR_K = 1.0

ap = argparse.ArgumentParser()
ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=None)
ap.add_argument("-o", "--out", default=os.path.join(ROOT, "out", "reel-17-v1.mp4"))
a = ap.parse_args()

SRC = os.path.join(ROOT, "work", "cache", "src.mp4")
ACACHE = os.path.join(ROOT, "work", "cache", "alpha"); os.makedirs(ACACHE, exist_ok=True)
os.makedirs(os.path.dirname(a.out), exist_ok=True)

panel = cv2.cvtColor(cv2.imread(os.path.join(ROOT, "assets", "berserk_panel.jpg")), cv2.COLOR_BGR2RGB)
panel = cv2.resize(panel, (PS, PS), interpolation=cv2.INTER_AREA).astype(np.float32)

seg_r = new_session("u2net_human_seg")
seg_mp = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
    output_confidence_masks=True, running_mode=vision.RunningMode.VIDEO))
K9 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
K25 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
prev_person = None


def matte(rgb, i):
    global prev_person
    p = os.path.join(ACACHE, f"{i:05d}.png")
    if os.path.exists(p):
        return cv2.imread(p, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    al = np.array(remove(rgb, session=seg_r, only_mask=True)).astype(np.float32) / 255
    res = seg_mp.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)),
                                   int(i * 1000 / FPS))
    cm = res.confidence_masks
    person = cv2.resize(sum(cm[c].numpy_view() for c in (1, 2, 3, 4)).astype(np.float32), (W, H))
    if prev_person is not None:
        person = 0.75 * person + 0.25 * prev_person      # light temporal smoothing, no flicker
    prev_person = person
    pm = cv2.dilate((person > 0.5).astype(np.uint8) * 255, K9)
    pm = cv2.GaussianBlur(pm, (0, 0), 3).astype(np.float32) / 255
    al = np.clip(al * np.clip(pm * 1.3, 0, 1), 0, 1)
    core = cv2.morphologyEx((al > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, K25)
    ff = core.copy(); m = np.zeros((H + 2, W + 2), np.uint8)
    for seed in [(0, 0), (W - 1, 0), (0, H // 2), (W - 1, H // 2)]:
        if ff[seed[1], seed[0]] == 0:
            cv2.floodFill(ff, m, seed, 2)
    holes = (ff == 0).astype(np.float32)
    holes = cv2.GaussianBlur(cv2.dilate(holes, np.ones((7, 7), np.uint8)), (0, 0), 1.5)
    al = np.maximum(al, holes)
    al = cv2.erode(al, np.ones((3, 3), np.uint8), iterations=1)
    al = cv2.GaussianBlur(al, (0, 0), 1.0)
    cv2.imwrite(p, (al * 255).astype(np.uint8))
    return al


def decontam(rgb, al):
    inside = (al > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
    solid = (dist > 8).astype(np.float32)
    num = cv2.GaussianBlur(rgb.astype(np.float32) * solid[..., None], (0, 0), 7)
    den = cv2.GaussianBlur(solid, (0, 0), 7)[..., None] + 1e-4
    w = np.where(al > 0.02, np.clip(1 - dist / 8, 0, 1), 0).astype(np.float32)[..., None]
    return rgb.astype(np.float32) * (1 - w) + (num / den) * w


def hdr(rgb, k):
    lab = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0]
    big = cv2.GaussianBlur(L, (0, 0), 25); mid = cv2.GaussianBlur(L, (0, 0), 6); fine = cv2.GaussianBlur(L, (0, 0), 1.2)
    lab[..., 0] = np.clip(L + k * 0.9 * (L - big) + k * 0.7 * (L - mid) + k * 0.35 * (L - fine), 0, 255)
    lab[..., 1:] = 128 + (lab[..., 1:] - 128) * (1 + 0.08 * k)
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)


def comp(rgb, al):
    body = hdr(decontam(rgb, al), HDR_K)
    bg = rgb.astype(np.float32)
    bg[PY:PY + PS, PX:PX + PS] = panel
    a3 = al[..., None]
    return np.clip(body * a3 + bg * (1 - a3), 0, 255).astype(np.uint8)


f0 = int(round(a.start * FPS))
dur = None if a.end is None else a.end - a.start
cmd_in = ["ffmpeg", "-v", "error", "-ss", str(a.start), "-i", SRC] + (["-t", str(dur)] if dur else []) + \
         ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
src = subprocess.Popen(cmd_in, stdout=subprocess.PIPE)
vid = a.out.replace(".mp4", "_video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
n = W * H * 3; i = f0
while True:
    b = src.stdout.read(n)
    if len(b) < n:
        break
    rgb = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    enc.stdin.write(comp(rgb, matte(rgb, i)).tobytes())
    i += 1
    if (i - f0) % 30 == 0:
        print("frame", i, flush=True)
enc.stdin.close(); enc.wait()

# sound: the gym room sound joined from WAV (work/audio/full.wav), sample accurate for the range
nfr = i - f0
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-ss", str(a.start), "-i",
                os.path.join(ROOT, "work", "audio", "full.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", "apad", "-t", f"{nfr / FPS:.4f}", "-c:a", "aac", "-b:a", "256k", a.out], check=True)
os.remove(vid)
print("done", a.out, nfr, "frames")
