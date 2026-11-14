# reel-08 "Comeback Day 1": how to rebuild

Status (2026-11-14): stills round 2 and low-res draft v2 sent. Not approved yet. Music and SFX not built yet.

Needs the Lemo-Opuscar library (`~/lemo-opuscar`, installed by the start-up hook) and the repo's `tools/lemo.sh`.
Run from the repo root.

1. Fonts (already in git): `sh projects/reel-08/film/fonts.sh`
2. Voice (paid, in git, never regenerate): `voices/full_take1.mp3`, ElevenLabs "Jessica" `cgSgspJ2msm6clMCkdW9`,
   eleven_multilingual_v2, stability 0.45, similarity 0.8, style 0.25, text in `work/script.txt`.
   Decode: `ffmpeg -i projects/reel-08/voices/full_take1.mp3 -ar 48000 -ac 1 projects/reel-08/work/full_take1.wav`
   It starts at film time 0.40 s. Word times: `work/words.json` (Scribe).
3. Her drawings: Codex images in `gen/` (prompts in `gen/poses.sh`, sheet prompt in the reel-08 lessons), cut out with
   `python3 projects/reel-08/work/cutout.py` (run inside `projects/reel-08`) into `film/her/` (in git).
4. Stills (2.5 s grid): `sh tools/lemo.sh node core/render/still.mjs "$PWD/projects/reel-08/film" --range 0:36.5:2.5 --size 1080x1920 --out "$PWD/projects/reel-08/work/grid"`
   then `python3 projects/reel-08/work/sheet.py projects/reel-08/work/grid projects/reel-08/work/contact.jpg 5 360`
5. Draft: `sh tools/lemo.sh node core/render/video.mjs "$PWD/projects/reel-08/film" --fps 15 --workers 3 --size 540x960 --out "$PWD/projects/reel-08/out/draft_silent.mp4"`
   (about 20 s), then mux the voice with `adelay=400` and re-encode at crf 28 (the library's encode is about 30 MB).
6. Final (after approval): same with `--fps 24 --size 1080x1920`, a mix WAV (music + SFX + voice), then
   `sh tools/lemo.sh sh core/render/mux.sh <video> <mix.wav> <out>/reel-08-final.mp4 24 0`.
