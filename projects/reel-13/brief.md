# Brief: reel-13 (Bulking series, episode 0)

## The job
- Instagram Reel, 9:16 1080x1920, 30 fps, 53.7 s (rough cut v2, approved).
- Goal: viewers meet the series ("bulk until I look like Toji") and believe a normal guy can do it, so they follow.
- Look: **edit-like-kallawaymarketing** (picked by the user 2026-11-28). Dark dotted ground, title in the top third
  with one serif accent word, one graphic per line, him in a rounded bottom strip with his head popping out,
  one-word captions, full-screen beats in between. Hard cuts only.
- Voice: his own (ElevenLabs isolated, `assets/el/voice_isolated.mp3`). Captions: one word, Inter Bold.
- Music: low dark bed from 0:00, ducked about 18 dB under the voice. Openverse SFX per the cue sheet.

## Planning doc (draft v1, waiting for approval)
Times are rough cut v2 edit times. SPLIT = graphic on top, him in the strip. FULL = him full screen.

| # | time | spoken | layout | type | on screen |
|---|---|---|---|---|---|
| 1 | 0.00-2.90 | "I am going to bulk until I look like an anime villain." | SPLIT | 2 word-by-word hook | Two assets only (user, 2026-11-28). Title builds per word: "Bulking until I look like / an *anime villain*". Under it: his photo or clip until "look like", hard cut to Toji on "anime villain", red glow on "villain". |
| 2 | 2.90-4.70 | "This is Toji Fushiguro." | SPLIT | 8 annotated example | Title "This is *Toji Fushiguro*". Toji image card in the centre, slow push in. |
| 3 | 4.70-9.57 | "Wide back, arms like carved stone, and a V-taper so sharp it looks fake." | SPLIT | 8 annotated example | Same card. Red arrows and labels pop on each phrase: "Wide back", "Arms like stone", "V-taper". "Looks fake" in a red box. |
| 4 | 9.57-13.00 | "But whenever I tell people they can build a body like this," | FULL | 21 | Snap back. One-word captions. |
| 5 | 13.00-19.80 | "I hear the same three excuses. I don't have the genetics. I don't have the time. It's not possible naturally." | SPLIT | 5a tracker + visuals | Title "The *3 Excuses*", pills in a compact row under it (red tab on the current one). One big visual per excuse, hard cut on its line (user asked for visuals, 2026-11-28): glowing DNA strand that turns red and cracks, clock with spinning hands, syringe with a question mark. Glossy 3D on black with red light (Codex). |
| 6 | 19.80-20.80 | "So I am going to show you" | SPLIT | 5a | The three visuals shrink into a row (0.2 s), then a red slash hits each about 0.25 s apart on "going", "show", "you", marker sound each. Syringe + glossy 3D approved 2026-11-28. |
| 7 | 20.80-22.43 | "what is possible" | FULL | 21 | Caption "possible" in serif. |
| 8 | 22.43-24.97 | "This is me after seven years of training." | SPLIT | 8 annotated example | Title "*7 years* of training". His physique photo (face showing) with a slow parallax push. |
| 9 | 24.97-27.67 | "Decent, but I'm not a genetic freak." | FULL | 21 | Honest beat, his face. |
| 10 | 27.67-32.50 | "I am twenty-seven. I work full time in tech, and I'm also a fitness coach." | SPLIT | 18 stacked pills | Title "Just a *normal* guy". Pills drop in on the words: "27 years old", "Full-time tech job", "Fitness coach". |
| 11 | 32.50-36.20 | "And I have been a type one diabetic since I was twelve." | SPLIT | 10 big number | Pills grey out. Big red card: "Type 1 diabetic" with "since age *12*", a simple glucose meter drawing. |
| 12 | 36.20-38.50 | "If I can build this body, so can you." | FULL | 21 | Caption "so can you." in serif. |
| 13a | 38.50-40.77 | "I'm already two months into this bulk," | SPLIT | 16 line path | Title "The *bulk* so far". A timeline line: Day 1 to a red dot at "Day 60, today". |
| 13b | 40.77-41.87 | "but from today," | FULL | 21 | Turn beat (keeps every graphics run under about 10 s, skill rhythm rule). |
| 13c | 41.87-43.27 | "I'm filming all of it." | SPLIT | 16 line path | Back on the timeline; a red REC badge blinks on the Day 60 dot. |
| 14 | 43.27-45.53 | "Training, food, supplements" | SPLIT | 18 carousel | One card per word: training, food, supplements. Real photos. |
| 15 | 45.53-47.80 | "The wins and the days it goes wrong." | SPLIT | 9 before / after | Two cards: "*Wins*" (green) and "*Bad days*" (red). |
| 16 | 47.80-50.60 | "How long will it take? Six months? A year?" | SPLIT | 16 line path | Back to the timeline. The line runs on past today: "6 months?" then "1 year?" tags pop. |
| 17 | 50.60-51.30 | "I don't know," | FULL | 21 | Shrug beat. |
| 18 | 51.30-53.67 | "but I'm not stopping until I look like him" | SPLIT | 9 side by side | Title "Until I look like *him*". Him now on the left, Toji on the right. Ends here. |

Screen time: SPLIT 78 %, FULL 22 %. Longest graphics run 9.6 s. Visual planning table with a Kallaway reference frame per row: https://claude.ai/artifact/PoALZah5AsG68BxrEo3stx (`work/plan/build_plan_page.py`).

## Open questions
- Ending: the script has no call to action. Default: end on row 18. Option: a 1.5 s silent card "Follow for *episode 1*".
- Caption height: he holds the mic at chest height; in SPLIT the caption sits above the strip so it is clear,
  in FULL it sits around y 1165, which may hit the mic. Check at the stills step.

## Assets needed
| row | asset | source |
|---|---|---|
| 1, 2, 3, 18 | 2 or 3 Toji images (one for the hook, can be a clip) (full body or back, clear muscles) | user (real anime frames; Codex can't draw him reliably) |
| 1 | a photo or clip of him for the hook | user |
| 5, 6 | DNA strand, clock, syringe (glossy 3D, red light, black) | Codex |
| 8, 18 | his physique photo with his face | user |
| 14 | a training clip or photo | user (else Codex) |
| 14 | a meal photo | user (else Codex) |
| 14 | his supplements | user (else Codex) |

## Cue sheet (draft)
| time | event | sound | level |
|---|---|---|---|
| 0.0-2.9 | hook word swaps | soft ticks | -22 dB |
| 2.9 | Toji card in | soft pop | -20 dB |
| 4.7, 5.5, 7.3 | labels pop, arrows draw | pop + faint sweep | -20 / -26 dB |
| 9.57, 20.8, 24.97, 36.2, 50.6 | cut to FULL | low thud on big words only | -16 dB |
| 13.0-18.2 | each pill lights | swish (different file each time) | -18 dB |
| 19.8-20.8 | red strike-throughs | marker squeak | -22 dB |
| 27.7-32.5 | pills drop | soft pops | -20 dB |
| 32.5 | big red card | soft hit | -18 dB |
| 38.5 | timeline draws | faint sweep | -26 dB |
| 43.3, 44.1, 44.7 | carousel slides | short whooshes, all different | -18 dB |
| 51.3 | side by side in | rise into a soft hit | -16 dB |
| 0.0-53.7 | music | low dark bed, ducked 18 dB under voice | |

## Sign-off checklist
- [ ] planning doc approved
- [ ] assets in
- [ ] stills approved (contact sheet)
