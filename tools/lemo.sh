#!/bin/sh
# Run a Lemo-Opuscar library command from the library root, with this container's fixes:
#   - ffmpeg 9 from imageio-ffmpeg first on PATH (the system ffmpeg is 6.1; the library needs 7+ for loudnorm)
#   - PLAYWRIGHT_CHROME = the preinstalled headless shell in /opt/pw-browsers (never npx playwright install)
#   - LIB exported (default ~/lemo-opuscar)
# Usage: sh tools/lemo.sh node core/render/still.mjs "/abs/path/projects/reel-08" 0 2.5 --size 1080x1920
# Pass project paths as absolute paths: the command runs from $LIB.
set -e
LIB=${LIB:-$HOME/lemo-opuscar}
[ -f "$LIB/AGENTS.md" ] || { echo "✗ no library at $LIB: run sh .claude/skills/lemo-opuscar/scripts/setup.sh"; exit 1; }
BIN=$HOME/.local/lemo-bin
if [ ! -x "$BIN/ffmpeg" ]; then
  mkdir -p "$BIN"
  ff=$(python3 -c 'import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())')
  ln -sf "$ff" "$BIN/ffmpeg"
  ln -sf "$(command -v ffprobe)" "$BIN/ffprobe"
fi
if [ -z "$PLAYWRIGHT_CHROME" ]; then
  shell=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | sort -V | tail -1)
  [ -n "$shell" ] && export PLAYWRIGHT_CHROME="$shell"
fi
export LIB PATH="$BIN:$PATH"
cd "$LIB"
exec "$@"
