# reel-17 render instructions

Raw: `raw/part1.mp4`, `raw/part2.mp4`, `raw/part3.mp4` (one pull-up set split in three 11 s uploads; not in git, ask again if gone).
Panel: `assets/berserk_panel.jpg`. Placement ref: `refs/mockup2_position.jpg`.

1. Join video: `ffmpeg -f concat -safe 0 -i work/concat.txt -map 0:v -c copy work/cache/src.mp4` (fix paths in concat.txt).
2. Audio: decode each part to `work/audio/partN.wav` (mono 48k), join trimmed to 11.0 / 11.0 / 11.0667 s -> `work/audio/full.wav`.
3. Render: `python3 work/render.py` -> `out/reel-17-v1.mp4` (matte cached in `work/cache/alpha/`, ~0.7 s a frame).
4. Preview: 720x1280 crf 24 -> `out/reel-17-v1-preview.mp4`.

Timeline page: https://claude.ai/artifact/JddNWSJwLTepHKWBEJHYpK (tools/timeline, `work/timeline/`).
