#!/bin/bash
# Build the meme: black 1080x1920 canvas, template video band (y 410..870 of 720x1280, cropped 24 px left and 10 px top/bottom = 4.6% zoom to hide the channel mark) scaled to 1080x692 at y 615,
# new caption on top, logo dropped, template audio copied untouched.
# usage: work/build.sh out/reel-07-v1.mp4 [extra ffmpeg output args]
cd "$(dirname "$0")/.."
OUT=${1:-out/reel-07-v1.mp4}; shift
ffmpeg -v error -y -i raw/template.mp4 -i work/caption.png -filter_complex \
 "color=black:s=1080x1920:r=60,format=yuv420p[bg];
  [0:v]crop=688:440:24:420,scale=1080:692:flags=lanczos[band];
  [bg][band]overlay=0:615:shortest=1[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]" \
 -map "[v]" -map 0:a -c:v libx264 -crf 16 -preset slow -g 60 -c:a copy -movflags +faststart "$@" "$OUT"
