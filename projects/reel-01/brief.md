# Brief: reel-01

> Ideabro Studio · Vibe Editing System. Decisions are filled in as they are approved.

## 1. The job (step 4, approved)
- **Video type:** talking-head
- **Goal:** the viewer spots at least one of the three habits in himself and feels called out, in a motivating way
- **Main takeaway:** your body is held back by your habits and mindset, not your circumstances
- **Audience:** men who want a better physique but keep making excuses
- **Platform / format:** Instagram Reels, 9:16, 1080x1920 (same file for Shorts and TikTok)
- **Length:** keep all content, about 56 s after trimming long pauses
- **Language:** English voice, English captions

## 2. Message
- **Hook:** "Three disgusting addictions stopping you from building your dream physique." (0:00)
- **Points:** 1 Being a yes man (0:03) · 2 Blaming your luck (0:15) · 3 Hating yourself (0:38)
- **CTA:** none for this video. Ends on "own it, and fix it."
- **Caption text fixes:** "to that habits" at 0:08 shows as "to their habits". "own it" stays as said.
- **On-screen names:** none (no name or handle)

## 3. Cuts and pacing (step 5, approved)
- Natural pace. Trim only pauses longer than about 0.4 s, never cut inside a word, keep the beat before punchlines.
- No jump-cut zooms on every sentence. Slow push-ins only on key lines.

## 4. Audio (step 6)
- **Voice:** ElevenLabs voice isolation (`work/voice_isolated.mp3`). Noise floor 9 dB lower, in sync within 4 ms.
- **Music:** option B (ElevenLabs): dark ambient, cello drones, distant piano, subtle ticking clock.
  Sits about 10.5 dB under the voice while speaking (`work/music_mix.json`). The track ends at 52 s, so it needs
  extending or regenerating to cover the full edit.
- **SFX (planned):** a paper brush swoosh on each red wipe, a deep low hit on the three titles, nothing else.

## 5. Design (step 7, style description approved, sample frame not yet shown)
- **References:** `refs/poster-echoes.jpg` (poster), `refs/ref-video.mp4` (grunge typography template, silent).
- Cream textured paper, huge black high-contrast serif, small bold sans caps, one red only (brush strokes, circle,
  highlight bars), halftone black and white statue, four-point stars, corner brackets, hand-drawn arrows.
- Pacing from the reference: calm holds, then fast 0.2 to 0.5 s transitions (red brush wipes, glitch squares).
- **Him:** stays in natural colour (never halftone), light warm muted grade with paper grain.
- **Poster moments:** hook title, the three section titles, the two Seneca quotes. Push-ins with red underline on
  "You, my friend, are different", "Say no", "type 1 diabetes", "fix it".
- **Seneca image:** `assets/seneca-bust-photo.jpg` (Wikimedia, credit "Photo: Wikimedia Commons" in the post caption).
  The engraving has a stock watermark and is not used.
- Keep graphics clear of the face and the handheld mic, and inside the safe zone (250 px top, 420 px bottom).

## 6. Beat sheet v2 (more visuals, waiting for approval)
Cut: pauses over 0.4 s shortened to 0.4 s (`work/cut_plan.json`), 57.3 s source to 56.3 s, plus a 1.5 s end hold = about 57.8 s.
Edit time = time in the finished video (source times in `work/word_times_edit.txt`).
Visuals: printed images = `assets/print/*.png` (from the user's images), drawn = `illus.py` (ink drawings in code).

| # | edit time | spoken line | visual | captions | sound |
|---|---|---|---|---|---|
| 1 | 0.0 to 3.2 | "Three disgusting addictions... dream physique." | HOOK COVER (built) with the physique print | none | music in, hit on "addictions" |
| 2 | 3.2 to 4.6 | "Being a yes man." | red wipe, card 01 (built) | none | swoosh, hit |
| 3 | 4.6 to 6.9 | "90% of people around you are out of shape." | black wipe to you. Torn paper strip low on screen: drawn crowd of 10 figures, 9 out of shape fill in one by one, the fit one gets a red ring on "shape". Red "90%" beside your head | none | paper slap on "90%" |
| 4 | 7.2 to 11.7 | "Saying yes to their habits is saying yes to that version of you..." | printed pizza and beer pop in on scraps either side of your head on "habits", red ticks on "yes" | on | pops |
| 5 | 12.3 to 13.1 | "You, my friend, are different." | push-in, a red outline glows around you (cut-out) | on, DIFFERENT highlighted | |
| 6 | 13.9 to 14.5 | "Say no." | red X slashes across the pizza and the beer, "NO." stamp | SAY NO. | stamp thud |
| 7 | 14.7 to 15.8 | "Blaming your luck." | red wipe, card 02 | none | swoosh, hit |
| 8 | 16.0 to 18.2 | "...your genetics, family, and circumstances." | three items on their words: drawn DNA helix, drawn family tree, printed dice. A red line strikes through all three | on | slaps |
| 9 | 18.9 to 21.3 | "I have had type 1 diabetes since I was a child," | drawn insulin pen and blood drop beside you, tag TYPE 1 DIABETES | on | music dips |
| 10 | 21.5 to 23.3 | "but that didn't stop me from looking like..." | push-in | on | |
| 11 | 23.3 to 25.3 | "...this." "Two thousand years ago," | PAYOFF: your gym clip as a full-screen framed print, warmed, others cropped out | on | hit |
| 12 | 25.3 to 30.5 | "Seneca wrote, 'If you don't know which harbor...'" | SENECA POSTER 1: printed ship in the storm with its red sun, Seneca bust halftone, quote builds | none | waves, drone swell |
| 13 | 30.6 to 34.7 | "And then luck has power over our lives because we live by luck." | you, printed dice tumble in and land beside you | on, serif italic | dice rattle |
| 14 | 34.6 to 37.6 | "Just pick a harbor and stop waiting for the wind." | printed lighthouse slides in, its red lamp flashes on "harbor" | on | |
| 15 | 37.4 to 38.5 | "Hating yourself." | red wipe, card 03 | none | swoosh, hit |
| 16 | 38.6 to 44.7 | "Seneca said, 'Why would I be scared of my mistakes...'" | SENECA POSTER 2: tight bust crop, a crack runs through it on "mistakes", heals with a red line on "forgive" | none | crack, drone |
| 17 | 45.4 to 47.3 | "You can't fix your body if you can't look at it." | printed mirror (woodcut), your physique photo inside the glass, dark until "look at it" | on | |
| 18 | 47.9 to 51.8 | "...stepping on the scale and stop tracking what you eat." | drawn bathroom scale and food diary, each struck through in red | on | slaps |
| 19 | 52.4 to 55.3 | "When you forgive yourself, you can look at your flaws," | drawn magnifying glass moves over your physique photo | on | music builds |
| 20 | 55.3 to 57.8 | "own it, and fix it." | END CARD: OWN IT. / FIX IT., physique print back, holds 1.5 s | none | final hit |

Look for footage beats: warm grade, paper grain, nothing over the face or the mic.
Captions: 2 to 3 words, Inter Tight 800 caps in cream with a thin black edge, about 1400 px down, key words on a red brush.

To do or test before the build:
- Music B ends at 52 s: extend it to about 58 s.
- Gym clip: other members behind you, crop tight or cut out.
- Seneca bust is small: test the halftone at poster size.
- Cut-out of you for beat 5 (outline glow).
- ElevenLabs sound effects still to make: paper slap, ink stamp, dice rattle, stone crack, waves.
- Image rights: the dice, beer, pizza, ship, mirror and lighthouse images were supplied by the user from online sources.

## 7. Sign-off checklist
- [x] beat table approved (v2 with visuals)
- [x] styled frame and motion sample approved (hook sample v2)
- [ ] v1 preview approved
- [ ] final export delivered
