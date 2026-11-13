---
name: lemo-opuscar
description: Animated explainers and short films made entirely in code, in one of the 99 film styles of the Lemo-Opuscar library (watercolor, chalkboard, whiteboard, newsreel, blueprint, ukiyo-e, neon tubes, pixel RPG, stick-figure explainer, isometric infographic, data storytelling, sketchnote, risograph, 1920s silent film and more), or in a style the user builds from their own colours, fonts and logo. Use when the user wants an animated explainer, a story or idea told as an animated short, a "Lemo" / "Opuscar" video, a video "in the X style" where X is a film or art style, asks which animation styles there are, or wants to make or reuse their own animation style. Not for editing footage (talking head, vlog, VFX): those have their own vibe-* skills, though a Lemo film can be cut into them as a segment.
---

# Lemo-Opuscar (in the Vibe editing setup)

The styles, guides and tools live in the Lemo-Opuscar library (github.com/lemomo-ai/lemo-opuscar, MIT code, docs
CC BY-NC; the user does not monetise, so copying from it is fine). This skill fetches it and hands you over to it, with
the house rules below on top. **Where the library and this repo's CLAUDE.md disagree, CLAUDE.md wins.**

Every command that runs library tools goes through the wrapper, which sets ffmpeg 9 (the container's ffmpeg is 6.1 and
the library needs 7+), the preinstalled headless browser and `LIB`, and runs from the library root:

```sh
sh tools/lemo.sh <command...>          # e.g. sh tools/lemo.sh node core/render/still.mjs "$PWD/projects/reel-08" 0 2.5 5
```

## 1. Get the library (usually already done)

The session start hook clones the library to `~/lemo-opuscar` and installs its core packages in the background (log
`/tmp/lemo-setup.log`, done when `~/.cache/vibe/lemo.ok` exists; it takes about a minute). If it is missing, run
`sh .claude/skills/lemo-opuscar/scripts/setup.sh` and then `PATH=$HOME/.local/lemo-bin:$PATH sh .claude/skills/lemo-opuscar/scripts/setup.sh deps`.
Its last line prints `LIB=<path>`. Never run `npx playwright install` (CLAUDE.md); `setup.sh deps` uses playwright-core's
own installer, which is a no-op while its version matches the preinstalled browser, and `tools/lemo.sh` points
`PLAYWRIGHT_CHROME` at `/opt/pw-browsers` anyway.

Do **not** install the `voice` tier (Kokoro, edge-tts, faster-whisper): voice and speech checks go through ElevenLabs
(below). Install `deps music` only if the film uses the library's `pluck.py`.

## 2. Follow the library

Read `$LIB/AGENTS.md` and do what it says (Start, finding the style, the one round of questions, treatment, production,
delivery), plus `$LIB/DIRECTOR.md`, `$LIB/TECHNIQUE.md` and the chosen `$LIB/styles/<slug>/STYLE.md`. To list the styles
for the user, copy the style list from `AGENTS.md` into your message (in English) and link the gallery
https://lemomo-ai.github.io/lemo-opuscar/ . The user's own styles live in `~/lemo-my-styles/`, which is wiped with the
container: keep them in the repo instead (see section 4, "Own styles").

## 3. What changes in this repo (house rules on top of the library)

| | |
|---|---|
| Project folder | `projects/<name>/` (name picked by CLAUDE.md "Working in several sessions": next free `reel-NN`, claimed with a push). Wherever the guides say `films/<name>/`, read this folder. Pass its **absolute** path to tools |
| Running tools | `sh tools/lemo.sh node core/render/still.mjs "<abs project>" 1.5 3` (the wrapper `cd`s to `$LIB`) |
| Library files in pages | absolute URLs: `/core/lib.js`, `/node_modules/three/…` (the project is served at `/@film/`) |
| Library files in scripts and `build.sh` | `$LIB/…`, with `LIB=${LIB:-$HOME/lemo-opuscar}` and `PATH=$HOME/.local/lemo-bin:$PATH` at the top of `build.sh`; never `../..` |
| Demo source | not downloaded by default. `sh tools/lemo.sh sh plugin/skills/lemo-opuscar/scripts/setup.sh demo <slug>`, only after `TREATMENT.md` is written (Edit & Documentary styles: before, for their material tools). A demo may need its own assets built first (fonts, paper texture: see its `build.sh`, step 0) |
| Frame size | the user's reels are **vertical 1080x1920** by default (`--size 1080x1920` on every still and video render; the library defaults to 1920x1080). Ask only if the platform is unclear. Keep text inside the reel safe zone (top 250 px and bottom 400 px hold platform UI) |
| Brief and questions | the CLAUDE.md workflow and the library's brief merge into **one** round of questions. Save the brief as `brief.md` next to the library's `TREATMENT.md` |
| Stills first (user rule) | the library's "storyboard only if asked, otherwise don't stop" is overridden. Before any full render: a contact sheet of one still every 2.5 s of the finished film (`--range 0:<DUR>:2.5`), each labelled with its time, plus full-size frames of anything new. Wait for approval. Offer a short low-res draft for moving beats (`--size 540x960 --fps 15`) |
| Voice | ElevenLabs text to speech (`POST /v1/text-to-speech/<voice_id>`, key injected), one request at a time, never regenerate existing paid audio. Save each line as `voices/<id>.wav` plus `voices/dur.json` as the library expects. The library's Whisper speech check is replaced by ElevenLabs Scribe: `python3 tools/transcribe_elevenlabs.py voices/<id>.wav -o work/asr_<id>.json`, and compare the words with the script |
| Music | either the library's code-made score (free: its sampler and `pluck.py`, see TECHNIQUE.md) or ElevenLabs `/v1/music`. Ask before generating paid music. CLAUDE.md music lessons apply (beat grid, phrase length, check where the track really ends) |
| SFX | CLAUDE.md Openverse rule: real recorded sounds first (`tools/openverse_sfx.py`), ElevenLabs sound generation for gaps. The library's synthesised `core/audio` sfx are fine for style-native sounds (typewriter ticks, chalk scratches) where they fit the style better |
| Image generation (✦ styles) | Codex CLI, signed in at the start of every session (CLAUDE.md). `sh tools/lemo.sh .venv/bin/python core/image/gen_image.py --check` confirms it |
| Speed | 4 cores, WebGL runs on SwiftShader (software): 2D canvas styles render fast (a 3 s vertical test took 3.5 s), 3D and shader styles are slow, so test-render a few seconds before committing to one. `--workers 3` |
| Delivery and git | CLAUDE.md export, size limits and SendUserFile rules apply. Commit the project's source, brief, treatment, voice/music/SFX files and `build.sh`; not `out/` or rendered frames. Write a `RENDER.md` with the exact rebuild commands |
| On-screen text and voice | plain human language, never em dashes (user rule) |

## 4. Own styles

When the user makes a style of their own (`$LIB/MY-STYLES.md`), keep it in the repo at `styles-own/<slug>/` (the folder
the library would put in `~/lemo-my-styles/<slug>/`), add it to `styles-own/README.md`, and before using it copy or link
it into `~/lemo-my-styles/` so the library finds it (`mkdir -p ~/lemo-my-styles && cp -r styles-own/* ~/lemo-my-styles/`).
It is a shared file: commit it separately and push it to the default branch (CLAUDE.md rule 4).

Deliver what `$LIB/DIRECTOR.md` §11 lists, in the project folder, then follow CLAUDE.md step 12.
