"""contact sheet of out/stills/t_*.png with time labels. python3 work/sheet.py out/sheet.png [cols] [width]"""
import cv2, glob, os, sys, numpy as np
out = sys.argv[1]; cols = int(sys.argv[2]) if len(sys.argv) > 2 else 4; tw = int(sys.argv[3]) if len(sys.argv) > 3 else 480
fs = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "stills", "t_*.png")))
tiles = []
for f in fs:
    im = cv2.imread(f); im = cv2.resize(im, (tw, im.shape[0] * tw // im.shape[1]), interpolation=cv2.INTER_AREA)
    lab = os.path.basename(f)[2:-4].lstrip("0") or "0"; lab = ("0" + lab if lab.startswith(".") else lab) + " s"
    cv2.rectangle(im, (0, 0), (92, 30), (0, 0, 0), -1); cv2.putText(im, lab, (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(im, (0, 0), (im.shape[1] - 1, im.shape[0] - 1), (128, 128, 128), 1)
    tiles.append(im)
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
cv2.imwrite(out, np.vstack(rows))
