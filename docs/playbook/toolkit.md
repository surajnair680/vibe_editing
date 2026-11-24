# Toolkit menu (read at the start of EVERY video, before the summary and again before the beat sheet)

Everything this repo can do, by what a moment in the video needs. Raw footage does not mean "talking head only":
for every beat, look down this list and ask "would one of these make this moment better?". Then offer the user the
best 3 to 5 ideas in the first summary, each tied to a time or line, and give every beat in the beat sheet a "tool"
column. He has had to name tools himself before ("you were not even aware that you had lemo opuscar"); this page
exists so that never happens again.

When a new skill, tool, kit or proven recipe is added to the repo, add a line here the same day (CLAUDE.md rule).

## The edit itself (pick one main playbook)
| Footage / ask | Skill |
|---|---|
| Him talking to camera, reply or reaction reels, podcasts, tutorials | `vibe-talking-head` (cuts, captions, punch-ins, B-roll) |
| Vlog, day in my life, travel, camcorder REC look | `vibe-mini-vlog` (overlay pack, vertical) |
| AI clips (Veo, Sora, Kling, Flow) or a faceless video | `vibe-ai-footage` |
| Promo, launch, course, ad with variants | `vibe-launch-ads`, `launch-video` |
| Many versions from one template, every format | `vibe-bulk-videos` |
| Music-led, audiogram, lyric, beat-synced | `vibe-audio-videos` |
| Copy a reference edit shot for shot | lessons section 2 (reel-03 method) + `reanimate` for single animations |
| Not sure which kind | `vibe-editing-system` (entry point) |

## A beat needs something on screen besides him
| The moment | Tool | Notes |
|---|---|---|
| Explaining a why / how / history point | `vox-explainer` | torn paper, halftone, strips on twos; tested kit `example/` |
| A still photo (archive, his physique pic, Codex still, screenshot) | `photo-parallax` | 2.5D camera move, never a flat zoom; inside Vox cards via `parallax.js` |
| A story, metaphor or idea told as animation | `lemo-opuscar` | 99 film styles (watercolor, newsreel, chalkboard, pixel RPG...), Codex draws main characters |
| A dialogue skit, him plus a sidekick explaining | `voxel-reels` | blocky 3D characters, ElevenLabs voices, "Comment KEYWORD" end |
| Clay, crayon, paper-cut, doodle, mascot look | `vibe-stylised-animation` | no AI images |
| A number, stat, result, before / after | `animated-chart`, `milestone-reveal` | values stay exact |
| UI, app, data or kinetic type effect (button to player, chart morph, masked type...) | `motion-effects` | 16 effects |
| Cinematic opener or big title | `title-sequence-3d` | Three.js, neon signs in a rainy street etc. |
| Apple-style product moment, notch widgets | `apple-launch-film` | |
| Logo intro or outro | reel-05 recipe (`projects/reel-05/work/layers.py`, `scene.py`), `vibe-motion-graphics` | |
| Cover GIF, loop for a newsletter | `loop-cover`, `newsletter-promo` | |
| Comparing three AI outputs side by side | `model-showdown` | |
| Turn a reference reel's moves into a plan | `reference-to-motion`, `motion-brief-writer`, `motion-prompt-writer` | |
| Copy one animation he liked (title pop, transition, caption style) | `reanimate` | measured against the reference |
| Missing footage, any image at all (food, gym, props, backgrounds, clean plates) | Codex image generation | `codex exec ... "Generate an image: ..."`, reach for it first |
| A manga look around real photos | reel-12 kit `projects/reel-12/work/mg/` | real food and photos stay unfiltered |
| Retro game / 8-bit look | reel-11 pixel RPG layer + 8-bit music `projects/reel-11/scene.py`, `work/music.py` | |
| Gym B-roll to ask for or tag | `docs/library/cinematic-gym-shotlist.md` | 35 named shots |

## Effects on his real footage
| The moment | Tool |
|---|---|
| Cut-out, text behind him, background swap, glow or outline, disappear, slow-mo, split screen | `vibe-vfx` |
| Light-snap silhouette, rim light build, glowing outline, pixel-to-clear, burnt film | reel-03 `projects/reel-03/work/build/fx.py` |
| Mattes on hard backgrounds (floral sofa, hands, hair) | `projects/reel-02/work/refine_matte.py`, `projects/reel-03/work/matte/make_c07_alpha.py` |
| Snap pull-out, slow drifts, feeling-word overlays | reel-04 `projects/reel-04/work/build.py`, `overlays.py` |
| Meme template caption swap | reel-07 `projects/reel-07/work/` |
| Make a vertical version, upload-safe export | `reel-export` |

## Sound (every edit)
| Need | Tool |
|---|---|
| Real SFX on every cut and key moment | `tools/openverse_sfx.py` (first choice) |
| Music, extra SFX, voice, voice clean-up | ElevenLabs (`/v1/music`, `/v1/sound-generation`, TTS, `/v1/audio-isolation`) |
| Transcript with word timings | `tools/transcribe_elevenlabs.py` (never Whisper) |
| Original chiptune / code-made music | reel-11 `work/music.py` |

## Session tools
`session-handoff` (move to a new chat), `vibe-wrap-up` (end of session lessons), `brand-intake` (his brand files for
the motion pack), `tools/seek_render.mjs` (render any `window.seek` page), `tools/lemo.sh` (Lemo commands).
