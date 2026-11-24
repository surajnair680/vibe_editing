---
name: photo-parallax
description: Vox-style parallax (2.5D) camera moves that make a still photo feel like video. The photo is split into foreground, midground and background layers by a local depth model, the areas each layer hid are patched, the layers are spaced in depth and a slow camera dolly or pan moves through them. Use when the user wants a photo, archive or historical image, Codex/AI still, physique photo or screenshot to "move", "look like a video", "come alive", a "Vox parallax", "2.5D", "3D photo", "Ken Burns but better", "depth effect", or a documentary-style still with motion; also whenever an edit needs B-roll from stills. Works inside any other skill's edit (vox-explainer, talking head, lemo, mini vlog).
---

# Photo parallax (the Vox "images that look like videos" trick)

Learned 2026-11-24 from the reel the user shared, "How Vox makes images look like videos" (37 s, 720x1280).
Breakdown and transcript: `reference/`. The tool: `tools/parallax.py` (shared, tested). Example: `example/`.

## What the reference teaches
1. A flat zoom on a photo feels "like an iMovie slideshow". Parallax (near things slide more than far things) is what
   makes a still feel filmed. Vox uses it on historical photos.
2. Pick an image with **plenty of depth**: a clear foreground, midground and background (rocks / cable car /
   mountains in the reel). Flat images (a wall, a face filling the frame) don't work; say so and suggest another.
3. Separate the elements into their own layers (Photoshop in the reel).
4. **Patch the areas hidden behind each layer** (clone stamp in the reel), or gaps open up when the layers slide.
5. Space the layers out in 3D (the free After Effects plugin "Depth" does it in one click: focal 50 mm, layer spacing
   1000) and **slowly** dolly or pan the camera. Slow is the point: the move is felt more than seen.
6. Look of the reel itself (useful for Vox-style edits): serif handwritten-feel labels with hand-drawn arrows
   ("foreground", "midground", "background"), red highlight boxes behind key words ("Animation", "effect", "bad"),
   small bold uppercase captions at the bottom. The `vox-explainer` skill has the torn-paper side of that look.

## How we do it here (all code, no After Effects)
```bash
# 1. layers: depth map -> N layers, crisp subject, hidden areas painted by Codex (about 1 minute per photo)
python3 tools/parallax.py layers projects/<name>/assets/photo.jpg -o projects/<name>/work/parallax/photo --n 4 --subject \
    --plate codex --remove "the bodybuilder and the wooden bench"
#    no Codex sign-in, or a quick draft: leave out --plate and --remove (code patch, 3 to 8 s)
#    look at work/parallax/photo/split.png (layers tinted + each layer on a checkerboard) before rendering
# 2. stills for the stills-first rule (frame times in seconds)
python3 tools/parallax.py stills projects/<name>/work/parallax/photo -o projects/<name>/out/photo_stills.png --move dolly-in --dur 6 --times 0,3,6
# 3. render the move (1080x1920 30 fps by default; about 30 s for a 6 s shot on 4 cores)
python3 tools/parallax.py render projects/<name>/work/parallax/photo -o projects/<name>/out/photo.mp4 --move dolly-in --dur 6
```
- Moves: `dolly-in` (default), `dolly-out`, `pan-left`, `pan-right`, `rise`, `fall`, `drift` (slow push + slide).
  Fine control: `--dolly 0.2` (camera travel as a fraction of the front layer's distance, minus = out), `--pan-x 0.04`,
  `--pan-y`, `--strength 0.6` to calm any preset, `--ease inout|linear|in|out`, `--blur-back 2` for a touch of depth of
  field. The original framing shows at the start of a dolly-in, the end of a dolly-out and the middle of a pan; the
  tool computes the extra zoom so layer edges never enter the frame (about 3 to 5 % for pans).
- Layers: `--n 3` or `4` (5 at most). `--subject` cuts the main subject with rembg isnet and gives it its own layer,
  placed in front of the ground it stands on (ranked by its feet). Wrong split? Move the cuts with `--cuts 0.3,0.65`
  (0..1 nearness, read `depth.png`), paint masks and pass `--masks front.png,mid.png` (white = layer, front first),
  or give a clean background yourself with `--plate plate.jpg`.
- `--spread 1.5` exaggerates depth spacing, `0.7` flattens it. `--band` (default 0.10) is how far each layer's
  patched texture reaches under the nearer one; raise it for big moves if a seam shows.

## Codex paints the hidden areas (default, user rule 2026-11-24: "You have codex image generation don't forget")
- `--plate codex --remove "<everything in front of the far background>"` sends the photo to Codex (`codex exec ... -i`,
  the user's ChatGPT sign-in) with a prompt to remove those things and their shadows and fill in what was behind them,
  same framing and size. The plate fills every layer's hidden area, so name all the near things (subject + foreground
  objects), not only the subject. Files: `plate.png` (Codex), `plate_aligned.jpg`, `codex_plate.log`.
- Tested on the beach example: Codex kept the framing pixel for pixel (ECC alignment found a 0.1 px shift), removed
  the bodybuilder, the bench and the man's shadow, and painted real sand and crowd. A pan 60 % stronger than the default
  showed no seams. Example: `example/codex_plate.jpg`, `example/split_codex_plate.jpg`.
- The tool still aligns (ECC affine) and colour-matches the plate on the shared area, in case Codex shifts or re-tones it.
  Check `plate_aligned.jpg` against the photo: if Codex moved or redrew things that should stay, run it again or drop
  back to the code patch. Your own retouched plate also works: `--plate my_plate.jpg`.
- Codex in the photo editing itself is also how to get photos with depth for parallax: ask for "clear foreground,
  middle ground and background" (see `example/README.md`).

## Numbers that worked (tested on example/beach.jpg and the reel's cable car frame)
- Depth model: Depth Anything V2 small, ONNX, CPU, 518x518 input. File `~/.cache/vibe/depth/depth_anything_v2_vits.onnx`
  (99 MB) from GitHub releases (fabio-sim/Depth-Anything-ONNX v2.0.0). Hugging Face is blocked here (403), GitHub works.
  The start-up hook downloads it plus rembg's isnet-general-use in the background (`~/.cache/vibe/parallax.ok`).
- The depth model alone often puts a subject and the ground at the same distance (it lumped the cable car in with the
  rocks). Use `--subject` whenever there is one clear subject.
- Default moves over 6 s: dolly-in 0.22 (front layer grows about 28 %, back about 5 %), pans 0.05 of the frame width.
  That reads clearly on a phone and stays calm. Halve it (`--strength 0.5`) for 3 s shots or busy edits.
- Code patch fill (no Codex): smooth colour (Telea at the rim, push-pull inside) plus real texture mirrored from the hole's edge
  (the clone-stamp stand-in), faded to matched grain deep inside. Only the edge band ever shows during a slow move,
  so deep-inside blur behind a person is fine. Old prints have dark borders: the fill ignores a 2 % edge strip.

## House rules
- Work in `projects/<name>/work/parallax/<shot>/`, renders in `out/`. Stills first (contact sheet + split.png when
  layers are new), wait for his OK, then render.
- His physique photos and his face stay real and unfiltered (CLAUDE.md lessons): parallax is fine on them (it only
  moves the camera), but check the cut-out at full size: hands, hair, fingers between the hips and arms. A bad edge on
  his body is worse than no effect; fall back to a plain slow zoom if the matte isn't right.
- Every physique shot shows his face too, and gets at least 0.6 to 0.7 s of clear, readable view.
- Sound: a soft air whoosh or room tone under a parallax shot, Openverse first, peak on the move's start if it begins
  on a cut. Never a big whoosh on a slow drift.
- Photo sources: his own photos, Codex stills (`codex exec ... Generate an image ...`, ask for "clear foreground,
  middle ground and background" in the prompt, as in `example/`), or archive photos with a licence that allows use.
