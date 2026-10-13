# Vibe editing project

Video editing with the Vibe Editing System by Ideabro Studio. Two guides are the source of truth, both in `docs/`:
- `docs/vibe-editing-system-reference.md` (Part 1): the technical reference. Tools, eyes and ears, filming, effects.
- `docs/vibe-editing-workflow.md` (Part 2): the step-by-step workflow for every edit, with copyable prompts and the
  reusable editing brief. Read it before starting any new video.

The skills in `.claude/skills/` are the playbooks per video type (`vibe-editing-system` picks the type; `vibe-talking-head`
for talking-head footage). Follow the workflow below for the order of work, and the matching skill for the techniques.

## The workflow (every video)
1. **Workspace:** one project folder per video under `projects/<name>/` (`new_project.py`). Check tools and do a short test render.
2. **Reference:** the two guides above are already loaded. Note any gap between them and this environment before editing.
3. **Inputs:** confirm every file opens. Report duration, frame size and audio. Transcribe with word timings, inspect frames,
   get the language and correct spellings of names and brands, what must stay and what to leave out. Summarise before cutting.
4. **Finished video:** purpose, audience, platform and aspect ratio, length, hook / main points / CTA, voice and caption language.
   Flag any clash between target length and required content.
5. **Cuts and pacing:** natural, tight, high-energy or story-led. Give a cut list with source timestamps and estimated
   length. Never cut inside a word. Show the rough cut before complex graphics.
6. **Music:** mood, energy, placement, speech stays clear (duck under voice, clean fades). Ask before substituting a track,
   generating music or using anything paid or unreviewed.
7. **Motion graphics design:** from refs, describe colours, type, layout, shapes and movement first. Show one styled frame
   and a short motion sample before styling everything. Keep graphics off the face and out of platform UI zones.
8. **SFX and VFX:** subtle, moderate or bold. Each effect has a word or time, place, duration and purpose. Feasibility test
   complex effects first. No repeated whooshes, nothing over the face or captions.
9. **Theme:** two or three feeling words, what to avoid, and which reference controls colour, motion and pacing.
10. **Build:** combine decisions into a saved brief (`brief.md`). Show a beat sheet first (edit time, source clip and time,
    spoken line, graphic, caption treatment, audio cue) plus missing assets and effects needing a test. Wait for approval.
    Build in passes: cut, then style, then graphics and audio. Save v1 and give a preview. Report anything incomplete.
11. **Review:** notes use timestamps from the current preview, not the source. Save the current version before every
    revision, apply only the notes, keep approved parts unchanged, save as v2, v3... and re-check alignment.
12. **Export:** render the approved edit, then open the actual MP4 and check start, end, captions, framing, voice, music,
    effect timing and no black frames. Deliver it with SendUserFile. Commit and push the editable project (source,
    brief, transcript, asset list, revision notes, render instructions). Report any blocked step honestly.

Habits: one change per note, always a time, approve the plan before the build, rough cut before effects, preview short
sections before a full render, save a template when an effect works.

## Folder names
The workflow guide names folders `input, assets, refs, project, previews, exports`. The skill's tools use a different
layout, so use the skill's and map them like this: input = `raw/`, assets = `assets/`, refs = `refs/` (create it),
project = `scene.py`, `timeline.py`, `brief.md` and `work/`, previews = `out/` drafts and stills, exports = `out/` finals
named `<project>-final.mp4`.

## Rules
- **Transcription:** never use Whisper or the skill's `vibe/transcribe.py`. Use ElevenLabs Scribe instead:
  `python3 tools/transcribe_elevenlabs.py raw/take1.mp4 -o work/words.json`
  It writes the same `words.json`, `segments.json` and `transcript.txt` the skill expects. The API key is injected
  by the environment's network secret, so never ask the user for it.
- **Music, SFX and voice:** ElevenLabs works through the same injected key: `POST /v1/music` (`prompt`,
  `music_length_ms`), `POST /v1/sound-generation` (`text`, `duration_seconds`), `POST /v1/text-to-speech/<voice_id>`.
  Voice clean-up: `POST /v1/audio-isolation` (multipart field `audio`) returns a 320 kbps mono mp3, in sync with the
  source; prefer it over `audio_kit.py voice --denoise`. Prefer these over audio_kit beds and Kokoro TTS. They cost the user's credits, so generate options deliberately. The plan allows at most 2 requests at a time.
- **Rendering with HyperFrames:** `HYPERFRAMES_BROWSER_PATH` is set by the session start hook
  (`/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`). CLI: `npx hyperframes@0.8.150`.
- **Web/shader renders (`templates/web/render.mjs`):** never run `npx playwright install`. Chromium is preinstalled
  at `/opt/pw-browsers` and Playwright finds it on its own.
- **Setup:** `.claude/hooks/session-start.sh` installs the Python packages and system libraries each new session.
  Heavy extras (rembg for cutouts, kokoro-onnx for AI voice) are installed only when a brief needs them.
- **Media and git:** this is a cloud session that gets wiped. Never modify original footage. Raw footage and rendered
  video are not committed (see `.gitignore`); GitHub blocks files over 100 MiB. Final videos reach the user through
  SendUserFile. Everything needed to rebuild the edit is committed and pushed.
- The user wants plain, human language and never uses em dashes. Keep that style in messages and on-screen text.
