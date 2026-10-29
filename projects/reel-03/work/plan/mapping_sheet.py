"""Reference frame vs the raw clip planned for each beat -> out/mapping_sheet.png (ungraded, for the beat sheet)."""
import subprocess, os, numpy as np, cv2
REF = "raw/reference.mp4"
# (label, ref time, clip, clip time)
BEATS = [
    ("1  0.0-2.6  black + tiny words", 1.0, None, 0),
    ("2  2.6-3.9  breathe.", 3.2, "raw/c06_dark_empty_gym.jpg", 0),
    ("3  3.9-5.0  light snap", 4.3, "raw/c07_back_photo.jpg", 0),
    ("4  5.0-8.9  want it that bad", 6.5, "raw/c02_man_in_gym.mp4", 1.5),
    ("5  8.9-9.2  you'll get", 9.0, "raw/c10_vid_180447.mp4", 0.1),
    ("6  9.2-9.9  a big", 9.5, "raw/c03_vid_164738.mp4", 0.6),
    ("7  9.9-10.3  piece of", 10.1, "raw/c03_vid_164738.mp4", 1.7),
    ("8  10.3-11.0  what you want", 10.6, "raw/c08_vid_185334.mp4", 0.1),
    ("9  11.0-11.8  flurry", 11.5, "raw/c09_vid_201511.mp4", 0.4),
    ("10  11.8-12.4  can happen and", 12.1, "raw/c09_vid_201511.mp4", 0.2),
    ("11  12.4-13.8  become a reality", 13.0, "raw/c05_glow_figure_beach.jpg", 0),
    ("12  13.8-14.5  I believe that", 14.2, "raw/c04_man_turning_head.mp4", 0.3),
    ("13  14.5-15.3  sincerely and", 14.9, "raw/c01_man_walking_gym.mp4", 1.0),
    ("14  15.3-16.0  I'll die on that", 15.4, "raw/c02_man_in_gym.mp4", 3.0),
    ("15  16.0-16.3  thought", 16.1, "raw/c06_dark_empty_gym.jpg", 0),
    ("16  16.3-18.0  okay?", 17.0, "raw/c04_man_turning_head.mp4", 3.2),
    ("17  18.0-22.2  black + tiny words", 19.5, None, 0),
]
def grab(path, t, w=270, h=480):
    if path is None:
        return np.zeros((h, w, 3), np.uint8)
    if path.endswith(".jpg"):
        im = cv2.imread(path)
    else:
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe",
                            "-vcodec", "png", "-"], capture_output=True).stdout
        im = cv2.imdecode(np.frombuffer(b, np.uint8), 1)
    ih, iw = im.shape[:2]                       # cover-fit to 9:16
    s = max(w / iw, h / ih); im = cv2.resize(im, (int(iw * s + 1), int(ih * s + 1)))
    y, x = (im.shape[0] - h) // 2, (im.shape[1] - w) // 2
    return im[y:y + h, x:x + w]
cells = []
for lab, rt, clip, ct in BEATS:
    a, b = grab(REF, rt), grab(clip, ct)
    c = np.full((480 + 44, 270 * 2 + 6, 3), 24, np.uint8)
    c[44:, :270], c[44:, 276:] = a, b
    cv2.putText(c, lab, (6, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA)
    cells.append(c)
while len(cells) % 6: cells.append(np.full_like(cells[0], 0))
rows = [np.hstack([np.pad(x, ((6, 6), (6, 6), (0, 0))) for x in cells[i:i + 6]]) for i in range(0, len(cells), 6)]
os.makedirs("out", exist_ok=True)
cv2.imwrite("out/mapping_sheet.png", np.vstack(rows))
