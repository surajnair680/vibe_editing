# reel-06 rebuild steps (YouTube Shorts version of the grandma reaction reel)

Raw (not in git, ask the user to re-upload): `raw/part1.mp4` (32.0 s), `raw/part2.mp4` (12.0 s), `raw/part3.mp4` (20.283 s),
the finished Instagram reel in 3 parts, 1080x1920 60 fps HEVC, AAC 44.1k stereo.

1. Join: decode each part's audio to WAV trimmed/padded to its video length (`work/audio/partN.wav`, `full.wav`),
   `ffmpeg -f concat -c:v copy` the video (`raw/parts.txt`) -> `raw/full.mov` (64.283 s).
2. Voice: ElevenLabs audio isolation of `full.wav` -> `work/audio/full-isolated.mp3` (paid, committed),
   decode to `voice_iso.wav`, then `python3 work/align_voice.py` (envelope cross-correlation + linear drift fit).
3. Music (paid, committed): `work/gen_music.sh` -> `assets/music/song_{a,b,c}.mp3`, `bed_{a,b}.mp3`.
4. Mix: `python3 work/mix.py <song a|b> <bed a|b> work/audio/mix_XY.wav`.
5. Preview: picture copied from `raw/full.mov`, audio = the mix.
6. Final (approved: song B + beat B):
   - Master, picture bit-exact: `ffmpeg -f concat -safe 0 -i raw/parts.txt -i work/audio/mix_bb.wav -map 0:v -map 1:a
     -c:v copy -tag:v hvc1 -c:a aac -b:a 320k out/reel-06-master.mp4` (no `-shortest`: it dropped the last 2 frames).
   - One file under 30 MiB: `work/encode_final.sh` -> `out/reel-06-final.mp4`.
   - Original-quality parts: each `raw/partN.mp4` video copied + its range of `mix_bb.wav` (0-32, 32-44, 44-64.283 s).
