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

## 3. Cuts and pacing (step 5, approved: rough cut v3)
- Clip A then clip B. Second takes of the two repeated lines ("At the end, the best photos all came..." and
  "Repeated actions will teach you...").
- Natural pace: up to 0:23.9 gaps between lines are about 0.25 s (approved). From "no matter how intelligent you are"
  to the end, cuts sit in measured silences and keep each inhale (v2, v3), "first, then make it perfect" is uncut, last line starts with the mic up and
  ends before the mic drops (v3).
- Plan: `work/plan_cut.py` -> `work/cut_plan.json`. Cut: `work/make_cut.py` -> `work/cut.mp4`.

## 4. Audio (step 6)
- **Voice:** ElevenLabs voice isolation on both full clips (`work/audio/<clip>-isolated.mp3`), in sync within 5 ms,
  noise floor 17 to 26 dB lower. Cut to the edit by `work/make_voice.py` -> `work/voice_cut.wav`.
- **Music:** bassy, fast paced and engaging beats, unlike reel-01's dark ambient. Two ElevenLabs options
  (`work/music_prompts.json`, 46 s each): A dark trap at 140 BPM, B gym phonk at 150 BPM.
  Previews: `work/music_preview.py a|b`, music ducked under the voice.
  **Picked: B (gym phonk).** Voice about 10% louder than in the B preview (+1.4 dB) with the music at exactly the
  same level as the preview: keep the preview's music chain and master gain fixed, raise only the voice.

## 5. Look (step 7)
- Same look as reel-01 (see `../reel-01/brief.md` section 5): cream textured paper, huge black serif, small bold
  sans caps, one red only, halftone prints, brush wipes, captions in cream caps with key words on a red brush.
- The user's physique photos and videos: `assets/physique-front.jpg` (mirror selfie, side chest),
  `assets/physique-back.jpg` (back pose), `raw/gym-1.mp4` (4.5 s gym mirror flex, white tank, people behind),
  `raw/gym-2.mp4` (old captions burned in, not used), `raw/gym-3.mp4` (the clean copy of gym-2: purple tank,
  side chest pose, lat spread). Print clips: `work/prep_gym.py`. Photo prints and the back sketch: `work/prep_images.py`.
- Poster (beat 8): gym-1 flex, flips to the gym-3 lat spread on the beat at 25.6 s. End card: gym-3 side chest at half speed.
- Music B ends at 41.6 s: repeat one 4-bar phrase (30.435 to 36.835 s, joined at 36.835 s) so the beat carries
  through the end card and fades with the video (a 2-bar repeat would jump mid-phrase).
- Wipes sit on music B's 150 BPM grid (`work/music_beats.json`); the track's drop (3.2 s) lands on the red wipe
  into the diagnosis card.
- Not just text: every section gets visual elements like reel-01 (printed cut-out images, drawn ink illustrations,
  stamps, strikes, push-ins), not only typography.

## 6. Beat sheet v1 (approved 2026-10-14; stills v2 approved; v1 approved as final)
Edit time = time in the finished video (`work/word_times_edit.txt`). Cut is 43.4 s plus a 1.5 s end hold = 44.9 s.
Every drawing is ink in code (no outside images). Wipes snap to the nearest beat of music B where they can.

| # | edit time | spoken line | visual | captions | sound |
|---|---|---|---|---|---|
| 1 | 0.0 to 3.0 | "Intelligent people like you cannot build their dream physique" | HOOK COVER like reel-01: you cut out over cream paper, red sun behind your head. INTELLIGENT masthead slams on its word, PEOPLE LIKE YOU word by word, torn black band with CANNOT BUILD THEIR DREAM PHYSIQUE., front physique photo taped on as a print, red ring + arrow on "physique" | none | music in hard, low hit on "intelligent" |
| 2 | 3.0 to 6.5 | "because you, my friend, have a disease called analysis paralysis" | red wipe to DIAGNOSIS card: small DIAGNOSIS: label, drawn brain wrapped in a red tangled scribble, ANALYSIS then PARALYSIS. slam in huge serif on their words, red RX stamp on "disease" | none | swoosh, stamp thud, hit on "paralysis" |
| 3 | 6.5 to 9.2 | "A photography professor split his class in two." | black wipe to you (clip B). Torn paper strip above your head: drawn camera, PHOTOGRAPHY CLASS, a row of 10 drawn students, a red brush line splits them 5 and 5 on "split" | on | swoosh, paper slap on "split" |
| 4 | 9.3 to 12.2 | "One group would be graded only on how many photos they took." | paper scrap left of your head: GROUP A / QUANTITY, little printed photos pile up fast on "how many photos", tally counter running | on, MANY highlighted | camera shutter clicks on the pile |
| 5 | 12.2 to 15.8 | "The other group had only one chance to take one perfect photo." | scrap right of your head: GROUP B / QUALITY, one empty photo frame, big red 1 on "one chance" | on, PERFECT highlighted | one shutter click |
| 6 | 15.9 to 20.3 | "At the end, the best photos all came from the group taking the most photos." | slow push-in. On "best": red scribble ring and a WINNER stamp on the GROUP A pile, GROUP B fades | on, BEST highlighted | stamp thud |
| 7 | 20.3 to 23.9 | "The perfect photo group just sat around thinking about perfection." | strip: drawn figure sitting with a thought bubble holding an empty frame, red 0 PHOTOS on "perfection" | on | |
| 8 | 23.9 to 27.4 | "Repeated actions will teach you things your thoughts never can," | red wipe to POSTER: your gym-1 flex clip as a big framed print over the red sun (people behind cropped out), the quote builds below in serif, NEVER CAN in red | none | swoosh, hit on "repeated" |
| 9 | 27.4 to 29.3 | "no matter how intelligent you are." | black wipe back to you, push-in | on, INTELLIGENT highlighted | |
| 10 | 29.8 to 34.8 | "Stop chasing the perfect exercise, perfect diet, and the perfect workout program." | strip: drawn dumbbell, plate, clipboard program pop in on their words, small red PERFECT over each, one red line strikes through all three on "program" | on | paper slaps, brush strike |
| 11 | 34.9 to 39.9 | "Bring it into existence first, then make it perfect, not the other way around." | red wipe to card: your back photo as a rough ink sketch with 1. EXIST on "existence", the sketch fills in with the real photo on "make it perfect" (2. PERFECT), on "not the other way around" a reversed 2 -> 1 appears and gets a red X | none | swoosh, hit on "perfect" |
| 12 | 39.9 to 42.2 | "With whatever knowledge you have right now," | black wipe back to you, push-in | on, NOW highlighted | |
| 13 | 42.2 to 44.9 | "just start." | red wipe to END CARD: JUST START. slams in huge, front physique photo as a print over the red sun, holds 1.5 s | none | final hit, music out |

Captions (reel-01 style): 2 to 3 words, Inter Tight 800 caps in cream with a thin black edge, about 1440 px down,
key words on a red brush. Graphics stay off your face and the mic, inside the safe zone (250 px top, 420 px bottom).
Footage: warm muted grade with paper grain, same as reel-01.

To make or test before the build:
- Cut-out of you for the hook (clip A, rembg matte as in reel-01).
- gym-1: crop tight so the people behind you are gone.
- Ink drawings to add: camera, photo prints, brain, sitting figure with thought bubble, dumbbell, plate, clipboard.
- Sketch to photo effect for beat 11 (feasibility test first).
- ElevenLabs sound effects (credits): brush swoosh, low hit, stamp thud, paper slap, camera shutter.

## 7. Sign-off checklist
- [x] rough cut approved (v3)
- [x] beat sheet approved (v1)
- [x] stills approved (v2: Rx stamp and barcode removed)
- [x] v1 approved as final (2026-10-14)
- [x] final delivered: `out/reel-02-final.mp4` (crf 25, 57 MB) sent in 2 parts (0 to 24.0 s, 24.0 s to end)
- [x] merged into the default branch
