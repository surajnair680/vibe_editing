"""Split the Automance logo into animatable layers.

Each layer is an RGBA PNG at final 1920x1080 scale (the reference padded with white and
scaled by H/1024), made with "colour to alpha" over white so black ink and the red parts
keep their exact look. Composited over white, all layers together give back the reference.

Run: python3 work/layers.py   -> work/layers/<name>.png + work/layers/boxes.json
"""
import json, os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "refs", "automance-logo-final-frame.jpg")
OUT = os.path.join(HERE, "layers")
W, H = 1920, 1080

# seam between car and bike: the white diagonal gap, x = SEAM_X0 - SEAM_K*(y-420) in source px
SEAM_X0, SEAM_K = 862.0, 0.338
ROAD_CAR_Y = 392   # in the merged car/road piece, ink above this row is the road
GROUND_Y = 684     # rows from here down (in the vehicle band) are the ground line


def color_to_alpha(img):
    """img float 0..1 BGR on white -> (rgb, alpha) with rgb unpremultiplied."""
    a = 1.0 - img.min(axis=2)
    a = np.clip((a - 0.04) / 0.92, 0, 1)          # clean paper noise, keep full ink
    rgb = (img - (1 - a[..., None])) / np.maximum(a[..., None], 1e-3)
    return np.clip(rgb, 0, 1), a


def main():
    os.makedirs(OUT, exist_ok=True)
    im = cv2.imread(SRC)
    h0, w0 = im.shape[:2]
    s = H / h0
    sw = round(w0 * s)
    big = cv2.resize(im, (sw, H), interpolation=cv2.INTER_LANCZOS4)
    canvas = np.full((H, W, 3), 255, np.uint8)
    ox = (W - sw) // 2
    canvas[:, ox:ox + sw] = big
    cv2.imwrite(os.path.join(OUT, "reference_1080.png"), canvas)

    # labels from the source-res connected components, then scaled up (nearest)
    ink = (im.min(2) < 170).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(ink, 8)
    yy, xx = np.mgrid[0:h0, 0:w0]
    part = np.zeros((h0, w0), np.int32)     # 0 none
    names = {}

    def put(mask, name):
        if name not in names:
            names[name] = len(names) + 1
        part[mask] = names[name]

    seam = SEAM_X0 - SEAM_K * (yy - 420)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        m = lab == i
        cx, cy = x + w / 2, y + h / 2
        if y >= 850:                                   # tagline row
            if w > 100:
                put(m & (xx < w0 / 2), "tag_line_l"); put(m & (xx >= w0 / 2), "tag_line_r")
            elif w < 8 and h > 20:
                put(m, "tag_bar")
            else:
                put(m, "tag_letters")
        elif y >= 700:                                 # AUTOMANCE letters
            idx = int(np.searchsorted([180, 400, 540, 690, 845, 1025, 1170, 1310], cx))
            put(m, f"letter_{idx}")
        elif cy < 260 and x > 850 and w < 140:
            put(m, "sun")
        elif y < 380 and x > 720 and h < 130:
            put(m, "mountains" if y < 300 else "road_far")
        elif y < 360 and x < 700 and w > 300 and h < 200:        # skyline + near road sweep
            put(m & (yy < 357) & (xx < 735), "skyline")
            put(m & ~((yy < 357) & (xx < 735)), "road_near")
        elif a > 1000:                                 # vehicles band
            road = m & (yy < ROAD_CAR_Y) & (xx > 700) & (xx < 1000)
            gnd = m & (yy >= GROUND_Y)
            rest = m & ~road & ~gnd
            put(road, "road_near")
            put(gnd, "ground")
            put(rest & (xx < seam), "car")
            put(rest & (xx >= seam), "bike")
        else:
            # small bits: assign by position
            if 690 > cy > 380:
                put(m, "car" if cx < SEAM_X0 - SEAM_K * (cy - 420) else "bike")
            else:
                put(m, "misc")

    # grow labels a few px so anti-aliased edges belong to their piece
    for _ in range(4):
        grown = cv2.dilate(part.astype(np.float32), np.ones((3, 3), np.uint8)).astype(np.int32)
        part = np.where(part == 0, grown, part)
    part_big = cv2.resize(part.astype(np.float32), (sw, H), interpolation=cv2.INTER_NEAREST).astype(np.int32)
    lbl = np.zeros((H, W), np.int32)
    lbl[:, ox:ox + sw] = part_big

    rgb, alpha = color_to_alpha(canvas.astype(np.float32) / 255)
    boxes = {}
    claimed = np.zeros((H, W), bool)
    for name, k in names.items():
        m = lbl == k
        claimed |= m
        a = alpha * m
        ys, xs = np.where(a > 0.02)
        if len(xs) == 0:
            continue
        boxes[name] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
        rgba = np.dstack([rgb, a]) * 255
        cv2.imwrite(os.path.join(OUT, f"{name}.png"), rgba.astype(np.uint8))
    left = alpha * (~claimed)
    print("unclaimed ink (max alpha, px>0.3):", float(left.max()), int((left > 0.3).sum()))
    json.dump(boxes, open(os.path.join(OUT, "boxes.json"), "w"), indent=1)
    print(json.dumps(boxes))


if __name__ == "__main__":
    main()
