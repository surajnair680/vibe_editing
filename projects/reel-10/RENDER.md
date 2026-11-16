# reel-10: how to rebuild
Raw footage is not in git: 21 phone parts (VID20261115180218 / 180454 / 181322 / 181836 / 182103, part1..5) linked as
raw/part1-5 (rec 1), raw/b_part1-5 (rec 2), raw/c_part1-4 (rec 3), raw/d_part1-2 (rec 4, horizontal),
raw/e_part1-5 (rec 5). Song: raw/music/thebox.mp3 (user's file) -> `ffmpeg -i raw/music/thebox.mp3 -ar 44100 work/audio/thebox.wav`.
1. `python3 work/hook/scribble.py` (bg_v0..2.png from head_sil.png, committed)
2. `VER=v1 python3 work/build.py stills draft` (stills + half-size draft)
3. `python3 work/build.py master` -> out/reel-10_master.mp4 (crf 14) + work/audio/mix.wav
