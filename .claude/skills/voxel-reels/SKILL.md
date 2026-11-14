---
name: voxel-reels
description: Blocky 3D cartoon dialogue reels built in code (Three.js), not AI video. Two box-built characters (the user as a voxel figure and a small sidekick) talk to camera; mouths move with the ElevenLabs voices, captions pop in word by word with yellow keywords, a top label chip tracks numbered steps, animated cards (checklists, count-ups, typing) land on the spoken word, and the reel ends on "Comment KEYWORD" with confetti. Use when the user asks for a voxel reel, 3D cartoon reel, blocky 3D characters, "me and a sidekick explaining", a reel like @what.if.3d / @canwebuildthis / @heyalok.ai, or a "Claude 3D cartoon reel". Vertical 1080x1920, 30 fps, 30 to 60 s.
---

# Voxel reels (3D cartoon dialogue reels in code)

Adapted from @heyalok.ai's free guide "Make 3D cartoon reels with Claude" (style by @what.if.3d and @canwebuildthis),
rebuilt for this setup and tested here on 2026-11-14. Preview of the kit: `kit/preview.jpg`.

**CLAUDE.md wins over anything below.** The workflow (brief, beat sheet, stills first, sound design, delivery) applies.

## What's in the kit (`.claude/skills/voxel-reels/kit/`)
| File | What it does |
|---|---|
| `reel.example.json` | the one file a reel is made from: voices, characters, look, lines with chips/cards/moods, CTA, sounds |
| `voice.py` | each line through ElevenLabs `/v1/text-to-speech/<voice>/with-timestamps` (word timings come back with the audio, so no transcription), never paying twice for an unchanged line; trims, loudness-matches both voices, joins with 0.14 s gaps into `build/vo.wav` and writes `build/timing.json` (lines, words, per-frame mouth envelope). `--dry` shows the character count first |
| `voxel.js` | the world (night-blue stage, glowing grid, bokeh, warm key + purple rim + fill, soft shadows) and the characters: `human` (skin, hair, shirt, pants, shoes, hairStyle short/long/bun/bald, beard) and `buddy` (box creature, eyes switch normal o o / happy ^ ^ / serious \| \|). Blinks, breathing, talking mouth, gestures, buddy bounce and squash, CTA wave |
| `reel.js` + `index.html` + `style.css` | the timeline: a cut on every line (close-up of the speaker; wide shot for lines with a card, a step or the CTA; `"shot": "cu" / "wide" / "two"` overrides), gentle push-in, captions 2 to 3 words at a time popping on each word, chip + step dashes, cards (`list` ticks on a named word, `count`, `type`, `text`), CTA box + confetti, and the cue list `window.EV` (cut, pop, tick, count, type, chime) for the mix |
| `mix.py` | voice + optional music ducked under the voice + one sound per cue (peak placed on the cue, cut sounds alternate) into `build/mix.wav` |
| `make_code_sfx.py` | fallback cue sounds made in code, for drafts only |

It follows the lemo-opuscar page contract, so the library's tools render it: `still.mjs`, `video.mjs`, `events.mjs`,
`sheet.py`, `mux.sh` (all through `sh tools/lemo.sh`, absolute paths). Needs the library (`~/.cache/vibe/lemo.ok`).

## Making one
1. **Project:** claim `projects/reel-NN/` (CLAUDE.md rule 1). Copy `kit/{index.html,style.css,voxel.js,reel.js}` into it
   and `kit/reel.example.json` as `reel.json`. Fix the project `.gitignore` so `voices/*.mp3`, `assets/sfx/` and
   `build/timing.json` are committed (paid audio) while `build/*.wav`, `out/` and `stills/` are not.
2. **Brief (one round, a default on every question):** topic, length (default 40 s), how he looks as a voxel
   character (skin, hair, beard, shirt colour; default from his photos if he has sent any), the sidekick (default the
   teal box robot; the guide's "little orange Claude" is Anthropic's character Clawd, so ask before using it), comment
   keyword, the two voices. ElevenLabs voices: reel-08 used "Jessica" `cgSgspJ2msm6clMCkdW9`; `/v1/voices` is not
   reachable here, so ask him for a second voice ID or a name from his ElevenLabs library. If he wants his own cloned
   voice, he gives the ID.
3. **Script:** two-character dialogue, hook in the first 3 s (topic first, then proof or a surprise), lines of 3 to
   10 words, the lesson as numbered steps said by the sidekick, CTA last ("Comment X and I'll send you the full
   guide"). Show it as a table (# | speaker | line | on screen) and wait for his OK. Plain human language, no em dashes.
4. **Voice:** `python3 .claude/skills/voxel-reels/kit/voice.py projects/reel-NN --dry`, then without `--dry` (paid,
   one request at a time, CLAUDE.md rule 7). Commit `voices/` straight away.
5. **Stills first:** `sh tools/lemo.sh node core/render/still.mjs "$PWD/projects/reel-NN" --range 0:<DUR>:2.5 --size 1080x1920`
   plus a still at the start of every line; contact sheet with `sh tools/lemo.sh .venv/bin/python core/render/sheet.py`.
   Check every frame yourself first: faces never under a card, chip, caption or CTA; whole head in close-ups; nothing
   in the top 250 px or bottom 400 px. Send, wait for approval. Offer a low-res draft (`--size 540x960 --fps 15`).
6. **Sound design:** real sounds first (CLAUDE.md Openverse rule): pick a whoosh, pop, tick/click, typing and chime
   (Freesound links are blocked here: send him the links to download, then `measure`); put their `peak` times in
   `reel.json` "sfx". Music optional (ask first if paid). Then
   `sh tools/lemo.sh node core/render/events.mjs "$PWD/projects/reel-NN" --size 1080x1920 --out "$PWD/projects/reel-NN/build/events.json"`
   and `python3 .claude/skills/voxel-reels/kit/mix.py projects/reel-NN`.
7. **Render (after he says go):** `sh tools/lemo.sh node core/render/video.mjs "<abs project>" --size 1080x1920 --fps 30 --workers 3 --out "<abs project>/out/video.mp4"`
   then `sh tools/lemo.sh sh core/render/mux.sh <abs>/out/video.mp4 <abs>/build/mix.wav <abs>/out/reel-NN-final.mp4 30 0`
   (grain 0: flat 3D, keeps the file small). Check the MP4 (CLAUDE.md step 12), deliver with SendUserFile.
8. **Thumbnail (optional):** a still with both characters facing camera plus a bold 2-line title; 1080x1920 and a
   1080x1440 crop.

Revisions follow CLAUDE.md: change `reel.json` or the scene, re-render stills of the changed lines, and for the video
render only the changed range when possible.

## Numbers (tested 2026-11-14, 4 cores, software WebGL)
- A still renders in about 0.25 s with shadows on. Video: 192 frames in 40 s (about 0.2 s a frame with 3 workers),
  so a 45 s reel (1350 frames) takes about 5 minutes. The guide's MacBook did 43 s in 3 minutes.
- 6.4 s test: 2.4 MB at mux.sh's default encode, loudness -14.1 LUFS, peak -1.6 dBFS.
- 72 characters of voice for 3 test lines (ElevenLabs bills by character, so one request per line costs the same as
  one long request and keeps every line separately re-doable).

## Framing that works in 9:16 (found on the test, keep it)
- Close-up: camera 5.2 units from a human (4.0 from the buddy), aimed below the head so the head sits in the upper
  third with room around it; push-in only 0.35 units per shot (a stronger push made the face fill the frame).
- Wide: camera at (±0.35, 2.0, 11) aimed at y 1.5; characters at x -0.5 and 0.62. Heads stay below the card.
- Overlay heights (1080x1920): chip 270, card 410, CTA 300, captions 1350. The CTA line always goes wide so the
  keyword box never covers a face. Cards default to wide shots for the same reason.
