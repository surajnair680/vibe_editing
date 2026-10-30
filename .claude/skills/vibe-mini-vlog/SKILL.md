---
name: vibe-mini-vlog
description: Mini vlogs and "day in my life" reels in a cinematic camcorder style, with the user's vlog overlay pack (REC, vlog, summer 2026, a day in my life, VLOG on blue, REC iris). Use when the user wants a mini vlog, day in my life, DITL, vlog series episode, travel or city vlog, "vlog style", camcorder or REC overlays, flicker title overlays, or says "like the overlay reel" / "use the overlays". Covers the reference reel breakdown, the 12 video + 2 image overlays (horizontal originals and vertical 9:16 versions), compositing (Screen blend, colour key, hold the last frame), and the reel's other effects (glossy 3D pop words, RGB-split glitch frames, oval colour frames, whip pans, Instagram post mockups). Use together with vibe-talking-head for cutting and captions.
---

# Mini vlogs with the camcorder overlay pack

Learned 2026-10-30 from a reference reel the user shared (a London creator, 53 s, 16:9) and the overlay pack that
reel gives away ("Overlay Designs 2", by sam.john.creates). The user is planning an Instagram series of mini vlogs,
**mostly vertical 9:16**, and wants every future edit to be able to look like this.

Paths are relative to this skill's folder:
- `assets/overlays/horizontal/` the original pack: `video-overlay-1..12.mp4` (1920x1080, 30 fps, ~10 s) and
  `image-overlay-1..2.jpg`.
- `assets/overlays/vertical/` the same 12 videos rebuilt for 1080x1920 (made by `scripts/vlog_overlays.py vertical`).
- `scripts/vlog_overlays.py` convert, contact sheet, quick comp, and `Overlay` / `screen` / `keyed` helpers for builds.
- `reference/` what the reel looks like (`ref-reel/`: 1 fps contact sheet, key frames, effects strip, pop word
  close-up, transcript) and the pack (`pack-horizontal.jpg`, `pack-vertical.jpg`, `comp-test.png`).

Work in the normal workflow (CLAUDE.md): project folder, brief, beat sheet, stills first. Copy
`scripts/vlog_overlays.py` into the project's `work/` and the overlays you use into `assets/` (never import across
folders; this skill folder counts as shared, so copying from it is fine).

## 1. The reference reel, beat by beat

| time | what happens | technique |
|---|---|---|
| 0.0 to 10 | Hook. Selfie on Westminster Bridge, mic in hand, talking to camera. | Faded film grade + vignette. Image overlay 2 (corner credits) and overlay 6 (vlog / summer 2026 / REC) on top. One glossy cyan 3D word per spoken word pops on the mic. |
| 10 to 12 | B-roll burst: keepy-ups with a volleyball, whip pan with "DAY IN THE LIFE". | Fast cuts on the beat, motion-blur whip pan, overlay 2 and 11 text. Beat drop with his "sha-bang, woo". |
| 12 to 18 | London Eye, Instagram post mockups on white, people playing volleyball. | Overlay 3 ("A CHILL DAY IN THE LIFE"), post screenshots as proof that vlogs work on IG. Small lowercase subtitles start. |
| 18 to 24 | The designs shown raw on black: blue REC circle, vlog + clocks, giant VLOG on blue. | One overlay per spoken phrase ("flashing in", "flickering", "key frames"), each with its SFX. |
| 24 to 38 | CapCut tutorial screen recording. | Overlay, blend mode Screen, chroma key, split and stretch. |
| 38 to 45 | CTA in the park, static mid shot. | "comment DESIGN". Overlay 8 ("a day in my life" outline) flashes on "stand out". |
| 45 to 47.5 | Energy spike: selfie in a white frame, then in an oval on green, then on red. | RGB split / chromatic edges, frame colour changes on each beat, cyan pop words again. |
| 47.5 to 53 | Plug for an older video, flat ending. | The weak part; don't copy it. End on a payoff or a loop. |

What makes it work: the hook shows the product (the designs) on screen while he talks about them; a B-roll burst
right after the hook resets attention; overlays are tiny, thin and at the edges so they never cover the face.

## 2. The look (recipe)

- **Grade:** lifted blacks, slightly cool and desaturated, gentle teal shadows, soft warm skin; strong but soft
  vignette; fine grain. Like a film camera on an overcast day. Build it as one 3x4 colour matrix (see CLAUDE.md speed
  notes) plus grain and vignette from motion_kit.
- **Overlay type:** tiny white UI text at the edges (REC with a red square dot, "summer 2026", "25FPS", "A CINEMATIC
  VLOG // 2026"), one bigger title per design. Flicker and type-on in, then hold. Never more than one big title at a time.
- **Subtitles:** small (about 3% of frame height), white, lowercase, plain sans (Helvetica/Inter style), no box, one
  short phrase at a time, low in the frame. On vertical put them above the Instagram caption zone (about y 1400 of 1920).
- **Pop words (hook and spikes only):** one word at a time, the word being said, heavy rounded sans (a chunky
  geometric bold, e.g. Poppins/Nunito Black), vertical gradient from bright cyan (#3fd4f0) to deep teal (#0a6f8f), a
  thin light top highlight for gloss, soft drop shadow, popping in with a quick scale (0.6 to 1.05 to 1.0 over
  0.12 s). Placed on the mic / hands, never on the face. See `reference/ref-reel/pop-word-closeup.jpg`.
- **Glitch frame (45 to 47.5):** footage scaled to about 85% inside a coloured border (white, then green, then red, one
  per beat); on green and red the footage sits in an oval; RGB channels offset 6 to 12 px at the edges; a quick blur.
- **Whip pan:** directional motion blur over 4 to 6 frames between two clips, with a whoosh.
- **Proof inserts:** screenshots of real Instagram posts on white, scaled in with a small bounce.

## 3. The overlay pack

All videos animate in during the first 0.1 to 2 s, then hold (the REC dot blinks until about 8 s). To make one
last longer, hold its last frame (`Overlay(n).frame(t)` does this) or, like the reel says, split after the animation
and stretch the tail. Built-in SFX (flicks, clicks, whooshes) are loud, peaking near 0 dB: duck them to sit under
the voice, or leave them out. V1, V5 and V12 are silent.

| # | shows | blend | notes |
|---|---|---|---|
| 1 | VLOG / A DAY IN MY LIFE, "starts in 3" countdown, SUMMER 2026, REC | Screen | Opening title. Countdown fits a "let's go" start. |
| 2 | A DAY IN MY LIFE, JUST PRESS REC, corner words DAY / IN / THE / LIFE | Screen | Clean all-purpose opener. |
| 3 | A CHILL DAY IN THE LIFE (flicker), REC, Summer 2026 script | Screen | Calm, slow days. |
| 4 | app icons (Notion, IG, X...), DAY IN THE LIFE GRINDING, WORKING, 25FPS, Q3 | Screen | Work / productive days. Icons are colour. |
| 5 | "pieces of my ... life lately" | Screen | Recap or montage episodes. |
| 6 | vlog / day in my life (chunky), 4 alarm clocks, summer 2026, REC | Screen | The hook look of the reel. Morning routine. |
| 7 | giant black VLOG on blue, REC; ~2 s then black | key blue (0,0,160), mode normal | Punch moment. Use on B-roll, not the face (letters cover it). Vertical: a band across the middle, blue above and below. |
| 8 | "a day in my life" pastel outline, vlog, REC, summer 2026 | Screen | Soft, cute. |
| 9 | "a day in [June]" spaced words, REC | Screen | Month-specific; the text is baked in (June). |
| 10 | media player window over pastel sky with a dock; ~1 s then black | Screen | Footage plays inside the window (black = footage). |
| 11 | DAY IN THE LIFE (glitch), June 2026, Shot on Sony, [REC] | Screen | Date and camera are baked in. |
| 12 | lavender REC circle (iris) for the full 10 s | key lavender (91,107,165), mode normal | Footage inside the circle, dark edges. Vertical: tall oval. A thin blue fringe can stay at the oval edge; raise tol to 80 if it shows. |
| img 1 | "a productive day in the life", "day in my life ★", "locking in", "REC." with 25FPS / WB: MANUAL | Screen | Stills: crop the piece you need. |
| img 2 | corner credits: A CINEMATIC VLOG // 2026, INSIPRE AND CREATE // VLOG, CREATIVE///ART DIRECTION... | Screen | Has the creator's credit "DESIGN MADE BY SAM.JOHN.CREATES" and the typo "INSIPRE". Crop or rebuild before use; ask the user. |

Baked-in text (SUMMER 2026, June, Shot on Sony) can't be edited. When the episode needs other words, rebuild the
design in code in the same style (skia text, flicker = random 1-frame alpha drops over 0.3 s, type-on = letters
appearing every 2 frames) rather than using text that is wrong for the video.

## 4. Vertical (the user's default)

`python3 scripts/vlog_overlays.py vertical` rebuilt `assets/overlays/vertical/` from the originals: it finds each
design's text blocks and moves them into 1080x1920, left blocks stay left, right stay right, others centre, rows
spread over the safe band y 230 to 1400 (clear of the IG top bar and the caption / button zone), and colliding blocks
are pushed down. 7 is padded to a band, 10 centre-cropped, 12 stretched to a tall oval with REC kept sharp.
Per-design tweaks (block scale, how far apart words still count as one block) are in `PRESETS`. Check
`reference/pack-vertical.jpg` before using one, and check the real frame in the stills step: the vertical versions
are automatic, so nudge a preset when a block lands on the face or on captions.

## 5. Using them in a build

```python
from vlog_overlays import Overlay, screen, keyed      # copied into the project's work/
ov6, ov12 = Overlay(6), Overlay(12)
def frame_at(t, base):                                 # base: BGR uint8 frame of the edit at time t
    if 0.0 <= t < 3.0:
        base = screen(base, ov6.frame(t - 0.0))
    if 3.0 <= t < 6.0:
        base = keyed(base, ov12.frame(t - 3.0), mode="normal")
    return base
```

Quick look without a build: `python3 scripts/vlog_overlays.py apply edit.mp4 out.mp4 --ov 6@0:3 --ov 12@3:3`.
SFX are not mixed by `apply`; take each overlay's audio (`ffmpeg -i video-overlay-N.mp4 -vn work/audio/ovN.wav`)
into the mix at the same start time.

Placement rules: one overlay design at a time (a corner-credit still can sit under it). Use them at the open, on
location or chapter changes and on energy spikes, not all the way through. Keep big titles off the face; small
corner text is fine. Time the flick-in on a cut or a beat.

## 6. Mini vlog episode template (vertical, 30 to 60 s)

1. **0 to 3 s hook:** best-looking shot + a line that makes them stay; title overlay (1, 2, 6 or 8) flicking in on
   the first cut; pop word on the key word.
2. **3 to 8 s B-roll burst:** 4 to 6 fast shots on the beat, one whip pan, an energy overlay (7 or 10) on the drop.
3. **Middle:** the day in short scenes, each 2 to 5 s, small subtitles; a location/chapter overlay (3, 4, 9, 11)
   at each new place; REC iris (12) for a POV or "pressing record" moment.
4. **Spike before the end:** glitch frame sequence or a fast montage.
5. **End:** payoff or a loop back to the first shot; CTA as a line, not a long ramble.

Ask the user for: the episode's story in one line, the clips, the music mood, which overlays they like, and whether
the baked-in "summer 2026" / "June" text fits the date.
