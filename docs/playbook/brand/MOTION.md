# MOTION.md: Suraj Nair

Read this in full before designing, generating or animating anything. Every colour, font, timing and motion value comes
from here. The file sets the look, not the ambition: when he says go all out, go all out. If something is not covered,
ask him rather than choosing. When done, check your own frames against this file, fix what fails, then show him.

Written 2026-11-24 from his words ("a darker, grainier tone makes the video look important") and five frames of the
reference reel he approved for reel-14 (`examples/`). The frames hold three looks: black, deep red and a light grey
section. **Master look: dark and grainy (black and deep red).** Light grey is only a short contrast section.

## 1. Colours
| Hex | Name | Use |
|---|---|---|
| `#050505` | black | The darkest ground. Openings, serious lines, behind footage |
| `#1C0202` | blood black | Edges of every red frame (vignette end) |
| `#4A0005` | deep red | Centre of red frames, darker than the reference (`#5C0006`) because he wants it darker |
| `#9E1A2B` | title red | Red title words and one key word per line. Never a big fill |
| `#880003` | circle red | Solid shapes: circles, bars, a struck letter |
| `#EDE7E1` | bone | Titles on dark |
| `#E8E2DC` | ash | Captions and body text on dark |
| `#D4D4D4` | light grey | The contrast section ground only, with `#111111` text |

No other colours on graphics. Real photos and footage keep their own colours (never tinted red).

## 2. Type
- Titles: **Bebas Neue**, upper case, tight tracking, 120 to 220 px on a 1080x1920 frame. One or two lines.
- Captions: **Inter** 500 to 600, sentence case, 44 to 56 px, left aligned in a block of 2 to 3 lines.
- Labels and numbers: Inter 600, or JetBrains Mono 700 for data.
- No em dashes, no decorative symbols.

## 3. Timing
- In: titles assemble over about 0.6 s (letters fade in scattered, or a short rise with a soft ease-out).
- Hold: **at least 0.8 s for anything on screen, titles 1 to 3 s.** A viewer must be able to read and follow.
- Out: a cut or a 0.2 s fade. Captions build word by word with the voice and stay until the sentence ends.
- Rhythm: calm, weighty. Slower than a hype edit, faster than a documentary. Cuts land on the beat or the word.

## 4. Movement
- 30 fps. Slow camera drift (2 to 4 % push over a shot), slow drifting hairlines and circles in the background.
- Easing: soft ease-out on arrivals, never bouncy, never elastic.
- Depth: light glow behind red title words (subtle, never neon), cards with soft shadows.
- One movement idea per shot.

## 5. Texture and finish
- **Heavy film grain on every frame**, visible on a phone: about 2x the house default (`motion_kit` grain, or a
  grain overlay at 0.2 to 0.3 overlay alpha in HTML), changing every frame. Grain makes files big: check size early.
- Strong vignette to blood black at the edges, crushed blacks, no pure white (bone is the lightest graphic colour).
- Thin hairlines (1 to 2 px, 10 to 20 % alpha) and large faint circles drifting in red frames.
- Optional light frame edge darkening. No lens flares, no light leaks in colour.

## 6. Never
1. Nothing on screen so briefly the viewer can't follow it (his v1 note: "like a stun grenade").
2. No bright, clean or cheerful looks: no white backgrounds, no pastel, no flat corporate gradients.
3. No filter or colour wash over his face, physique, his footage or real photos.
4. No graphics over his face or physique, and no physique shot without his face.
5. No bouncing, elastic or typewriter text, no emoji, no meaningless ornaments.

## 7. Done right, shot by shot (example, 6 s)
1. 0.0 to 1.5 s. Black `#050505`, heavy grain. His photo, unfiltered, fades up from black on the left. Bone caption
   block builds word by word on the right: "Normal people".
2. 1.5 to 3.5 s. Cut to a deep red frame (`#4A0005` to `#1C0202`), hairlines drifting. Title assembles over 0.6 s in
   Bebas Neue bone, last word in title red with a soft glow: "DON'T BUILD THIS". Holds 1.4 s.
3. 3.5 to 6.0 s. Cut to the light grey section with circle-red circles. One circle slides in on a soft ease-out, black
   Inter text next to it: "Outliers do." Holds 1.5 s, then a 0.2 s fade to black.

## Ask me
- His logo and any offer or link (none yet).
- Whether the light grey section is welcome in every video or only when the reference calls for it.
