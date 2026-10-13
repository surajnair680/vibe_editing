#!/bin/bash
# Installs what the Vibe Editing System skill needs in a fresh cloud session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# System libraries the skia graphics engine needs
if ! ldconfig -p | grep -q 'libEGL.so.1'; then
  apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1 \
    || { apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 >/dev/null 2>&1; }
fi

# Python packages (faster-whisper skipped: transcription goes through ElevenLabs)
if ! python3 -c "import scipy, imageio_ffmpeg, skia, soundfile, cv2" >/dev/null 2>&1; then
  python3 -m pip install -q --root-user-action=ignore \
    scipy imageio-ffmpeg skia-python soundfile opencv-python-headless
fi

# Renderer path for HyperFrames
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' >> "$CLAUDE_ENV_FILE"
fi
