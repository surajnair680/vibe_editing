# reel-05 brief: Automance logo reveal (channel intro)

- **Purpose:** intro sting for the Automance channel (cars, bikes, road trips).
- **Format:** 16:9, 1920x1080, 30 fps, 2.5 s. Final frame = `refs/automance-logo-final-frame.jpg` exactly
  (scaled to 1080 high, white sides). Checked: last frame matches it pixel for pixel.
- **Story:** night sky, the car drives in from the right going left, the bike from the left going right, they slide
  together and lock into the logo shape, the sun rises, a flash turns the sky white, the scenery draws in, the
  wordmark slams in, the red A lands last, the tagline opens.
- **Theme:** fast, bold, clean. Avoid: busy particles, lens-flare clutter, anything that changes the logo itself.
  Colours come only from the logo (black, white, its red) plus a night navy and a red sunrise glow.

## Beat sheet (edit time)
| time | picture | audio (planned) |
|---|---|---|
| 0.00-0.10 | night sky, twinkling stars, slow camera push begins (1.06 to 1.00 over 2.25 s) | low night air |
| 0.10-0.95 | car in from the right, bike in from the left, white glowing line art with motion blur, easing to a stop | car engine pass right to left, bike rev pass left to right |
| 0.20-0.75 | ground line draws out from the centre | |
| 0.30-0.95 | red sun rises behind the mountains, sky warms red; mountains draw in left to right (0.40-0.90) | |
| 0.95 | car and bike lock together: shake + white flash from the joint | impact hit |
| 0.95-1.04 | sky turns white, line art flips from white to black | |
| 1.00-1.38 | skyline rises from its base, the road draws in both ways | |
| 1.08-1.51 | A U T O M _ N C E slam in left to right (scale down with blur), 0.05 s apart | quick ticks |
| 1.42-1.62 | red A drops in last with a red glow, small shake | metallic hit |
| 1.55-1.95 | tagline lines grow outward, CARS / BIKES / ROAD TRIPS open from the centre | soft swish |
| 1.98-2.30 | thin light glint sweeps across the wordmark | shimmer |
| 2.22-2.50 | settles into the exact logo and holds | tail of the hit |

## Status
- v1 chosen by the user over v2 (2026-11-04); final delivered with sound (mix_v1.py).

## v2 (2026-11-04): rebuilt after the user's 9-frame storyboard (refs/storyboard/)
- 3.0 s, 60 fps. Night landscape (dark hill, skyline, snowy mountains, road with light edges), pink glow, red sun
  rises, bike in from the left (0.78 s), car in from the right (0.98 s), both slow, then cross (car in front) and lock
  into the logo at 1.95 s while the camera pulls back and the world turns white. AUTOMANCE rises in from 2.00 s, red A
  drops last (2.42 s), orange light streak under the word (2.10-2.50), tagline opens from it (2.40-2.72), exact logo
  from 2.84 s. Code: `work/scene2.py`, fills `work/fills.py`, sound `work/mix.py` (assets/sfx/*.mp3, ElevenLabs).
- The bike has no rider: the logo's bike has none, and a rider vanishing at the lock would look wrong.
