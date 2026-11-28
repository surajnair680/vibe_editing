---
name: edit-like-kallawaymarketing
description: Edit a talking-head reel in the Kallaway (kallawaymarketing) style - a top-third title with a serif accent word, one animated graphic in the middle, a one-word caption, and the speaker in a rounded strip at the bottom with his head popping out of it, alternating with full-screen talking-head beats (72% graphics / 28% A-roll, a change every 0.5 to 1 s). Use when the user says "Kallaway style", "edit like Kallaway", "kallawaymarketing style", "split layout with my head popping out", or wants an education reel where every line gets a matching visual (frameworks, steps, scripts, tools, charts).
---

# Edit like kallawaymarketing

Learned from 17 kallawaymarketing reels (807 scenes, measured frame by frame, Nov 2026) plus the "Editing Like
Kallaway (Using ONLY AI)" guide. The big idea: **every visual does a storytelling job; none of it is decoration.**
A human (the user) directs what goes where; this skill supplies the look, the rules and the tools.

## Vibe editing house rules (read first)
- This skill works inside the vibe_editing workflow (CLAUDE.md): project folder `projects/<name>/`, Scribe
  transcription (`tools/transcribe_elevenlabs.py`), stills before any render, Openverse sound, lessons logged.
- Graphics are `window.seek` HTML pages (this kit) rendered with `node tools/seek_render.mjs`. The talking head,
  pop-out cut-out and captions are added by `kit/compose.py`. No Remotion.
- On-screen words follow the user's rule: simple words a child understands, short, no jargon, no em dashes.

## Files
| file | read it when |
|---|---|
| `references/scene-types.md` | always: the 22 scene types (design, animation, when and why) |
| `references/frames/<type>/` | to see real examples of a type; `00-hires-measured/` has full-size frames |
| `rules/layout.md` | the two layouts, exact positions, the strip and the pop-out, safe zones |
| `rules/design.md` | fonts, sizes, the title treatments, colour, shapes |
| `rules/animation.md` | timings, easing, camera moves, what not to do |
| `rules/pacing.md` | measured pacing, the reel skeleton, which scene for which line, caption rules |
| `rules/sound.md` | the cue sheet |
| `kit/` | `kallaway.css` + `kallaway.js` (panel kit), `example/index.html` (5 tested scenes), `new_page.sh`, `compose.py` |
| `assets/` | Inter + Instrument Serif fonts (OFL), `bg-dark.png`, `bg-light.png` |

## Workflow
1. **Inputs.** The raw take(s). Transcribe with Scribe. Cut the talking head first (silences, retakes) with the
   talking-head kit, so you have `raw/cut.mp4` (or `work/cut.mp4`) and `work/words_cut.json` on one timeline.
   Report the framing: 16:9 or 9:16, and where the head is.
2. **Planning doc (the most important step; the guide says the human spends ~15 minutes here).** Make a table, one row
   per script line or phrase: `time | spoken words | layout (split / full / broll) | scene type # | what happens on
   screen | reference frame`. Pick scene types with the decision order in `rules/pacing.md`, follow the skeleton
   (hook, name reveal, tracker + steps, recap, CTA) and the rhythm (a FULL beat every 2 to 6 graphic scenes, never
   more than ~12 s of SPLIT in a row). Put it in the project's `brief.md` beat sheet with the cue sheet. **Show it and
   wait for approval.** The user may rewrite any row; their call wins.
3. **Assets.** List what is needed per row: real screenshots, thumbnails, logos, photos, numbers (with sources). Ask
   for what you don't have. Real assets are the credibility; never fake a screenshot or a number.
4. **Panel page.** `sh .claude/skills/edit-like-kallawaymarketing/kit/new_page.sh projects/<name>/mg/panel`, then write one `<section class="k-scene">`
   per SPLIT stretch (FULL and B-roll times can be left empty: compose.py does not use the panel there). Time every
   `data-in` to the Scribe word start of the word it belongs to. Keep the strip zone (y 1403 down) empty.
   Check single frames with `node tools/seek_render.mjs mg/panel/index.html --size 1080x1920 --at 1.2,4.5 --dir out/panel_stills`
   (in a browser: `index.html?t=4.5&guides=1`).
5. **Matte.** `python3 vibe/matte.py raw/cut.mp4` (u2net_human_seg; birefnet-portrait for hair) gives
   `work/matte/cut_alpha.mp4`. Check a few frames: the cap and hair edge are what pop out.
6. **plan.json for compose.py** (format in its docstring): speaker, matte, panel, words, serif words (the framework
   name, the CTA keyword), and the segments from the planning doc. For 9:16 footage start with `"strip": {"scale":
   0.7, "band_top": "auto", "popout": 60}`; for 16:9 use `scale 1.0`.
7. **Stills first.** Render the panel (`node tools/seek_render.mjs mg/panel/index.html --size 1080x1920 --fps 30 --dur
   <D> -o out/panel.mp4`), then `python3 .claude/skills/edit-like-kallawaymarketing/kit/compose.py plan.json --every 2.5 --sheet out/sheet.jpg --dir
   out/stills`. Check every still yourself first: title cut off, caption hitting the head, wrong word, face covered,
   safe zones. Send the sheet plus full-size frames of anything new. Wait for "go".
8. **Render.** `python3 .claude/skills/edit-like-kallawaymarketing/kit/compose.py plan.json -o out/<name>-v1.mp4` (carries the cut's voice). For a note,
   re-render only the range with `--start/--end` and splice (CLAUDE.md revision rule).
9. **Sound.** Build the cue sheet from `rules/sound.md` (every pop, swish, whip, line draw, CTA hit), pick sounds from
   Openverse with peaks on the frames, mix voice + SFX (+ optional bed), mux onto the picture.
10. **Export and log** as CLAUDE.md says. Add anything learned to `docs/playbook/lessons-learned.md`.

## Quick rules (the ones that make it look like Kallaway)
- Title in the top third, max ~7 words, key phrase on line 2, ONE accent: serif italic word, red underline, red box, or
  size contrast.
- One graphic per scene, centred. One red focus at a time. Everything else greys.
- Caption: one word, Inter Bold ~56 px, at y ~1285 in SPLIT and ~1165 in FULL. Framework name and CTA keyword in serif.
- Speaker strip x 68 to 1012, top y 1403, radius 50, running off the bottom; the cut-out head pokes out 40 to 90 px.
- Dark ground with dot texture by default; light grey grid ground for real examples, tool demos and the CTA.
- Something changes every 0.5 to 1 s, on a spoken word. Long scenes build inside and the camera moves.
- Trackers come back before every step (blurred upcoming items, red tab on the current one).
- Hard cuts only. No bounce, spin, glitch or confetti.
- End: CTA card ('Comment *"word"*' + red box + the actual lead magnet), then FULL with the stacked keyword caption.

## Filming tips to give the user (best results)
- Film **16:9 horizontal** at a desk, chest-up, with space above the head (like Kallaway), or 4K vertical from a bit
  further back. Then one take gives both the strip shot and the FULL punch-in.
- A tidy dark background with one or two practical lights reads like his studio; keep the hair and cap edge clear of
  busy background so the matte is clean.

## For a fitness reel (examples of the types in the user's niche)
- Tracker (5a / 5b): "The 3-Step Fat Loss Method" pills, or a 3D dumbbell rack as the hero object.
- Script doc (6) becomes a **workout or meal card**: colour-coded rows (red = main lift, yellow = accessory, green = finisher).
- Graph (10): strength going up week by week, a scale weight line, a "hunger" gauge.
- Device (7): a workout log app or a client's progress photos in a phone.
- Brain (15): motivation, cravings, habits. Metaphor (17): a car running on empty fuel for low energy.
- Before / after (9): two meal plates, two training splits. Proof grid (1): client transformation thumbnails.
