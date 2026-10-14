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

Revisions: never re-render the whole video for a local note. Render only the affected time range
(`Stage.render(..., start=a, end=b)` widened to whole seconds), splice it into the previous master, then
re-encode and compare frames against the previous version so only the intended ranges changed. Before
rendering, check whether the change also alters frames earlier or later than the note (e.g. an element that
appears before the noted moment) and keep those frames identical. Long renders: background them with absolute paths.
Speed: motion_kit grain/vignette use cached noise banks and masks (cv2, ~5 ms); grades are a single 3x4 colour
matrix via cv2.transform (see hook_scene.grade_matrix); render masters with `crf=14, preset="veryfast"` since the
delivery file is re-encoded. A full 1080x1920 minute renders in about 5 to 8 minutes on 4 cores.

Stills first (user rule): before ANY full render, v1 or a revision, send the user still frames and wait for their
approval. Only render the video after they say go. The stills: one frame every 2.5 seconds of the finished video
(0, 2.5, 5, 7.5 ... so a 60 s reel = 24 stills), shown as a contact sheet with each frame labelled with its time,
plus full-size frames of anything new or changed. Stills cannot show motion, so offer a short low-res draft clip
for beats where timing or movement matters.
Apply their notes on the stills first and resend if anything changed.

Habits: one change per note, always a time, approve the plan before the build, rough cut before effects, preview short
sections before a full render, save a template when an effect works.

## Working in several sessions at once (user rule, 2026-10-14)
The user edits several videos at the same time, one chat (cloud session) per video. Each session has its own container,
its own clone of this repo, its own uploads and its own CPU. Handle everything below yourself; never make the user
deal with git, branches or naming.

1. **One session = one video = one folder.** At the start of a new video, fetch first (`git fetch origin`), then pick the
   next free name `reel-NN` that exists in no branch (`git ls-tree -d --name-only origin/<branch> projects/` for every
   remote branch) unless the user names it. Create `projects/<name>/`, commit and push it at once to claim the name.
   Tell the user in one line: the video name and the branch. If the user refers to an existing video, work in that
   video's folder and branch; ask only if it is unclear which video they mean.
2. **Stay in your own folder.** Never edit, move or delete another video's files. To reuse something from another video
   (a scene, a look), copy it into your own folder; never import across project folders.
3. **Branches.** Work and push on the branch the session was given. If the user names a branch for a video, use it.
   Before every push: `git fetch origin` and merge the remote branch you push to (`git pull --no-rebase`), then push.
   If a push is rejected, fetch, merge and retry (up to 4 times with 2, 4, 8, 16 s waits). Never force-push and never
   rewrite history.
4. **Shared files** (`CLAUDE.md`, `tools/`, `.claude/`, `docs/`, the skills' toolkits): change them only when the user
   asks for a rule or tool change, in a commit separate from video work. Then deliver it to every future session:
   merge the default branch into yours, and push the same commit to the default branch too
   (`git push origin HEAD:<default branch>`, after `git fetch` and a merge if it moved). The user has given standing
   permission for this push to the default branch, for shared-file changes and finished videos only. Find the default
   branch with `git remote show origin` (HEAD branch).
5. **Picking up other sessions' changes.** At the start of a session and before starting any new step, run
   `git fetch origin` and merge the default branch into yours (it only brings shared files and other videos' folders,
   which never conflict with your folder). If the user says "pull the latest rules", do exactly this and re-read CLAUDE.md.
6. **When a video is approved as final,** merge your branch into the default branch and push it (standing permission),
   so the default branch holds every finished video's editable project.
7. **ElevenLabs is shared by all sessions** (one account: at most 2 requests at a time and one pool of credits). Make
   requests one at a time per session. On `429` / `concurrent_limit_exceeded`, wait and retry (5, 10, 20, 40 s) instead of
   failing; tell the user only if it still fails. Don't regenerate paid audio that already exists in the project.
8. **Uploads and raw footage are per session** and not in git. If the user mentions footage they sent to another chat,
   ask them to upload it in this chat (in parts under 30 MB if needed). If a session restarts and raw files are gone,
   say so and ask for them again; everything else rebuilds from the repo (see the project's RENDER.md).
9. **Renders** never compete across sessions (separate machines), so no waiting on other chats is needed.

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
  SendUserFile, which accepts at most 30 MiB per file (uploads from the user are also capped at 30 MB). For bigger
  finals never lower the quality: encode with a keyframe every second (`-g 30 -keyint_min 30 -sc_threshold 0`),
  split with `-c copy -f segment -segment_time 15`, check each part is under 30 MiB and that the rejoined parts
  match the original frame for frame (framemd5), then send the parts. Everything needed to rebuild the edit is
  committed and pushed.
- The user wants plain, human language and never uses em dashes. Keep that style in messages and on-screen text.
