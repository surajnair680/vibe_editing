# Contact sheet with time labels: python3 work/sheet.py <dir> <out.jpg> [cols] [w]
import sys, glob, os, re
from PIL import Image, ImageDraw, ImageFont
d, out = sys.argv[1], sys.argv[2]; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5; w = int(sys.argv[4]) if len(sys.argv) > 4 else 360
fs = sorted(glob.glob(os.path.join(d, 't_*.jpg')), key=lambda f: float(re.findall(r't_([\d.]+)\.jpg', f)[0]))
ims = [Image.open(f) for f in fs]; h = int(ims[0].height * w / ims[0].width); lab = 34
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * w + (cols + 1) * 8, rows * (h + lab) + (rows + 1) * 8), (30, 30, 30)); D = ImageDraw.Draw(S)
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
except Exception: F = ImageFont.load_default()
for i, (f, im) in enumerate(zip(fs, ims)):
    r, c = divmod(i, cols); x = 8 + c * (w + 8); y = 8 + r * (h + lab + 8)
    t = float(re.findall(r't_([\d.]+)\.jpg', f)[0]); D.text((x + 4, y + 5), f'{int(t // 60)}:{t % 60:04.1f}', fill=(255, 255, 255), font=F)
    S.paste(im.resize((w, h), Image.LANCZOS), (x, y + lab))
S.save(out, quality=90); print(out, S.size)
