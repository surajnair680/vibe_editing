# reel-13 handoff: Bulking series, episode 0 (anime villain intro)

Written 2026-11-28 at the end of the first chat. A new session only needs: "read projects/reel-13/HANDOFF.md and
carry on". Read CLAUDE.md, docs/playbook/lessons-learned.md and docs/playbook/toolkit.md first as always.

## Project overview
- User: Suraj, fitness coach on Instagram. Plain human language, no em dashes, short messages.
- Video: **reel-13**, episode 0 of a new **bulking series**: "I am going to bulk until I look like an anime villain"
  (Toji Fushiguro from Jujutsu Kaisen). Instagram Reel, 9:16, 1080x1920, 30 fps.
- Repo: surajnair680/vibe_editing. Session branch: `claude/adoring-bohr-rgq328`. Default branch:
  `claude/compassionate-hawking-7vx8wu` (shared-file changes and finished videos get pushed there too).
- Project folder: `projects/reel-13/`. Rebuild steps: `projects/reel-13/RENDER.md`. Revision log: `work/revisions.md`.
- Timeline editor page for this video (private to him): https://claude.ai/artifact/A7KL71kEmBsgwF6a57nTiF

## Raw files (not in git; ask him to upload again if the container is new)
| File in raw/ | Length | What it is |
|---|---|---|
| ep0_part1.mp4 | 36.0 s | HEVC 1080x1920 30 fps. Hook, Toji, three excuses, "So I am going to show you what is possible" |
| ep0_part2.mp4 | 36.0 s | Who he is (7 years, 27, tech job, coach, type 1 diabetic since 12), "so can you", 2 months in, "Training, food, supplements" |
| ep0_part3.mp4 | 13.1 s | "The wins and the days it goes wrong. How long will it take? Six months? A year? I don't know, but I'm not stopping until I look like him" |
Three separate takes (no line crosses a seam; no hidden audio pre-roll). His room: pink sheet, black tee, handheld mic.
He uploaded them as "Bulking_series_episode_0_part_1/2/3.mp4".

## Secrets (names only)
- ElevenLabs: key injected by the environment's network secret (never ask him).
- Codex CLI: signs in per container with his ChatGPT account (device code flow at the start of every session).

## Current state
- **Rough cut v2 is approved** ("Everything is good except..." on v1, fixed in v2). 53.67 s, 26 pieces.
  Out files (not in git): `out/reel-13-rough-v2.mp4`, `out/reel-13-rough-v2-preview.mp4` (720p, 10.5 MB, sent).
- Voice: ElevenLabs isolation of all three parts, paid and committed: `assets/el/voice_isolated.mp3`
  (never regenerate). Aligned to source by `work/align_voice.py` (2.6 ms offset, within 1 ms).
- Nothing else built yet: no captions, music, graphics or SFX, no brief.md beat sheet.
- Timeline page (version 4 published): tracks Cuts / Voice / Words / Graphics / SFX / Music / Notes, "Last render"
  plays rough v2, "Live cut" plays trims from the raw proxy. Checked 2026-11-28: no trims (`edits/current` absent)
  and no notes in its database.

## What was done (chronological)
1. Claimed reel-13, scaffolded with the talking-head new_project.py, copied reel-12's .gitignore.
2. Transcribed each part with Scribe (`work/words.json`, `work/p2/`, `work/p3/`), contact sheets, summary.
3. `work/join_audio.py`: parts' audio on one timeline (offsets 0 / 36 / 72, `aresample=async=1:first_pts=0` keeps
   each part's 19 / 8 ms start gap). `work/parts.json`.
4. Voice isolation (one request on the joined 85.1 s WAV), alignment.
5. `work/plan_cut.py` (from reel-12): pauses over 0.38 s cut, envelope-based in/out points; `IN_FLOOR` skips the mic
   being raised at 5 lines (5.82, 10.24, 32.12, 56.5, 69.32 source); `work/mic_motion.py` measures that motion.
   `work/make_cut.py`: one ffmpeg input per piece, audio from the aligned isolated voice, 5 ms fades, peak -1.5 dBFS.
   Scribe check of the cut: every word kept.
6. v1 note: "the part just after 'supplements' where I reach out to pause the camera needs to be cut" ->
   `OUT_CEIL {71.58: 71.70}`, 7 frames removed at 45.53 s, rest unchanged (frame check). v2 approved.
7. Toolkit pass offered 5 ideas (below). He has not picked yet and has not sent assets.
8. He asked for a video editor where he can see the complete timeline. Built the shared `timeline-editor` skill
   and `tools/timeline/` (export_timeline.py, make_proxy.py, build_page.py, editor.html), CLAUDE.md rule, toolkit
   line, lessons; pushed to the default branch; other open chats were told.
9. Page fixes from his questions: "I cant see 'Send to Claude'" (it only showed after a change, buried on phone),
   then "so there is no point in having that button right?" -> removed it. Trims and notes save automatically;
   he says "done" in the chat. Timecode shows hundredths, not frames (0:53.17 read as seconds).
10. He asked "show me the video made till now" (resent rough v2), then whether we use HyperFrames or Remotion:
    neither (ffmpeg + Python + our own browser renderer); HyperFrames is installed but unused, Remotion not
    installed. Advice given: no switch; the real gain is building graphics as web pages so the timeline page could
    play them live. He has not answered that.

## What to do next
1. Ask for the visuals assets (or confirm Codex makes them):
   - his physique photo or clip for "this is me after seven years" (face must show, lessons rule)
   - 2 or 3 Toji images (real anime frames; Codex cannot reliably draw a named character)
   - anything for "two months into this bulk" and for training / food / supplements / bad days (Codex fills gaps)
2. Get his pick of the toolkit ideas (default: all five). Times are rough v2 edit times:
   - 0:03-0:09 Toji: parallax push on a Toji image, ink callout lines + slammed words on "wide back", "arms like
     carved stone", "V-taper" (photo-parallax + reel-12 manga lettering)
   - 0:13-0:20 three excuses as numbered stamps, crossed out in red on "what is possible"
   - 0:22 his physique photo with parallax; 0:51 "until I look like him" = him and Toji side by side
   - 0:27-0:36 kinetic stat cards: 7 YEARS / 27 / TECH + COACH / TYPE 1 DIABETIC SINCE 12 (motion-effects)
   - 0:38-0:47 DAY 60 counter (milestone-reveal) + one visual per list item (Codex, parallax)
   - music from 0:00, dark villain-style build, ducked about 18 dB under the voice; Openverse SFX on cuts and hits
   - New since: `edit-like-kallawaymarketing` skill (top title, one graphic per line, him in a rounded bottom strip,
     head popping out). Worth offering as a look option for this episode.
3. Then the normal workflow: brief.md + beat sheet with a tool column, approval, stills every 2.5 s before any
   render, build, update the timeline page (export with the new --version, upload the new preview, rebuild,
   publish the same file path), review, final.
4. Caption height: he holds a mic at chest height; ask about caption height at the stills step.

## Important constraints and gotchas
- Stills first before any full render; apply notes on stills first.
- Every physique shot shows his face; every spoken list item gets its own visual; real photos stay unfiltered.
- Cut audio only from WAVs decoded from the start (never seek the MP4 audio). Paid audio is committed; never pay twice.
- His parts end with him reaching to stop the camera and lines start with the mic rising: check the frames at every
  part's last out-point and every in-point.
- Timeline page: when he says "done", ArtifactData `get edits/current` + `list notes` on the page URL, restate,
  save trims to `work/timeline_edits.json` (plan_cut.py applies them by segment id c01..), apply notes, render,
  republish the page, then delete `edits/current` and mark notes done. The page cannot wake the session.
- Live cut only shows raw footage; graphics appear after a render (say so plainly).
- Every shared-file change: separate commit, cherry-pick onto the default branch in a temp worktree, push, notify
  other open sessions (list_sessions mine:true, send_message).
- Uploads to the page: asset upload max 15 MB per file; urls `/_blob/<id>` live in `work/timeline/media.json`.
