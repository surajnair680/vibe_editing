#!/usr/bin/env python3
"""Track an element in video frames by colour (vibe editing addition to reanimate).

A video or reel reference has no DOM, so capture.ts can't give a track.json. This finds the pixels close to a
colour in each frame (optionally inside a region) and writes their box per frame: x, y, w, h, cx, cy and
coverage (share of the region, a stand-in for opacity or scale). Print one property as a series for easing.ts:

  python3 track_color.py ref/frames --color ffd600 --tol 40 --fps 30 --out ref/track-card.json
  python3 track_color.py ref/frames --color ffd600 --fps 30 --series y > y.json
  bun <skill>/scripts/easing.ts --series "$(cat y.json)"

--region x,y,w,h limits the search (pixels of the frames). Frames where the colour is absent get null and are
left out of --series. Several elements: run once per colour or per region.
"""
import argparse, json, sys, glob, os
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("frames"); ap.add_argument("--color", required=True); ap.add_argument("--tol", type=float, default=40)
ap.add_argument("--fps", type=float, default=30); ap.add_argument("--region"); ap.add_argument("--min-px", type=int, default=30)
ap.add_argument("--out"); ap.add_argument("--series", choices=["x", "y", "w", "h", "cx", "cy", "coverage"])
a = ap.parse_args()
target = np.array([int(a.color[i:i + 2], 16) for i in (0, 2, 4)], float)
files = sorted(glob.glob(os.path.join(a.frames, "*.png")))
rx = ry = 0
rows = []
for i, f in enumerate(files):
    im = np.asarray(Image.open(f).convert("RGB"), float)
    if a.region:
        rx, ry, rw, rh = map(int, a.region.split(",")); im = im[ry:ry + rh, rx:rx + rw]
    m = np.linalg.norm(im - target, axis=2) < a.tol
    t = round(i * 1000 / a.fps, 1)
    if m.sum() < a.min_px:
        rows.append({"t": t, "frame": i}); continue
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min() + rx, xs.max() + rx, ys.min() + ry, ys.max() + ry
    rows.append({"t": t, "frame": i, "x": int(x0), "y": int(y0), "w": int(x1 - x0 + 1), "h": int(y1 - y0 + 1),
                 "cx": float(xs.mean() + rx), "cy": float(ys.mean() + ry), "coverage": float(m.mean())})
if a.out:
    json.dump({"fps": a.fps, "color": a.color, "frames": rows}, open(a.out, "w"), indent=1)
if a.series:
    print(json.dumps([[r["t"], r[a.series]] for r in rows if a.series in r]))
elif not a.out:
    json.dump(rows, sys.stdout, indent=1)
