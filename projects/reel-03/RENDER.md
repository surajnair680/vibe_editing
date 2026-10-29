# reel-03: how to rebuild

Shot-for-shot remake of a reference edit (Tom Platz voiceover) with the user's footage. The audio is the
reference's own track, untouched.

## Inputs (not in git, ask the user to re-upload if the session restarted)
raw/reference.mp4 (the reference reel, audio source), c01_man_walking_gym.mp4, c02_man_in_gym.mp4,
c03_vid_164738.mp4 (deadlift), c04_man_turning_head.mp4, c05_glow_figure_beach.jpg, c06_dark_empty_gym.jpg,
c07_back_photo.jpg, c08_vid_185334.mp4 (lat pulldown), c09_vid_201511.mp4 (mirror pose), c10_vid_180447.mp4 (shoulder press).

## Build (from projects/reel-03)
    python3 work/build/edit.py stills 2.5 5 ...     # check frames -> out/stills/
    python3 work/build/edit.py draft 0 5 --half     # quick low-res range with audio
    python3 work/build/edit.py render               # out/master.mp4, 25 fps, crf 14 (~3 min on 4 cores)

## Delivery
    ffmpeg -i out/master.mp4 -i raw/reference.mp4 -map 0:v -map 1:a -c:v libx264 -crf 22 -preset slow \
      -g 25 -keyint_min 25 -sc_threshold 0 -pix_fmt yuv420p -movflags +faststart -c:a copy -shortest out/reel-03-v2-onefile.mp4
crf 20 (33 MB) is sent as two parts split at 11 s (video copied, audio from work/audio/reference.wav per part).

Timings live in work/build/edit.py (CAPS = captions, TIMELINE = shots), effects in work/build/fx.py.
Beat sheet: brief.md section 5.
