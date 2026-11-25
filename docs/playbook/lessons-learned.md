# Lessons learned (the knowledge base that carries across sessions)

Read this whole file before starting any new video, and again before the stills step. Every entry came from a real
edit and cost a revision, a re-render or a question once. Newest videos at the bottom of each section. Tags say where
each lesson came from: [r01] reel-01, [r02] reel-02, [r03] reel-03, [vlog] the mini vlog style study (2026-10-30),
[codex] the Codex CLI setup session (2026-11-01), [r04] reel-04 (cinematic work-session edit, 2026-11-01), [r05] reel-05 (Automance logo intro, 2026-11-04), [openverse] the Openverse sound library setup (2026-11-06), [r06] reel-06 (YouTube Shorts music swap of a finished reel, 2026-11-06), [r07] reel-07 (meme template caption swap, 2026-11-11), [lemo] the Lemo-Opuscar setup (2026-11-13), [r08] reel-08 (Comeback Day 1, a test intro as a Lemo Urban Sketch animation, 2026-11-13), [r09] reel-09 (bicep curl "Current vs Correct" form explainer, 2026-11-14), [voxel] the voxel reels setup (2026-11-14), [reanimate] the reanimate skill setup (2026-11-15), [r10] reel-10 (home pull-up and ring dip reel, 2026-11-16), [r11] reel-11 (sarcastic reply to an "inspiring" English-speaking clip, 2026-11-18), [r12] reel-12 ("Ghar ka khaana" sarcastic reply reel, 2026-11-19), [r14] reel-14 ("Successful people are not normal" reaction reel, 2026-11-23), [parallax] the Vox photo parallax lesson (2026-11-24), [toolkit] the toolkit menu (2026-11-24).

How this file grows: see "Learning loop" in CLAUDE.md. Add to it during every video, not only at the end.
Other docs and when to read them: `docs/README.md`.

---


## 1. The user (Suraj): taste, preferences, how he works
- Fitness coach on Instagram ("build your greatest physique"): training, muscle, fat loss, mindset. Audience judges
  real results, so **his physique is the product**. [r03]
- **Never let an effect eat the physique shot.** In reel-03 the back photo was shown for 0.16 s before the light-snap
  silhouette took over; he asked for more time on the back. Give the money shot at least 0.6 to 0.7 s of clear view
  before any effect, even when the reference does it faster. [r03]
- **Show the full physique** in payoff shots (both arms, the whole torso). Re-cropped the gym clip in reel-01 for this.
  Background people are acceptable if needed for the full physique. [r01]
- **Outlines of his body must be anatomically right.** He spotted a flat head (hair missing above his hand) and a hard
  vertical cut on the deadlift outline. Check every cut-out at full size, especially head, hands and edges. [r03]
- Long static holds bore him: a 4 s hold of one shot "becomes monotonous". Something must happen in its second half
  (in reel-03: a rim light builds, then the body fills with glowing grain on the key word). [r03]
- **HDR on his training clips when he asks (reel-14).** "Add HDR so my muscles look sharper" overrides the
  no-filter default for his training clips (not his photos unless asked). A plain CLAHE + sharpen boosted the phone's
  noise into gritty skin; the version that worked boosts a denoised layer: bilateral on lightness, CLAHE 2.0 (8x8),
  clarity 0.40 at sigma 18, detail 0.35 at sigma 2, add back half the noise, saturation x1.12. About 90 ms a frame.
  `hdr()` in `projects/reel-14/work/build3/scene3.py`. Always check a full-size crop of skin before sending. [r14]
- **Grainy Vox reels are huge at real quality (reel-14).** 1:42 at 1080x1920 with heavy grain: master crf 14 = 1.2 GB,
  crf 22 = about 8 MB a second (about 600 MB, 21 parts), 8 Mbps = about 120 MB (5 parts), 2-pass 2150k = 28 MB in one
  file (grain softened, face fine). Audio-only revisions remux the last review video with the new mix in a minute. [r14]
- **Music level for phone speakers (reel-14).** With his own track (Jake Chudnow "Turquoise") ducked 18 dB under the
  voice he "cannot hear it without earphones". About 10 dB under the voice while he talks (+4 dB in pauses) works for
  phone speakers. The reel-12 "18 dB under" figure was for a busy track; check on a phone-speaker basis. [r14]
- **Draft before every full render, without being asked (reel-14).** He asked "why not show me the preview first, to
  save time?" A half-size 15 fps draft of the changed range takes about 3 minutes against 20 for the full render
  (`scene3.py draft a b out.mp4`, 4 ranges in parallel, voice mix muxed from the same start). Send it first, render
  full quality only after he approves the motion. [r14]
- **Physique shots need time: at least about 2 s each (reel-14).** At 0.7 to 1.4 s his photos and training clips
  "just look like glimpses". Give every physique photo or clip 2 s or more (the ending 3 s), taking the time from the
  graphics around it, and keep graphics windows from running under a full-screen print. [r14]
- **Never caption an emotional image (reel-14).** Labels DISCOMFORT, GROW and NO OPTION on the statue photos were
  "fucking lame". Labels help abstract symbols (a scale = BALANCE); a strong image plus his voice needs nothing on it. [r14]
- **Emotion beats diagrams (reel-14).** He called the brain and bicep drawings "so boring" and sent two dark B&W
  statue photos instead: Sisyphus pushing the boulder (discomfort you push through) and the self-made man carving
  himself (building yourself). For feeling lines (struggle, growth, becoming stronger) use dramatic, symbolic real
  images like these as torn prints; keep diagrams for facts. Assets: `projects/reel-14/assets/photos/statue_*.jpg`. [r14]
- **Charts carry meaning by position (reel-14).** He caught Elon Musk placed on the LEFT end of the bell curve, which
  reads as below average. Outliers and "you" always sit on the right (high) end; check where each element sits on a
  chart, not just that it is visible. Also keep recognisable people big (Jobs about 520 px, not 300). [r14]
- **The child test (reel-14, 2026-11-24).** He asked: would a child understand every frame? Fixes that made abstract
  visuals readable: a word label on every symbol (NORMAL PEOPLE, BALANCE, MIND / BODY, COMFORT, JUDGING), name strips
  under celebrity photos, people instead of charts (a crowd labelled MOST PEOPLE inside a bell curve with you as a lone
  red YOU dot; grey figures stopping at a MOST PEOPLE STOP HERE line while one red figure carries on), a drawn arm that
  cracks then grows instead of abstract muscle fibres, and no text under about 40 px. Check this before sending stills. [r14]
- **Text is not a visual (reel-14, 2026-11-24).** He called the v2 look "awful... just a bunch of text, no visual
  element at all. For pizza you just wrote it on the screen". Every spoken line needs something to look at that shows
  it (a pizza for pizza), made in code or with Codex image generation; titles only support it. He wants Vox style
  (torn paper collage) for this kind of eye-opening talk reel. Plan the visual per line in the beat sheet. [r14]
- **His look: darker and grainier = "important" (brand intake, 2026-11-24).** He couldn't answer brand questions in
  the abstract; fill them from what you know and ask him to correct. Master look in `docs/playbook/brand/MOTION.md`:
  black and deep red (#4A0005 to #1C0202), heavy grain (about 2x the house default), bone titles, ash captions. [brand]
- He wants his face visible and recognisable. Pixelating half the face (reference style) works against him; the
  version he chose: start pixelated, resolve to the clear face. [r03]
- He likes to understand why an effect exists ("what is the point of pixelating half the face?"). Explain meaning
  briefly when proposing effects. Explain any decorative element (he had the "Rx" stamp and a barcode removed). [r02][r03]
- He asks "first tell me if you understand" before revisions: restate his note, propose the fix, wait. [r03]
  Same on reel-11 with a fault note: "this part is not cut properly. First tell me what you notice". List the causes
  you measured in plain words (here three: missing audio at a part seam, picture cut early, fades mid-word), propose
  the fix, wait for "yes fix it". [r11]
- **When he asks "do you get what I want?", answer that first, in two or three plain lines, before anything else.** On
  the Openverse request I replied with a plan, a network blocker and a domain list; he came back with "At least tell me
  if you understood what I want." Restate the goal in his terms, then (separately, or after he confirms) the blockers
  and plan. [openverse]
- He shares other creators' reels (pasted transcripts) about AI tools and means "add this to my system". Build it as a
  shared tool + CLAUDE.md rule + skill line, so every session has it. [openverse] Confirmed again on Lemo-Opuscar: he
  pasted only a transcript and caption, I looked the tool up and offered four options, and he picked "add it to our
  setup". Next time: look it up, then put "add it to the setup" first as the recommended option. [lemo]
- **He does not monetise his content** (2026-11-13). Non-commercial licences (CC BY-NC docs, prompts, styles) are fine
  to copy and use: mention a licence only when it would block him (ND, or a paid tool), not as a caveat. [lemo]
- Footage requests: give a list of **the kind of footage that fits each moment** (feel + examples), not exact shots
  to film; he may not be able to film exactly what is asked. Then a short "still needed" list, updated per upload. [r03]
- He sends clips one at a time and says "done" at the end. Report each clip in a few lines (length, shape, where it fits,
  issues) and wait. He may send clips "to use in place of" a list item: map it to the closest open item. [r03]
- He uses Google Flow (Veo) to generate clips and animates his own photos with it. When he says the physique is his and
  real, take it at face value. Don't repeat AI-label advice once he has answered. [r03]
- Learning projects: he remakes reference edits to learn, credits the original in the Instagram caption, keeps the
  original audio. No CTA unless asked. [r03]
- Quality matters to him: he asked why the one-file version "is not high quality" and then wanted the near-lossless parts.
  Lead with the best file when it fits; explain numbers plainly. [r03]
- Planning an Instagram **mini vlog series, mostly vertical 9:16**, in the camcorder overlay style of a reference reel he
  shared. Everything for it is in the skill `.claude/skills/vibe-mini-vlog/` (reel breakdown, overlay pack in horizontal
  and vertical, compositing helpers, episode template). Load it for any vlog / day in my life video. [vlog]
- **"Learn this permanently" means build it into the repo, not just remember it.** When he shares a reference reel
  plus assets for a future series, he wants a skill: the assets committed, a tool to use them, a written breakdown of
  the reference and reference stills. Do that, then tell him what was saved. He confirmed "same page" means future
  sessions must be able to edit in that style without being taught again. [vlog]
- He sometimes just says "watch this reel": give a short breakdown (what is said, the look, what works, what is weak)
  and ask what he wants to do with it. Don't start a project until he says. [vlog]
- Plain human language, no em dashes, short messages. [all]
- **Setup jobs: he wants it automatic and fixed at the root.** He gives exact steps ("check the domains, stop if one is
  blocked, install, device sign-in, add it to the hook") and wants short replies: what was done, what he does next.
  When another session gets something wrong, he shows it here: fix the shared rule so no session repeats it, and tell
  that session yourself. He asked for Codex sign-in to be requested at the start of every session, not when needed. [codex]
- Before suggesting a workaround to a repeated chore (like saving the Codex login), he wants it looked up and the
  honest trade-off given; he accepted "sign in each session" once he saw why the shortcut breaks. [codex]
- **Cinematic edits of everyday footage open in the middle of the action.** In reel-04 (him working at his desk) he
  cut the walk-in and sit-down: "begin with me already sitting and working". Start on the activity already going;
  walk-outs at the end are fine. Learning pieces stay private, so no blurring of client names on screens. [r04]
- **Overlays on a cinematic edit: engaging but never distracting.** His brief for reel-04: overlays should keep it
  engaging "but not so overwhelming that the viewer feels distracted by the editing instead of connected to the
  subject's world". What he approved first time: only 4 moments (open, drop, breath, ending), small lowercase lines
  naming the feeling ("the quiet hours", "locked in.", "the world goes quiet", "same time tomorrow."), pack text that
  doesn't fit masked out (V4: kept WORKING + REC only), nothing over the fast montage, and the V12 REC iris closing
  to black as the ending (rebuild its mask: eroded lavender area, no blue fringe; clip the last line inside it).
  Code: `projects/reel-04/work/overlays.py`. [r04]
- **He wants motion from the very first frame.** "When the video starts I want some sort of motion, zooming, so it
  looks dynamic." Approved first try: a snap pull-out 1.30 -> 1.08 in 1 s (ease-out, zoom blur) then a slow drift,
  a lateral slide past a foreground frame, and a push-in that accelerates into the drop; then a slow push or drift on
  every shot. Plan an opening move in every cinematic edit. Code: `projects/reel-04/work/build.py` (MOVES). [r04]
- He gives free rein on taste calls ("make your own judgment") for sound design: propose a palette with a reason per
  sound, keep it subtle with one or two bold hits, and let him react to the result. [r04]

- **He may answer a first draft with a storyboard** (numbered AI frames, reel-05): treat it as the plan for order,
  look and staging, rebuild it in code (never just crossfade his frames), drop the number badges, and keep the end
  frame exactly his logo. Ask for sound in the same pass he asked for it. [r05]
- **reel-05 outcome:** shown both, he chose the first code-built logo reveal (v1, 2.5 s: night sky, white line-art
  car and bike lock together, flash to white, letters slam in, red A last) over the version rebuilt from his own
  storyboard (v2). Keep earlier versions alive and offer the choice; don't assume the newest wins. He noticed v1 had no
  sound: when sound is approved for one version, add it to every version you send. Reuse paid SFX by retiming
  (`projects/reel-05/work/mix_v1.py` imports `mix.py`). Intros: about -13 LUFS, peak -3 dB, engines panned with the
  vehicles. [r05]
- **He also makes brand intros** (reel-05: "Automance", a cars / bikes / road trips channel): 16:9, very short
  (2.5 s asked, 3 s for the storyboard version), used as a channel intro, the logo image he supplied is the last
  frame. He states the idea in a few lines (dark sky start, car right to left, bike left to right, dynamic text) and
  asks "first confirm if you understand": restate, propose how to get from dark to the white logo, ask format,
  length, sound and use in one message. [r05]
- **Reposting an Instagram reel on YouTube Shorts:** Bollywood songs get the Short blocked by Content ID. He wants the
  song swapped for an ElevenLabs track with the same energy, and the quiet beat under his talking replaced too, while
  the picture and his voice stay exactly as they were. Suggest a Private YouTube upload first: YouTube Studio's "Checks"
  step lists every matched range. [r06]

- **Meme template swaps (reel-07):** he sends a meme reel (caption on black above a funny clip, a brand logo below) and
  a new caption line. He wants the same clip and sound, only his caption; the other brand's logo removed and nothing in
  its place (he said no to a handle); proper brand spelling ("ChatGPT", not "chatgpt"); the footage's TV channel mark
  hidden with a small zoom (4.6%: crop 24 px off the left of the 720 wide band). Measure the template's bands (caption
  lines, video band, logo) with row maxima, re-render the caption crisp at 1080x1920 in Inter SemiBold sized to the
  original line width, copy the audio bit-exact. 12 s render takes seconds. Code: `projects/reel-07/work/`. [r07]
- **He may upload a reel with no message at all** (reel-07). Give a short breakdown (what it is, format, audio) plus 2 or 3
  options and wait; he answered with just the new caption line. Mention footage rights once at most: he uses meme
  templates as they are (the clip, the sound), so don't push "use your own footage" again. [r07]
- **He asks for an Instagram post caption after the video** ("make a caption that explains the joke"). He turned down
  two versions before approving: the first read as AI (stacked short lines, "It can't X, it can't Y", a moral line,
  "tag the friend" CTA), the second as a rant (story details, lowercase slang, emoji). Approved: two short plain
  paragraphs, proper capitals, no emoji, no hashtags, no CTA. Line 1 names what the clip shows ("He has the saw, the
  wood and someone to copy, but he's not cutting anything."), line 2 maps it to the fitness problem in one or two
  sentences (no form checks, no progress tracking, no adjusting when you stall, so nothing changes). [r07]

- **People in Lemo animations: never use the urban-sketch engine's tube figure for a main character.** On reel-08 the
  user said "the human itself looks weird" (pipe arms, baggy hips, blank oval face). Fixed in one round with Codex:
  a 4-view character sheet first, then each pose with `--ref <sheet>` (mirror selfie, bent over out of breath, a
  4-frame walk cycle on one sheet, waving); all came out consistent on the first try, about 30 s each. Cut out with
  `projects/reel-08/work/cutout.py` (colour-to-alpha silhouette for a paper knock, black-hat ink lines so the pen can
  still draw her before the colour blooms, walk sheet split at column gaps, torso-centre anchor). Drawn by `her()`
  in `projects/reel-08/film/film.js`; a waving hand = the forearm region rotated a few degrees around the elbow. [r08]
- **Test runs with no footage (reel-08):** he said "This is just for testing. So no footage is present." I offered
  four ways in one question (AI stills + AI voice, placeholder cards, a Lemo animated explainer, plan only); he chose
  the animated explainer. When there is no footage, offer these right away instead of a footage list. [r08]
- **Defaults in brackets get one-word answers.** I listed the brief questions with my default in brackets ("5",
  "ElevenLabs female voice", "free music", "captions", "9:16 about 38 s"); he answered "Urban Sketch, defaults".
  Put a sensible default on every question so he can skip them all. [r08]
- **People on screen must look like real people to him,** even in a sketch style: his only note on round 1 was the
  figure ("looks wierd"), not the story, captions or camera. [r08]

- **Form explainers for Telegram (reel-09):** he makes short "Current vs Correct" exercise clips (red vs green,
  15 s, 9:16) for clients who watch muted. He said **no sound effects** on this one: the house sound design rule
  gives way when he says so. He sends a full written brief (scenes with times, text, rules) and asks "first tell me
  what you understand": restate it, flag clashes, give defaults in brackets. [r09]

- **Home workout reel (reel-10):** he sends many phone clips split in parts (5 recordings, 21 parts, about 4 min) with
  no message: report each part in a few lines (what happens, best moments, problems like the waistband brand) and
  keep a running table. Then he answers in pieces: a reference reel for the hook, his own song, a look note.
- **Boxed visual hook (reel-10):** he liked a reference with a red scribble line-art head on black and the clip in a
  wide box in the middle, but "only for the visual hook, rest of the edit normal ratio". He chose a **generic head
  like the reference** (over his own silhouette) and no hook text. Built: Codex silhouette + code scribble lines
  (random walks steered back inside the shape, 170 strokes, mostly 1 px, 3 boil variants every 0.5 s), box at the
  reference's place (x 120 to 890, y 729 to 1125 at 1080x1920), song cued so the drop breaks the box out to full
  screen in 0.3 s. Code: `projects/reel-10/work/hook/` (`scribble.py`, `hook.py`). [r10]
- **He wants grain on his footage** ("raw and authentic"): picked **medium** from a full-size none / light / medium /
  heavy comparison (strength 0.06, grain size 1.6 px, midtone weighted, 16-field bank). `projects/reel-10/work/look.py`. [r10]
- **"Flash band while posing":** shown two versions on the beats of the pose, he picked **strobe** (3 to 5 bright
  horizontal bands flickering on frames 0, 2, 3 of each hit, slight exposure lift) over a diagonal light sweep. Keep
  the first half second of a pose clean. `flash_band()` in `projects/reel-10/work/hook/hook.py`. [r10]
- **He supplies commercial songs** (The Box guitar remix): fine to use, keep out of git, map it (intro, build, drop)
  and cue the song so its drop lands on the edit's big moment. [r10]

- **Stylised edits keep real assets real (reel-11).** For a Pixel RPG treatment he said: the celebrity photo, his gym
  B-roll and his physique photos must be "properly visible" and "used as it is". Only what we make (world, menus,
  counters, sprites) takes the style; real photos and footage get at most a styled border or window, never a filter.
  Same for his face: real video, never pixelated.
- **Face visible throughout, as a head popping out of a circle (reel-11).** He showed a reference (a presenter in a
  rounded box whose head breaks out above it) and asked for a circle instead. His face may move around and change size
  between beats as long as it is always visible. Sample: pixel-stepped circle with a gold ring and warm dithered fill,
  head unclipped above the circle's centre line, rembg `u2net_human_seg` matte (clean on his room footage, mic and
  hand included). Code: `projects/reel-11/work/sample/sample_frame.py`.

- **Music from the first frame (reel-11).** I planned no music under the clip he reacts to; he wanted it "from the
  start even when I'm reacting to the video, so that the vibe is established from the start". Default: the edit's
  music starts at 0:00, ducked under every voice. He asked for "Mario like music": made an original 8-bit platformer
  track in code (pulse lead, triangle bass, noise drums, 152.5 BPM chosen so a bar lands on the key reveal), never
  the real melodies or sounds. Code: `projects/reel-11/work/music.py`, `sfx.py`, `mix.py`.
  Mix numbers that worked (measured, since I can't listen): bed 7 dB under the voice level in gaps, -10 dB duck keyed
  from the voice (15 ms attack, 300 ms release, 120 ms hold), the lead a further -5 dB under speech and a sparser line
  while he talks; voice 17 to 20 dB above the music under speech; her quieter clip +5 dB to match his takes; music
  gated during the PAUSED screen like a real game; -14.3 LUFS, -1.5 dBFS peak. Measure voice vs music RMS per section
  under the speech key before sending. [r11]

- **His gym's logos are fine on screen (reel-12):** "You dont have to hide the logo i dont mind" (the "cloud" sign and
  Hammer Strength machines in his gym B-roll). Don't crop or blur them; still check for other brands' logos. [r12]
- **B-roll clips are raw material, not fixed lengths (reel-12):** he said trimming is expected; use only the best part
  of each clip (one clean rep, the first clean second before someone walks in) without asking. [r12]
- **Rough cut notes he gave on reel-12:** voice cleaned with ElevenLabs isolation, every pause cut ("everything I say
  should be clearly heard, the gaps should be cut obviously"), long spoken lists after the first 2 items at 1.5x (pitch
  kept with ffmpeg `rubberband=tempo=1.5:window=short`, Scribe confirmed every word). He decides sound and graphics
  only after the cut is right. Code: `projects/reel-12/work/plan_cut.py`, `make_cut.py`. [r12]

- **Codex manga characters have an "AI slop" look to him (reel-12):** "codex generates generic looking manga
  characters that clearly have that ai slop look". Codex is still allowed; guard against the look: ask for a specific
  hand (G-pen ink, uneven tapered line weight, flat black spots, no glossy shading, no soft gradients, no big shiny
  anime eyes or symmetrical pretty faces), re-print every drawing through the code screentone step (threshold the
  lines, dot-screen the flats) so it reads as printed ink, prefer objects and props over faces, keep any drawn people
  small or partial (hands, silhouettes, backs), and reject and redo anything that looks generic before he sees it.
  The main people are his real footage and photos. [r12]

- **Physique pics always show his face (reel-12):** "whenever my physique asset is used my face should be visible too
  otherwise what the point". The sample cropped his mirror pic at the chin for "losing fat, not muscle"; he rejected it
  at once. Frame every physique photo or clip from the hair down (face + body together); make the panel taller rather
  than cropping the head; a photo without his face (back pose) needs his OK before use. [r12]

- **Talking-head reply reels (reel-11):** he reacts to someone else's clip, then answers it on camera with deadpan
  sarcasm (here: a village woman's "stop chasing perfection" English clip, then "I don't understand what is so
  inspiring about her" and a mock case FOR waiting for perfection, applied to fitness). He sends it as numbered parts
  ("1_part1..4" = her clip, "2", "3_part1..4" = his takes, retakes of the ending inside), then "That's it". Pick the
  strongest ending take (here "next Monday since 2020" + a sarcastic follow CTA) and say why. [r11]
- **First rough cut = cut and trim only (reel-11):** "For now just the cut and trim don't do anything else". No
  captions, music, zooms or effects in the first pass; graphics come after the cut is right (same on reel-12). [r11]
- **He picks the graphics style himself and comes back with constraints (reel-11):** asked for the look options, then
  "check if there is a pixel style animation in lemo opuscar", then "Tiger shroff should be properly visible and my
  broll and physique photo as well" (real assets stay real, above). Lemo-Opuscar styles work as the graphics layer of a
  talking-head reel: show the style list with what each would do for HIS script, line by line. [r11]
- **He asks where the files live (reel-11):** "Is the video stored in the server or gh?" Answer with a table: renders
  and raw footage only on the wiped cloud server, the delivered file in the chat, everything to rebuild on GitHub
  (raw footage must be re-uploaded). Tell him to save the delivered file to his phone. He then asked for the
  full-quality master in parts. [r11]
- **Blocked sound sources: he wants the honest options, then decides (reel-11).** On "Can the server block issue be
  solved?" I tested (tunnel established, then Freesound's own empty 403 on the site, the API and cdn), explained it is
  the site blocking cloud IPs, and offered: run downloads on his computer through Remote Control (none attached yet),
  download the links himself, ElevenLabs sound generation (credits), or keep code-made sounds. He chose the code-made
  ones for this reel. [r11]

- **Food stays in normal colour even in a manga/comic style (reel-12):** "make the food items normally... the viewer
  wont be able to tell what food it is" in black-and-white ink. Codex photo-style food (thali, protein spread, roti
  stack: `projects/reel-12/assets/codex/`) inside ink panels; only panels, stamps and lettering are manga. Same rule
  as his photos: anything the viewer must recognise stays real. [r12]
- **Sound brief for reel-12:** "dont make it ai sloppy, and dont let the viewer get distracted from the content".
  Built: ElevenLabs music from 0:00, about 18 dB under the voice while he talks (measure stems, not the mix:
  a -17 dB music gain first left it 30 dB under, inaudible), ink swish only on section panels, list photos change
  silently, low pen ticks per item, stamps on the big words, two booms (impact frames). `projects/reel-12/work/mix.py`. [r12]

- **Every spoken list item needs a visual that shows that item (reel-12):** in v1 the benefit lists just cycled his
  photos and clips; he said "the assets do not correlate with what is being listed... you have not used anything to
  portray the listed benefits". Map item by item: his physique / gym asset where it shows the benefit (back pic on
  "less back pain", mirror pic on "better looks", dumbbell pic on "strength"), a simple code-drawn illustration for
  abstract ones (sugar line, bone, moon). Show the mapping table before building. [r12]

- **reel-12 outcome and numbers:** approved at v2 after one note (list visuals). Manga hybrid kit worth reusing:
  `projects/reel-12/work/mg/manga.py` (screentone, focus lines, slam lettering, manga face circle with paper rim and
  hair-edge clean-up), `scene.py` (beats, captions with Hinglish transliteration table, list item box with counter
  and red tick), `benefits.py` (benefit illustrations: gauge, age chart, flame, sugar line, bone, shield, hourglass,
  mood, moon). Per-frame rembg mattes: about 2 frames/s per process, 3 processes for 1,800 frames in about 5 min. Full
  92 s render about 0.6 s a frame, 5 parallel parts about 8 min. Final: crf 18 slow = 89 MiB (4 parts), 2-pass
  2350k post file = 28 MiB (SSIM 0.979). Revisions spliced at keyframes and proved with framemd5. [r12]

- **Asked about the graphics style, he wants the repo's own menu (reel-12):** "Look at the repo you'll find premade
  motion graphics like lemo opuscar and more". List what the repo has (his reel-motion-graphics skill: Lab notebook /
  Stoic poster; Lemo-Opuscar's fitting styles; voxel, vlog overlays, reanimate) with what each would do for this
  script. He then named one himself ("manga panels"); give an honest fit verdict with the catch, then test frames. [r12]
- **He changes his mind on insert placement, so confirm it in one line before building (reel-12):** the ending meme
  went "after the last line", then "during the last sentence, ending at the same time", then "after the ending" again.
  Ask where an inserted clip sits (after / over which words / ending where) before rendering it. [r12]
- **Speed notes come as rules, not times (reel-12):** "play the first 2 list items at 1x and rest at 1.5x". Apply the
  rule to every list in the video and switch speed in the pause after item 2. [r12]

- **Asset answers on reel-14 (reaction reel in Text Flash Cuts):** faceless *training* clips (pull-ups from behind,
  a press filmed from behind his head) are fine, unlike faceless physique photos; another brand's poster in his gym
  (INJA collagen) can stay, no crop; no extra held lines under celebrity photos. He adds famous people as proof
  ("Elon Musk and Steve Jobs to showcase people who dont live like normal people", then "Arnold too") and sends the
  photos himself, since Wikimedia Commons is unreachable from the container (connection refused, 000). Small photos
  (365 px wide) go in a framed card, never stretched full screen. He remembers clips from older sessions ("you have
  clips of me bench pressing"): raw video is never in git, so say so and ask for a re-upload; photos are in git on
  other branches (`git ls-tree -r origin/<branch>` + `git show`). [r14]

- **Flash cards are "a stun grenade" to him (reel-14 v1).** Text Flash Cuts cards held 2 to 9 frames (the style's
  own rule) plus 3 to 7 frame clip flashes: "several parts are so brief that the viewer doesn't know what the hell is
  going on". Every word, photo or clip must stay readable, about 0.8 s at least, whatever a style guide says. He then
  dropped the style for a reference he supplied (a premium dark red motion-graphics reel: cut-out subjects on deep
  red with drifting hairlines, condensed titles whose letters fade in scattered, captions that build word by word
  with a blur-in, a light grey section with red circles) and asked for the reanimate skill to copy it. Build of that
  look: `projects/reel-14/work/build2/` (fx2.py, scene2.py), spec `projects/reel-14/reanimate/spec.md`. [r14]

## 2. Remaking a reference edit shot for shot [r03]
- **Measure the reference frame by frame.** `select='gt(scene,0.12)'` gives a first cut list; busy parts need sheets of
  every frame (`-ss a -t b`, `drawtext=%{pts}`), because shots can be 1 to 2 frames long (reel-03's reference: about
  45 shots in 22 s).
- **Use the reference's frame rate** (25 fps in reel-03, not 30) so every cut lands on the same frame and the audio can be
  reused unchanged. Edit time = reference time.
- **Caption timing comes from the reference picture, not the transcript.** Crop the caption band of every 0.08 s into a
  strip sheet and read when each phrase appears. Keep the reference's on-screen wording ("gotta", "you get a big",
  "it's from") even where it differs from the speech.
- **Measure text**: width as a fraction of the frame, centre height, colours sampled from full-size frames. reel-03:
  small captions Liberation Sans Bold sized so "something i read," is 312 px wide at 1080, centred at 0.494 H, white on
  black and pale warm white (#F0EBD6 area) over footage; "breathe." coral #DE585C 750 px wide; "okay?" mint #A8D4BC 305 px.
- **Reuse the audio bit-exact**: `-map 1:a -c:a copy` from the reference into the delivery; check it sample by sample.
- Few clips for many shots is fine: reuse each clip with a different crop, colour and effect. The references do this too.
- Make a **mapping sheet** (reference frame left, the user's clip right, per beat) for the beat-sheet approval.
- Typical "edit style" (moody motivational) vocabulary: black open with tiny words and closing bars; one big coloured
  word on the hook; slow hold; a fast flurry of 1 to 4 frame flashes with colour shifts and glitch; glowing silhouettes;
  pixelated face; warm framed film shots with soft edges; big coloured punch word; black close with tiny words.

- **Copying one animation (a title, card, caption pop, logo move) from a reference: use the `reanimate` skill**
  [reanimate setup, 2026-11-15]. It measures instead of eyeballing: colour tracking (`vibe/track_color.py`) +
  `easing.ts` named the hidden curve (easeOutBack, about 470 ms) of a test title, and three compare rounds took the clone
  from 5.9 % mismatch to 0.6 %. Compare with `--offset 0` (auto-align locked onto the wrong frame and hid a 0.33 s
  error), and watch `animation-fill-mode: both`, which shows the element before its delay. Example and numbers in the
  skill's `vibe/example/` and "Vibe editing house rules".

## 3. Footage handling
- **Google Flow watermark**: small sparkle at about (0.93, 0.93) of the frame. A punch-in (zoom >= 1.15) hides it. [r03]
- Horizontal clips in a 9:16 edit: crop (fine from 4K, soft but OK from 1080p under grain), frame in the middle with
  soft edges on black, or use as background. Never stretch, never blurred copy behind. [r03]
- Stills (photos, Pinterest images) work as shots: slow push, breathing light, flicker, moving grain. [r03]
- Real gyms are busy: check every crop for logos ("the cloud" sign on the press machine), staff, people walking past,
  people behind the subject. [r01][r03]
- Check user clips for burned-in captions before planning them in; ask for the clean original. [r02]
- The user's phone clips often have no audio and are 1080x1920 at 30 fps; Flow clips are 1080x1920 at 24 fps, 4 s. [r03]
- **Gym footage vocabulary**: the user shared a cinematic gym shot list (Matt Nikishin), saved in
  `docs/library/cinematic-gym-shotlist.md`. Use its step and shot names when asking for gym B-roll or tagging clips; keep
  handheld shake, use foreground layers and low-angle flare as hero shots. [2026-10-30]
- **Google Drive links shared by someone else:** the Drive connector can open the folder's metadata but lists no files
  in a folder that is shared by link only, and this environment blocks drive.google.com, so it cannot be downloaded.
  Ask right away for a zip uploaded in the chat (Drive's "Download" gives one; under 30 MB) or a copy in his own
  Drive. A zip upload of the overlay pack (5.4 MB) worked first time. [vlog]
- Overlay / asset packs: probe every file (size, fps, audio), make a "max of all frames" composite per video to see
  everything it ever shows on one tile, and measure when it stops moving and whether it has sound. That one sheet
  answered every question about the pack. [vlog]
- **His filming knowledge (shared on reel-04):** a five-shot system for every scene: establishing wide, action shot
  with a foreground element, medium shot with the hands busy (repeat 1 to 2 actions from the wide for clean cuts),
  close-up detail, over-the-shoulder POV (focus on the background, shoulder soft). Also: record the same action from
  several angles, foreground layers for depth, golden hour light, focus lock on a stand-in object at about f/2.8, floor
  tape for frame edges when filming solo, shoot 4K for digital moves in a 1080 timeline. Map his clips to the five
  shots when planning; his phone clips are 1080 wide, so digital zooms stay under about 1.15 except on fast moves. [r04]
- His phone clips (reel-04): HEVC 1920x1080 with rotation -90, so they play as 1080x1920; ffmpeg auto-rotates on
  decode. Room audio is quiet (about -30 dB mean); a close typing shot peaked at 0 dB from key clicks. [r04]
- **Joining his split uploads of one clip (reel-11):** each part's audio starts at its own stream `start_time`
  (0, 0.010, 0.021, 0.009 s on her clip). Placing every decoded part's audio at `8*i + start_time` gave a seamless
  25.0 s track (no overlap, no gap); video joined with concat + `setpts=N/(60*TB)`, 1500 frames. Parts of HIS
  recordings instead hide audio before the picture (section 7). Code: `projects/reel-11/RENDER.md` step 2. [r11]

- **His reaction reels arrive as a ready-made composite + split takes (reel-12):** part 1 already held the other
  creator's reel with her burned-in banner and subtitles plus his reaction inset (the hook stays untouched), then his
  talking takes split into 4 phone parts (1080x1920, 60 fps, CFR, audio pre-roll only 5 to 9 ms this time, so the
  seams were clean). Join all parts first into one source (picture stream copy + audio placed at each part's
  start_time, padded to its picture length): `projects/reel-12/work/join.py`. Meme inserts can be odd sizes
  (1080x1316): framed full width on black, never stretched. [r12]

- **Client promos use the client's brand, not his (reel-15, ZAZI).** He said "take care of the vibe of the brand":
  pull the client site's own fonts (computed styles with Playwright: ZAZI = Tenor Sans uppercase 2px tracking +
  Outfit 300), colours and lines, keep product photos ungraded, no prices, slow dissolves. His dark grainy look
  (`docs/playbook/brand/`) is only for his own reels. [r15]
- **Tall photos in a 16:9 edit: Codex outpaint, then paste the original back (reel-15).** Pad the photo to 3:2 with
  grey bars, ask Codex to extend only the bars, then `projects/reel-15/work/make_wide.py`: ECC-align the original,
  blur Codex's sides to the original's softness, carry the low-frequency tone difference across the seam, feather
  110 px. People and products stay the real pixels. Trim the original's 4 px border first: Codex copies a thin white
  border line into its output as a visible stripe. Shopify sites block `/products.json` (403); scrape the home page. [r15]

## 4. Cut-outs (mattes)
- **No single model does it all.** Compare on the actual image before committing: [r03]
  - MediaPipe selfie_multiclass: good person region, rough edges, lumpy heads. Class 1 = hair (useful), 0 = background.
  - rembg `u2net`: cleanest body outline on stills, misses hands and hair above an arm.
  - rembg `u2net_human_seg`: good on video frames of a single person; merges people standing close behind.
  - rembg `isnet-general-use`: catches hands and fingers.
  - Best recipe for a still: max(u2net, isnet x dilated MediaPipe person) + MediaPipe hair and person in the head area,
    close, keep the largest component, soft edge. Draw props (a phone) in by hand as a polygon.
    Reference: `projects/reel-03/work/matte/make_c07_alpha.py`.
- **Never remove a background person with a straight cutting line.** It leaves a hard vertical edge on the subject.
  Fade the effect out with a smooth ramp on that side so it reads as shadow. [r03]
- Mirror selfies: hand and phone mix together, the arm over the head hides the head's top. Check those areas. [r03]
- Floral sofa (reel-01/02 home footage): rembg keeps the sofa; refine with MediaPipe:
  `projects/reel-02/work/refine_matte.py --grow 6 --thresh 0.3 --kill-florals --solid-below 0.68`. [r02]
- Per-frame mattes of a clip: cache to `work/matte/<clip>/NNN.png` so re-renders don't recompute. [r03]
- **His room talking-head footage (pink sheet, grey tee, mic in hand): rembg `u2net_human_seg` alone is clean**, hair,
  beard, mic and hand included, no MediaPipe refinement needed. Keep the largest component (dilated 9 px so the mic
  stays). 983 frames of 1080x1920 took about 10 minutes as two parallel jobs (about 1 s a frame each).
  `projects/reel-11/work/matte_frames.py`. [r11]

- **Hair edge on his room footage (reel-12):** rembg `u2net_human_seg` keeps bits of the beige wall at the top corners
  of his hair. Fix at compose time: inside the top 22 % of the matte and within 60 px of its edge, drop pixels with luma
  > 82, then darken what remains of the soft edge toward the hair tone (despill). A first version without the edge
  limit punched a hole in his forehead. `face_circle()` in `projects/reel-12/work/mg/manga.py`. [r12]

- **Cut-out of his room footage onto a new background (reel-14 v2):** the reel-12 hair-edge fix (drop pixels with
  luma > 95 within 40 px of the matte edge) must be limited to the hair band (matte top row + 300 px): run over the
  whole head it ate his ears and cheeks. Scaling him to 0.82 (bottom anchored) leaves room for titles above his head
  but cuts the shoulders in a hard vertical line at the old frame edge: fade the matte over the outer 170 px.
  `edge_fix()` and `his_layer()` in `projects/reel-14/work/build2/scene2.py`; mattes `work/matte_frames.py`. [r14]

- **rembg subject cut-outs fail on patterned clothes and backgrounds (reel-15).** A hanging embroidered coat came out
  with holes and a halo; an artisan on a patterned carpet and a woman with a boy left fringes. Only the hero (dark coat
  on a plain street) was clean. Check every parallax subject at full size; fall back to a slow push on the whole photo
  (`render_flat` in `projects/reel-15/scene.py`) when the edge isn't perfect. [r15]

## 5. Effects that worked (copy the code from the project, never import across projects)
All in `projects/reel-03/work/build/fx.py` (helpers) and `edit.py` (beats). Deterministic (seeded) so re-renders match.
- Light-snap silhouette from one photo: normal for a beat, flash to blown-out white with rays, body to black, one
  flicker, cool to blue. `back_layers`, `sil_frame`, `b_snap`. [r03]
- Rim light that builds on a moving person, then a glowing yellow-green grain fill with sparkles, scan bands and a few
  dark flicker frames, timed to words. `b_want`. [r03]
- Glowing outline of a moving person (dilate - erode of the matte, blurred glow). `b_ghost`. [r03]
- "Lightning" from footage: Canny edges of a lift, dilated and glowed white. `bolt`. [r03]
- Pixelated to clear: block size shrinks while random cells pop clear. `b_pixel`. [r03]
- Burnt film: framed picture with soft edges, dust and scratches, flicker, burn to warm then black. `b_okay`, `soft_frame`,
  `film_dirt`. [r03]
- Fluorescent tube flicker in a still: isolate the bright tube by luma, off frames = image x 0.22 without the tube. [r03]
- Two-colour ramps (`tint_bw`) give the green, teal, blue, orange flashes of a flurry fast and consistently. [r03]
- Ink illustrations, printed-paper look, Seneca posters, brush wipes: reel-01 / reel-02 `illus.py`, `reel_scene.py`. [r01][r02]
- Vlog overlay pack (REC, vlog titles, VLOG on blue, REC iris): `.claude/skills/vibe-mini-vlog/scripts/vlog_overlays.py`.
  White-on-black designs use Screen blend (1-(1-a)(1-b)); the blue VLOG (7) and the lavender REC circle (12) need a
  colour key with mode "normal" so their dark parts stay dark. Hold the last frame to stretch a design. [vlog]
- Making 16:9 overlays vertical: find the text blocks from the max of all frames, dilate (70x46 px; wider when spaced
  words must stay one row: 170 for the clocks, 300 for "a day in"), keep left/right/centre anchors, spread rows over
  y 230 to 1400, push colliding blocks down. A full-frame circle stretched to 1080x1920 becomes a nice tall oval iris,
  but paint over the stretched copy of its text before pasting the sharp one. [vlog]
- **Moody warm grade, approved from stills first time** (reel-04 `work/build.py`, `look()`): per-clip levels from a
  mid frame applied at half strength, curve with gamma 1.12, gentle S, highlight roll-off above 0.82, lifted blacks
  (0.035), split tone (teal shadows, warm highlights) as a per-channel LUT, saturation 0.82, halation from highlights
  above 205 at quarter res (the first try at 190 smeared orange on frame edges), vignette 0.42, grain 0.035 from a
  16-field bank. About 0.5 s per 1080x1920 frame including moves. [r04]
- Revision splice tool: `projects/reel-04/work/splice.py` swaps re-rendered ranges into the previous master frame by
  frame and prints which frames changed, so you can prove only the noted seconds moved. [r04]

- **Animating a flat logo image (reel-05):** split it into layers with connected components on the ink (threshold
  min(RGB) < 170, then grow labels 4 px for anti-aliased edges) plus a few hand rules (a seam line between merged
  shapes), and "colour to alpha" over white so the layers composite back to the exact logo. Solid white bodies: a
  hand-traced outline polygon beat every closing/hole-fill trick on open line art. Upsample layer crops 2x with a
  sharpened alpha so zoomed-in shots stay crisp. End by blending into the exact reference so the last frame matches
  pixel for pixel. Code: `projects/reel-05/work/layers.py`, `fills.py`, `scene2.py`. [r05]
- **Logo reveal kit (reel-05), copy from `projects/reel-05/work/`:**
  - Night line art: neutral ink recoloured white with a soft additive glow on the dark sky, red parts keep their red;
    a soft white bloom from the joint at the lock hides the switch to black ink on white (`scene.py`, `place`, `bloom`).
  - Speed: horizontal box blur sized from the per-frame displacement (about 0.5 x px per frame) on the layer.
  - Smooth motion: PCHIP keyframes for positions (continuous speed, add a duplicate end key so it lands at rest)
    and smootherstep for cameras (`scene2.py`, `BIKE_L`, `CAR_L`, `CAM_S`).
  - Parallax: two cameras, scenery zoomed 1.6 to 1.8 and vehicles 1.12 low on screen, both easing to identity on the
    lock, so the end frame is the logo exactly (`scene2.py`, `M_scenery`, `M_vehicle`).
  - Speed streaks smeared out of a vehicle's back at quarter resolution also hide a flat cut edge (the logo's bike
    is cut along the seam where it meets the car) (`scene2.py`, `streak`). Draw all streaks before all vehicles, or a
    streak paints over the other vehicle.
  - Sun rising behind mountains: clip the disc per column at the logo sun's own bottom edge, so it lands exactly as
    drawn. Red flash ring around a letter looked like a stray circle over the tagline; a short red glow behind the
    letter worked. A wide soft "sheen" on black letters reads as a smudge; a 14 px glint works.
  - Wordmark: letters slam or rise in 0.035 to 0.05 s apart, the red A lands last with a small hit; an orange light
    streak under the word that opens into the tagline (his storyboard idea). [r05]
- **Lemo Urban Sketch film kit (reel-08, `projects/reel-08/film/film.js`):** colour withheld as story (ink-only
  flashback strip, one coral dumbbell that lifts off line by line with `drawPen(..., from)` plus coral crumbs on
  "slowly disappeared", colour blooming back on "starting again"); a sticky-note week tracker ticked on the words
  "five days a week" then scribbled out on "then life happened"; breath drawn as ink curls; an empty thought bubble
  on "nothing." with a 0.4 s punch-in shake; a checklist written in the sky (ticks, coral strike-throughs) on the
  spoken words; a page turn to a blank "Day 2" page as the series ending. Camera = eased keyframes for designed moves
  and a pre-simulated spring (240 Hz) for the follow. [r08]
- **Colour arriving around a moving subject:** a colour front that trails just ahead of her left big white "holes"
  on screen. Sweep the colour across the whole view in about 2 s and keep it ahead of the camera. Text written in
  world space next to a walker must be placed ahead of her (about +330 px), or it scrolls off half written. [r08]

- **Exercise figure in code (reel-09):** a small 3D rig (torso from cross sections, tapered limbs, ellipsoid head)
  projected orthographically and drawn flat with skia-python (preinstalled; pycairo is not). 0.04 s per 1080x1920
  frame, so a 15 s video renders in about 20 s. **A pure side view hides the elbow-to-ribs gap** (it points at the
  camera): use a front three-quarter view (55 deg) and curl with the far arm, so the arm sits outside the body
  outline and the gap shows as clear space; slim the waist (V-taper) so the gap reads. Pinned elbow = upper arm
  pulled in onto the ribs, shoulder raised with a trap line, hitchy 3-step lift + tremor, red glow and ring on the
  contact spot; free elbow = cosine 2 s up / 2 s down, elbow drifts 6 deg forward, dashed green dumbbell arc.
  Code: `projects/reel-09/work/fig.py`, `scene.py`. [r09]

- **Pixel RPG graphics layer over real footage (reel-11), approved from stills first time**, in plain Python, no
  library engine: native 216x384 grid scaled x5 nearest-neighbour; ENDESGA-style palette; 4x4 Bayer dither for every
  gradient; 16-bit blue windows (ink / white / silver border, dithered blue fill); Press Start 2P at 8 px native
  (`vibe/fonts.py "Press Start 2P:400"`, PIL draws it without anti-aliasing at that size) with a 1 px ink shadow; ASCII
  sprites with an automatic 1 px ink outline (hero with beard, friend with red cap, shield, hand cursor); a hand cursor
  that bobs 1 px at 4 Hz and stops when a choice is made; mosaic transitions (block size steps, never alpha fades);
  3-2-1 px screen shake; a glitch tear-away (row blocks shifted, RGB split, one inverted frame) into real footage; the
  physique photo shrinking into a pixel-framed card for the end card. Beats: quest window, calendar pages flying, day
  counter, CHOOSE PLAN menu with an undecided cursor, 99 % loading bar, SAVE GAME, couch + BODY FAT +1, item fanfare,
  [LISTEN] [SKIP], quest log. 0.35 s per 1080x1920 frame; render in 4 parallel ranges.
  Code: `projects/reel-11/scene.py`, `timeline.py`. [r11]
- **Face circle with the head breaking out (reel-11):** a pixel-stepped circle (mask drawn on the native grid, so its
  edge has pixel steps), 2 px gold ring + 1 px ink, warm gold-to-orange dithered fill so the face pops off the cool
  world; his matted frame scaled `0.62 * r / 60`, placed so the hair top sits about 105 px above the circle top; the
  alpha is clipped to the circle below the centre line and free above it. Move and resize it per beat so it never
  covers UI or real photos. `face()` in `projects/reel-11/scene.py`. [r11]

- **Manga hybrid over real footage (reel-12), copy `projects/reel-12/work/mg/`:** paper #F3F0E8, ink #121212, one
  red #F03C1E (stamps, ticks, anger marks only). Every grey is a dot screen (`dot_tone`), focus lines are tapered
  wedges re-seeded 10 times a second (boil), panels ink in right to left in 0.12 s with an 8 px border, shouts are
  three-layer slam lettering (`sfx`), impact = 2 inverted frames + a decaying shake. His head breaks out of a manga
  circle (ink ring, paper rim, screentone + focus lines inside) with a 12 px paper rim + ink outline where it leaves
  the circle; the circle moves and resizes between sections (`KEYS` in `scene.py`). Real photos, clips and Codex food
  stay full colour inside ink panels. Benefit illustrations in `benefits.py` (gauge, age chart, flame + kcal counter,
  sugar line smoothing, X-ray bone, shield, hourglass, cloud to sun, moon + Zzz); clip drawings to their panel
  (`Pen.done(clip=...)`) or sliding elements spill onto the page. [r12]

- **Vox-style torn-paper explainer (motion graphics pack, 2026-11-24), copy `.claude/skills/vox-explainer/example/`:**
  red #B8312A, cream #F1E6D0, paper #FBF7EE, navy #14213D, yellow #F2C230, Anton for headlines, JetBrains Mono for
  labels. Torn sheets = a jagged path cached per seed (same paper every frame) with a 10 px white fibre fringe under it
  and a soft shadow; halftone = a 16 px dot pattern at 6 to 12 % inside big colour sheets; grain changes on twos.
  All motion goes through `twos(t) = floor(t*12)/12` at 24 fps (checked: consecutive frames differ only every second
  frame). Photo cards keep the photo unfiltered inside a torn white margin. The question's first line must already be
  landing on frame 0. Sound: Openverse CC0 paper flips on every landing, a swoosh on each paper wipe, a soft thud under
  the big word, a marker for the circle and highlighter, peaks placed on their frames (`example/mix.py`). Render with
  `tools/seek_render.mjs`: 14 s at 24 fps in 47 s, 24.7 MB at crf 14. [mg-pack]

- **Vox photo parallax (stills that feel like video), skill `photo-parallax`, tool `tools/parallax.py`:** learned from
  the reel "How Vox makes images look like videos". Split a deep photo (clear foreground / midground / background)
  into layers, patch what each layer hid, space them in depth, move the camera slowly. Here: Depth Anything V2 small
  (ONNX, CPU, from GitHub releases since Hugging Face is blocked) splits by depth; `--subject` (rembg isnet) gives the
  main subject its own crisp layer, ranked by its feet so it stands in front of its ground (the depth model alone
  lumped the cable car in with the rocks). Patch = Telea rim + push-pull inside + texture mirrored from the hole edge,
  faded to grain deep inside (mirrors of mirrors make streaks); ignore a 2 % border strip (old prints have dark edges
  that turned the fill black). Each layer reaches 10 % of the image size under the nearer one, or a dark seam shows
  above the bench at the end of a dolly. 6 s dolly-in 0.22: front +28 %, back +5 %, reads well on a phone. Layers
  in 3 to 8 s, a 6 s 1080x1920 render in about 33 s. Tested example: `.claude/skills/photo-parallax/example/`. [parallax]
  He reminded: "You have codex image generation don't forget". So the hidden areas are painted by Codex by default
  (`--plate codex --remove "<all the near things>"`, about 1 minute): it kept the framing to 0.1 px and painted real
  sand, crowd and shadows, far better than any code patch. Prompt with the image goes after the text: `codex exec ...
  "<prompt>" -i photo.jpg` (with `-i` first, Codex reads the prompt as another image path and waits on stdin). [parallax]
  He also reminded: "we use this for vox motion graphics". So parallax lives inside the Vox kit: `kit/parallax.js` in
  the photo-parallax skill, tested shot `.claude/skills/vox-explainer/example/parallax.html`, layers made with
  `--web 1600` (WebP + layers.js, 0.5 MB). Camera smooth on real time while graphics step on twos; `focus` on the face
  (a centred push hid his head under the headline strip); captions and strips off the face and off the nearest layer.
  When saving a new technique, wire it into every skill that would use it the same day, not just a standalone tool. [parallax]

## 6. Text and captions
- Captions sit on a handheld mic at about 1440 px; ask about caption height at the stills step when he holds a mic. [r01][r02]
- Keep text off his face and beard: move the picture (crop) rather than the text when a centred word lands on the face. [r03]
- A caption over the brightest glow is hard to read: move the picture so the glow sits below the caption line, and give
  captions over footage a soft dark halo. [r03]

- **Post captions (Instagram text under the reel):** explain, don't preach. Say what the clip shows, then the point in
  plain sentences. No rhetorical triplets, no "tag a friend", no emoji or hashtags unless he asks. See section 1. [r07]

- **Caveat's digit 5 reads as an S** at caption size ("no 5am punishment" read "Sam punishment"). In handwritten fonts,
  spell small numbers out ("five days a week") or space them ("5 a.m.") and check the line at full size. [r08]

- **Typed dialog-box captions: set the line breaks by hand (reel-11).** A greedy chunker (break on gaps, punctuation,
  line overflow) left orphans ("months", "Monday" alone) and joined "her Let's say". A hand-set list of words per
  line (`LINES` in `projects/reel-11/scene.py`) with asserts (word count matches, 25 characters a line at 8 px from
  x 9 on a 216 px grid) fixed it. Show a chunk from its first word's start, never earlier, or the box flashes empty.
  Words type at 40 characters a second, the spoken word in gold. [r11]
- **Check every real photo with a caption over it (reel-11):** the top caption box covered his face on the dumbbell
  photo; moved the photo 200 px down (pixel wall above). The FOLLOW button touched his face on the mirror photo;
  moved it to an end card. Both caught at my stills check. [r11]

- **Hinglish captions from a Hindi Scribe transcript (reel-12):** Scribe writes Hindi words in Devanagari; keep a
  hand-made transliteration table (`TR` + per-word `FIX` in `projects/reel-12/work/mg/scene.py`) and caption in
  Latin script. Chunking: sentences (punctuation or a pause over 0.28 s) split into near-equal chunks of at most
  4 words, so no orphan "hai." chunk. Narration box with the spoken word inverted (paper on ink). During spoken lists
  the item box (counter + text + red tick on its last word) is the caption. [r12]

## 7. Audio
- Cut audio from WAV decoded from the start, never by seeking an MP4/MP3 (up to 100 ms off). Verify sync by
  cross-correlation against audio decoded from the start. [r02]
- Cut points from the voice envelope (10 ms steps), not padded word times; start on the inhale; watch the frames for mic
  movements. `projects/reel-02/work/plan_cut.py`. [r02]
- Music: find tempo, grid phase and phrase length before looping; repeat whole phrases; check where the generated track
  really ends. `projects/reel-02/work/mix.py`. [r02]
- "Voice louder, music the same": key ducking from the voice before the boost, fix master gain to the approved preview. [r02]
- SFX: place each so its peak lands on its frame (`work/sfx_cues.json`). Music ducked about 10.5 dB under voice;
  final about -14 LUFS, peak about -1.4 dB. [r01]
- Reused reference audio stays untouched: no isolation, no new music, no loudness change. [r03]
- **Openverse is the sound library (user rule, 2026-11-06).** He wants real sound design on every cut and asked for the
  free Openverse library (openverse.org, no key) so he never buys a sound pack. Tool: `tools/openverse_sfx.py`
  (search / pick / get / measure / credits). Facts found while building it: the API needs `format=json` (it serves
  HTML otherwise); multi-word searches match every word, so "cinematic hip hop" found nothing while "hip hop" found 17
  Jamendo tracks; `license_type=commercial` still includes by-sa, so the tool passes `license=cc0,pdm,by` itself;
  `category=sound_effect` returns nothing for Freesound sounds (their category is empty), so SFX are found with
  `length=shortest` plus a duration cap; Wikimedia's hits for "whoosh" are mostly people saying the word (Lingua Libre
  `LL-Q...`, category `pronunciation`), filtered out. From the cloud container: Jamendo downloads fine, Freesound
  answers 403 to everything (cloud IP block; the bulk of the SFX), Wikimedia comes and goes with 429. Do not spoof a
  browser to get round it (auto mode blocks it, rightly): give him the sound page links to download and upload, then
  run `measure`. Measured shapes: up to 50 ms attack = hit, 50 to 400 ms = swoosh, longer = swell. [openverse]
- Freesound re-checked on 2026-11-18 (reel-11): the proxy tunnel is established, then freesound.org, its `/apiv2/` and
  cdn.freesound.org answer 403 with an empty body. An API key would not help. Every Openverse SFX hit for "whoosh",
  "swish" and "glitch" was on Freesound. Code-made 8-bit cues (`projects/reel-11/work/sfx.py`) covered a game-styled
  reel. [r11]

- Downloaded overlay packs carry their own SFX, often mastered loud (the vlog pack peaks at -0.8 to -5 dB). Mix
  them as separate tracks under the voice, never at their original level. [vlog]
- ElevenLabs music ignores section timings in the prompt (asked for a dip at 18 s, got none; all three 36 s requests
  ended about 33 s). Generate, then map the real track (librosa beat_track for tempo/grid, per-beat sub/mid/hi energy
  for drops and fills, downbeats from where fills land) and fit the cuts to it. reel-04 moody track: 92.3 BPM,
  downbeats every 2.60 s from 2.56. Script: `projects/reel-04/work/el_gen.py` (music/SFX with 429 back-off). [r04]
- **Risers and swells from ElevenLabs come out bright and piercing** (riser_exit: 79% of its energy above 3 kHz;
  reverse swell 86%). He called them "harsh and ear piercing". Low-pass risers around 2.2 to 3.2 kHz (keep about 15%
  dry for air) and sit them 2 to 3 dB lower before he hears them. Code: `projects/reel-04/work/mix.py` (SOFTEN). [r04]
- Room sound under a no-voice edit: about 0.3 of the clip level, keys 0.55, bottle and cap 0.8, halved on the ending.
  Audio-only revisions: copy the picture stream (`-c:v copy`) from the previous preview, mux the new mix, check sync
  by cross-correlation (0 ms). [r04]
- ElevenLabs sound-generation for an intro (reel-05): 5 prompts, 2.5 s engine pass-bys (bike loudest 0.6 to 1.0 s
  into the clip, car 0.9 to 1.6 s), 1.5 s impact (peak at 0 s), 1.5 s swell (peak 0.88 s), 1.2 s shimmer (peak 0.3 s).
  Measure each clip's envelope in 0.1 s bins, then place the loud part on the motion. Pan engines from the vehicle's
  screen x (equal-power, 0.85 max). One request at a time went through with no 429. `work/gen_sfx.sh`, `work/mix.py`.
  [r05]
- **Swapping music in a finished, mixed video (reel-06):** ElevenLabs audio isolation gives his voice back, but it
  also keeps *sung* vocals (the song's singer) and drops every sound effect. So: use the isolated voice only where he
  speaks, put the new music in where the song was, and keep the original mix in gaps that hold only an effect (whoosh,
  explosion), where the old bed sits about 25 dB under it. Map the song's structure first (held intro, break on the
  cut, drop, stop) and pick the generated option whose shape matches; the one that matched (126.6 vs 126 BPM, drop
  at 7.76 s) needed only a 0.17 s offset. Measure the original bed in silent gaps: here a sub-heavy hum about 25 dB
  under the voice; the new bed sits 26 dB under. The original was mastered very loud (-7 LUFS, peaks 0 dB): match the
  talk level with make-up gain on voice + bed and a look-ahead limiter, not by scaling the whole mix.
  Code: `projects/reel-06/work/mix.py`. [r06]
- **Aligning an isolated voice: use the envelope, not the waveform.** Waveform cross-correlation on one 10 s window put
  the isolated voice 10.5 ms early, and the isolated file also drifts (about -0.12 ms per second). Band-passed RMS
  envelopes (300 to 3000 Hz) in 4 s windows, a linear fit of lag over time, then resampling brought every window
  within 0.25 ms. Code: `projects/reel-06/work/align_voice.py`. [r06]
- **Joining the user's split uploads:** the parts' seams carry odd timestamps (frame gaps of 26 and 35 ms). Copying
  them into a master works, but re-encoding that master dropped frames at the seams and the last 0.5 s (the payoff
  shot), and `-shortest` dropped the last 2 frames. Encode from the parts with `setpts=N/(60*TB)` and `-fps_mode
  passthrough`, no `-shortest`, then count packets against the source (3857 here) before sending. HEVC 2-pass
  3.5 Mbps for 64 s of 1080x1920 at 60 fps = 28.5 MiB, SSIM about 0.986 to the source. [r06]
- Original reel audio with a commercial song in it stays out of git (`full_src.mp3` ignored). [r06]
- **Split uploads hide audio before the picture starts (reel-11).** His phone-split parts 2, 3, 4 of one recording
  had their audio begin 0.24 to 0.26 s before the picture (negative audio pts; check with `ffprobe -select_streams a
  -show_entries packet=pts_time`). A normal decode to WAV silently drops that pre-roll, so a line that ran across the
  part boundary ("while sitting / on your ass") lost a quarter second of speech and sounded chopped; he caught it on
  the first rough cut. The previous part's picture also runs that much past its own audio. Fix: copy the raw stream
  (`-map 0:a -c copy x.aac`) and decode that (keeps the pre-roll; cross-correlate it with the normal WAV to measure the
  offset), then build the line as ONE piece: part A picture and audio to their real ends, part B's full audio + picture,
  picture frames fitted to the audio length, no fades at the seam. Check every seam a used line crosses: envelope
  stays up, no sample step, picture frame diff normal. Code: `projects/reel-11/work/make_cut.py`. [r11]

- ElevenLabs TTS on this account: `output_format=mp3_44100_192` is refused (403, Creator tier and up); use
  `mp3_44100_128`. One request for the whole script (voice "Jessica" `cgSgspJ2msm6clMCkdW9`, multilingual v2,
  stability 0.45, style 0.25) read naturally with good pauses, 75 words in 32.8 s, Scribe matched every word. [r08]

- **ElevenLabs on reel-12:** voice isolation on 86 s of his part came back 3.5 ms early with -0.11 ms/s drift
  (envelope fit fixed it: `projects/reel-12/work/align_voice.py`). Music: both 90 s requests ended about 84 s again;
  option A (pizzicato comedy, measured 161 = 80.7 BPM, steady) won over B (groove with frequent full stops, choppy
  under a voice). SFX generation quirks: "pop" came out at -45 dBFS, riser / swell / whoosh clipped above 0 dBFS,
  shimmer and tick are 94 to 98 % above 3 kHz: normalise and low-pass before placing. Measure generated sounds with
  `projects/reel-12/work/measure_sfx.py` (the Openverse `measure` needs an Openverse id). [r12]
- **Measure music against voice on separate stems, never on the mix (reel-12):** a -17 dB music gain looked fine
  until the stems showed it 30 dB under the voice (inaudible); -5 dB put it 17 to 19 dB under while he talks and about
  -25 dB in pauses. Write `_stem_music.wav` / `_stem_sfx.wav` from the mix script and compare RMS per section. [r12]

- **The last line of every split part ends with him reaching to stop the camera (reel-13).** The out-point walk
  (voice under -45 dB for 80 ms) ran 0.23 s past "supplements" into the reach sound, and the mic left frame; he asked
  for it cut. At every part's last line, end where the word has decayed (about -35 dB on the isolated voice) and check
  the frames for the hand going to the phone. Same for line starts where the mic is lifted into frame: start once it
  is up (`IN_FLOOR` / `OUT_CEIL` in `projects/reel-13/work/plan_cut.py`, motion check `work/mic_motion.py`). [r13]

- **He raises the mic before every line and drops it after (reel-14).** The inhale walk-back put most in-points
  0.3 to 0.5 s before the first word, with the mic still rising into frame. Automatic rule that fixed all 32 lines
  at once: start no earlier than 0.10 s before the first word (the mic is up by then), and if the lower half of the
  frame starts moving before the out-point, end at the later of the -35 dB decay + 1 frame and the first moving
  frame. Merge pieces whose gap is under 0.1 s so the out rule never leaves a 2-frame jump cut mid-sentence.
  `projects/reel-14/work/plan_cut.py` (`LEAD`, `first_motion`). [r14]

- **Freesound from the container, 2026-11-23 (reel-14):** some downloads worked (metal hit, boom, shield bash, shutter,
  riser) and others answered 403 from cdn.freesound.org on the same run; retrying with waits got 3 more. Try `get` a
  few times before asking him to download by hand. The project `.gitignore` ignores `*.wav`: add
  `!assets/sfx/openverse/*.wav` so the trimmed sounds are committed. [r14]

## 8. Workflow and process
- Stills first, every time (contact sheet every 2.5 s + full-size changed frames), plus a short low-res draft clip when
  timing matters. For reel-03 the user approved from stills + a 2.6 s draft of the changed range. [all]
- Style the key moments first (hook word, flurry, the special effect, the punch word), send stills + a short motion
  sample, then style the rest. [r03]
- **Look at every still yourself before sending** and fix what you see (logo in frame, text on the beard, caption over
  glow, hard edges). Then list the remaining doubts for the user with times. [r03]
- **New outside service: test reachability first with one small request,** then give him the exact hosts to allow
  (the API host plus every host the files are served from: for Openverse that was api.openverse.org, cdn.freesound.org,
  freesound.org, upload.wikimedia.org, ccmixter.org, Jamendo). He adds them himself in the environment settings and it
  works at once. Then check each file host honestly: a 403 or 429 from the site itself (tunnel established) is the site
  blocking the cloud IP, not the network policy, and must not be worked round by faking a browser. [openverse]
- Test a complex effect on the user's actual asset early (the light-snap test on his back photo) and send it. [r03]
- One ffmpeg input per cut piece; long `trim` chains get killed for memory. [r02]
- ffmpeg `fps=2` contact sheets can show frames about 0.25 s off their labels. For exact checks pull frames by number
  (`select=eq(n\,N)`) and compare to the renderer. [r03]
- Revisions: save the current master (`master_vN.mp4`), render only the changed whole seconds, splice into the previous
  master, re-encode, then SSIM per frame against the previous version: list the changed ranges and the minimum SSIM
  outside them (reel-03: >= 0.984 is just re-encode noise). [r01][r03]
- Keep a revision log `work/revisions.md` and `RENDER.md` with rebuild steps in every project. [all]
- Style studies (no video yet) go in a skill, not a project folder: `.claude/skills/<name>/` with `SKILL.md`,
  `assets/`, `scripts/`, `reference/`; add it to the router table in `vibe-editing-system/SKILL.md`, CLAUDE.md and
  `docs/README.md`. Committed as a shared-file change. [vlog]
- Analysing a reference reel: 1 fps contact sheet with time labels, a few full-size key frames, a close-up of any
  custom type, and a Scribe transcript (costs a few credits; say so). [vlog]
- Environment: `xxd` is not installed (use Python for pixel values); the sandcastles plugin failed to connect
  (proxy 403) on 2026-10-30. [vlog]
- Codex CLI (2026-11-01): installed by the start-up hook, signed in with the user's ChatGPT Go account via
  `codex login --device-auth` (never an API key), asked for at the start of every session; full rule in CLAUDE.md.
  `codex exec` generates images with no API billing (test: `codex-images/manga-laptop.png`, a clean manga panel with
  legible thought-cloud text on the first try). A new session once wrongly said Codex needed an API key because no rule
  existed yet: any tool the user sets up needs a CLAUDE.md rule the same day. [codex]
- Lemo-Opuscar (2026-11-13): he saw a YouTube short about it and asked to "add it to our setup". It is a Claude Code
  plugin with 99 code-made film styles (the video said 66; 33 were added on 2026-11-12). He does not monetise, so
  copying from its CC BY-NC docs is fine. Set up as the `lemo-opuscar` skill (vendored SKILL + setup.sh, house rules on
  top), `tools/lemo.sh` wrapper and a start-up hook step. Container facts found on the way: the library wants ffmpeg 7+
  (system is 6.1: `loudnorm` under-reports length and its `mux.sh` rejects the file), and imageio-ffmpeg already ships
  ffmpeg 9, so the wrapper puts that first on PATH; the global Playwright (1.63) matches the library's playwright-core,
  so its browser install is a no-op; WebGL is SwiftShader (software), so 3D and shader styles render slowly. Tested: a
  sparse clone is 33 MB, core packages install in about 5 s, watercolor demo stills render in about 0.1 s each, a 3 s
  1080x1920 film in 3.5 s. Pages outside the library import `/core/lib.js` fine. Codex is detected as the image
  generator for the ✦ styles. `HYPERFRAMES_BROWSER_PATH` in the start-up hook pointed at `chromium_headless_shell-1194`,
  gone from the image (now `-1243`, with a different inner folder name): the hook now globs for the newest. A demo's
  first still failed (`paper.jpg` 404, "source image cannot be decoded") until its `build.sh` step 0 ran (fonts, paper
  texture): demos are reference code, not ready to render. [lemo]
- **New shared tool: test the start-up hook from a wiped state before pushing** (delete the install, run
  `CLAUDE_CODE_REMOTE=true bash .claude/hooks/session-start.sh`, wait for the done marker, then render through the
  wrapper). That is what a new session gets; a tool that only works in the session that set it up is not set up. [lemo]
- Environment checks: curl on auth.openai.com / chatgpt.com returns 403 with `cf-mitigated: challenge` (Cloudflare,
  fine); a real proxy block fails the CONNECT instead (see `curl -sS "$HTTPS_PROXY/__agentproxy/status"`, recent relay
  failures). developers.openai.com is not on the allowed list, so OpenAI docs come only through web search. Codex login
  lives in `~/.codex/auth.json`; copying it between sessions breaks because the token rotates (about every 8 days, and
  whenever any copy refreshes). [codex]
- Codex image test, artwork on a product (2026-11-01, Berserk poster on a black tee): let Codex make only the blank
  product (shirt came out straight and clean in one try, 1024x1536) and put the user's artwork on in code, because
  Codex redraws art and mangles lettering. "Blend into a black shirt" = no box: inside dark panels light becomes ink,
  in the light margin flip it (black text prints white), keep white-filled lettering (katakana) as its own mask, and
  zero a 5 px band on panel borders or a thin outline appears. Fabric bend must be tiny (about 1.5 px; 30 px looked like
  water). He confirmed the two-step plan before generating, which he asked for. Code and result:
  `codex-images/tee-mockup/` (`print_on_tee.py`). [codex]
- Order that worked on reel-04 (no revisions to the cut beyond one note): clip-by-clip report, his guidelines mapped
  to the clips, cut list with source times, 3 music options, map the chosen track, refit the cut list to its bars,
  low-res rough cut, motion test of the opening, look stills + before/after, sound design + full v1, then overlays as
  stills + a joined draft of only the overlay moments, rendered as spliced ranges. [r04]
- **The project scaffold's `.gitignore` ignores `work/` and `*.mp3`,** so scripts and paid ElevenLabs audio were not
  committed at first in reel-04. At project start, rewrite it: keep raw/, out/, video, wav and heavy work files out,
  keep scripts and mp3 in; also ignore `work/*.log` and `*.mbtree` (x264 two-pass leftovers, 17 MB slipped in once). [r04]
- Never pipe a long build script into `head`: the broken pipe kills the script mid-render (reel-04 rough v2). Write the
  log to a file and `tail` it. [r04]
- Clear `out/stills/` (or use a fresh folder) before each stills round: old PNGs mixed into a new contact sheet and
  looked like a bug in the iris. [r04]
- Environment: librosa is not preinstalled (`pip install librosa` works). The Google Drive connector is connected
  (lists and reads his files) but uploads pass the whole file inside one call, so it can't carry videos (even a 27 MB
  preview); deliver big files in parts through SendUserFile. Full 32 s 1080x1920 picture render with the reel-04 look:
  about 8 minutes on 4 cores; four 2 to 4 s ranges rendered in parallel took about 3 minutes. [r04]
- **Very short videos: the 2.5 s stills grid gives one frame.** For intros, send stills every 0.1 s (25 to 31 tiles)
  labelled with time, plus a half-size draft clip, because motion is the whole point. Labels: ffmpeg drawtext with
  image metadata did not render; `projects/reel-05/work/sheet.py` (cv2) does. [r05]
- Render speed (reel-05, numpy/cv2 layer compositing, 4 cores): 1920x1080 at about 1.2 s per frame (v1, 75 frames in
  about 1.5 min); stills about 0.8 s each. [r05]
- Before writing the beat sheet, test the riskiest step on the real asset first (here: can the logo be split into
  car, bike, letters?). The split worked in three passes and decided the whole plan. [r05]

- **Lemo Urban Sketch on a tall vertical page (reel-08):** no need for the demo's 5120 px GL world. A 2D canvas page
  with half-res wash layers per scene (revealed by noisy clip shapes), ink strokes drawn per frame with `drawPen` in
  stroke order, and the engine's `figure()` rig renders a 1080x1920 still in about 0.15 s and a 540x960 15 fps draft
  of 36 s in 22 s. Pass `smooth: false` for boxes or `penStroke` rounds them into blobs. Code: `projects/reel-08/film/film.js`. [r08]
- **Codex for characters, speed and quality (reel-08):** a 4-view character sheet (16:9) took about 60 s, each pose
  with `--ref <sheet>` about 30 s, through `sh tools/lemo.sh .venv/bin/python core/image/gen_image.py "<prompt>"
  --aspect 2:3 --ref <sheet> --out <proj>/gen --name <pose>`. Ask for "plain white paper background, nothing else
  drawn, no cast shadow, full body" so the cut-out is clean. A 4-frame walk cycle in one image stays consistent;
  the gaps between frames can be only 15 px, so split on column gaps with a tiny merge threshold. Black-hat (9 px
  ellipse) on the grey image, minus 18, over 50, gives clean ink lines for a pen draw-on. [r08]
- **The library's `video.mjs` encodes drafts big** (36 s at 540x960, 15 fps = 31 MB). Re-encode drafts at crf 28
  (2.4 MB) before sending. [r08]

- **Voxel reels setup (2026-11-14).** He pasted only an artifact link (@heyalok.ai's "Claude 3D cartoon reels" guide);
  I read it, offered options with "add it to the setup" first, and he chose that. The guide's prompts were in the
  page's script (the read summary said they were missing): extract the script text when a guide page looks empty.
  Built as the `voxel-reels` skill with a tested kit instead of copying the 7 prompts. What the test showed: [voxel]
  - ElevenLabs `/v1/text-to-speech/<voice>/with-timestamps` works through the injected key and returns character
    timings with the audio: word-timed captions with no Scribe pass. One request per line costs the same (billed per
    character) and lets one line be redone alone. Word end times can run past the trimmed line: clamp them.
  - Software WebGL (SwiftShader) is fine for box-built 3D with soft shadows: about 0.25 s a still, 0.2 s a video frame
    with 3 workers (45 s reel about 5 min). Don't assume 3D is too slow here; measure.
  - Bugs caught only by looking at the stills: captions empty (a chunk's end read the next chunk's start before it was
    set), close-ups far too tight (a 0.7 unit push-in on a vertical frame), the CTA box over the face, the mouth lost
    in a dark beard, captions on the sidekick's face. Fixed values are in the skill's "Framing" section.
  - Freesound still answers 403 for every whoosh and pop; the kit ships code-made fallback cues
    (`kit/make_code_sfx.py`) for drafts, and real sounds still need his download.
  - `/v1/voices` is not reachable, so a second voice ID has to come from him; reel-08's "Jessica" is
    `cgSgspJ2msm6clMCkdW9`.
  - The guide's sidekick is Anthropic's Clawd: ask before drawing it.

- **A bare link with no instruction (a GitHub repo, a tool) = read it, say in plain words what it does and what it would
  do for his reels, then offer numbered options** (add as a shared skill / use it now on a clip / just your opinion).
  He answered "Add it as a shared skill" in one line. [reanimate]
- **Importing an outside Claude skill:** copy only its skill folder into `.claude/skills/<name>/` with its LICENSE,
  keep the upstream text, put a "Vibe editing house rules" section at the top (what overrides what, where work goes,
  the tested numbers), patch the code as little as possible and mark each patch in a comment, gitignore its
  `node_modules/`, install it from the start-up hook in the background with an `.ok` file, add a video-specific test
  example inside the skill, then rerun setup and the example from a fresh copy before pushing. Recipe:
  `.claude/skills/reanimate/` (setup.sh, lib.ts `chromiumExecutable()`, vibe/). [reanimate]
- **Tools that pin their own Playwright** (reanimate wants 1.64.1; the container has 1.63 and Chromium build 1243)
  fail with "Executable doesn't exist". Pass `executablePath: "/opt/pw-browsers/chromium"` (a symlink to the newest
  build) instead of downloading a browser. Bun 1.4 is preinstalled; npm packages that download binaries from GitHub
  releases (ffmpeg-static) install fine through the proxy. [reanimate]

- **Cut points: check the picture where the envelope walks back far (reel-11).** The walk-back from each onset found
  1 s of sound before two lines: a mic being raised (take 2) and a long breath with the mic already still. Frame strips
  around the in-point decided the override (`lo` in `projects/reel-11/work/plan_cut.py`). [r11]
- **The stop hook flags untracked files after every step (reel-11, five times).** Commit and push after each step, and
  put intermediates in the project `.gitignore` up front: `*.aac` (streams copied out of raw footage), `work/parts/`
  (split pieces), `work/**/*.png|jpg` (stills, mattes). [r11]

- **Check the stills against the beat sheet line by line (reel-12):** the anger mark at "yeh khud ko kya samajhti
  hai" was in the approved beat sheet but missing from the build; it was caught only while placing sounds. Tick off
  every beat-sheet row in the stills before sending them. [r12]
- **Revision ranges must start on the master's keyframes (reel-12):** parts rendered in parallel each restart the
  keyframe grid (keyframes at part start + 30k), so pick splice points on those frames, split the old master with
  `-f segment -segment_frames`, concat copy, and prove the rest unchanged with framemd5 per frame. [r12]
- **Guard "current item" lookups for the gap before the first item (reel-12):** a list branch that starts 0.05 s
  before item 1 crashed two render parts (`[...][-1]` on an empty list). Fall back to the first item. [r12]

- **Imported skills packs follow the reanimate recipe (2026-11-24):** he asked to import charlie947's whole
  motion graphics pack. Copy each skill with its LICENSE, put a marked "Vibe editing house rules" block at the top of
  every SKILL.md plus one long house-rules file (`docs/library/motion-graphics-skills/HOUSE-RULES.md`), replace their
  installs and renderers with ours (`tools/seek_render.mjs` for `window.seek` pages), build and render one tested
  example, and only then write the numbers into the rules. skills.sh pages don't resolve from this container; the
  GitHub repo behind them clones fine. [mg-pack]

- **Toolkit pass at the start of every video (2026-11-24):** sessions handed raw footage reached for one skill and
  forgot the rest; he once had to tell a session it had Lemo-Opuscar. Now `docs/playbook/toolkit.md` lists every skill,
  tool and proven recipe by what a moment needs. Read it with the lessons file, offer the best 3 to 5 ideas tied to
  times in the first summary, fill the beat sheet's tool column, and add every new tool to the menu the same day. [toolkit]

## 9. Delivery and quality
- File sizes with per-frame grain (1080x1920): reel-03, 22.2 s: crf 14 = 65 MB, crf 20 = 33 MB, crf 22 = 25 MB.
  reel-02 paper grain, 45 s: crf 18 = 435 MB, crf 25 = 57 MB. Grain is the size driver. [r02][r03]
- crf 20 vs 22 measured 98.6% vs 98.2% SSIM to the master: invisible on a phone. Instagram re-encodes to about 3 to 5 Mbps,
  so anything above about 9 Mbps doesn't change what followers see. Say this plainly; "Upload at highest quality" in
  Instagram settings matters more. [r03]
- Offer: one file under 30 MiB to post + the higher-quality version in parts. He may want the near-lossless parts (crf 14)
  to join himself: pick split points from cumulative packet sizes so each part is under 30 MiB; tell him to check the
  seams in his joining app. [r03]
- Split procedure (keyframe every second, video-only segment copy, fresh audio per part from WAV, framemd5 + 0 ms checks)
  is in CLAUDE.md. [r02][r03]
- When he asks how to get the video: resend the file card last in the chat and give phone save steps. [r03]
- reel-04 file sizes (32 s, 1080x1920, per-frame grain): crf 14 master 372 MB, crf 22 112 MB, crf 24 72 MB; two-pass
  6.6 Mbps = 27.4 MB, under the 30 MiB send limit, good enough for a phone preview. [r04]
- A 2.5 s 1920x1080 intro at crf 16, keyframe every second, AAC 256k = 1.1 MB: one send, no parts. [r05]
- **Splitting: read the real part lengths before muxing audio (reel-11).** `-f segment -segment_times 12.5,25` on a
  master with sparse keyframes cut at the next keyframes (15.67 and 33.33 s), not at the asked times, so audio cut
  for 12.5 s parts would have drifted. ffprobe each video part's duration first and cut the WAV for those ranges.
  Master render parts each start on a keyframe, so a split there needs no re-encode. 49.9 s master (52 MB) went as
  3 parts of 27.3 / 9.4 / 13.1 MiB, framemd5 identical to the master, audio at 0 ms. [r11]
- Pixel-art reel, 49.9 s 1080x1920 (reel-11): crf 14 master 52 MB; two-pass 4.5 Mbps, keyframe every second, AAC 192k
  = 28 MiB, SSIM 0.992 to the master, one send. [r11]

## 10. Mistakes made (so they never repeat)
- Copied the reference's 0.16 s photo beat literally; the physique deserved 0.7 s. [r03]
- Straight-line kill of background people cut through his hips. [r03]
- MediaPipe-only matte gave a lumpy head; first u2net matte lost the hair above the hand. [r03]
- Missed a gym logo in a flurry frame; "okay?" sat on his beard; caption over the glow. Caught at stills. [r03]
- Fixed word-time pads clipped words; seeking MP4 audio drifted lip sync. [r02]
- Decorative ornaments with no meaning ("Rx", barcode) were removed on request. [r02]
- First automatic vertical layout of the overlays scattered the 4 clocks (V6), reordered "a day in" (V9) and lost the
  REC circle's shape (V12); then the stretched copy of REC showed under the sharp one. Caught by checking the vertical
  contact sheet and a full-size crop before calling it done: always look at every converted asset. [vlog]
- My first wait-for-sign-in loop used `grep -i "logged in"`, which also matches "Not logged in", so it ended at once.
  Match the success text exactly ("Logged in using"). [codex]
- Set up Codex without writing a CLAUDE.md rule, so the next session told him it needed an API key. Write the rule the
  same day as any new tool. [codex]
- reel-04: scaffold `.gitignore` kept scripts and paid audio out of git until noticed; piped a build into `head`
  and killed it; reused a stills folder so old frames confused a check; let x264 pass logs into git. [r04]
- reel-05: a scripted find-and-replace that cut from one marker to the next also deleted a whole function (`streak`)
  and broke a render. After any block replace, grep that the neighbouring functions still exist and render one still.
  Also: two parallel Bash calls run in different working directories (one edit failed with "no such file"); use
  absolute paths. `ffmpeg -ss <last time>` past the final frame gives no frame: use `-sseof -0.04`. First tries at
  filling open line art (closing + hole fill, "outside through wide channels") left stripes open or made bumps; a
  hand-traced polygon fixed it in one go. [r05]
- Mixed units in `openverse_sfx.py`: the hit / swell thresholds compared 10 ms frames against millisecond numbers, so a
  1.6 s riser came out as "swoosh". Caught by testing the measurement on generated sounds of known shape (ffmpeg
  `anoisesrc` + `afade`: a sharp hit, a 0.2 s swoosh, a 1.6 s riser). Always test analysis code on synthetic inputs
  with a known answer before trusting it on real files. The BPM estimate can come out double (hip hop read as 154,
  really about 77): read it as "or half". [openverse]
- reel-07: `cd dir; rm -f out/stills/*` was blocked by the safety check (relative glob after a cd can't be resolved):
  use a fresh folder or absolute paths, never a glob removal after cd. Scene detection on a meme reel found no cuts
  because the static black bands dominate the frame: crop to the video band first. A `git log --grep` with the
  wrong capitalisation returned nothing, so `cherry-pick` got no commit: take the hash from `git log --oneline`.
  Scribe on a music-only clip returns 0 words (costs a few credits): check for speech by ear-level loudness and
  frames first when the clip is a meme. [r07]
- reel-08: used an array (`NOTES`) in a scene block before its `var` declaration (hoisted as undefined, page error);
  declare shared lists at the top. `still.mjs` names explicit times `t_20.jpg` but `--range` names them `t_20.00.jpg`,
  so re-rendering a few times into the grid folder doubled tiles in the contact sheet: render fixes with `--range`
  names or into a fresh folder. The first seawall reveal and the first punch-in (bubble cropped) were caught at the
  stills check, before the user saw them. [r08]
- reanimate setup: patched `setup.sh` with Python `s.replace(old, new)` where `old` came out as an empty string, which
  inserts `new` between every character and wrecked the file. For small files, rewrite the whole file with a heredoc;
  when replacing in Python, `assert old in s and old` first. A frame comparison's auto-align also hid a 0.33 s timing
  error by shifting the clone 15 frames: when both sides start at t = 0, compare with a fixed offset and always read
  the offset the report prints. [reanimate]
- reel-11: a line crossing a split-part boundary came out chopped because part 2's audio pre-roll (negative pts)
  was dropped on decode, part 1's picture was cut early and 5 ms fades dipped mid-word. Check packet pts of every
  part before cutting across a seam (lesson in section 7). [r11]
- reel-11: planned no music under the clip he reacts to (he wanted it from 0:00); an automatic caption chunker left
  orphan words; text and a button over his face on two real photos and the face circle over his arm (caught at my
  stills check). Pushed the session branch HEAD to the default branch with a lessons commit, which carried the
  unfinished reel-11 folder along: push lessons by cherry-picking the lessons commit onto the default branch in a
  temporary worktree (vibe-wrap-up step 5). [r11]
- reel-12: the stills claimed "every beat" but the 27.3 s anger mark was missing (caught later, fixed before v1);
  a chained `cd && mkdir && cd && nohup ... &` backgrounded the whole chain, so the next line ran before the folder
  existed; `sed` with a `\u2713` pattern never matched the literal tick (grep showed 0) and a Python replace on the
  escaped text failed too: find the line with grep -n and replace by line number; `rm -f dir/*` after `cd` was blocked
  again (use explicit file names); an interrupted tool call still wrote its edit, so check and revert after any stop;
  a stale still from an earlier run sneaked into a contact sheet folder again. [r12]
