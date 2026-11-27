"""Codex-widened photo -> 1920x1080, with the ORIGINAL photo pasted back over the centre
(feathered edge) so people and garments are untouched. Codex only supplies the sides.
python3 work/make_wide.py <key> <crop_y 0..1>"""
import sys, cv2, numpy as np
SRC = {'hang': '33coats.jpg', 'spin': 'KullviWhims_ZAZI_by_JanneHoevelaken74.jpg',
       'pair': 'Our_story_0002_Zazi-fall-winter-campaign-22-photographer-Dolly-Devi-94.jpg',
       'shop': 'ZAZI_Boutique_by_JanneHoevelaken14.jpg'}
k = sys.argv[1]; cy = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
orig = cv2.imread('refs/site/img/' + SRC[k]).astype(np.float32)[4:-4, 4:-4]  # some site photos carry a 1-2 px white border
wide = cv2.imread(f'work/outpaint/{k}_wide.png').astype(np.float32)
W, H = 1920, 1280
wide = cv2.resize(wide, (W, H), interpolation=cv2.INTER_LANCZOS4)
# original placed at full height in the centre (as sent to Codex), refined by ECC
s = H / orig.shape[0]; ow = round(orig.shape[1] * s)
o = cv2.resize(orig, (ow, H), interpolation=cv2.INTER_AREA)
x0 = (W - ow) // 2
warp = np.array([[1, 0, x0], [0, 1, 0]], np.float32)
g1 = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY); g2 = cv2.cvtColor(wide, cv2.COLOR_BGR2GRAY)
try:
    _, warp = cv2.findTransformECC(g1, g2, warp, cv2.MOTION_TRANSLATION,
                                   (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1e-5), None, 5)
except cv2.error as e:
    print('ECC failed, using centre', e)
print(k, 'offset', warp[:, 2] - [x0, 0])
# Codex copies the photo's thin border line into its output: inpaint a band at both original edges
band = np.zeros((H, W), np.uint8)
for xe in (x0, x0 + ow - 1):
    band[:, max(0, xe - 6):min(W, xe + 7)] = 255
wide = cv2.inpaint(np.clip(wide, 0, 255).astype(np.uint8), band, 5, cv2.INPAINT_TELEA).astype(np.float32)
# colour match codex sides to the original on the shared area
mask_full = np.zeros((H, W), np.float32)
placed = cv2.warpAffine(o, warp, (W, H))
m = cv2.warpAffine(np.ones(o.shape[:2], np.float32), warp, (W, H))
inner = cv2.erode(m, np.ones((15, 15), np.uint8))
sel = inner > 0.5
for c in range(3):
    a = wide[..., c][sel]; b = placed[..., c][sel]
    wide[..., c] = (wide[..., c] - a.mean()) / (a.std() + 1e-6) * b.std() + b.mean()
# soften Codex sides to the original's sharpness, then carry the low-frequency tone difference
# across the seam (measured just inside the original's edge, fading out over 350 px)
wide = cv2.GaussianBlur(wide, (0, 0), float(sys.argv[3]) if len(sys.argv) > 3 else 1.2)
inside = cv2.erode(m, np.ones((61, 61), np.uint8))
lp = lambda x: cv2.GaussianBlur(x, (0, 0), 25)
wsum = lp(inside)[..., None] + 1e-4
diff = (lp(placed * inside[..., None]) - lp(wide * inside[..., None])) / wsum
cols = np.where(inside.max(0) > 0.5)[0]; L, R = cols.min() + 30, cols.max() - 30
d = diff.copy()
xs = np.arange(W)
d[:, :L] = diff[:, L:L + 1]; d[:, R:] = diff[:, R:R + 1]
fade = np.clip(1 - np.maximum(L - xs, xs - R).clip(0) / 350.0, 0, 1)[None, :, None]
wide = wide + d * fade
# feathered paste: 110 px ramp inside the original's edge
feather = cv2.GaussianBlur(cv2.erode(m, np.ones((121, 121), np.uint8)), (0, 0), 30)[..., None]
out = placed * feather + wide * (1 - feather)
y0 = int(round((H - 1080) * cy))
out = np.clip(out[y0:y0 + 1080], 0, 255).astype(np.uint8)
cv2.imwrite(f'assets/wide/{k}.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 95])
