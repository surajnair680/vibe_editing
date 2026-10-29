"""v2 cut-out of raw/c07_back_photo.jpg -> work/matte/c07_alpha.png (phone kept in the silhouette)."""
import os, numpy as np, cv2
from rembg import remove, new_session
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
src = cv2.imread("raw/c07_back_photo.jpg"); rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
u = np.asarray(remove(rgb, session=new_session("u2net"), only_mask=True)).astype(np.float32) / 255
i = np.asarray(remove(rgb, session=new_session("isnet-general-use"), only_mask=True)).astype(np.float32) / 255
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
    output_confidence_masks=True))
p = 1 - seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))).confidence_masks[0].numpy_view()
pm = cv2.dilate((p > 0.3).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))).astype(np.float32)
a = np.maximum(u, i * pm)                                                   # u2net body, isnet adds the hand
cv2.fillPoly(a, [np.array([[283, 478], [427, 474], [433, 748], [289, 752]], np.int32)], 1.0)   # the phone
for y in range(1450, a.shape[0]):                                           # waistband solid to the edge
    xs = np.flatnonzero(a[y] > 0.5)
    if xs.size: a[y, xs[0]:xs[-1] + 1] = 1
b = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
n, lab, st, _ = cv2.connectedComponentsWithStats(b); b = (lab == 1 + int(np.argmax(st[1:, 4]))).astype(np.float32)
al = np.clip((cv2.GaussianBlur(b, (0, 0), 2.2) - 0.5) * 2.5 + 0.5, 0, 1)
cv2.imwrite("work/matte/c07_alpha.png", (al * 255).astype(np.uint8))
