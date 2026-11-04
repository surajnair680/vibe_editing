# Rebuild reel-05

Chosen version: **v1** (`work/scene.py`, 2.5 s, 1920x1080, 30 fps) with sound `work/mix_v1.py`.
v2 (storyboard version, `work/scene2.py` + `work/mix.py`, 3 s, 60 fps) is kept as an alternative.

1. `python3 work/layers.py` splits `refs/automance-logo-final-frame.jpg` into layers in `work/layers/` (not in git).
   For v2 also `python3 work/fills.py`.
2. Stills: `python3 work/scene.py still 0.0 0.1 ...` then `python3 work/sheet.py out/contact_sheet.png 4 480`.
3. Video: `python3 work/scene.py render $PWD/out/reel-05-v1-master.mp4` (about 1.5 min; `--scale 0.5` for a draft).
4. Sound: `python3 work/mix_v1.py` -> `work/audio/mix_v1.wav` (uses `assets/sfx/*.mp3`, already paid, never regenerate).
5. Final: `ffmpeg -i out/reel-05-v1-master.mp4 -i work/audio/mix_v1.wav -map 0:v -map 1:a -c:v libx264 -crf 16
   -preset slow -pix_fmt yuv420p -g 30 -keyint_min 30 -sc_threshold 0 -c:a aac -b:a 256k -movflags +faststart
   -shortest out/reel-05-final.mp4` (about 1 MB).
