# reel-12: how to rebuild

Raw (not in git, ask the user to re-upload if missing): raw/ghar_ka_khaana_p1.mp4 .. p4.mp4 (1080x1920, 60 fps).

1. `python3 work/join.py` -> work/full.mp4 + work/audio/full.wav (parts joined, p2 at 39.0, p3 70.0, p4 102.0)
2. Voice isolation is paid and committed: work/audio/him_isolated.mp3 (ElevenLabs /v1/audio-isolation on full.wav
   from 24.5 s). `python3 work/align_voice.py` -> work/audio/full_iso.wav (aligned within ~1 ms)
3. Transcripts (Scribe): work/words.json, work/p2..p4/words.json, merged to work/words_full.json
4. `python3 work/plan_cut.py` -> work/cut_plan.json; `python3 work/make_cut.py v3` -> out/reel-12-rough-v3.mp4 (needs raw/ending_clip.mp4, the meme)
5. Manga build: `python3 work/mg/matte_frames.py 741 2556` (per-frame mattes of rough v3 -> work/matte_v3/), then
   `python3 work/mg/scene.py stills out/stills/v1` and `python3 work/mg/scene.py render <a> <b> work/render/pN.mp4`
   for 0-741, 741-1350, 1350-1960, 1960-2556, 2556-2761 (parallel), concat -> work/render/master_v1.mp4
6. Sound: paid audio in assets/el/ (`work/gen_sfx.sh`, `work/el_gen.py` never regenerate existing files);
   `python3 work/mix.py v1 a` -> work/audio/mix_v1.wav; mux with -c:v copy -> out/reel-12-v1-master.mp4
7. v2 lists: frames 1440-1830 and 1990-2380 re-rendered (`scene.py render`), spliced into master_v1 at keyframes
   (work/render/v2/list.txt) -> work/render/master_v2.mp4
8. Final: master_v2 + work/audio/mix_v1.wav (music A) -> out/reel-12-final.mp4 (crf 18 slow, keyframe every second,
   89 MiB); parts: video-only segment at 36/66/87 s + audio cut from the mix WAV per part -> out/parts/ (4 parts, all
   under 30 MiB, framemd5 identical to the full file, audio at 0 ms); post file: 2-pass 2350k -> out/reel-12-final-post.mp4
   (28 MiB, SSIM 0.979 to the final).
