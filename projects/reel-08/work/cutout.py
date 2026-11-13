# Cut Codex poses out of their white paper: full colour (for multiply over a paper knock), ink lines only
# (for the pen draw-on) and a solid silhouette (the paper knock). Writes film/her/<name>.png, <name>_ink.png,
# <name>_mask.png and film/her/her.json with each crop's size and foot anchor. Run: python3 work/cutout.py
import cv2, numpy as np, json, glob, os
SRC = 'gen'; OUT = 'film/her'; os.makedirs(OUT, exist_ok=True)
def latest(name): return sorted(glob.glob(f'{SRC}/{name}_*.png'))[-1]
def process(img, name, meta):
    a = (255 - img.min(axis=2)).astype(np.float32) / 255           # colour-to-alpha over white
    sil = (a > .07).astype(np.uint8) * 255
    sil = cv2.morphologyEx(sil, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(sil)
    keep = np.zeros_like(sil)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 1500: keep[lab == i] = 255
    ff = keep.copy(); h, w = ff.shape; m = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, m, (0, 0), 255)
    keep = keep | cv2.bitwise_not(ff)                                # fill holes
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    ys, xs = np.where(keep > 0); x0, x1, y0, y1 = xs.min() - 4, xs.max() + 5, ys.min() - 4, ys.max() + 5
    x0, y0 = max(0, x0), max(0, y0)
    crop = img[y0:y1, x0:x1]; k = keep[y0:y1, x0:x1]
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)
    inka = np.clip((bh - 18) / 50, 0, 1) * (g < 150)                  # thin dark lines only
    ink = np.zeros((*g.shape, 4), np.uint8); ink[..., 0], ink[..., 1], ink[..., 2] = 32, 37, 43; ink[..., 3] = (inka * 255).astype(np.uint8)
    full = np.dstack([crop, k])
    cv2.imwrite(f'{OUT}/{name}.png', full); cv2.imwrite(f'{OUT}/{name}_ink.png', ink)
    mk = np.zeros((*k.shape, 4), np.uint8); mk[..., 0], mk[..., 1], mk[..., 2] = 222, 238, 245; mk[..., 3] = k; cv2.imwrite(f'{OUT}/{name}_mask.png', mk)
    ys2, xs2 = np.where(k > 0); foot_y = int(ys2.max()); bottom = xs2[ys2 > foot_y - 40]
    meta[name] = { 'w': int(x1 - x0), 'h': int(y1 - y0), 'footX': int(bottom.mean()), 'footY': foot_y, 'top': int(ys2.min()) }
meta = {}
for nm in ['selfie', 'tired', 'wave']: process(cv2.imread(latest(nm)), nm, meta)
walk = cv2.imread(latest('walk')); a = (255 - walk.min(axis=2)) > 18
cols = a.sum(axis=0) > 2; runs = []; inr = False
for x, c in enumerate(cols):
    if c and not inr: s = x; inr = True
    if not c and inr: runs.append((s, x)); inr = False
if inr: runs.append((s, len(cols)))
runs = [r for r in runs if r[1] - r[0] > 40]
# merge runs closer than 25 px (a hand or ponytail strand split off)
mr = [list(runs[0])]
for r in runs[1:]:
    if r[0] - mr[-1][1] < 6: mr[-1][1] = r[1]
    else: mr.append(list(r))
print('walk frames', mr)
assert len(mr) == 4, mr
H = walk.shape[0]
for i, (s, e) in enumerate(mr):
    pad = np.full((H, e - s + 40, 3), 255, np.uint8); pad[:, 20:20 + e - s] = walk[:, s:e]
    process(pad, f'walk{i}', meta)
json.dump(meta, open(f'{OUT}/her.json', 'w'), indent=1); print(json.dumps(meta))
