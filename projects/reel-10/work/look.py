"""reel-10 look: film grain for a raw, authentic feel.

Grain is a seeded bank of 16 noise fields (cached), picked per frame so it moves like film.
Size: noise made at 1/size resolution and upscaled, so each grain is about `size` px.
Strength is the grain's standard deviation in 0..1 units, weighted toward the midtones
(film grain shows least in pure black and pure white).

    from look import Grain;  g = Grain(1080, 1920, strength=0.06);  frame = g(frame, n)
"""
import cv2, numpy as np


class Grain:
    def __init__(self, w, h, strength=0.06, size=1.6, bank=16, seed=10):
        self.w, self.h, self.s = w, h, strength
        rng = np.random.default_rng(seed)
        sw, sh = int(w / size) + 2, int(h / size) + 2
        self.bank = []
        for _ in range(bank):
            n = rng.normal(0, 1, (sh, sw)).astype(np.float32)
            n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
            n /= n.std() + 1e-6
            self.bank.append(n)

    def __call__(self, img, n):
        if self.s <= 0:
            return img
        f = img.astype(np.float32) / 255.0
        luma = f @ np.float32([0.114, 0.587, 0.299])
        wgt = 0.35 + 0.65 * (4 * luma * (1 - luma))          # midtone weighted, still some in shadows
        g = self.bank[n % len(self.bank)] * (self.s * wgt)
        f += g[..., None]
        return np.clip(f * 255.0 + 0.5, 0, 255).astype(np.uint8)
