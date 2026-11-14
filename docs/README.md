# Docs index

Every doc in this folder, with when to read it. Start here. When you add a doc, put it in the right folder and add
one line below. Don't nest deeper than these three folders.

## system/ : the Ideabro guides (bought, never edit)
| File | Read it when |
|---|---|
| `system/vibe-editing-system-reference.md` | Part 1. Tools, eyes and ears, filming, effects. Look things up during any edit. |
| `system/vibe-editing-workflow.md` | Part 2. Step-by-step workflow and the editing brief. Read before every new video. |

## playbook/ : the user's own knowledge (grows every video)
| File | Read it when |
|---|---|
| `playbook/lessons-learned.md` | Every video, in full, at the start and again before stills. Taste, recipes, mistakes. |

## library/ : outside references the user shared (read when the video needs them)
| File | Read it when |
|---|---|
| `library/cinematic-gym-shotlist.md` | Gym or physique video: asking for B-roll, planning a shoot, tagging gym clips. |

## Elsewhere
- `CLAUDE.md` (repo root): the rules. Always loaded.
- `.claude/skills/<type>/`: one playbook per video type, with its own `reference/` files (they ship with the skill pack).
- `.claude/skills/vibe-mini-vlog/`: the user's own skill for mini vlogs (camcorder overlay pack, reference reel breakdown).
- `.claude/skills/lemo-opuscar/`: animated explainers and short films in the Lemo-Opuscar library's 99 code-made styles
  (library cloned to `~/lemo-opuscar` each session, run through `tools/lemo.sh`), with this repo's house rules on top.
- `.claude/skills/voxel-reels/`: blocky 3D cartoon dialogue reels in code (Three.js kit, ElevenLabs voices with word
  timings, captions, cards, CTA), adapted from @heyalok.ai's guide; renders through the lemo-opuscar tools.
- `.claude/skills/vibe-wrap-up/`: run at the end of every session (`/vibe-wrap-up`): reviews the session, explains what was
  learned and writes it into `playbook/lessons-learned.md` and `CLAUDE.md` for all future sessions.
- `projects/<reel>/`: each video's brief, RENDER.md and code. The lessons file points to reusable recipes there.
