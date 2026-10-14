# reel-02 revisions

## Rough cut v1 -> v2 (2026-10-14)
Note: "From 'no matter how intelligent you are' till the end the cuts were abrupt. Before that it's perfect."
- Cause: fixed 0.10 s / 0.16 s pads clipped word endings ("are.", "first,", "perfect,") and cut into inhales
  before "Stop", "Bring", "not the other way around", "With whatever".
- Fix: segments 7 to 11 use cut points measured from the voice envelope (`EXACT` in `work/plan_cut.py`), the
  "first, then" pause is no longer trimmed, the last line keeps its exhale and fades out over 0.4 s.
- Check: frames 0 to 23.8 s are identical to v1 (framemd5). Length 41.2 s -> 44.6 s.
- v1 plan kept as `work/cut_plan_v1.json`.

## Rough cut v2 -> v3 (2026-10-14)
Notes: "no matter how intelligent you ar[abrupt cut]", "perfect workout progra[abrupt cut]", too much time before
"Not the other way around", too much time before "With whatever" (seen starting the recording), too much time at
the end (seen lowering the mic and looking down at the phone).
- "are" out 48.48 -> 48.78 (its trailing "r" runs to 48.70). "program" out 55.63 -> 55.85.
- "not" in 63.57 -> 64.10 (dropped the long breath). "With" in 67.23 -> 68.10 (mic up by 68.1).
- End out 72.00 -> 71.60 (exhale ends 71.45, mic drops at 71.8), fade 0.4 -> 0.15 s.
- Check: frames 0 to 23.8 s identical to v1 (framemd5). Length 44.6 s -> 43.4 s. v2 plan kept as `work/cut_plan_v2.json`.

## Audio sync fix (2026-10-14)
- Found while cutting the isolated voice: the rough cut drafts v1 to v3 took audio by seeking the phone MP4, which
  landed up to 100 ms off the picture on some lines (picture itself was within a frame of the plan).
- `work/make_cut.py` now reads audio from `work/audio/<clip>.wav` (decoded from the start); drafts are now exact.
- The mix uses `work/voice_cut.wav` (isolated voice, `work/make_voice.py`), which is within about 10 ms of the plan.
