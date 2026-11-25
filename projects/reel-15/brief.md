# reel-15 brief: ZAZI coat season promo

Status: beat sheet waiting for approval (2026-11-25). Nothing built yet.

## The job
- Client: ZAZI (theworldofzazi.com), artisanal luxury fashion, Amsterdam boutique at Herengracht 394.
  Handmade embroidered coats with shearling collars, co-created with women artisans (Saheli Women, India).
- Goal: promo for the coats ("it's coat season", limited drops every month).
- Format: 16:9, 1920x1080, 25 fps, about 25 s. Music only, no voice. On-screen text in English.
- Footage: none yet. Built from the site's own photos (`refs/site/img/`). Client clips can replace beats later.

## Brand vibe (the rule for every choice)
- Feeling words: **warm, crafted, unhurried.** Quiet luxury, feminine, earthy, human.
- Colours from the site: cream #FBF8F4 (background), ink #262428 (text), rust #732706 (one accent), gold logo.
  Product photos keep their real colours: no grade, no filter, no grain on the coats. The coats are the product.
- Type from the site: Tenor Sans, uppercase, wide tracking (headings); Outfit Light (small lines).
  Few words, small and centred, never bold.
- Motion: slow eases, soft dissolves and masked wipes, slow parallax on photos. Cuts land on the music.
- Avoid: fast cuts, snap zooms, glitch, flashes, whooshes, bold sans captions, heavy grain, dark moody looks
  (that is the user's own brand, not ZAZI's), prices on screen (luxury promos rarely show them; prices also change).

## Assets
| id | file | use |
|---|---|---|
| hero | omslag_zazi_dominique.jpg (2000x1135, wide) | model in an embroidered coat, red door |
| hang | 33coats.jpg (portrait) | coat hanging in a doorway |
| spin | KullviWhims_ZAZI_by_JanneHoevelaken74.jpg (portrait) | artisan spinning wool |
| pair | Our_story_0002_...jpg (square) | two artisans at a window |
| zebay F/B | Correct_0017 / Correct_0024 | Zebay coat front / back |
| madina-brown F/B | Correct_0028 / Correct_0029 | Madina coat, brown collar |
| madina-navy F/B | Correct_0001 / Correct_0034 | Madina coat, navy and gold |
| madina-red F/B | Correct_0049 / Correct_0048 | Madina coat, burgundy |
| shop | ZAZI_Boutique_by_JanneHoevelaken14.jpg (portrait) | the boutique rail |
| logo | zazi_golden.png | gold ZAZI wordmark |

Portrait photos in a wide frame: either sit them in a frame on cream, or extend them to 16:9 with Codex
(outpainting: only walls and floor are added, the coat and people stay untouched). Decide at the styled frame.

## Beat sheet (times are a plan; they snap to the music's bars once the track exists)
| # | edit time | picture | text | tool | audio |
|---|---|---|---|---|---|
| 1 | 0.0-4.0 | hero, full frame, slow parallax push toward the model | "FALL / WINTER '26" small, then "IT'S COAT SEASON" letters fade in softly | photo-parallax, type in code | music in from 0:00, soft fabric rustle |
| 2 | 4.0-6.5 | hang, coat in the doorway, slow drift | "HANDMADE. ONE OF A KIND." | photo-parallax (+ Codex outpaint) | soft dissolve, no hit |
| 3 | 6.5-9.0 | spin, artisan spinning wool | "FROM HER HANDS" | photo-parallax | quiet |
| 4 | 9.0-11.5 | pair, two artisans at the window | "TO YOURS" | photo-parallax | quiet |
| 5 | 11.5-19.5 | the coat run on the pink studio background, 4 coats x 2 s: front, then the back wipes in like the coat turns | coat name small under each: "ZEBAY", "MADINA" | masked image reveal (motion-effects), studio background extended in code | a soft cloth swish on each turn, landing on the beat |
| 6 | 19.5-22.0 | shop, the boutique rail with the chandelier, slow push | "VISIT US · HERENGRACHT 394, AMSTERDAM" | photo-parallax (+ Codex outpaint) | room tone fades in under the music |
| 7 | 22.0-25.0 | cream screen, gold ZAZI logo reveals (light passes across the gold) | "LIMITED DROPS EVERY MONTH" then "theworldofzazi.com" | logo reveal (reel-05 recipe) | soft shimmer on the logo, music resolves |

## Music
- ElevenLabs `/v1/music`, about 27 s, no vocals: warm and elegant, soft strings, plucked acoustic or harp, a gentle
  hand drum, around 80 to 90 BPM, a small lift at the coat run and a resolve on the logo. Two options, the user picks.
  Then map its bars and snap the cuts to them.

## Sound design
- Openverse first: fabric / cloth swish (coat turns), soft room tone (boutique), a light shimmer or chime (logo).
  All subtle; no whooshes, no hits.

## Still needed
- Client video (optional): model walking or turning in a coat, hands embroidering, the boutique rail, embroidery
  close-ups. Horizontal.
