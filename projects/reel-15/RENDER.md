# reel-15 render instructions (ZAZI coat season promo)

Everything needed is in git except the rendered videos. No raw footage: all photos come from theworldofzazi.com
(`refs/site/img/`, re-download with the URLs in `refs/site/images.json` if needed).

1. Wide photos (Codex outpaint already done, results in `work/outpaint/*_wide.png`):
   `python3 work/make_wide.py hang 0.35 1.8; python3 work/make_wide.py spin 0.3 1.6; python3 work/make_wide.py pair 0.4; python3 work/make_wide.py shop 0.55`
2. Hero parallax layers are committed (`work/parallax/hero/`). To rebuild:
   `python3 tools/parallax.py layers projects/reel-15/refs/site/img/omslag_zazi_dominique.jpg -o projects/reel-15/work/parallax/hero --n 4 --subject --plate codex --remove "the woman in the embroidered coat and her shadow"`
3. Stills: `python3 scene.py stills out/stills 0,2.5,5,7.5,10,12.5,15,17.5,20,22.5,24.96`
4. Picture: `python3 scene.py render out/master_v1_pic.mp4 0 25` (about 2.5 min on 4 cores; `--scale 0.5` for a draft)
5. Mix: `python3 work/mix.py m1 0 25 work/mix_v1.wav 3` (music `assets/music/m1.mp3`, paid, never regenerate)
6. Delivery:
   `ffmpeg -i out/master_v1_pic.mp4 -i work/mix_v1.wav -map 0:v -map 1:a -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -g 25 -keyint_min 25 -sc_threshold 0 -movflags +faststart -c:a aac -b:a 256k -shortest out/reel-15-final.mp4`
   v1 final: 25.0 s, 625 frames, 23 MB, -14.8 LUFS, peak -1.4 dBFS.
