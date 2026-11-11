# Lessons learned (the knowledge base that carries across sessions)

Read this whole file before starting any new video, and again before the stills step. Every entry came from a real
edit and cost a revision, a re-render or a question once. Newest videos at the bottom of each section. Tags say where
each lesson came from: [r01] reel-01, [r02] reel-02, [r03] reel-03, [vlog] the mini vlog style study (2026-10-30),
[codex] the Codex CLI setup session (2026-11-01), [r04] reel-04 (cinematic work-session edit, 2026-11-01), [r05] reel-05 (Automance logo intro, 2026-11-04), [openverse] the Openverse sound library setup (2026-11-06), [r06] reel-06 (YouTube Shorts music swap of a finished reel, 2026-11-06), [r07] reel-07 (meme template caption swap, 2026-11-11).

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
- He wants his face visible and recognisable. Pixelating half the face (reference style) works against him; the
  version he chose: start pixelated, resolve to the clear face. [r03]
- He likes to understand why an effect exists ("what is the point of pixelating half the face?"). Explain meaning
  briefly when proposing effects. Explain any decorative element (he had the "Rx" stamp and a barcode removed). [r02][r03]
- He asks "first tell me if you understand" before revisions: restate his note, propose the fix, wait. [r03]
- **When he asks "do you get what I want?", answer that first, in two or three plain lines, before anything else.** On
  the Openverse request I replied with a plan, a network blocker and a domain list; he came back with "At least tell me
  if you understood what I want." Restate the goal in his terms, then (separately, or after he confirms) the blockers
  and plan. [openverse]
- He shares other creators' reels (pasted transcripts) about AI tools and means "add this to my system". Build it as a
  shared tool + CLAUDE.md rule + skill line, so every session has it. [openverse]
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

## 6. Text and captions
- Captions sit on a handheld mic at about 1440 px; ask about caption height at the stills step when he holds a mic. [r01][r02]
- Keep text off his face and beard: move the picture (crop) rather than the text when a centred word lands on the face. [r03]
- A caption over the brightest glow is hard to read: move the picture so the glow sits below the caption line, and give
  captions over footage a soft dark halo. [r03]

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

