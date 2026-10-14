# Brief: reel-02

> Ideabro Studio · Vibe Editing System. Decisions are filled in as they are approved.

## 1. The job (step 4)
- **Video type:** talking-head
- **Platform / format:** Instagram Reels, 9:16, 1080x1920
- **Length:** about 43.4 s after trimming
- **Language:** English voice, English word-by-word captions. No spellings to check.
- **CTA:** none. Ends on "just start."

## 2. Inputs
- `raw/VID20261007161237.mp4` (clip A, 11.1 s): the hook, no mic in frame.
- `raw/1000097826.mp4` (clip B, 72.9 s): the story and lesson, holding a mic. Joined from 5 uploaded parts
  (`raw/parts.txt`, `ffmpeg -f concat -c copy`).
- Transcripts: `work/short/` (clip A) and `work/main/` (clip B), ElevenLabs Scribe.

## 3. Cuts and pacing (step 5, rough cut v3 sent, waiting for notes)
- Clip A then clip B. Second takes of the two repeated lines ("At the end, the best photos all came..." and
  "Repeated actions will teach you...").
- Natural pace: up to 0:23.9 gaps between lines are about 0.25 s (approved). From "no matter how intelligent you are"
  to the end, cuts sit in measured silences and keep each inhale (v2, v3), "first, then make it perfect" is uncut, last line starts with the mic up and
  ends before the mic drops (v3).
- Plan: `work/plan_cut.py` -> `work/cut_plan.json`. Cut: `work/make_cut.py` -> `work/cut.mp4`.

## 4. Music (step 6)
- New ElevenLabs track. The user is deciding the kind of music first.

## 5. Look (step 7)
- To be discussed after the trim is approved.
