"""Cut the back photo (raw/c07_back_photo.jpg) out: rembg edges x MediaPipe person mask -> work/sil/alpha.png"""
import numpy as np, cv2, sys
from rembg import remove, new_session
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
import os
src = cv2.imread("raw/c07_back_photo.jpg")
rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
a1 = remove(rgb, session=new_session("u2net_human_seg"), only_mask=True)
a1 = np.asarray(a1).astype(np.float32) / 255
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.expanduser("~/.cache/vibe/selfie_multiclass.tflite")),
    output_confidence_masks=True))
r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
person = 1 - r.confidence_masks[0].numpy_view()          # class 0 = background
pm = cv2.dilate((person > 0.3).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))).astype(np.float32)
pm = cv2.GaussianBlur(pm, (0, 0), 3)
alpha = np.clip(a1 * pm, 0, 1)
cv2.imwrite("work/sil/alpha_rembg.png", (a1 * 255).astype(np.uint8))
cv2.imwrite("work/sil/alpha_mp.png", (person * 255).astype(np.uint8))
cv2.imwrite("work/sil/alpha.png", (alpha * 255).astype(np.uint8))
