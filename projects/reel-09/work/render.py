"""Render reel-09. python3 render.py <out.mp4> [--draft] [--start a --end b]"""
import argparse, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cv2
import scene

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--draft", action="store_true", help="540x960, crf 26")
ap.add_argument("--start", type=float, default=0.0)
ap.add_argument("--end", type=float, default=scene.DUR)
ap.add_argument("--crf", type=int, default=16)
a = ap.parse_args()
w, h = (540, 960) if a.draft else (scene.W, scene.H)
n0, n1 = round(a.start * scene.FPS), round(a.end * scene.FPS)
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
       "-r", str(scene.FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(26 if a.draft else a.crf),
       "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", "-sc_threshold", "0", "-movflags", "+faststart", a.out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(n0, n1):
    im = scene.frame(n / scene.FPS)
    if a.draft:
        im = cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA)
    p.stdin.write(im.tobytes())
p.stdin.close()
sys.exit(p.wait())
