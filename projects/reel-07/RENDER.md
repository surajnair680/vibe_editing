# reel-07 render instructions
1. Put the template reel at `raw/template.mp4` (720x1280, 60 fps, 11.88 s; not in git, ask the user to upload it again).
2. `python3 work/caption.py work/caption.png` (Inter SemiBold 59 px, two lines, bottom at y 542 of 1080x1920).
3. `work/build.sh out/reel-07-final.mp4` (crf 16, audio copied bit-exact from the template).
Checks done on v1: 713 video frames (same as the template), audio MD5 identical to the template, no black frames
in the picture band, channel mark gone (crop 24 px left = 4.6% zoom), first and last frames checked.
