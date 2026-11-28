# Layout rules (1080 x 1920)

All numbers were measured on full-size Kallaway frames (`references/frames/00-hires-measured/`).

## The two layouts
About **72% of screen time is SPLIT**, **28% is FULL** (measured across 17 reels). Never run SPLIT for more than about
12 s without a FULL beat, and never run FULL for more than about 5 s in the body (the CTA end can hold longer).

### SPLIT (the graphic layout)
| zone | y range | what goes there |
|---|---|---|
| Title | 150 to 440 | 1 or 2 lines, centred. Top of the cap height at about y 160 (light) to 280 (dark). |
| Graphic | 450 to 1180 | the scene's one object or diagram, centred. Keep about 120 px clear above the caption. |
| Caption | 1220 to 1350 | one word (sometimes 2 to 3), centred, just above the strip. |
| Speaker strip | 1403 to 1920+ | the talking head in a rounded window that runs off the bottom edge. |

**The speaker strip**
- Window: x 68 to 1012 (944 px wide, 68 px side margins), top edge at y 1403, runs off the bottom of the frame.
- Corner radius about 50 px (only the top corners show).
- Inside: the speaker, chest-up, face in the upper half of the window, studio background visible.
- **Pop-out:** a cut-out of the speaker sits on top of the window, lined up pixel for pixel with the footage inside it.
  Outside the window only the cut-out shows, so the head and cap break above the window's top edge by 40 to 90 px.
  This gives depth and makes the person feel inside the scene, not boxed in. The cut-out has no outline and no shadow.
- On the light theme the window is the same. On some light scenes it is a smaller inset (x 90 to 990). Keep one size
  per video.

**Adapting the strip to vertical phone footage (the user films 9:16):** crop a horizontal band from the vertical
frame (full width, from about 8% above the top of the head down to mid-chest; band height = 1080 * 517 / 944 = about
590 px of source) and scale it to 944 px wide. Make the cut-out from the same source frame with the same crop, so the
two line up. If the head touches the top of the band, the pop-out does the rest.

### FULL (the talking-head layout)
- Speaker full frame, punched in chest-up (eyes at about y 600 to 700).
- Caption: one word, white bold, centred at about **y 1140 to 1190** (over the chest, under the chin).
- Same caption font as SPLIT. No title, no graphic. A small logo or doc image may pop under the caption word
  ("Sandcastles.ai" + app icon, "Master Prompt" + doc page).

### FULL B-roll
Full-frame footage with the same caption position as FULL. Used in short bursts (see `rules/pacing.md`).

## Grounds
- **Dark** (default, most reels): near-black #050505 to #0A0A0A, a fine dot grid (1 px dots every 14 px at about 6%
  white), a soft vignette. `assets/backgrounds/bg-dark.png`.
- **Light**: light grey #E2E2E1 with a faint dot texture and a thin square grid (about 40 px) that is visible near
  the edges and fades out in the middle. `assets/backgrounds/bg-light.png`.
- Pick per section, not per scene: whole tool or tutorial reels can be light (08, 12, 18); framework reels are dark
  with light inserts for real examples and the CTA. A theme switch is itself a "new section" signal.

## Safe zones
- Nothing important above y 150 or in the right 120 px (Instagram buttons) below y 1100, except the strip itself.
- The graphic never covers the face. The caption never touches the pop-out head: if the head rises above y 1360, move the
  caption up to keep 20 px clear.
