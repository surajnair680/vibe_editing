# reel-11: how to rebuild

Raw files (not in git, re-upload if the session was wiped) go in `raw/`:
her_part1..4.mp4 (her speech, 4 parts of one clip), me_2.mp4 ("I don't understand..."),
me_3a..d.mp4 (one recording split in 4 parts).

1. Audio to WAV: `for f in raw/*.mp4; do ffmpeg -i $f -vn -ac 1 -ar 48000 work/audio/$(basename $f .mp4).wav; done`
2. Join her parts: video by concat (`work/her_list.txt`, `setpts=N/(60*TB)`), audio placed at each part's own
   start time (0, 8.010, 16.021, 24.009 s), which gives a seamless 25.0 s track -> work/her_full.mp4 / .wav
3. Cut plan: `python3 work/plan_cut.py` (envelope based in/out points) -> work/cut_plan.json
4. Rough cut: `python3 work/make_cut.py` -> out/reel-11-rough-v1.mp4 (preview: 2-pass 4.3 Mbps, -g 30)
