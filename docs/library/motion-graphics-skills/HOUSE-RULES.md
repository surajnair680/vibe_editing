# Motion graphics skills pack: Vibe editing house rules

Imported 2026-11-24 from github.com/charlie947/motion-graphics-skills (MIT, `LICENSE`), commit `229022e` (2026-10-11).
15 skills, each in `.claude/skills/<name>/` with a short house-rules block on top of the upstream text. This file is the
long version and applies to all of them. Where it disagrees with the upstream text, this file wins. The pack's README,
prompts and validator are kept next to this file for reference (`README.md`, `prompts/`, `validate-skills.sh`).

| Skill | What it makes | Notes for this repo |
|---|---|---|
| `vox-explainer` | Vox-style documentary explainer: torn paper, halftone, condensed type, stepped motion | Tested kit and example in `example/` |
| `motion-effects` | 16 premium UI / data / type / system effects, 8 s loop or hold | Recipes in `references/effects.md`. Use hold mode under a voice |
| `animated-chart` | Bars to line, count-up, before / after | Every value exactly as given |
| `milestone-reveal` | Particle sky pulls into a real number | Followers, PRs, kg lifted: real numbers only |
| `launch-video` | 30 to 45 s product / offer launch | For his coaching offers or programs |
| `apple-launch-film` | Mac notch to widgets launch film | Needs an outside skill, see its block |
| `title-sequence-3d` | 8 to 15 s Three.js cinematic opener | Local Three.js, see its block |
| `newsletter-promo` | 12 to 20 s promo for an edition | |
| `loop-cover` | Seamless looping cover GIF | |
| `reel-export` | Wide video to a clean 1080x1920 Reel | Our delivery rules on top |
| `model-showdown` | Same brief to three AIs, side by side | Claude here plus Codex; third model needs him |
| `brand-intake` | Writes brand.md and MOTION.md | Saved in `docs/playbook/brand/`, never in root CLAUDE.md |
| `motion-brief-writer` | Turns an idea into a build brief | |
| `motion-prompt-writer` | 8-part prompt for Claude Motion | Writes a prompt, builds nothing |
| `reference-to-motion` | Reference to a scene-by-scene Motion prompt | Writes a prompt, builds nothing |

## 1. Where things go
- Every piece of video work lives in its own project folder, `projects/<name>/` (the `reel-NN` naming and claiming rule
  in CLAUDE.md). A pack build goes in `projects/<name>/mg/<piece>/index.html` with its `fonts/`, `assets/` and
  `work/` next to it. Never inside the skill folder (that holds only the tested example).
- Start like any other video: read `docs/playbook/lessons-learned.md`, then the workflow steps (inputs, brief,
  beat sheet, approval).

## 2. Brand
- The upstream skills say "run brand-intake first". Here: if `docs/playbook/brand/brand.md` and `MOTION.md` exist,
  read them and use them. If not, do not block: offer his reel colours or the skill's own defaults (labelled as
  defaults), with every brief question carrying a default in brackets, and offer `brand-intake` once.
- `brand-intake` saves to `docs/playbook/brand/` (shared, pushed to the default branch like any playbook file) and
  adds one line to `docs/README.md`. It never pastes its block into the root CLAUDE.md; a per-video look goes in the
  project's `brief.md`.

## 3. Size, frame rate and safe zones
- Default 1080x1920 (Reels), even where the upstream default is 16:9. Make 16:9 or 4:5 only when he asks.
- 30 fps, except `vox-explainer`: 24 fps with every pose held for 2 frames ("on twos").
- Words and logos inside y 250 to 1420 and out of the right 120 px. A headline over footage follows `reel-export`
  (y 360 to 1420). Nothing over his face, his physique or the captions.

## 4. Rendering: `tools/seek_render.mjs`
The pack's pages define `window.seek(seconds)`. Render them with our tool, which uses the preinstalled Chromium:
```
node tools/seek_render.mjs <page>.html --size 1080x1920 --dur 14 --every 2.5 --sheet out/sheet.png     # stills
node tools/seek_render.mjs <page>.html --size 1080x1920 --at 3.2,7.5 --dir out/stills                  # chosen frames
node tools/seek_render.mjs <page>.html --size 1080x1920 --fps 30 --dur 14 --scale 0.5 -o out/draft.mp4 # low-res draft
node tools/seek_render.mjs <page>.html --size 1080x1920 --fps 30 --dur 14 --audio work/mix.wav -o out/master.mp4
```
- Add `--start a --end b` to render one range for a revision (then splice, as CLAUDE.md says).
- Masters use lossless PNG frames, crf 14, bt709, limited range, yuv420p, faststart. Speed: about 7 frames a second
  at 1080x1920 (the 14 s test, 336 frames, took 47 s). Stills take a few seconds.
- It also reads `window.renderFrame(t)` pages (the Ideabro `templates/web` format).
- Never run `npx skills add heygen-com/hyperframes`, `playwright install` or any browser download. HyperFrames is
  available pinned (`npx hyperframes@0.8.150`, browser path set by the start-up hook) but expects its own composition
  format; for a `window.seek` page use `seek_render.mjs`.
- Pages must be self-contained: fonts loaded with `@font-face` from local files (copy TTFs from another project's
  `fonts/` or download the Google Fonts TTF into the project), images local, nothing loaded at render time. Expose
  `window.ready` (a promise) that waits for images and fonts; the tool waits for it and draws frame 0 once before
  capturing (the pack's "frame 0 in the wrong font" bug).

## 5. Stills first
CLAUDE.md's rule beats the pack's "build, then export": a contact sheet every 2.5 s plus full-size frames of anything
new, checked by you first (cut-off text, overlaps, spelling, safe zones, faces), then sent; render only after he says
go. Offer a half-size draft for beats where motion matters.

## 6. Sound
- The pack says "write a score in code". Here: real recorded sounds from Openverse on every landing, cut and wipe
  (`tools/openverse_sfx.py`), each one's peak on its frame (see `vox-explainer/example/mix.py`), and music when it
  fits (ElevenLabs, ask first). A code-made bed only if he asks for it.
- Voice: his own recording or ElevenLabs. Time shots to the voice from Scribe word timings
  (`tools/transcribe_elevenlabs.py`), never Whisper or Kokoro.

## 7. Content
- Every number, name, date and quote on screen comes from him or from a source you show him (the pack says the same).
- His photos, his footage and celebrity photos stay unfiltered: a torn white paper frame or a card around them is fine,
  halftone or a colour wash over them is not. His face shows in every physique picture.
- Plain words on screen, no em dashes, no decorative symbols that mean nothing to his audience.
- Real logos come from real files, never drawn from memory.
- Images he does not have: Codex image generation (CLAUDE.md), but no AI-drawn people for a style he would call slop.

## 8. Into a reel and delivery
- A pack graphic inside a talking-head reel: render it as its own clip at the reel's size and fps and cut it in, or give
  it a pure black background and Screen-blend it over the footage.
- Delivery and the 30 MiB limit: CLAUDE.md "Media and git". The 14 s Vox test at crf 14 is 24.7 MB.
- Commit the page, fonts, assets, mix script, Openverse sounds and brief; renders stay out of git.

## Updating from upstream
Clone the repo, copy each `skills/<name>/` over ours, then put back the house-rules block at the top of each SKILL.md
(keep a diff of the block first) and bump the commit above. Keep `LICENSE` in every skill folder.
