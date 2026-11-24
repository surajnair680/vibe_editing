# Tested example (2026-11-24)

`beach.jpg`: made with Codex for the test. Prompt: "a vintage 1950s black and white documentary photograph, vertical
9:16, of a muscular bodybuilder posing on Muscle Beach, Santa Monica. Clear depth: sand and a wooden bench close in
the foreground at the bottom, the bodybuilder full body in the middle ground, a crowd, palm trees and the pier far in
the background. Film grain, real photo look."

```bash
python3 tools/parallax.py layers .claude/skills/photo-parallax/example/beach.jpg -o /tmp/px/beach --n 4 --subject
python3 tools/parallax.py stills /tmp/px/beach -o /tmp/px/stills.png --move dolly-in --dur 6 --times 0,3,6
python3 tools/parallax.py render /tmp/px/beach -o /tmp/px/beach.mp4 --move dolly-in --dur 6
```
Result: 4 layers (back plate z 4.45, sand 1.92, bodybuilder 1.67, bench 1.0), `split.jpg`; the move
`dolly_stills.jpg` (0 s and 6 s), `pan_strip.jpg` (pan-right), `cable_drift_strip.jpg` (the reel's own cable car frame,
3 layers with --subject, drift). Layers in about 8 s, a 6 s 1080x1920 render in about 33 s.
