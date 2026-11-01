"""vlog_overlays: the camcorder-style vlog overlay pack, made vertical and composited in numpy/cv2.

    python3 vlog_overlays.py vertical            # rebuild assets/overlays/vertical/ from horizontal/
    python3 vlog_overlays.py vertical 6 11       # only these numbers
    python3 vlog_overlays.py sheet out.jpg       # contact sheet of the vertical pack (what each shows)
    python3 vlog_overlays.py apply base.mp4 out.mp4 --ov 1@0.0 --ov 12@4.2:2.5   # quick comp, number@start[:dur]

In a project build (copy this file into the project's work/, never import across folders):

    from vlog_overlays import Overlay, screen, keyed
    ov = Overlay(6)                         # vertical video-overlay-6, held on its last frame when stretched
    frame = screen(frame, ov.frame(t - t0)) # white-on-black designs: Screen blend
    frame = keyed(frame, Overlay(12).frame(t - t1), key=(91, 107, 165))   # blue ones: key the colour

How vertical works: each design is a few small text blocks near the edges of a 16:9 frame. We find the blocks
(union of every frame, dilated), then move each block into a 1080x1920 frame: left blocks stay left, right
blocks stay right, the rest centre; rows are spread over the safe band (clear of the Instagram top bar and the
caption / button zone). Blocks that would collide are pushed down. Full-frame designs (7, 10, 12) are scaled
and padded instead. Audio (the built-in SFX) is copied unchanged.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
PACK = HERE.parent / "assets" / "overlays"
W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 230, H - 520       # IG top bar / caption + buttons; keep blocks inside
MARGIN = 72

# Per-design settings. mode "blocks": re-lay text blocks; "frame": scale whole frame and pad.
# scale: block size vs the horizontal source (1080-wide phone shows these bigger, so ~1.0 to 1.2 reads well).
PRESETS = {
    1: dict(mode="blocks", scale=1.15),
    2: dict(mode="blocks", scale=1.2),
    3: dict(mode="blocks", scale=1.2),
    4: dict(mode="blocks", scale=1.1),
    5: dict(mode="blocks", scale=1.3),
    6: dict(mode="blocks", scale=1.0, kernel=(170, 46)),   # keep the 4 clocks as one row
    7: dict(mode="frame", scale=0.5625, pad="edge"),    # VLOG on blue: band across the middle, blue fills
    8: dict(mode="blocks", scale=1.25),
    9: dict(mode="blocks", scale=1.3, kernel=(300, 46)),   # "a  day  in" stays one row
    10: dict(mode="frame", scale=1.0, pad="black"),     # player window: centre crop keeps the window
    11: dict(mode="blocks", scale=0.95),
    12: dict(mode="iris"),                               # REC circle: stretched to a tall oval iris, REC kept sharp
}


def src_path(n):
    return PACK / "horizontal" / f"video-overlay-{n}.mp4"


def vert_path(n):
    return PACK / "vertical" / f"video-overlay-{n}.mp4"


def read_all(path):
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    return frames, fps


def find_blocks(frames, kernel=(70, 46)):
    """Boxes (x, y, w, h) of everything that ever lights up, grouped into text blocks."""
    comp = np.max(np.stack(frames[::2]), 0).max(2)
    mask = (comp > 24).astype(np.uint8)
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_RECT, kernel))
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    boxes = []
    for x, y, w, h, area in stats[1:]:
        if area < 400:
            continue
        x0, y0 = max(0, x + 10), max(0, y + 8)          # undo most of the dilation, keep a little air
        boxes.append([x0, y0, min(1920, x + w - 10) - x0, min(1080, y + h - 8) - y0])
    return boxes


def layout(boxes, scale):
    """Target (x, y, s) for each box in the vertical frame."""
    placed = []
    order = sorted(range(len(boxes)), key=lambda i: boxes[i][1])
    out = [None] * len(boxes)
    for i in order:
        x, y, w, h = boxes[i]
        s = min(scale, (W - 2 * MARGIN) / w)
        tw, th = w * s, h * s
        cx, cy = (x + w / 2) / 1920, (y + h / 2) / 1080
        if cx < 0.36:
            tx = MARGIN
        elif cx > 0.64:
            tx = W - MARGIN - tw
        else:
            tx = (W - tw) / 2
        ty = SAFE_TOP + cy * (SAFE_BOTTOM - SAFE_TOP) - th / 2
        ty = min(max(ty, SAFE_TOP), SAFE_BOTTOM - th)
        moved = True
        while moved:                                      # push down past anything it would overlap
            moved = False
            for px, py, pw, ph in placed:
                if tx < px + pw + 24 and px < tx + tw + 24 and ty < py + ph + 30 and py < ty + th + 30:
                    ty = py + ph + 30
                    moved = True
        placed.append((tx, ty, tw, th))
        out[i] = (int(round(tx)), int(round(ty)), s)
    return out


def edge_colour(frames):
    f = frames[min(15, len(frames) - 1)]
    return np.median(np.concatenate([f[:6].reshape(-1, 3), f[-6:].reshape(-1, 3)]), 0).astype(np.uint8)


def convert(n):
    p = PRESETS[n]
    frames, fps = read_all(src_path(n))
    out_frames = []
    if p["mode"] == "blocks":
        boxes = find_blocks(frames, p.get("kernel", (70, 46)))
        plan = layout(boxes, p["scale"])
        for f in frames:
            canvas = np.zeros((H, W, 3), np.uint8)
            for (x, y, w, h), (tx, ty, s) in zip(boxes, plan):
                piece = cv2.resize(f[y:y + h, x:x + w], (max(1, int(w * s)), max(1, int(h * s))),
                                   interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
                ph, pw = piece.shape[:2]
                region = canvas[ty:ty + ph, tx:tx + pw]
                np.maximum(region, piece[:region.shape[0], :region.shape[1]], out=region)
            out_frames.append(canvas)
    elif p["mode"] == "iris":
        for f in frames:
            canvas = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)   # tall oval iris, cut edges hide under IG UI
            white = (f.min(2) > 200) | ((f[..., 2] > 180) & (f[..., 1] < 80))   # REC text and its red dot
            ys, xs = np.nonzero(white)
            if len(xs):
                x0, x1, y0, y1 = xs.min() - 4, xs.max() + 5, ys.min() - 4, ys.max() + 5
                sx, sy = W / 1920, H / 1080                       # cover the stretched copy with the circle colour
                bx0, bx1, by0, by1 = int(x0 * sx) - 6, int(x1 * sx) + 6, int(y0 * sy) - 6, int(y1 * sy) + 6
                fill = np.median(canvas[by0 - 20:by0 - 4, bx0:bx1].reshape(-1, 3), 0)
                canvas[by0:by1, bx0:bx1] = fill.astype(np.uint8)
                piece, m = f[y0:y1, x0:x1], white[y0:y1, x0:x1]
                tx, ty = (W - (x1 - x0)) // 2, (H - (y1 - y0)) // 2
                region = canvas[ty:ty + y1 - y0, tx:tx + x1 - x0]
                region[m] = piece[m]
            out_frames.append(canvas)
    else:
        s = p["scale"]
        pad = edge_colour(frames) if p["pad"] == "edge" else np.zeros(3, np.uint8)
        for f in frames:
            sw, sh = int(1920 * s), int(1080 * s)
            g = cv2.resize(f, (sw, sh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
            canvas = np.empty((H, W, 3), np.uint8)
            canvas[:] = pad
            x0, y0 = (W - sw) // 2, (H - sh) // 2
            sx0, sy0 = max(0, -x0), max(0, -y0)
            dx0, dy0 = max(0, x0), max(0, y0)
            cw, ch = min(sw - sx0, W - dx0), min(sh - sy0, H - dy0)
            canvas[dy0:dy0 + ch, dx0:dx0 + cw] = g[sy0:sy0 + ch, sx0:sx0 + cw]
            out_frames.append(canvas)
    dst = vert_path(n)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-i", str(src_path(n)), "-map", "0:v", "-map", "1:a?",
           "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy",
           "-shortest", str(dst)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in out_frames:
        proc.stdin.write(f.tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"V{n} -> {dst.relative_to(PACK.parent.parent)}")


class Overlay:
    """Frames of one pack design, by number. t past the end holds the last frame (the 'stretch' trick)."""

    def __init__(self, n, vertical=True, hold=True):
        self.frames, self.fps = read_all(vert_path(n) if vertical else src_path(n))
        self.hold = hold

    def frame(self, t):
        if t < 0:
            return None
        i = int(t * self.fps)
        if i >= len(self.frames):
            if not self.hold:
                return None
            i = len(self.frames) - 1
        return self.frames[i]


def screen(base, ov, opacity=1.0):
    """Screen blend: black vanishes, white stays white. base/ov uint8 BGR, same size."""
    if ov is None:
        return base
    b = base.astype(np.float32) / 255
    o = ov.astype(np.float32) / 255 * opacity
    return ((1 - (1 - b) * (1 - o)) * 255 + 0.5).astype(np.uint8)


def keyed(base, ov, key=(91, 107, 165), tol=60, soft=30, mode="screen"):
    """Key one colour (RGB) out of a full-frame design so the footage shows there, then lay the rest on top.
    mode "normal" keeps dark parts dark (the black VLOG letters of 7, the iris edge of 12)."""
    if ov is None:
        return base
    k = np.array(key[::-1], np.float32)
    d = np.linalg.norm(ov.astype(np.float32) - k, axis=2)
    a = np.clip((d - tol) / soft, 0, 1)[..., None]             # 0 where the key colour is: footage shows
    top = ov if mode == "normal" else screen(base, ov)
    return (base * (1 - a) + top * a + 0.5).astype(np.uint8)


def sheet(out):
    tiles = []
    for n in range(1, 13):
        frames, _ = read_all(vert_path(n))
        comp = np.max(np.stack(frames[::3]), 0)
        cv2.putText(comp, f"V{n}", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 255, 255), 8)
        cv2.rectangle(comp, (0, SAFE_TOP), (W - 1, SAFE_BOTTOM), (60, 60, 60), 3)
        tiles.append(cv2.resize(comp, (360, 640)))
    rows = [np.hstack(tiles[i:i + 6]) for i in (0, 6)]
    cv2.imwrite(out, np.vstack(rows))
    print(out)


def apply(base, out, specs):
    cap = cv2.VideoCapture(base)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    ovs = []
    for s in specs:
        n, rest = s.split("@")
        start, _, dur = rest.partition(":")
        ovs.append((int(n), Overlay(int(n)), float(start), float(dur) if dur else None))
    ok, f = cap.read()
    h, w = f.shape[:2]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps),
           "-i", "-", "-i", base, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    i = 0
    while ok:
        t = i / fps
        for n, ov, t0, dur in ovs:
            if t < t0 or (dur is not None and t > t0 + dur):
                continue
            o = ov.frame(t - t0)
            if o is not None and o.shape[:2] != (h, w):
                o = cv2.resize(o, (w, h))
            if n == 7:
                f = keyed(f, o, key=(0, 0, 160), mode="normal")
            elif n == 12:
                f = keyed(f, o, mode="normal")
            else:
                f = screen(f, o)
        proc.stdin.write(f.tobytes())
        ok, f = cap.read()
        i += 1
    proc.stdin.close()
    proc.wait()
    print(out, "(overlay SFX not mixed in; mix them in the audio pass)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["vertical", "sheet", "apply"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--ov", action="append", default=[])
    a = ap.parse_args()
    if a.cmd == "vertical":
        for n in (map(int, a.args) if a.args else range(1, 13)):
            convert(n)
    elif a.cmd == "sheet":
        sheet(a.args[0] if a.args else "vertical_sheet.jpg")
    else:
        apply(a.args[0], a.args[1], a.ov)
