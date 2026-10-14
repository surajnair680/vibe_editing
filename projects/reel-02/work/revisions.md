# reel-02 revisions

## Rough cut v1 -> v2 (2026-10-14)
Note: "From 'no matter how intelligent you are' till the end the cuts were abrupt. Before that it's perfect."
- Cause: fixed 0.10 s / 0.16 s pads clipped word endings ("are.", "first,", "perfect,") and cut into inhales
  before "Stop", "Bring", "not the other way around", "With whatever".
- Fix: segments 7 to 11 use cut points measured from the voice envelope (`EXACT` in `work/plan_cut.py`), the
  "first, then" pause is no longer trimmed, the last line keeps its exhale and fades out over 0.4 s.
- Check: frames 0 to 23.8 s are identical to v1 (framemd5). Length 41.2 s -> 44.6 s.
- v1 plan kept as `work/cut_plan_v1.json`.
