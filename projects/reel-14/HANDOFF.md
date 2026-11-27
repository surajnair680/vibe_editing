# reel-14 handoff: "Successful people are not normal" (reaction reel)

Written 2026-11-24 with the session-handoff skill. A new session: read CLAUDE.md, docs/playbook/lessons-learned.md,
then this file, then carry on from "What to do next".

## Project overview
- Repo: github.com/surajnair680/vibe_editing. This video: `projects/reel-14/`. Session branch:
  `claude/epic-hopper-okz762`. Default branch: `claude/compassionate-hawking-7vx8wu` (shared files and finished
  videos go there; the hook `.claude/hooks/sync-rules.sh` merges it into the session branch before every message).
- The user (Suraj, fitness coach on Instagram, "build your greatest physique") makes vertical reels with Claude as
  editor. Plain human language, no em dashes, short messages.
- reel-14 is a reaction reel: another creator's clip (a woman: "I don't think the best physiques are built by
  mentally normal people") with his reaction inset, then his answer to camera: normal people can't build a physique
  like this, success is abnormal, outliers, balance means nothing ("a class where everybody gets an A"), discomfort
  makes you grow, people judge you (crazy, boring, obsessed), "You, my friend, were never supposed to be normal".
- Format: Instagram Reel, 1080x1920, 30 fps, about 1:42 (cut 101.43 s + 0.9 s end hold in v2).

## Raw files (not in git: ask the user to upload them again after a wipe, in parts under 30 MB)
| file in raw/ | length | what it is |
|---|---|---|
| part1.mp4 | 42.0 s | her reel + his reaction inset (0 to 27.3167 s, untouched), then his take starts |
| part2.mp4, part3.mp4, part4.mp4 | 29.0 / 28.0 / 28.0 s | his talking take, continued (60 fps phone, mic in hand) |
| part5.mp4 | 5.3 s | last line "You, my friend, were never supposed to be normal" |
| flex_p1.mp4 | 16.0 s | mirror posing in his gym, 4 shots cut together (best: front pose 6.8-10.6, side chest 10.6-14.5) |
| flex_p2.mp4 | 12.1 s | more posing (front pose 8.5-12 usable) |
| pullups.mp4 | 11.0 s | shirtless pull-ups at home from behind (reps 4.5-11) |
| vid_1111.mp4 | 11.2 s | wide incline dumbbell press (reps 4.3-11), INJA poster behind (user: leave it) |
| vid_1111b.mp4 | 10.2 s | close side view dumbbell press, pillar foreground, face in profile |
| vid_1111c.mp4 | 9.9 s | press filmed from behind his head, "40" kg dumbbells; use 3.3-6.0 only (women in mirror before, staff after 6.0); cropped zoom 1.2 cx 0 cy 1 |
Original upload names: "Successful_people_are_not_normal_part_1..5.mp4", "flex_12OCT2026_part_1/2.mp4",
"pullups_16nov.mp4", "VID_20261111_180348.mp4", "VID_20261111_180912_1.mp4", "VID_20261111_181801_1.mp4".
Reference reel he wants copied: `refs/ref_klickpin.mp4` (also not in git; 720x1280, 43.9 s, "From Klickpin.com ...
budget vacation roundup..." upload).

## In git (no re-upload needed)
- Photos `assets/photos/`: me_physique_mirror.jpg, me_gym_dumbbell.jpg, me_physique_front.jpg (his 3 approved
  photos, face visible), me_physique_back.jpg (faceless, NOT used), celebrity_musk.jpg (365x547, small: framed, never
  full screen), celebrity_jobs.jpg (706x644 B&W), celebrity_arnold.jpg (738x414 B&W, crowd below him). He sent the
  celebrity photos himself.
- Paid ElevenLabs audio `assets/el/` (never regenerate): voice_isolated.mp3 (his takes from 27.3167 s), music_a.mp3
  (chosen: 150 BPM harpsichord / pizzicato / clock, has a break at 52.4-53.8 s and re-entry at 55.254 s),
  music_b.mp3 (spare), prompts.json.
- Sound effects `assets/sfx/openverse/` (real recordings, CREDITS.md has the "credit needed" lines for the post
  caption): metal_hit, boom, shield_bash, shutter, riser (.wav trimmed + orig/).
- Transcripts (Scribe): work/words.json, work/p2..p5/words.json; edit-time words work/words_edit.json.

## Secrets (names only)
- ElevenLabs: injected by the environment's network secret (no key in the repo or chat).
- Codex: signs in per session with his ChatGPT account (`codex login --device-auth`), asked at the start of every
  session (CLAUDE.md rule). Not needed for reel-14 so far.

## Architecture (how the edit is built)
1. `work/join.py`: joins the 5 parts (stream copy) -> work/full.mp4, work/audio/full.wav, work/parts.json
   (offsets 0/42/71/99/127). Lines cross the p1/p2 and p2/p3 seams; audio pre-roll is only 4-13 ms here.
2. Voice isolation (paid, committed) + `work/align_voice.py` -> work/audio/full_iso.wav (3 ms offset fixed).
3. `work/plan_cut.py` -> work/cut_plan.json (approved rough v1 cut, 101.43 s). Rules inside: pauses > 0.38 s cut,
   lines start no earlier than 0.10 s before the first word (he raises the mic before every line), end before he
   drops the mic (motion check), merge gaps < 0.1 s. `work/make_cut.py v1` -> pieces + work/audio/rough_v1.wav (her
   clip +3 dB to match). `ffmpeg -f concat -i work/cut/list.txt -c copy work/base.mp4` = the picture base.
4. v1 graphics (rejected): `work/build/fx.py`, `scene.py` (Text Flash Cuts).
5. v2 graphics (current): `work/build2/fx2.py` (backgrounds, titles, captions, cut-outs, frames) and
   `work/build2/scene2.py` (INS = inserts and celebrity scenes, TIT = titles with times, GREY section, MOVES = his
   scale/position, caption blocks). Mattes from `work/matte_frames.py` (work/matte/NNNNN.png, not in git).
6. Sound: `work/mix.py` (`--v2` reads scene2 events, `--no-music` drops music A). Master -14 LUFS, peak -1.5 dBFS.
7. Rebuild steps in full: `RENDER.md`. Revision log: `work/revisions.md`. Beat sheet (v1): `work/beats.md`.
   Motion spec of the reference: `reanimate/spec.md`. Brief: `brief.md` (written for v1; the look section is
   superseded by v2 below).

## Current state
- Rough cut v1: approved (he moved on to graphics).
- v1 (Text Flash Cuts, red/black/paper serif flash cards 2-9 frames): delivered as out/reel-14-v1.mp4 (28.5 MiB,
  voice + SFX). REJECTED. His words: "several parts are so brief that the viewer doesn't know what the hell is going
  on. Like some words just come up briefly like a stun grenade", then "I didn't like what you made. Use the look and
  feel of the attached video. I think reanimate skill helps do this."
- v2 (reference look) plan he approved with "yes, go ahead":
  - his talking shots cut out of his room onto a deep red background with drifting hairlines (real colours, only the
    room replaced), scaled 0.82 so titles read above his head, shoulders faded at the old frame edge;
  - condensed Bebas Neue titles, letters fading in scattered over about 0.6 s, held 1 to 3 s (20 titles);
  - Inter captions building word by word (60 % in 0.15 s, full by 0.8 s, 4 px blur-in), top of frame; frosted box
    on gym clips; no caption on physique photos;
  - grey section with red circles for "Balance is something everybody can do ... The A means nothing", red A struck
    through, hard cut back to red on SCREW / BALANCE;
  - Jobs cut out on red; Arnold framed under OUTLIERS; Musk framed;
  - CRAZY / BORING / OBSESSED stacked left while he slides right;
  - every element at least about 0.8 s; still NO music ("Don't add music yet"), sound effects only.
- v2 stills (every 2.5 s) + 8 key frames + a 12 s motion sample were sent. WAITING for his notes or "go".
  After sending, BALANCE/SCREW titles were extended to hold until "need" (69.96 s) and the close press clip starts
  there (not yet shown to him; tiny change).
- Reanimate: used to film and measure the reference (frames, caption energy curve, letter reveal); the full
  side-by-side compare loop (`compare.ts --offset 0`) was NOT run. Offered to him as optional.

## Bugs fixed this session (all caught before he saw them unless noted)
- Mic raise/drop visible at cut points -> LEAD 0.10 s + motion-based out rule (plan_cut.py), commit 21bb811.
- 2-frame jump cut mid-sentence from the out rule -> merge gaps < 0.1 s, same commit.
- Women in the mirror in vid_1111c -> later src + zoom 1.2 crop, commit 5402982.
- Flash cards unreadable / cut-off giant words (v1) -> redesigned layouts; then the whole style was rejected by him.
- "So Is something" capital from Scribe's part start -> lowercased in captions.
- Mix: soft limiter let peaks to -0.4 dBFS -> look-ahead limiter; music 10-13 dB under voice late in the reel ->
  level riding (16-23 dB under), commit 6c5b2df.
- v2: wall fringe around his hair -> edge_fix limited to the hair band (first version ate ears and cheeks); titles
  hidden behind his head -> cut-out scale 0.82; hard vertical shoulder edge -> 170 px fade; CRAZY drawn twice; red
  circles colliding with titles; strike-through drawn too high; cv2 on a read-only array -> copy. Commits ca493b1,
  fab3210.

## What was done this session (short)
Codex sign-in -> 5 parts reported -> rough cut v1 (ElevenLabs isolation) -> look options (Lemo double exposure,
then Text Flash Cuts chosen) -> his photos found on old branches, gym clips uploaded, Musk/Jobs/Arnold photos ->
beat sheet approved -> v1 built, music A mixed but held back -> v1 rendered and rejected -> reference reel ->
reanimate measurement -> v2 kit, mattes, stills and motion sample -> session-handoff skill installed (shared,
commit 1d38004 on the default branch, other session notified).

## What to do next
1. Wait for his notes on the v2 stills and motion sample. Apply notes on stills first (CLAUDE.md "Stills first").
2. On "go": render v2 in 4 ranges (RENDER.md step 10), `python3 work/mix.py v2 --no-music --v2`, mux, 2-pass under
   30 MiB, check the real MP4 (frames, black frames, sync 0 ms, start/end), send, log in work/revisions.md.
3. Music only when he asks: drop `--no-music`. Music A is already arranged so its break sits under "an A. The A
   means nothing" and slams back on "Screw" (68.83 s).
4. Offer the post caption (lessons: two plain paragraphs, no emoji, hashtags or CTA) and the credit lines from
   assets/sfx/openverse/CREDITS.md.
5. When he approves the final: merge the branch into the default branch and push (standing permission), run the
   wrap-up review (vibe-wrap-up skill).
6. Revisions after a full render: splice only changed seconds (CLAUDE.md "Revisions").

## Constraints and gotchas
- Nothing on screen shorter than about 0.8 s (his hard note on v1). No flash cuts.
- His face visible in every physique photo; no caption over physique photos; faceless training clips are fine;
  faceless physique photo (back pose) not used.
- Real assets stay real: his footage, photos, gym clips and the celebrity photos are never recoloured; only
  backgrounds and graphics take the style.
- Her clip 0-27.3 s stays untouched (picture and sound).
- Never regenerate paid audio. ElevenLabs: one request at a time, retry on 429.
- Freesound downloads are flaky from the container (some 403): retry `tools/openverse_sfx.py get` with waits.
- Mattes take about 30 min on 4 cores and block other work: start them early, background with absolute paths.
- `work/build2/scene2.py` imports `work/build/fx.py` for the clip loader: keep both.
- Render speed: about 0.3 s a frame per process; 4 ranges in parallel for a full render.
- The project .gitignore drops *.wav, *.png, *.mp4: SFX wavs are re-included; reference frames are excluded.
