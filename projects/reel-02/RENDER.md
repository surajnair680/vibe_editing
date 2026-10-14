# Rebuild reel-02

Raw files are not in git: `raw/VID20261007161237.mp4`, `raw/1000097826_part1..5.mp4` (joined to
`raw/1000097826.mp4` with `raw/parts.txt`), `raw/gym-1.mp4`, `raw/gym-3.mp4` must be supplied again.
Run from this folder, in order:

1. Audio for cutting: `ffmpeg -i raw/<clip>.mp4 -vn -ac 1 -ar 48000 -c:a pcm_s16le work/audio/<clip>.wav` for both clips;
   isolated voice is in git (`work/audio/<clip>-isolated.mp3`), decode each to `work/audio/<clip>-isolated.wav`.
2. Cut: `python3 work/plan_cut.py`, `python3 work/make_cut.py` (-> work/cut.mp4), `python3 work/make_voice.py`
   (-> work/voice_cut.wav), `python3 work/words_edit.py` (-> work/words_cut.json).
3. Hook cut-out: `ffmpeg -i work/cut.mp4 -t 3.4 -vf fps=30 -an work/hook_src.mp4`, then
   `python3 vibe/matte.py work/hook_src.mp4 --model u2net_human_seg` and
   `python3 work/refine_matte.py work/hook_src.mp4 work/matte/hook_src_alpha.mp4 -o work/matte/hook_src_alpha_clean.mp4 --grow 6 --thresh 0.3 --kill-florals --solid-below 0.68`
   (needs rembg, mediapipe, libgles2 and work/models/selfie_multiclass.tflite from storage.googleapis.com/mediapipe-models).
4. Prints: `python3 work/prep_gym.py`, `python3 work/prep_images.py`. Fonts: `python3 vibe/fonts.py "Playfair Display:900" "Inter Tight:800" "Instrument Serif:400" -o fonts/`.
5. Picture: `python3 reel_scene.py sheet` (stills first), then `python3 reel_scene.py render` -> out/reel-02_silent.mp4.
6. Sound and final: `python3 work/mix.py` -> out/reel-02_v1.mp4. Delivery and the 2-part split: see work/revisions.md (v1 render).
