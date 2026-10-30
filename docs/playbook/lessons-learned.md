# Lessons learned (the knowledge base that carries across sessions)

Read this whole file before starting any new video, and again before the stills step. Every entry came from a real
edit and cost a revision, a re-render or a question once. Newest videos at the bottom of each section. Tags say where
each lesson came from: [r01] reel-01, [r02] reel-02, [r03] reel-03, [vlog] the mini vlog style study (2026-10-30).

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
- Plain human language, no em dashes, short messages. [all]

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

## 8. Workflow and process
- Stills first, every time (contact sheet every 2.5 s + full-size changed frames), plus a short low-res draft clip when
  timing matters. For reel-03 the user approved from stills + a 2.6 s draft of the changed range. [all]
- Style the key moments first (hook word, flurry, the special effect, the punch word), send stills + a short motion
  sample, then style the rest. [r03]
- **Look at every still yourself before sending** and fix what you see (logo in frame, text on the beard, caption over
  glow, hard edges). Then list the remaining doubts for the user with times. [r03]
- Test a complex effect on the user's actual asset early (the light-snap test on his back photo) and send it. [r03]
- One ffmpeg input per cut piece; long `trim` chains get killed for memory. [r02]
- ffmpeg `fps=2` contact sheets can show frames about 0.25 s off their labels. For exact checks pull frames by number
  (`select=eq(n\,N)`) and compare to the renderer. [r03]
- Revisions: save the current master (`master_vN.mp4`), render only the changed whole seconds, splice into the previous
  master, re-encode, then SSIM per frame against the previous version: list the changed ranges and the minimum SSIM
  outside them (reel-03: >= 0.984 is just re-encode noise). [r01][r03]
- Keep a revision log `work/revisions.md` and `RENDER.md` with rebuild steps in every project. [all]

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

## 10. Mistakes made (so they never repeat)
- Copied the reference's 0.16 s photo beat literally; the physique deserved 0.7 s. [r03]
- Straight-line kill of background people cut through his hips. [r03]
- MediaPipe-only matte gave a lumpy head; first u2net matte lost the hair above the hand. [r03]
- Missed a gym logo in a flurry frame; "okay?" sat on his beard; caption over the glow. Caught at stills. [r03]
- Fixed word-time pads clipped words; seeking MP4 audio drifted lip sync. [r02]
- Decorative ornaments with no meaning ("Rx", barcode) were removed on request. [r02]
