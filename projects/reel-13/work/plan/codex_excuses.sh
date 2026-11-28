#!/bin/sh
# Codex renders for scene 5 (reel-13). Run from projects/reel-13/assets/codex.
STYLE="Square 1:1 image. One single glossy 3D object, centred, floating on a pure black background (#050505), no floor, no text, no logos, no watermark. Studio product render look: glossy dark materials, strong red rim light (#E3262C) from behind, soft white key light, subtle red glow around the object, crisp edges, lots of empty black around it so it can be cut out. Premium, dark, cinematic, like a 3D icon in a high end tech explainer."
codex exec --skip-git-repo-check --sandbox workspace-write "Generate an image: A DNA double helix strand, made of glossy glass-like white and dark segments, the lower half turning red and cracking apart with small broken shards. $STYLE Save it here as excuse_genetics.png"
codex exec --skip-git-repo-check --sandbox workspace-write "Generate an image: A classic round analog wall clock in glossy black metal with a white face, the hands motion-blurred as if spinning very fast. $STYLE Save it here as excuse_time.png"
codex exec --skip-git-repo-check --sandbox workspace-write "Generate an image: A medical syringe with a needle, glossy clear plastic barrel with red liquid inside, lying diagonally, with a big glossy red 3D question mark floating beside it. $STYLE Save it here as excuse_natural.png"
ls -la
