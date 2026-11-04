# Rebuild reel-05
1. `python3 work/layers.py` splits `refs/automance-logo-final-frame.jpg` into layers in `work/layers/` (not in git).
2. Stills: `python3 work/scene.py still 0.0 0.1 ...` then `python3 work/sheet.py out/contact_sheet.png 4 480`.
3. Video: `python3 work/scene.py render $PWD/out/reel-05-master.mp4` (`--scale 0.5` for a draft). About 1.5 min.
