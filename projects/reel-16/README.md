# reel-16: soundtrack for the ZAZI editorial promo (zazi_v1.mp4)

Input: `raw/zazi_v1.mp4` (not in git), 1280x720, 25 fps, 24.0 s, no audio. An editorial, magazine-style
ZAZI coat promo (kinetic serif type on cream, cuts about every 1.1 s). Same client as reel-15.
Job: add a soundtrack (music + light sound design) matched to the cuts.

## Soundtrack v1 (2026-11-25)
- Music: `assets/music/m1.mp3` (ElevenLabs, option 1 "runway warm": minimal deep house, Rhodes, kalimba / sitar-like
  accent, 104.85 BPM). Rebuilt to 24 s by whole phrases and sped up 2.4 % so the ending chord lands on the
  white ZAZI card cut at 22.36 s. Fade out over the last 0.8 s.
- SFX (all CC0, no credit needed): paper flips on the ZAZI / MADE / CRAFT / grid / HANDMADE cards, cloth on the
  red-door model, fabric flap on LIMITED DROPS, soft chime on the logo.
- Rebuild: put the video at `raw/zazi_v1.mp4`, then `cd projects/reel-16 && python3 work/mix.py`
  (writes `work/mix.wav`, -14 LUFS, and `out/reel-16-final.mp4`, video stream copied untouched).
