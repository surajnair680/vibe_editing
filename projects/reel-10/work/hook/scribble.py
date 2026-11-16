"""Red scribble head (reel-10 visual hook background).

A generic head silhouette (head_sil.png, made by Codex) is filled with long tangled red
lines drawn in code, like the reference reel (refs/ref1.mp4). Lines are random walks that
steer back inside the shape when they reach the edge, so the outline comes out denser.
"Boil": a few seeded variants with small per-variant wobble, swapped every 0.5 s.

    python3 scribble.py            -> writes bg_v0.png .. bg_v2.png (1080x1920, black bg)
"""
import cv2, numpy as np, os

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
RED = (18, 14, 228)          # BGR, sampled close to the reference's red
N_VARIANTS = 3


def head_mask():
    sil = cv2.imread(os.path.join(HERE, "head_sil.png"), cv2.IMREAD_GRAYSCALE)
    m = (sil < 128).astype(np.uint8)
    # place: back of skull x 95 -> 60, nose tip x 882 -> 930, head top y 325 -> 576 (ref layout)
    s = (930 - 60) / (882 - 95)
    M = np.float32([[s, 0, 60 - 95 * s], [0, s, 576 - 325 * s]])
    out = cv2.warpAffine(m * 255, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    return (out > 127).astype(np.uint8)


def strokes(mask, seed, n=170):
    rng = np.random.default_rng(seed)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    # gradient of an outside-distance field: points back into the shape
    inv = cv2.distanceTransform(1 - mask, cv2.DIST_L2, 5)
    field = dist - inv
    field = cv2.GaussianBlur(field, (0, 0), 6)
    gy, gx = np.gradient(field)
    ys, xs = np.nonzero(mask)
    ey, ex = np.nonzero((mask > 0) & (dist < 45))
    out = []
    for _ in range(n):
        if rng.random() < 0.55:
            i = rng.integers(len(ex)); x, y = float(ex[i]), float(ey[i])
        else:
            i = rng.integers(len(xs)); x, y = float(xs[i]), float(ys[i])
        a = rng.uniform(0, 2 * np.pi)
        w = 0.0
        L = int(rng.integers(260, 900))
        step = 4.0
        pts = [(x, y)]
        for _k in range(L):
            w = 0.95 * w + rng.normal(0, 0.012)
            a += w
            xi, yi = int(np.clip(x, 0, W - 1)), int(np.clip(y, 0, H - 1))
            if field[yi, xi] < 4:   # near or past the edge: steer inward along the gradient
                ta = np.arctan2(gy[yi, xi], gx[yi, xi])
                d = (ta - a + np.pi) % (2 * np.pi) - np.pi
                a += 0.22 * d
            x += step * np.cos(a); y += step * np.sin(a)
            if not (-20 < x < W + 20 and -20 < y < H + 40):
                break
            pts.append((x, y))
        out.append(np.array(pts, np.float32))
    return out


def render(strk, seed):
    rng = np.random.default_rng(1000 + seed)
    img = np.zeros((H, W, 3), np.uint8)
    for p in strk:
        # small smooth wobble per variant = the boil
        k = len(p)
        t = np.linspace(0, rng.uniform(2, 5) * np.pi, k)
        ph = rng.uniform(0, 2 * np.pi, 2)
        amp = rng.uniform(0.6, 2.2)
        q = p + np.stack([amp * np.sin(t + ph[0]), amp * np.cos(t + ph[1])], 1)
        th = 2 if rng.random() < 0.3 else 1
        shade = rng.uniform(0.5, 1.0)
        col = tuple(int(c * shade) for c in RED)
        cv2.polylines(img, [np.round(q * 4).astype(np.int32)], False, col, th, cv2.LINE_AA, shift=2)
    glow = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.0, glow, 0.25, 0)


def main():
    mask = head_mask()
    base = strokes(mask, seed=7)
    for v in range(N_VARIANTS):
        cv2.imwrite(os.path.join(HERE, f"bg_v{v}.png"), render(base, v))
    print("ok")


if __name__ == "__main__":
    main()
