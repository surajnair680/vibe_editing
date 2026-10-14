"""Refine a rembg matte with MediaPipe's people segmenter so background objects (the sofa) drop out.

    python3 work/refine_matte.py work/hook_src.mp4 work/matte/hook_src_alpha.mp4 -o work/matte/hook_src_alpha_clean.mp4

final alpha = rembg alpha x (MediaPipe person mask, grown and softened). rembg keeps the fine edges,
MediaPipe decides what counts as the person.
"""
import argparse, subprocess, sys
import numpy as np, cv2
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("matte"); ap.add_argument("-o", "--out", required=True)
ap.add_argument("--grow", type=int, default=21, help="px to grow the person mask before multiplying")
ap.add_argument("--thresh", type=float, default=0.5)
ap.add_argument("--kill-florals", action="store_true", help="drop saturated pink/red/yellow pixels (the sofa)")
ap.add_argument("--solid-below", type=float, default=None, help="below this height (0..1) use max(alpha, person mask)")
ap.add_argument("--model", default="work/models/selfie_multiclass.tflite")
a = ap.parse_args()

def frames(path, w, h, gray=False):
    pix = "gray" if gray else "rgb24"; ch = 1 if gray else 3
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", pix, "-"], stdout=subprocess.PIPE)
    n = w * h * ch
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(h, w, ch) if ch > 1 else np.frombuffer(b, np.uint8).reshape(h, w)

info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate",
                       "-of", "csv=p=0", a.src], capture_output=True, text=True).stdout.strip().split(",")
W, H = int(info[0]), int(info[1]); fps = info[2]
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=a.model), output_confidence_masks=True,
    running_mode=vision.RunningMode.VIDEO))
out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", fps,
                        "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (a.grow * 2 + 1, a.grow * 2 + 1))
prev = None
for i, (rgb, m) in enumerate(zip(frames(a.src, W, H), frames(a.matte, W, H, gray=True))):
    res = seg.segment_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)), int(i * 1000 / 30))
    bg = res.confidence_masks[0].numpy_view()                 # class 0 = background
    person = cv2.resize((1.0 - bg).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    person = (person > a.thresh).astype(np.uint8) * 255
    person = cv2.dilate(person, k)
    person = cv2.GaussianBlur(person, (0, 0), a.grow / 2).astype(np.float32) / 255
    if prev is not None: person = 0.6 * person + 0.4 * prev       # light temporal smoothing, no flicker
    prev = person
    alpha = m.astype(np.float32) * np.clip(person * 1.3, 0, 1)
    if a.kill_florals:
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)               # H 0..179, S/V 0..255
        hh, ss, vv = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        floral = (((hh >= 150) | (hh <= 4) | ((hh >= 19) & (hh <= 35))) & (ss > 100) & (vv > 120))
        navy = (hh >= 100) & (hh <= 135) & (ss > 70) & (vv > 60)          # dark blue leaves, shoulder band only
        navy[:int(0.57 * H)] = False
        navy[int(0.70 * H):] = False
        floral = (floral | navy).astype(np.uint8)
        floral = cv2.morphologyEx(floral, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        floral = cv2.GaussianBlur(cv2.dilate(floral, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 2)
        alpha *= 1 - np.clip(floral, 0, 1)
    if a.solid_below is not None:
        y0 = int(a.solid_below * H)
        body = np.clip(person * 1.3, 0, 1) * 255
        ramp = np.clip((np.arange(H) - y0) / 40.0, 0, 1)[:, None]        # 40 px blend into the rule
        alpha = alpha * (1 - ramp) + np.maximum(alpha, body) * ramp
    alpha = alpha.astype(np.uint8)
    out.stdin.write(alpha.tobytes())
out.stdin.close(); out.wait()
print("refined matte ->", a.out, "frames:", i + 1)
