"""Feasibility stills for reel-17: Berserk panel fixed on screen behind his body, HDR on his body only.

    python3 work/test_stills.py

Layers: gym (bar included) -> panel (solid square, fixed on screen) -> him (cut out).
Matte: rembg u2net_human_seg alpha x MediaPipe person mask (grown, softened), as in reel-02's refine_matte.py.
"""
import subprocess, os
import numpy as np, cv2
from rembg import new_session, remove
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "test")
os.makedirs(OUT, exist_ok=True)
PANEL = os.path.join(ROOT, "assets", "berserk_panel.jpg")
W, H = 1080, 1920
# Mockup placement (his screenshot, video area scaled 0.828): square 540 px wide at x 270, y 196.
PX, PY, PS = 270, 196, 540

SHOTS = [("bottom", "part1", 1.0), ("rising", "part1", 4.6), ("top", "part1", 5.3), ("top2", "part2", 2.0),
         ("lowering", "part1", 7.0), ("top3", "part3", 4.0)]

seg_r = new_session("u2net_human_seg")
seg_mp = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
    output_confidence_masks=True))


def grab(part, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", os.path.join(ROOT, "raw", part + ".mp4"),
                          "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()


def matte(rgb):
    a = np.array(remove(rgb, session=seg_r, only_mask=True)).astype(np.float32) / 255
    res = seg_mp.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    # classes: 0 bg, 1 hair, 2 body skin, 3 face skin, 4 clothes, 5 others (catches the rings: left out)
    cm = res.confidence_masks
    person = sum(cm[i].numpy_view() for i in (1, 2, 3, 4))
    person = cv2.resize(person.astype(np.float32), (W, H))
    person = (person > 0.5).astype(np.uint8) * 255
    person = cv2.dilate(person, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    person = cv2.GaussianBlur(person, (0, 0), 3).astype(np.float32) / 255
    a = np.clip(a * np.clip(person * 1.3, 0, 1), 0, 1)
    # fill holes inside the body (neck gap at the top of a rep): flood the background from the border
    core = (a > 0.5).astype(np.uint8)
    core = cv2.morphologyEx(core, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    ff = core.copy(); m = np.zeros((H + 2, W + 2), np.uint8)
    for seed in [(0, 0), (W - 1, 0), (0, H // 2), (W - 1, H // 2)]:
        if ff[seed[1], seed[0]] == 0:
            cv2.floodFill(ff, m, seed, 2)
    holes = (ff == 0).astype(np.float32)
    holes = cv2.GaussianBlur(cv2.dilate(holes, np.ones((7, 7), np.uint8)), (0, 0), 1.5)
    a = np.maximum(a, holes)
    # pull the edge in a touch so the wall-coloured fringe of the blurred hair goes
    a = cv2.erode(a, np.ones((3, 3), np.uint8), iterations=1)
    return cv2.GaussianBlur(a, (0, 0), 1.0)


def decontam(rgb, a):
    """Edge pixels carry wall colour: replace them with colour pushed out from the solid body."""
    inside = (a > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
    solid = (dist > 8).astype(np.float32)
    num = cv2.GaussianBlur(rgb.astype(np.float32) * solid[..., None], (0, 0), 7)
    den = cv2.GaussianBlur(solid, (0, 0), 7)[..., None] + 1e-4
    est = num / den
    # band within 8 px of the edge: fade to the pushed-out body colour (full at the edge)
    w = np.where(a > 0.02, np.clip(1 - dist / 8, 0, 1), 0).astype(np.float32)[..., None]
    return (rgb * (1 - w) + est * w).astype(np.uint8)


def hdr(rgb, k):
    """Local contrast on lightness (big + medium detail) and a little fine sharpening. k=0 is off."""
    if k <= 0:
        return rgb
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[..., 0]
    big = cv2.GaussianBlur(L, (0, 0), 25)
    mid = cv2.GaussianBlur(L, (0, 0), 6)
    fine = cv2.GaussianBlur(L, (0, 0), 1.2)
    L2 = L + k * 0.9 * (L - big) + k * 0.6 * (mid - big) * 0 + k * 0.7 * (L - mid) + k * 0.35 * (L - fine)
    lab[..., 0] = np.clip(L2, 0, 255)
    lab[..., 1:] = 128 + (lab[..., 1:] - 128) * (1 + 0.08 * k)
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)


panel = cv2.cvtColor(cv2.imread(PANEL), cv2.COLOR_BGR2RGB)
panel = cv2.resize(panel, (PS, PS), interpolation=cv2.INTER_AREA)


def comp(rgb, a, k):
    body = hdr(decontam(rgb, a), k).astype(np.float32)
    bg = rgb.astype(np.float32).copy()
    bg[PY:PY + PS, PX:PX + PS] = panel
    a3 = a[..., None]
    return (body * a3 + bg * (1 - a3)).astype(np.uint8)


def label(img, txt):
    img = img.copy()
    cv2.putText(img, txt, (30, 1880), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 9, cv2.LINE_AA)
    cv2.putText(img, txt, (30, 1880), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3, cv2.LINE_AA)
    return img


tiles = []
for name, part, t in SHOTS:
    rgb = grab(part, t)
    a = matte(rgb)
    cv2.imwrite(os.path.join(OUT, f"alpha_{name}.png"), (a * 255).astype(np.uint8))
    out = comp(rgb, a, 1.0)
    cv2.imwrite(os.path.join(OUT, f"comp_{name}.png"), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    tiles.append(label(out, f"{name} {part} {t}s"))
    if name == "top":
        hdr_tiles = [label(comp(rgb, a, k), f"HDR {k}") for k in (0, 0.6, 1.0, 1.6)]
        crop = [cv2.resize(x[500:1500, 140:940], (400, 500)) for x in hdr_tiles]
        cv2.imwrite(os.path.join(OUT, "hdr_levels.png"),
                    cv2.cvtColor(np.hstack([cv2.resize(x, (540, 960)) for x in hdr_tiles]), cv2.COLOR_RGB2BGR))

sheet = np.hstack([cv2.resize(x, (360, 640)) for x in tiles])
cv2.imwrite(os.path.join(OUT, "sheet.png"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
print("done", OUT)
