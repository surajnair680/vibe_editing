# reel-11: how to rebuild

Raw files (not in git, re-upload if the session was wiped) go in `raw/`:
her_part1..4.mp4 (her speech, 4 parts of one clip), me_2.mp4 ("I don't understand..."),
me_3a..d.mp4 (one recording split in 4 parts).

1. Audio to WAV: `for f in raw/*.mp4; do ffmpeg -i $f -vn -ac 1 -ar 48000 work/audio/$(basename $f .mp4).wav; done`
2. Join her parts: video by concat (`work/her_list.txt`, `setpts=N/(60*TB)`), audio placed at each part's own
   start time (0, 8.010, 16.021, 24.009 s), which gives a seamless 25.0 s track -> work/her_full.mp4 / .wav
3. Cut plan: `python3 work/plan_cut.py` (envelope based in/out points) -> work/cut_plan.json
3b. Part 3b's hidden audio pre-roll: `ffmpeg -i raw/me_3b.mp4 -map 0:a -c copy work/seam/3b.aac` then decode it to
    work/audio/me_3b_all.wav (starts 0.2604 s before the picture)
4. Rough cut: `python3 work/make_cut.py v2` -> out/reel-11-rough-v1.mp4 (preview: 2-pass 4.3 Mbps, -g 30)
5. Mattes for the face circle: `python3 work/matte_frames.py 469 959` and `... 960 1452` (two in parallel, ~10 min)
   -> work/matte/NNNNN.png (edit frames of work/cut_v2_14.mp4 = `ffmpeg -f concat -i work/cut/list.txt -c copy`)
6. Stills: `python3 scene.py grid` (contact sheet), `python3 scene.py sheet <out.jpg> <t...>`
7. Picture: `python3 scene.py render` -> out/reel-11-picture.mp4 (audio mixed separately)
8. Sound: `python3 work/music.py && python3 work/sfx.py && python3 work/mix.py` -> work/audio/mix_v1.wav
9. Full picture in 4 parts: `python3 scene.py render 0 12.5 work/render/part_1.mp4` (12.5-25, 25-37.5, 37.5-49.9),
   concat copy -> out/reel-11-picture.mp4, mux mix_v1.wav (AAC 256k) -> out/reel-11-v1-master.mp4;
   delivery: 2-pass x264 4500k, -g 30 -keyint_min 30 -sc_threshold 0, AAC 192k -> out/reel-11-v1.mp4
