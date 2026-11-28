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
6. Graphics: `python3 work/build/words_edit.py` (edit-time words), `ffmpeg -f concat -i work/cut/list.txt -c copy work/base.mp4`,
   stills `python3 work/build/scene.py still <t> ...`, picture in 4 parallel ranges
   `python3 work/build/scene.py render 0 26 work/render/p_0.mp4` (26-52, 52-77, 77-102), about 1 min each.
7. Sound: `python3 work/mix.py v1 --no-music` (v1 as approved for now: voice + SFX), without the flag for music A.
8. Mux: concat work/render/p_*.mp4 + work/audio/mix_v1.wav -> out/reel-14-v1-master.mp4 (crf 14, 135 MB);
   delivery 2-pass x264 2150k + AAC 192k -> out/reel-14-v1.mp4 (28.5 MiB).

## v2 (reference look, current)
9. Mattes of his takes: `python3 work/matte_frames.py 819 1374` (and 1375 1930, 1931 2486, 2487 3042 in parallel)
   -> work/matte/NNNNN.png (rembg u2net_human_seg, about 30 min on 4 cores; not in git, rebuild after a wipe).
   Celebrity cut-outs build themselves on first use into work/cutouts/ (rembg isnet-general-use).
10. Stills: `python3 work/build2/scene2.py still <t> ...` -> out/stills/v2/. Picture: 4 parallel ranges
   `python3 work/build2/scene2.py render 0 26 work/render/v2_0.mp4` (26-52, 52-77, 77-103); LEN = cut + 0.9 s.
11. Sound: `python3 work/mix.py v2 --no-music --v2` -> work/audio/mix_v2.wav (voice + SFX on titles; drop
   --no-music for music A, re-arranged so its break lands before "Screw").
12. Mux and deliver as in step 8 (2-pass about 2150k for under 30 MiB).

## v3 (dark Vox collage, 2026-11-24)
13. Picture: `python3 work/build3/scene3.py render 0 26 work/render/v3_0.mp4` (and 26-52, 52-77, 77-103 in parallel,
    about 20 min on 4 cores). Needs raw/, work/base.mp4 and work/matte/ (steps 1 to 9) and the committed
    assets/codex/*.png, assets/photos/statue_*.jpg. Stills: `python3 work/build3/scene3.py still <t> ...`.
14. Sound: `python3 work/build3/mix3.py` -> work/audio/mix_v3.wav (voice + soft low-passed paper sounds, no music).
15. Master: concat the 4 parts (`-f concat -c:v copy`) + mix_v3.wav (aac 256k, `-t` LEN) -> out/reel-14-v3-master.mp4
    (about 1.26 GB at crf 14 because of the grain). Review copy under 30 MiB: 2-pass x264 at 2150k + aac 160k.

## Timeline editor page
https://claude.ai/artifact/CyphKAUjA3xdGepq8yg4bM (private). Rebuild: `python3 work/build3/timeline_extra.py`, then
`tools/timeline/export_timeline.py projects/reel-14 --version <v>`, `make_proxy.py`, `build_page.py` (media in work/timeline/media.json).
