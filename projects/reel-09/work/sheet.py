"""Contact sheet: a frame every 2.5 s, labelled. python3 sheet.py <out.png> [step]"""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scene
step = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
ts = list(np.arange(0, scene.DUR - 1e-6, step)) + [scene.DUR - 1 / scene.FPS]
tiles = []
for t in ts:
    im = cv2.resize(scene.frame(t), (324, 576), interpolation=cv2.INTER_AREA)
    im = cv2.copyMakeBorder(im, 0, 44, 4, 4, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    cv2.putText(im, f"{t:.2f} s", (10, 610), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2, cv2.LINE_AA)
    tiles.append(im)
cols = 4
while len(tiles) % cols:
    tiles.append(np.full_like(tiles[0], 255))
rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
cv2.imwrite(sys.argv[1], cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))
