# Vibe editing project

Video editing with the Vibe Editing System by Ideabro Studio. **Docs map: `docs/README.md`** lists every doc and when
to read it, in three folders: `docs/system/` (the bought Ideabro guides, never edit), `docs/playbook/` (the user's own
knowledge, grows every video) and `docs/library/` (outside references the user shared). New doc: put it in the right
folder and add one line to `docs/README.md`. The two guides are the source of truth:
- `docs/system/vibe-editing-system-reference.md` (Part 1): the technical reference. Tools, eyes and ears, filming, effects.
- `docs/system/vibe-editing-workflow.md` (Part 2): the step-by-step workflow for every edit, with copyable prompts and the
  reusable editing brief. Read it before starting any new video.
- `docs/library/cinematic-gym-shotlist.md`: a 9-step, 35-shot gym session shot list (LS / MS / CU) with cinematic tips. Use it
  to name shots in footage requests, plan a gym shoot, tag the user's gym clips and order gym B-roll.

The skills in `.claude/skills/` are the playbooks per video type (`vibe-editing-system` picks the type; `vibe-talking-head`
for talking-head footage; `vibe-mini-vlog` for mini vlogs / day in my life with the camcorder overlay pack, vertical by
default). Follow the workflow below for the order of work, and the matching skill for the techniques.

## The workflow (every video)
1. **Workspace:** one project folder per video under `projects/<name>/` (`new_project.py`). Check tools and do a short test render.
2. **Reference:** the two guides above are already loaded. Also read `docs/playbook/lessons-learned.md` in full (everything
   learned on past videos: the user's taste, recipes, mistakes). Note any gap between them and this environment before editing.
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
5. **Picking up other sessions' changes (automatic, never the user's job).** The hook `.claude/hooks/sync-rules.sh`
   runs before every user message: it fetches the default branch and merges it into yours (it only brings shared files
   and other videos' folders, which never conflict with your folder). When it reports changed shared files, re-read
   CLAUDE.md and any changed skill, hook or tool before doing anything else, tell the user in one line that the latest
   rules are loaded, and push the merge with your next push. If it reports a failed merge, merge by hand and re-read.
   Also fetch and merge yourself before starting any new step. Never ask the user to remember, relay or trigger
   anything between sessions (no "tell your other chat to..."): after changing shared files, notify the user's other
   open sessions on this repo yourself (claude-code-remote `list_sessions` with `mine: true`, then `send_message`).
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
- **Setup:** `.claude/hooks/session-start.sh` installs the Python packages and system libraries each new session
  (including libGLESv2, which MediaPipe needs). It also starts a background install of the cut-out tools (rembg,
  onnxruntime, mediapipe, the u2net_human_seg model and MediaPipe's person model at
  `~/.cache/vibe/selfie_multiclass.tflite`); log in `/tmp/vibe-extras.log`, done when `~/.cache/vibe/extras.ok` exists.
  Kokoro-onnx (AI voice) is still installed only when a brief needs it.
- **Media and git:** this is a cloud session that gets wiped. Never modify original footage. Raw footage and rendered
  video are not committed (see `.gitignore`); GitHub blocks files over 100 MiB. Paid audio (isolated voice, music,
  SFX as .mp3) is committed so it is never paid for twice. Final videos reach the user through SendUserFile, which
  accepts at most 30 MiB per file (uploads from the user are also capped at 30 MB). Everything needed to rebuild the
  edit is committed and pushed. Delivery of a final bigger than 30 MiB:
  1. Encode with a keyframe every second (`-g 30 -keyint_min 30 -sc_threshold 0`). Per-frame paper grain or noise
     makes files huge (reel-02: 45 s at crf 18 = 435 MB, about 17 parts). If the file needs more than about 3 parts,
     show the user the options with real numbers (crf, size, number of parts, a full-size crop comparison) and let
     them choose; never lower the quality without asking. Instagram re-compresses every Reel, so also remind them to
     turn on Settings > Data usage and media quality > Upload at highest quality.
  2. Split the video only: `-map 0:v -c copy -f segment -segment_times <t1,t2..> -reset_timestamps 1` at keyframes.
     A plain `-c copy -f segment` split of video plus audio leaves each part's audio one AAC frame (21 ms) off.
  3. Mux each part's audio fresh from the master mix WAV for exactly that part's range (`-ss`/`-t` on the WAV, which
     is sample accurate), AAC 256k.
  4. Check: each part under 30 MiB; the parts' video joined with the concat demuxer matches the full file frame for
     frame (framemd5 of the video stream); each part's audio cross-correlates with the mix at 0 ms. Then send.
- The user wants plain, human language and never uses em dashes. Keep that style in messages and on-screen text.

## Learning loop (user rule, 2026-10-29): get better with every video
The user wants every lesson, skill and piece of knowledge from every session carried into all future sessions, with
nothing missed. Memory does not survive between sessions; only this repo does. So:
1. **Start of every video:** read `docs/playbook/lessons-learned.md` in full, and apply it from the first message (footage list,
   beat sheet, stills checks, delivery).
2. **During the video, as it happens:** whenever the user gives a note, corrects something, states a preference, or a
   technique, tool, model or number proves itself (or fails), add it to `docs/playbook/lessons-learned.md` in the right section,
   tagged with the video name. Don't wait for the end; a session can be cut off.
3. **The most important ones** (things that cost a revision, or that apply to every video) also go as a short bullet in
   the lessons list below, since CLAUDE.md is always loaded.
4. **Before calling a video done** (final approved, or the user moves on): review the whole session for anything not yet
   written down (user taste, effects that worked with their code location, mattes, timings, sizes, mistakes), add it,
   and tell the user in one line what was added. The user can also call **`/vibe-wrap-up`** (`.claude/skills/vibe-wrap-up/`)
   at the end of a session: it does this full review, explains every lesson in detail and pushes it to the default branch.
5. These are shared-file changes: commit them separately from video work and push them to the default branch at once
   (rule 4 of "Working in several sessions at once"), so the next session starts with them. No need to ask first.
6. Reusable code (effects, matte recipes) stays in its project folder; the lessons file points to it by path and the
   next project copies it in.

## Lessons from past edits (keep adding to this list; full detail in docs/playbook/lessons-learned.md)
Learned on reel-02 (2026-10-14). Each one cost a revision or a re-render once; follow them from the start.
- **Cut audio from WAV, never by seeking into the phone MP4 or an MP3.** `-ss` on a phone MP4's AAC track (and on
  MP3s) lands up to 100 ms off, so rough cuts drift out of lip sync. Decode each clip's audio to WAV from the start
  (`work/audio/<clip>.wav`, and the isolated voice .mp3 to .wav too) and cut that. Seeking the picture is fine (it
  lands within a frame). Verify sync by cross-correlating each cut piece against audio decoded from the start of the
  source, never against another seeked read (two equally wrong reads agree with each other).
- **Cut points come from the sound and the picture, not from padded word times.** Scribe's word end times are early
  on soft endings ("are", "program": the r, m, n, s ring on 0.2 to 0.4 s) and ignore breaths. Fixed pads (0.1 s in,
  0.16 s out) clipped words and chopped inhales, which the user heard as abrupt cuts. For every in and out point:
  measure the voice envelope in 10 ms steps, end only after the word has decayed to the noise floor, start a line on
  its inhale (or in silence just before the onset when the inhale is long), and look at the frames around the cut for
  movement the user does not want seen (raising or lowering the mic, looking down at the phone to start or stop
  recording). Keep gaps between lines tight but never cut into sound. Reference: `projects/reel-02/work/plan_cut.py`.
- **One ffmpeg input per cut piece.** Feeding one long input into many `trim` filters buffers the whole clip and gets
  the process killed (SIGKILL, out of memory). Give each segment its own `-ss/-t` input. Reference:
  `projects/reel-02/work/make_cut.py`.
- **Music: find the beat grid and the phrase length before looping or extending.** Detect the tempo and grid phase
  (kick onsets in the low band) and the phrase length (bars whose rhythm envelopes match, usually 4 bars). Repeat whole
  phrases at phrase boundaries; a 2-bar repeat can jump mid-phrase even when the splice is on the beat. Check where the
  generated track really ends (ElevenLabs tracks can end before their requested length) against the edit length.
  Snap wipes and slams to the grid and put the drop on a big transition. Reference: `projects/reel-02/work/mix.py`.
- **"Voice louder, music the same":** key the music's ducking from the voice before the boost and fix the master gain
  to the approved preview's, instead of normalising the new mix (normalising would turn the music down).
- **Captions vs a handheld mic.** At reel-01's caption height (about 1440 px) the captions sit on a handheld mic.
  Ask about caption height when the user holds a mic, at the stills step, not after.
- **Cut-outs over the floral sofa:** rembg alone keeps the sofa. Refine with MediaPipe:
  copy `projects/reel-02/work/refine_matte.py` into the project and run it with
  `--grow 6 --thresh 0.3 --kill-florals --solid-below 0.68 --model "$HOME/.cache/vibe/selfie_multiclass.tflite"`.
- **Check user-supplied clips for burned-in captions** (a previous edit's text) before planning them in; ask for the
  clean original.
- **Explain any decorative element in the stills.** The user asked what "Rx" and the barcode were and had both removed:
  avoid ornaments that carry no meaning for this audience.

Learned on the mini vlog style study (2026-10-30):
- **Mini vlog series is coming, mostly vertical.** For any vlog or day in my life video load `vibe-mini-vlog`: it has
  the reference reel breakdown, the overlay pack (horizontal + vertical versions), Screen / key compositing and the
  episode template. Image overlay 2 carries the pack creator's credit and a typo: crop or rebuild it, ask first.

Learned on reel-03 (2026-10-29), a shot-for-shot remake of a reference edit with the user's footage:
- **His physique is the product.** Never let an effect eat the physique shot: give it at least 0.6 to 0.7 s of clear view
  before a silhouette, glow or flash takes over, even when the reference cuts faster. A 4 s static hold needs something
  to happen in its second half.
- **Silhouettes and outlines of his body must be anatomically right** (head, hair above a raised hand, hands). Combine
  mattes (u2net body + isnet hands + MediaPipe hair/person for the head); check at full size. Recipe:
  `projects/reel-03/work/matte/make_c07_alpha.py`. Never remove background people with a straight cutting line: fade
  the effect out on that side instead.
- **Remaking a reference:** use its frame rate, measure every cut frame by frame, time captions from the reference's
  picture (caption-band strip sheet), copy its audio bit-exact. Method and effects: `docs/playbook/lessons-learned.md` sections
  2 and 5, code in `projects/reel-03/work/build/`.
- **Footage requests:** describe the kind of footage each moment needs (feel + examples), not exact shots; track a short
  "still needed" list as clips arrive. Google Flow's sparkle watermark (bottom right) hides with a punch-in of 1.15+.
- **Check every still yourself before sending:** logos and bystanders in crops, text on the face or beard, captions over
  the brightest glow.
- **Quality talk:** grain drives file size (22 s: crf 14 = 65 MB, crf 20 = 33 MB, crf 22 = 25 MB, visually the same on a
  phone; Instagram re-encodes to 3 to 5 Mbps). Offer the one-file version plus near-lossless parts under 30 MiB each.
