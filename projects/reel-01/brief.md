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

## 6. Beat sheet (step 10, waiting for approval)
Cut: pauses over 0.4 s shortened to 0.4 s (`work/cut_plan.json`), 57.3 s source to 56.3 s, plus a 1.5 s end hold = about 57.8 s.
Edit time = time in the finished video. Source = time in `raw/take-01.mp4`.

| # | edit time | source | spoken line | on screen | captions | sound |
|---|---|---|---|---|---|---|
| 1 | 0.0 to 3.2 | 0.2 to 3.2 | "Three disgusting addictions stopping you from building your dream physique." | HOOK COVER (built): you cut out on cream paper, red sun, ADDICTIONS masthead, physique print, words build, red ring + arrow on "physique" | none, the design carries the words | music in, deep hit on "addictions" |
| 2 | 3.2 to 4.6 | 3.4 to 4.5 | "Being a yes man." | red brush wipe to card 01 / BEING A / YES / MAN. (built) | none | swoosh, hit on "yes" |
| 3 | 4.6 to 6.9 | 4.9 to 6.9 | "90% of people around you are out of shape." | black ink wipe to your room. "90%" slams in big red serif beside your head, "ARE OUT OF SHAPE" in small caps under it | none here | paper slap on "90%" |
| 4 | 7.2 to 11.7 | 7.5 to 11.9 | "Saying yes to their habits is saying yes to that version of you who is okay with having that body." | you, slow push-in | on, "their" shown (not "that") | |
| 5 | 12.3 to 13.1 | 12.7 to 13.5 | "You, my friend, are different." | push-in to 1.12 on "different" | on, red brush highlight on DIFFERENT | |
| 6 | 13.9 to 14.5 | 14.3 to 14.5 | "Say no." | red ink stamp "NO." thuds beside your head, slightly rotated | SAY NO. | stamp thud |
| 7 | 14.7 to 15.8 | 15.2 to 15.8 | "Blaming your luck." | red wipe to card 02 / BLAMING / YOUR LUCK. | none | swoosh, hit |
| 8 | 16.0 to 18.2 | 16.5 to 18.2 | "You blame your genetics, family, and circumstances." | three typed paper slips stack beside you on each word: GENETICS, FAMILY, CIRCUMSTANCES. A red line strikes through all three at the end | on | paper slap per slip |
| 9 | 18.9 to 21.3 | 19.4 to 21.3 | "I have had type 1 diabetes since I was a child," | poster tag: TYPE 1 DIABETES / SINCE CHILDHOOD on a red brush, slow push-in | on, "type 1" as a numeral | music dips |
| 10 | 21.5 to 23.3 | 22.0 to 23.8 | "but that didn't stop me from looking like this." | you, push-in | on | |
| 11 | 23.3 to 25.3 | 23.8 to 25.9 | "...this." then "Two thousand years ago," | PAYOFF: your gym clip slams in full screen as a framed print, warmed to match, other gym members cropped out | on | hit on "this" |
| 12 | 25.3 to 30.5 | 25.9 to 31.2 | "Seneca wrote, 'If you don't know which harbor you are sailing for, no wind is favorable.'" | SENECA POSTER 1: halftone bust on cream paper, red sun, red brush across the eyes, quote builds in serif, small label SENECA | none, the quote is the text | low drone swell |
| 13 | 30.6 to 34.7 | 31.3 to 35.4 | "And then luck has power over our lives because we live by luck." | back to you, captions in serif italic (still quoting) | on, serif italic | |
| 14 | 34.6 to 37.6 | 35.4 to 37.6 | "Just pick a harbor and stop waiting for the wind." | you, push-in, red underline on PICK A HARBOR | on | |
| 15 | 37.4 to 38.5 | 38.2 to 38.5 | "Hating yourself." | red wipe to card 03 / HATING / YOURSELF. | none | swoosh, hit |
| 16 | 38.6 to 44.7 | 39.4 to 45.6 | "Seneca said, 'Why would I be scared of my mistakes when I can just say: I forgive you this time. Don't do it again.'" | SENECA POSTER 2: tighter crop of the bust, different layout from poster 1, quote builds | none | drone swell |
| 17 | 45.4 to 47.3 | 46.3 to 48.2 | "You can't fix your body if you can't look at it." | you, push-in | on | |
| 18 | 47.9 to 51.8 | 48.9 to 52.7 | "When you hate yourself, you stop stepping on the scale and stop tracking what you eat." | two paper slips: STEPPING ON THE SCALE, TRACKING WHAT YOU EAT, each struck through in red | on | paper slaps |
| 19 | 52.4 to 55.3 | 53.4 to 56.3 | "When you forgive yourself, you can look at your flaws," | you, slow push-in, music lifts | on | music builds |
| 20 | 55.3 to 57.8 | 56.3 to 57.3 | "own it, and fix it." | END CARD: cream paper, OWN IT. / FIX IT. in the masthead serif, the physique print returns, holds 1.5 s | none | final hit, music ends |

Look for all footage beats: warm grade, paper grain, nothing over the face or the mic.
Captions: 2 to 3 words at a time, Inter Tight 800 caps in cream with a thin black edge, about 1400 px down
(on the chest, inside the safe zone), key words on a red brush highlight.

Missing or needing a test before the build:
- Music B ends at 52 s: extend it to about 58 s (repeat a calm passage, test the seam).
- Gym clip: other members walk behind you. Test a tight crop first, a cut-out if the crop isn't clean.
- Seneca bust is small (250 x 375): test the halftone at full poster size.
- Two more ElevenLabs sound effects: a paper slap and an ink-stamp thud.

## 7. Sign-off checklist
- [ ] beat table approved
- [ ] styled frame and motion sample approved
- [ ] v1 preview approved
- [ ] final export delivered
