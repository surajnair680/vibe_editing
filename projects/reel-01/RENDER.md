# Rebuild reel-01

Raw files are not in git: `raw/take-01.mp4` (the joined take) and `raw/physique-clip.mp4` must be supplied again.
Run from this folder, in order:

1. `python3 work/make_cut.py`  -> work/cut.mp4, work/voice_cut.wav (needs work/voice_isolated.mp3 from ElevenLabs
   audio isolation of the take, see CLAUDE.md)
2. Hook segment and mattes: `ffmpeg -i raw/take-01.mp4 -t 5.6 -vf fps=30 -an work/hook_src.mp4`, then
   `python3 vibe/matte.py work/hook_src.mp4 --model u2net_human_seg` and
   `python3 work/refine_matte.py work/hook_src.mp4 work/matte/hook_src_alpha.mp4 -o work/matte/hook_src_alpha_clean.mp4 --grow 6 --thresh 0.3 --kill-florals --solid-below 0.68`
   (same for work/glow_src.mp4 = cut.mp4 from 11.6 s for 2.2 s)
3. Gym clip: `ffmpeg -i raw/physique-clip.mp4 -vf fps=30 -an work/gym_src.mp4`, then
   `ffmpeg -ss 1.45 -t 1.9 -i work/gym_src.mp4 -vf "crop=900:1200:150:120,colorchannelmixer=rr=1.06:gg=1.0:bb=0.80,eq=saturation=0.85:contrast=1.06:brightness=0.02" -an work/gym_print.mp4`
4. Images: `python3 work/prep_images.py` -> assets/print/*.png
5. Music: option B from ElevenLabs (prompt in brief), extended:
   `ffmpeg -i assets/music/option-b.mp3 -filter_complex "[0:a]asplit=2[x][y];[x]atrim=0:30.9,asetpts=PTS-STARTPTS[p1];[y]atrim=25.0,asetpts=PTS-STARTPTS[p2];[p1][p2]acrossfade=d=0.6:c1=tri:c2=tri" work/music_b_extended.wav`
6. Picture: `python3 reel_scene.py render` -> out/reel-01_silent.mp4 (stills: `python3 reel_scene.py stills 5.5 9.0`)
7. Sound and final: `python3 work/mix.py` -> out/reel-01_v1.mp4
