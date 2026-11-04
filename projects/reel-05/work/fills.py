"""White body fills for the car and bike so they look solid (like the storyboard), not see-through.
Car: hand-traced outer silhouette (source px of the logo, on the stroke centre lines).
Bike: closing + hole fill, eroded a little so it stays under the strokes.
Also a tyre disc for the car (black in the night/sunrise part, fades before the lock).
-> work/layers/car_fill.png, bike_fill.png, car_tyre.png (full 1920x1080 masks)"""
import json, os, cv2, numpy as np
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
LAY = os.path.join(HERE, "layers")
S, OX = 1080 / 1024, (1920 - round(1536 * 1080 / 1024)) // 2   # source -> 1080 canvas

CAR = [(274, 546), (296, 570), (272, 594), (272, 622), (250, 662), (400, 671), (560, 680), (771, 686),
       (873, 385), (800, 388), (730, 409), (660, 437), (610, 455), (540, 459), (480, 468), (420, 482),
       (370, 500), (320, 520)]
TYRE = (542, 626, 84)    # centre x, y, radius in source px


def to_canvas(pts):
    return np.array([[OX + x * S, y * S] for x, y in pts], np.float32)


def main():
    car = np.zeros((1080, 1920), np.uint8)
    cv2.fillPoly(car, [np.round(to_canvas(CAR) * 8).astype(np.int32)], 255, cv2.LINE_AA, shift=3)
    cv2.imwrite(os.path.join(LAY, "car_fill.png"), car)
    ty = np.zeros_like(car)
    cx, cy = to_canvas([TYRE[:2]])[0]
    cv2.circle(ty, (int(cx * 8), int(cy * 8)), int(TYRE[2] * S * 8), 255, -1, cv2.LINE_AA, shift=3)
    ty[int(683 * S):] = 0                      # keep it above the ground line
    cv2.imwrite(os.path.join(LAY, "car_tyre.png"), ty)

    im = cv2.imread(os.path.join(LAY, "bike.png"), -1)
    ink = (im[..., 3] > 90).astype(np.uint8)
    cl = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
    fill = ndimage.binary_fill_holes(cl).astype(np.uint8)
    fill = cv2.erode(fill, np.ones((5, 5), np.uint8))
    fill = np.maximum(fill, ink)
    cv2.imwrite(os.path.join(LAY, "bike_fill.png"), cv2.GaussianBlur(fill.astype(np.float32) * 255, (0, 0), 0.8).astype(np.uint8))


if __name__ == "__main__":
    main()
