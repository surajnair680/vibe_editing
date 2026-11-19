"""Per-frame person matte of the rough cut v3 (out/reel-12-rough-v3.mp4) for the face circle.
Usage: python3 work/mg/matte_frames.py <first_frame> <last_frame>   (edit frames at 30 fps, inclusive)
Writes work/matte_v3/NNNNN.png (8-bit alpha, 1080x1920), largest component only. Skips frames already done.
rembg u2net_human_seg (clean on his room footage, mic and hand included). Hair-edge cleanup happens at compose time
(manga.face_circle)."""
import os, sys, subprocess
import numpy as np, cv2
from rembg import remove, new_session
a, b = int(sys.argv[1]), int(sys.argv[2])
os.makedirs("work/matte_v3", exist_ok=True)
sess = new_session("u2net_human_seg")
W, H = 1080, 1920
p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a / 30:.4f}", "-i", "out/reel-12-rough-v3.mp4", "-frames:v",
                      str(b - a + 1), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
for n in range(a, b + 1):
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    out = f"work/matte_v3/{n:05d}.png"
    if os.path.exists(out):
        continue
    im = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    m = np.array(remove(im, session=sess, only_mask=True))
    k, lab, st, _ = cv2.connectedComponentsWithStats((m > 128).astype(np.uint8))
    if k > 1:
        keep = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        m = np.where(cv2.dilate((lab == keep).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0, m, 0)
    cv2.imwrite(out, m)
    if n % 30 == 0:
        print(n, flush=True)
print("done", a, b, flush=True)
