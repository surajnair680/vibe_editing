---
name: reference-to-motion
description: Turn references you admire into a scene-by-scene Claude Motion prompt for your own topic and brand. Takes a video for the moves (screenshots, frames or a contact sheet of a reel or ad) and, optionally, a look reference for the style (a website, a brand, a moodboard). Use when someone says "make me something like this", "break down this reference", "use my website as the look" or "turn this into a Motion prompt". Outputs a short breakdown, then one paste-ready Motion prompt with timings for every scene.
---

## Vibe editing house rules (read first; they override the upstream text below)

Imported 2026-11-24 from github.com/charlie947/motion-graphics-skills (MIT, `LICENSE`), commit `229022e`.
Read `docs/library/motion-graphics-skills/HOUSE-RULES.md` before starting. In short: work in `projects/<name>/mg/<piece>/`,
1080x1920 by default, brand from `docs/playbook/brand/` (or defaults in brackets, never blocked), render with
`node tools/seek_render.mjs` (never install HyperFrames skills or browsers), stills every 2.5 s approved before any
full render, real Openverse sounds with peaks on their frames, his photos and footage never filtered, plain words.
- Writes a prompt for Claude Motion and builds nothing. To copy a reference's motion exactly, use `reanimate`; to build
  the video here, follow the prompt with `motion-effects` or `vox-explainer` and render with `seek_render.mjs`.


You turn references into a Claude Motion prompt. A reference does one of two jobs:
- A MOVES reference is a video. It gives the pace, the scene changes and the one idea.
- A LOOK reference is a website, a brand, a moodboard or my own site. It gives the colours, fonts and feel.
One reference can do both if I say so. If I do not say, a video is a moves reference and anything still (a website, a moodboard) is a look reference. You never copy a video. My topic and my words build the film.

<task>
1. Look at everything I attach and sort it into moves and look.
2. Do not ask about views. If I mention them, you may say what they suggest (people watched to the end), never use them as a gate.
3. Break the moves reference down in five short lines:
   - Pace: how long each shot holds.
   - Change: how one scene turns into the next.
   - Type: size, weight, how words arrive.
   - Colour and light.
   - The one idea that carries the whole video.
4. If I gave a look reference, add a Look line: background, text and accent colours as hex codes, fonts (or the closest Google Fonts), and how it should feel and move.
5. Then ask me, in one batch: my topic, the exact words on screen, the length in seconds and the size (9:16, 1:1, 4:5 or 16:9). Ask for brand colours and font only if there is no look reference and no brief. Skip anything I already gave you. Wait for my answers.
6. Write the prompt.
</task>

<rules>
- From a moves reference, take the pace, the scene changes and the one idea. Leave out its logo, copy, colours and characters.
- From a look reference, take the colours, fonts and feel. Never its logo or copy.
- The look comes from, in order: my look reference, then my motion brief, then a neutral dark palette labelled "Neutral default, replace with your brand".
- Never invent a number. Use only the numbers I give you.
- One visual idea per scene, and each scene grows out of the last one.
- Every timing is in seconds and the scenes add up to the exact length.
- Claude Motion builds, plays and exports the video itself. So never write code, file names, HTML, seek functions, frame captures or export steps into the prompt.
- Keep the prompt under 300 words. Short scene lines beat long specs.
</rules>

<output_format>
Part 1: the five-line breakdown, plus the Look line if I gave a look reference.
Part 2: one prompt in a code block, written to paste into a Claude Motion chat:
- First line: "Make me a motion graphic." Then the format, size and exact length.
- A look line: background, panels, one accent colour, fonts, how things move (ease-out, no bouncing).
- One line per scene: the time range in seconds, a NAME in capitals, what the viewer sees, and the exact words in quotes.
- Last line: "Before you finish, render a still every 2 seconds, check each one for cut-off or unreadable text, and fix it."
</output_format>
