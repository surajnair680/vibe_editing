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
- The user's physique photos and videos are used in this reel too (waiting for uploads; build starts after them).
- Not just text: every section gets visual elements like reel-01 (printed cut-out images, drawn ink illustrations,
  stamps, strikes, push-ins), not only typography.
