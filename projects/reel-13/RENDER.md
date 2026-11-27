# reel-13: how to rebuild (Bulking series, episode 0)

Raw (not in git, ask the user to re-upload if missing): raw/ep0_part1.mp4, ep0_part2.mp4, ep0_part3.mp4
(1080x1920 HEVC, 30 fps, 36.0 / 36.0 / 13.1 s; three separate takes, no line crosses a seam).

1. `python3 work/join_audio.py` -> work/audio/full.wav + work/parts.json (offsets 0 / 36.0 / 72.0)
2. Voice isolation is paid and committed: assets/el/voice_isolated.mp3 (ElevenLabs /v1/audio-isolation on full.wav).
   `python3 work/align_voice.py` -> work/audio/full_iso.wav (offset 2.6 ms, aligned within 1 ms)
3. Transcripts (Scribe): work/words.json, work/p2/words.json, work/p3/words.json (part-local times)
4. `python3 work/plan_cut.py` -> work/words_full.json, work/cut_plan.json (mic-raise in-point floors inside)
5. `python3 work/make_cut.py v2` -> out/reel-13-rough-v2.mp4 + -preview.mp4 (53.67 s, approved cut)

## Timeline editor page
https://claude.ai/artifact/A7KL71kEmBsgwF6a57nTiF (private). Rebuild: `python3 tools/timeline/export_timeline.py
projects/reel-13 --version <ver>`, `python3 tools/timeline/make_proxy.py projects/reel-13` (only if raw changed),
`python3 tools/timeline/build_page.py projects/reel-13 [--preview <asset url>]`, publish work/timeline/index.html.
Media urls in work/timeline/media.json (rough-v2 preview, proxy). His trims: ArtifactData get edits/current ->
work/timeline_edits.json -> plan_cut.py applies them.
