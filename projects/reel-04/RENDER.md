# reel-04 rebuild steps

Raw clips (not in git) go in raw/ with these names: wide.mp4 (VID20261101122253), x1a/x1b (x1 part 1/2),
x2, x3, x4, x5a/x5b (x5 part 1/2). Music and SFX (paid, ElevenLabs) are committed in assets/.

1. Picture (cut + camera moves + grade + grain), about 8 min on 4 cores:
   python3 work/build.py --w 1080 --crf 14 --out work/picture_v1.mp4
   Stills only: python3 work/build.py --stills 0,2.5,5   (PNG in out/stills/)
2. Sound: python3 work/mix.py   -> work/mix_v1.wav (-14 LUFS); cue list in work/sfx_cues.json
3. Master: ffmpeg -i work/picture_v1.mp4 -i work/mix_v1.wav -map 0:v -map 1:a -c:v copy -c:a pcm_s24le -shortest work/master_v1.mov
4. Delivery: fade to black over the last 1.5 s (fade=t=out:st=30.47:d=1.5), keyframe every second.
   Preview under 30 MiB: two-pass libx264 -b:v 6.6M, AAC 256k (27.5 MB).
   The crf 14 master is about 370 MB because of the per-frame grain.

Timing lives only in timeline.py (shots fitted to the 92.3 BPM music grid).
