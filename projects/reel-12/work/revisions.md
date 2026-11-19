# reel-12 revisions

- rough v1 (2026-11-19): her clip 0-24.70 untouched; his lines with every pause over 0.38 s cut (envelope cut points), ElevenLabs isolated voice. 111.1 s raw -> 94.8 s. 'phir' line starts after the mic is back up (77.63).
- rough v2 (2026-11-19): ending meme (raw/ending_clip.mp4, 6.83 s, muted) hard cut right after 'agar bola to', full width on black. 101.6 s.
- rough v3 (2026-11-19): benefit lists 1.5x after the first 2 items (protein list from 'losing', gym list from 'more muscle'), pitch kept with ffmpeg rubberband (window=short); Scribe check: every word still there. Meme audio on. 92.0 s.
- v1 (2026-11-19): manga build (work/mg/scene.py over rough v3), colour Codex food (thali, protein spread, roti stack),
  ElevenLabs music A (and B as an option) from 0:00 ducked about 18 dB under the voice, stops on the "toh" impact;
  63 ElevenLabs SFX cues (work/sfx_cues.json). Mix -14 LUFS, peak -1 dBTP (work/mix.py). Meme keeps its own sound.
- v2 (2026-11-19): music A chosen. Benefit lists rebuilt with one matching visual per item (work/mg/benefits.py:
  his assets where they show the benefit, code-drawn manga illustrations for abstract ones). Only frames 1440-1829 and
  1990-2379 re-rendered and spliced into master_v1 at keyframes; framemd5 proves every other frame identical
  (66.33-67.45 is a re-encode of identical content, PSNR 46 dB). Audio unchanged (mix_v1, music A).
