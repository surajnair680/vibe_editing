# Design rules

## Fonts (in `assets/fonts/`)
| role | font | size at 1080 wide | notes |
|---|---|---|---|
| Title, main words | Inter ExtraBold (800) | 84 to 100 px | tight tracking, -0.045em; line height 0.95 |
| Title accent word | Instrument Serif Italic | 1.05 to 1.15 x the title size | one word or short phrase per title |
| Caption | Inter Bold (700) | 52 to 58 px | tracking -0.03em; white on dark and on footage, near-black #111 on light |
| Caption, named term | Instrument Serif Italic | 60 to 70 px | only for the framework name and the CTA keyword |
| Small labels, pills, UI | Inter SemiBold (600) | 24 to 34 px | |
| Big numbers | Inter Black (900) | 160 to 260 px | "6 topics": number 2 to 3 x the word next to it |

## The title (two lines, max about 7 words)
- Line 1 sets context, line 2 carries the point. The key phrase sits on line 2.
- Four accent treatments (pick one per title):
  1. **Serif accent word**: one word in Instrument Serif Italic ("How To Create a *Killer* Hook").
  2. **Red underline**: a 5 px #A5000A bar under line 2, starting a little inside its left edge and ending a little
     inside its right edge ("Social Media Forever").
  3. **Red box**: line 2 in white on a #8D0003 box, 8 px corner radius, padding 6 px 22 px ("To Get The Doc",
     "YOUR CONTENT"). Can hold serif italic inside ("*The Full Breakdown*").
  4. **Size contrast**: small line + huge heavy line ("Ask interesting / QUESTION").
- White on dark, #111 on light.

## Colour
- **One accent: red.** Box #8D0003, lines and underlines #A5000A, glows #E0102A at 40% with blur. Red marks the one focus
  thing in the scene: the active step, the drop in a chart, the word that matters. Never more than one red focus at a
  time.
- Greys for everything else: cards #111 to #161616 on dark (1 px border #2A2A2A), #FFFFFF cards on light with a soft
  shadow (0 12px 40px rgba(0,0,0,.12)).
- Meaning colours, only inside diagrams: green #22C55E = good / works / validated; yellow #F5C518 = middle step;
  magenta #D946EF = body / extra layer. Keep a colour tied to one meaning for the whole video (reel 17: red = hook
  loop, yellow = intensifier, green = rehook).
- Brand colours of a real product are allowed inside its own logo scene (Claude orange, Sandcastles blue).

## Shapes
- Rounded everything. Cards and windows 16 to 24 px radius; device frames as real devices; pills fully round; logo
  tiles 22% radius.
- Thin strokes: 1 to 2 px lines, dashed lines 6 px dash / 6 px gap.
- Circles for avatars and user icons. Rounded rectangles for lists and options. Pills for labels and emphasis.
- Glow, not drop shadow, on dark: white or red outer glow, 20 to 40 px blur, 20 to 35% opacity.
- Upcoming items are blurred (6 to 10 px) and dimmed to 40%, not hidden. The viewer sees there is more to come.

## Real assets
- Use real thumbnails, real screenshots, real UI, real logos. They are the credibility. Rounded corners and a thin
  white border on every screenshot.
- Every number on screen comes from the user or a source shown to them.

## Text amount
- Title max about 7 words. Pills max 4 words. A scene has one title, one graphic and one caption word. If it needs more,
  it is two scenes.
