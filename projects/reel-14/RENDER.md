# reel-14: how to rebuild ("Successful people are not normal" reaction reel)

Raw (not in git, ask the user to re-upload if missing): raw/part1.mp4 ... part5.mp4 (1080x1920, 60 fps,
42.0 / 29.0 / 28.0 / 28.0 / 5.28 s). Part 1 = her reel with his reaction inset (0 to 27.3167 s), then his take.
Lines cross the p1/p2 and p2/p3 seams; audio start_times are 0 to 13 ms (no hidden pre-roll).

1. `python3 work/join.py` -> work/full.mp4 (stream copy), work/audio/full.wav, work/parts.json (0/42/71/99/127)
2. Voice isolation is paid and committed: assets/el/voice_isolated.mp3 (ElevenLabs /v1/audio-isolation on full.wav
   from 27.3167 s). `python3 work/align_voice.py` -> work/audio/full_iso.wav (offset 3.0 ms, within 1 ms after)
3. Transcripts (Scribe): work/words.json, work/p2..p5/words.json (part-local times)
4. `python3 work/plan_cut.py` -> work/words_full.json, work/cut_plan.json (mic raise / drop rules inside)
5. `python3 work/make_cut.py v1` -> out/reel-14-rough-v1.mp4 + -preview.mp4 (101.4 s)
