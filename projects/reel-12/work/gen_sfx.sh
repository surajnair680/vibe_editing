#!/bin/bash
# reel-12 sound effects, ElevenLabs sound generation, one request at a time (paid: committed in assets/el/)
set -e
g() { python3 work/el_gen.py sfx "$1" "$2" "$3"; }
g ink_swish 0.6 "a single soft quick brush stroke swish on paper, dry, close, short"
g hit 0.7 "a single punchy comic book hit, short thump with a small snap, dry, no reverb"
g stamp 0.8 "a heavy rubber stamp slammed once on a wooden desk, single thud, dry, close"
g tick 0.5 "a single quick pen tick mark scratched on paper, short, dry"
g lockon 0.8 "a short electronic target lock-on sound, two quick clean beeps"
g shimmer 1.2 "a soft gentle sparkle shimmer, light glassy chimes, short"
g swell 1.6 "a short soft rising whoosh swell that builds and stops abruptly"
g whoosh 0.6 "a quick soft air whoosh passing by, short"
g drip 0.6 "a single cartoon water drop, plip, short"
g pop 0.5 "a single cartoon bubble pop, short and playful"
g boom 1.6 "a big deep cinematic boom impact with a short tail"
g riser 3.5 "a tense rising tension riser that builds louder and stops abruptly"
