import cv2, numpy as np
p = cv2.imread('poster_crop.png'); g0 = cv2.cvtColor(p, cv2.COLOR_BGR2GRAY)
L = g0.astype(np.float32)
bright = np.clip((L-45)/(215-45), 0, 1)
dark = np.clip((200-L)/(200-60), 0, 1)
# regions: panels positive, margin inverted, katakana positive
pos = np.zeros_like(L)
pos[117:476, 17:347] = 1; pos[484:532, 17:136] = 1
n, lab, st, _ = cv2.connectedComponentsWithStats((g0>150).astype(np.uint8), 8)
counters = {2,3,4,6,7,8}
kata = np.zeros(L.shape, np.uint8)
for i in range(2, n):
    x,y,w,h,a = st[i]
    if y < 117 and a >= 50 and i not in counters: kata[lab==i] = 1
kata = cv2.dilate(kata, np.ones((5,5),np.uint8))
pos = np.maximum(pos, kata.astype(np.float32))
a_poster = pos*bright + (1-pos)*dark
band = np.zeros(L.shape, np.uint8)
for (y0,y1,x0_,x1_) in [(117,476,17,347),(484,532,17,136)]:
    cv2.rectangle(band, (x0_,y0), (x1_-1,y1-1), 1, 5)   # 5 px wide band on the border
band[kata>0] = 0                                         # keep katakana crossing the top edge
a_poster[band>0] = np.minimum(a_poster[band>0], pos[band>0]*bright[band>0]*0)
cv2.imwrite('alpha_poster.png', (a_poster*255).astype(np.uint8))

tee = cv2.imread('tee_blank.png').astype(np.float32)/255
H, W = tee.shape[:2]
pw = 450; ph = round(pw*p.shape[0]/p.shape[1])
a = np.clip(cv2.resize(a_poster, (pw, ph), interpolation=cv2.INTER_LANCZOS4), 0, 1)
top = 355; x0 = W//2 - pw//2
alpha = np.zeros((H, W), np.float32); alpha[top:top+ph, x0:x0+pw] = a
g = cv2.cvtColor(tee, cv2.COLOR_BGR2GRAY)
gb = cv2.GaussianBlur(g, (0,0), 8)
dx = cv2.Sobel(gb, cv2.CV_32F, 1, 0, ksize=3); dy = cv2.Sobel(gb, cv2.CV_32F, 0, 1, ksize=3)
s = 1.5 / (np.percentile(np.abs(np.r_[dx[300:1100,200:820].ravel(), dy[300:1100,200:820].ravel()]), 99) + 1e-6)
mx, my = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
alpha = cv2.remap(alpha, mx + dx*s, my + dy*s, cv2.INTER_LINEAR)       # ~1.5 px bend at folds
local = cv2.GaussianBlur(g, (0,0), 3) / (cv2.GaussianBlur(g, (0,0), 40) + 1e-4)
shade = np.clip(1 + (local-1)*0.8, 0.82, 1.1)
rng = np.random.default_rng(3)
tex = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0,0), 0.7)
ink = np.array([0.84, 0.87, 0.88], np.float32)
inkc = ink[None,None,:] * (shade*(1 + tex*0.03))[...,None]
alpha = np.clip(alpha*(0.95 + tex*0.03), 0, 1)
out = tee*(1-alpha[...,None]) + inkc*alpha[...,None]
o8 = (np.clip(out,0,1)*255).astype(np.uint8)
cv2.imwrite('berserk_tee_back.png', o8)
cv2.imwrite('detail.png', o8[top-15:top+330, x0-15:x0+pw+15])
cv2.imwrite('detail2.png', o8[top+ph-200:top+ph+15, x0-15:x0+pw+15])
