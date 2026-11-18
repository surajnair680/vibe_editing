# reel-11 brief: "What's so inspiring about her?"

**Idea.** A village woman's sincere "stop chasing perfection, just start speaking" English clip plays first. Then Suraj,
deadpan: "I don't understand what is so inspiring about her", and he argues *for* waiting for perfection, applied to
fitness. The sarcasm makes her point for her. Ends on an ironic follow CTA over his real training footage.

- Platform: Instagram Reel, 9:16 1080x1920, 30 fps. Length about 48 to 50 s (cut approved as rough v2, 48.4 s).
- Look: **Lemo-Opuscar 16-bit Pixel RPG** for everything made (world, windows, menus, counters, sprites, icons).
  Native 216x384 grid scaled x5 nearest-neighbour, ENDESGA-style indexed palette, Bayer dither, no alpha fades.
- **Real assets stay real** (user rule for this reel): Tiger Shroff photo, his gym B-roll, his physique photos and his
  face video are never pixelated or recoloured. Pixel art only frames them (borders, windows).
- **His face is visible the whole time:** real video, his head breaking out above a pixel-stepped circle (gold ring,
  warm dithered fill). The circle may move and change size per beat.
- Captions: the RPG dialog box is the subtitle, at the top under the 250 px safe zone, Press Start 2P 8 px native,
  white with the spoken word in gold, typed in sync with the voice.
- Her clip: plays as it is, full screen, burned-in captions kept.
- Waistband logo on the mirror photo: leave as it is (user). Phone in the mirror photo: keep.

## Assets
| File | Use |
|---|---|
| work/her_full.mp4 (from raw/her_part1..4) | opening, as it is |
| raw/me_2, me_3a..d | his talking video (face circle / full screen) |
| assets/photos/celebrity_tiger.jpg (495x619) | "favorite celebrity", framed card about 70 % width |
| assets/photos/me_gym_dumbbell.jpg, me_physique_mirror.jpg | payoff, clean |
| raw/gym_01 (bench press low angle, clean 0 to 5.5 s), gym_02 (incline press side, crop Cloud 9 sign), gym_03 (wide, kick-up at 4 to 7 s) | payoff, clean |

## Beat sheet (edit times from rough v2)
| # | Edit time | Spoken line | Picture | Face | Audio cue |
|---|---|---|---|---|---|
| 1 | 0.00 to 12.87 | Her: "Stop chasing perfection... courage to speak." | her clip as it is | (her clip already shows his cutout) | original |
| 2 | 12.87 to 15.63 | "I don't understand what is so inspiring about her." | her last frame mosaics into a PAUSE screen (0.3 s), cut to him **full screen**, slow push-in | full screen | pause blip, game music stops |
| 3 | 15.63 to 17.9 | "Let's say you want to look like your favorite celebrity." | pixel world opens (mosaic in). QUEST window types "NEW QUEST: look like your favorite celebrity". On "celebrity" (17.31) the **Tiger photo** pops in, clean, in a pixel portrait frame | circle bottom right | quest jingle, chiptune bed starts |
| 4 | 17.9 to 21.1 | "Therefore, you should procrastinate for six months" | wall calendar pages fly off Jan to Jun ("six months" 20.05), DAY counter races 1 to 183, hero sprite idle | circle bottom right | page flips, counter ticks |
| 5 | 21.1 to 25.9 | "overthinking whether keto, intermittent fasting, or push-pull legs is the perfect plan." | CHOOSE PLAN menu, cursor jumps on each word (22.03 / 22.55 / 24.0), never selects; "perfect plan" (25.17): bar "FINDING PERFECT PLAN 99 %" stuck | circle bottom right (**sample frame**) | cursor blips, error buzz on 99 % |
| 6 | 26.1 to 29.4 | "But why start now when you can wait for next Monday" | SAVE GAME? window: "START NOW / WAIT FOR NEXT MONDAY", cursor picks Monday (27.99), "GAME SAVED. CONTINUE: MONDAY" | circle bottom left | save ticks |
| 7 | 29.05 to 31.0 | "while sitting on your ass gaining fat" | hero sprite slumps on a pixel couch with chips, "BODY FAT +1" pops (30.16), stat bar fills, 3-2-1 px shake | circle bottom left | munch, stat-up blip |
| 8 | 31.25 to 35.37 | "so that you can successfully protect a physique you are unhappy with anyway." | item fanfare on "protect" (31.87): shield icon, "YOU OBTAINED: COMFORT ZONE. DEF +99"; on "unhappy" (33.89) status screen "PHYSIQUE: UNHAPPY", hero sprite only (never his real body here) | circle bottom right | item-get fanfare |
| 9 | 35.53 to 38.1 | "Just ignore this lady" | her clip returns in a small pixel window, "LADY: stop chasing perfection", choice [LISTEN] [SKIP], cursor picks SKIP, window mosaics out | circle bottom right | select blip, window close |
| 10 | 38.1 to 41.0 | "and whatever you do, do not share this video with that one friend" | "SHARE?" prompt, cursor on NO; a second sprite (the friend) walks in on "that one friend" (39.45) | circle bottom left | blips |
| 11 | 41.07 to 44.9 | "who has been starting their fitness journey next Monday since 2020." | friend's quest log "FITNESS JOURNEY: STARTS NEXT MONDAY"; year counter flips 2020 to 2026 on "since 2020" (43.57); "STATUS: NOT STARTED" | circle bottom left | counter ticks, sad jingle |
| 12 | 45.17 to end | "And follow me to learn how to skip the gym and stay stuck forever." | the pixel world glitches and breaks away to **real** footage, full screen: gym_03 kick-up, gym_02 press, gym_01 low angle, mirror physique photo (at least 0.7 s clear each); end card: pixel FOLLOW button over the physique photo, about 1.5 s tail after the voice | small circle top corner, then off for the physique hold | glitch hit, chiptune drops out, real whoosh on each cut |

Sound: style-native chiptune blips (code-made) for UI, real recorded whooshes and hits (Openverse) on the big
transitions (beat 2, 3, 12), a light code-made chiptune bed ducked about 8 dB under the voice. Final -14 LUFS.

## Needs a test before building
- Head-pop matte on every frame of his talking footage (about 33 s, rembg u2net_human_seg per frame, cached).
- The pixel world break-out into real footage at 45.17.
