#!/bin/bash
# One-file delivery under 30 MiB: HEVC 2-pass, 3.5 Mbps video, AAC 256k, keyframe every second.
# Picture straight from the 3 original parts with clean 60 fps timestamps (the parts' seams have odd
# timestamps; encoding from the copied master dropped frames at the seams and the last 0.5 s).
cd /home/user/vibe_editing/projects/reel-06
IN="-f concat -safe 0 -i raw/parts.txt"
V="-vf setpts=N/(60*TB) -fps_mode passthrough -c:v libx265 -preset medium -b:v 3500k -pix_fmt yuv420p -tag:v hvc1 -color_primaries bt709 -color_trc bt709 -colorspace bt709"
X="keyint=60:min-keyint=60:scenecut=0:stats=work/x265.log:log-level=error"
ffmpeg -v error -y $IN -map 0:v $V -x265-params $X:pass=1 -an -f null /dev/null
ffmpeg -v error -y $IN -i work/audio/mix_bb.wav -map 0:v -map 1:a $V -x265-params $X:pass=2 -c:a aac -b:a 256k -movflags +faststart out/reel-06-final.mp4
ls -la out/reel-06-final.mp4
