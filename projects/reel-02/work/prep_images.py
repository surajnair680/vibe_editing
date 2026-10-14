"""Physique photos -> print pieces in assets/print/ (RGBA PNGs).
    python3 work/prep_images.py
front.png        assets/physique-front.jpg, phone cropped off, warm grade, cream print border.
back_photo.png   assets/physique-back.jpg, warm grade, cream print border.
back_sketch.png  the same crop as a pencil-and-ink sketch on transparent paper (same size, lines up with back_photo).
"""
import sys
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, "vibe"); sys.path.insert(0, ".")
from style import grade

BORDER = 22
CREAM = (238, 233, 222)


def load(p, box):
    return np.asarray(Image.open(p).convert("RGB").crop(box))


def framed(rgb):
    out = np.full((rgb.shape[0] + 2 * BORDER, rgb.shape[1] + 2 * BORDER, 4), (*CREAM, 255), np.uint8)
    out[BORDER:-BORDER, BORDER:-BORDER, :3] = rgb
    return out


def save(a, name):
    Image.fromarray(a).save(f"assets/print/{name}.png"); print(name, a.shape[1], "x", a.shape[0])


front = grade(load("assets/physique-front.jpg", (190, 0, 1072, 1400)))
save(framed(np.clip((front.astype(np.float32) - 128) * 1.05 + 128, 0, 255).astype(np.uint8)), "front")

back = load("assets/physique-back.jpg", (60, 80, 1500, 1790))
save(framed(grade(back)), "back_photo")

# sketch: colour dodge (gray / inverted blur) gives pencil lines; strong edges get a darker ink pass on top
g = cv2.cvtColor(back, cv2.COLOR_RGB2GRAY).astype(np.float32)
blur = cv2.GaussianBlur(255 - g, (0, 0), 9)
dodge = np.clip(g * 255 / np.maximum(1, 255 - blur), 0, 255)
pencil = 1 - dodge / 255                                                  # 0 = paper, 1 = graphite
pencil = np.clip((pencil - 0.04) / 0.32, 0, 1) ** 0.75
edges = cv2.Canny(cv2.GaussianBlur(g.astype(np.uint8), (0, 0), 2.2), 30, 80).astype(np.float32) / 255
edges = cv2.GaussianBlur(cv2.dilate(edges, np.ones((2, 2), np.uint8)), (0, 0), 0.8)
a = np.clip(np.maximum(pencil * 0.92, edges), 0, 1)
sk = np.zeros(back.shape[:2] + (4,), np.uint8); sk[..., :3] = (20, 19, 18); sk[..., 3] = (a * 255).astype(np.uint8)
paper = np.zeros((sk.shape[0] + 2 * BORDER, sk.shape[1] + 2 * BORDER, 4), np.uint8)
paper[BORDER:-BORDER, BORDER:-BORDER] = sk
save(paper, "back_sketch")
