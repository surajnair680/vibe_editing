# Reference "reel title" animation the clone must rediscover: card slides up with an overshoot, words pop in staggered.
import numpy as np, subprocess
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,N=540,960,30,60
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",54)
def back(t,s=1.70158): t-=1; return t*t*((s+1)*t+s)+1
def cubic_out(t): return 1-(1-t)**3
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-pix_fmt","yuv420p","-crf","16","ref.mp4"],stdin=subprocess.PIPE)
words=["3","GYM","MISTAKES"]
for i in range(N):
    t=i/FPS; im=Image.new("RGB",(W,H),(18,18,22)); d=ImageDraw.Draw(im)
    u=min(max((t-0.3)/0.5,0),1); y=int(560+ (1-back(u))*220) if u>0 else None
    if y is not None:
        d.rounded_rectangle([60,y,480,y+170],28,fill=(255,214,0))
        x=90
        for k,w in enumerate(words):
            v=min(max((t-0.6-0.1*k)/0.25,0),1); a=cubic_out(v)
            if a>0:
                c=tuple(int(255*(1-a)+20*a) for _ in range(1)) ; col=(int(255+(20-255)*a),int(214+(20-214)*a),int(0+20*a))
                d.text((x,y+55+int((1-a)*30)),w,font=font,fill=col)
            x+=d.textlength(w+" ",font=font)
    p.stdin.write(np.asarray(im).tobytes())
p.stdin.close(); p.wait()
