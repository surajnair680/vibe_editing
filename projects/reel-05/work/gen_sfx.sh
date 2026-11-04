#!/bin/bash
# reel-05 sound effects (ElevenLabs, one request at a time; skips files that exist)
cd "$(dirname "$0")/.."
G="python3 work/el_gen.py sfx"
$G "superbike sport motorcycle engine high revving fast pass by, aggressive throttle, close up, no music" 2.5 assets/sfx/bike_pass.mp3
$G "sports car V8 engine roar accelerating fast pass by, deep exhaust growl, close up, no music" 2.5 assets/sfx/car_pass.mp3
$G "deep cinematic impact hit with short metallic clank and soft low boom tail, logo reveal" 1.5 assets/sfx/impact.mp3
$G "soft airy cinematic swell rising, warm sunrise atmosphere, gentle, no music" 1.5 assets/sfx/swell.mp3
$G "quick sharp whoosh and shimmering metallic sparkle for logo text reveal" 1.2 assets/sfx/text_shimmer.mp3
