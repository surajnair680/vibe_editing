# reel-13 revisions

- rough v1 (2026-11-23): cut and trim only. ElevenLabs voice isolation, every pause over 0.38 s cut, in-points
  moved past the mic being raised at 5.7, 10.1, 32.0, 56.3, 69.1 s (source). 85.1 s -> 53.9 s. Scribe check: every word kept.
- rough v2: user note "cut the part after 'supplements' where I reach out to pause the camera". Out-point 71.93 -> 71.70
  (source), 7 frames removed at 45.53 s of the edit. Every other frame unchanged (checked v1 vs v2). 53.67 s.

## Kallaway v1 draft -> v2 draft (2026-11-28)
Note: "The movement looks like typical AI. I want the movement to be fluidic, like Kallaway's videos. Also some
visuals are on screen for an extremely short time ... visuals and captions should flow in a cadence the viewer can
follow, but in perfect sync."
- Motion engine (`mg/panel/kallaway.js`): no overshoot pops; `soft` entrance (opacity, 26 px rise, blur, easeOutQuint),
  smootherstep camera and states, `data-keys` for elements that glide between positions, `data-pulse` for the REC dot.
- Scenes flow: Toji slides in beside "you" in the hook and carries on into the labels; the excuses are one canvas the
  camera glides along (DNA, clock, syringe), then pulls back for the strikes; you and Toji slide side by side.
- Time on screen: third strike now visible (SPLIT runs to 21.2); 27 from 27.95 to 29.25; carousel shows all three
  cards at once; both graphs up from the start; FULL beat "I don't know" dropped so "1 year?" holds 1.3 s; Toji at the
  end from 52.3 (was 0.3 s), end card at 53.95 (reel 55.95 s).
- Captions: 2 to 3 word phrases split evenly inside each sentence (`caption_phrases` in plan.json), not single words.
- 3D renders made truly transparent (`mg/panel/img/*.png`) so camera moves don't show black boxes.
