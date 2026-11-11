"""Render the caption PNG (1080x1920, transparent) for the meme template.
Layout measured from the template at 720x1280: caption lines 51 px apart, text bottom at y=361,
video band y=410..870, logo band 1113..1181 (dropped). Everything x1.5 for 1080x1920."""
from PIL import Image, ImageDraw, ImageFont
import sys
LINES = ["Watching a friend try to build", "his dream body using ChatGPT"]
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
W, H = 1080, 1920
REF_W = 530 * 1.5          # "defense counsel try to build" width in the template, scaled
PITCH = 51 * 1.5           # baseline to baseline
BOTTOM = 361 * 1.5         # lowest descender row of the last line
COLOUR = (240, 241, 242, 255)

def font_for(width_target, sample="defense counsel try to build"):
    lo, hi = 20, 120
    while hi - lo > 0.5:
        m = (lo + hi) / 2
        w = ImageFont.truetype(FONT, int(round(m))).getlength(sample)
        lo, hi = (m, hi) if w < width_target else (lo, m)
    return ImageFont.truetype(FONT, int(round(lo)))

f = font_for(REF_W)
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
asc, desc = f.getmetrics()
last_base = BOTTOM - desc * 0.85
for i, line in enumerate(LINES):
    base = last_base - PITCH * (len(LINES) - 1 - i)
    x = (W - f.getlength(line)) / 2
    d.text((x, base), line, font=f, fill=COLOUR, anchor="ls")
img.save(sys.argv[1] if len(sys.argv) > 1 else "work/caption.png")
print("font size", f.size)
