# reel-04 revisions

## rough v1 -> v2 (2026-11-01)
Note: "begin with me already sitting and working, not moving towards the chair".
- Shots 1 to 3 (0 to 10.36 s) replaced: wide 13.00 (working), x1a 5.00 (working), x5a 7.00 (working).
- Everything from 10.36 s on is unchanged (montage, breath, exit with the walk-off, empty chair ending).

## opening motion test (2026-11-01)
Note: "when the video starts I want some sort of motion, zooming, so it looks dynamic".
- work/build.py: shot 1 snap pull-out 1.30 -> 1.08 in 1 s (ease-out, zoom blur) then slow drift to 1.04;
  shot 2 lateral slide at 1.12 past the door frame; shot 3 push-in 1.00 -> 1.13 accelerating into the drop.
- Sent out/motion_test.mp4 (first 10.37 s, 540 wide).

## v1 (2026-11-01)
- Look approved from stills (contact_v1). Sound design: 9 ElevenLabs SFX (assets/sfx), cue list work/sfx_cues.json;
  music low-passed at 520 Hz during the breath (18.17 to 23.37); room sound kept low, keys and bottle closer.
- Preview: out/reel-04-v1-preview.mp4 (6.6 Mbps two-pass, 27.5 MB).

## v1 -> v2 (2026-11-01)
Note: "the risers are too harsh and ear piercing, make them more pleasant".
- riser_build (8.0-10.4), riser_exit (26.6-28.6) and the reverse swell (16.0-18.2) low-passed (2.2 / 2.6 / 3.2 kHz,
  15% dry kept for air) and 2 to 3 dB quieter. Master gain fixed at v1's +0.7 dB (not re-normalised).
- Checked: only 8.0-10.5, 16.5-18.2 and 26.75-28.6 differ from v1; picture stream copied from v1; audio sync 0 ms.
