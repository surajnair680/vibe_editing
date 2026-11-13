#!/bin/bash
# Installs what the Vibe Editing System skill needs in a fresh cloud session.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# System libraries the skia graphics engine needs, plus libGLESv2 for MediaPipe (person masks for cut-outs)
if ! ldconfig -p | grep -q 'libEGL.so.1' || ! ldconfig -p | grep -q 'libGLESv2.so.2'; then
  apt-get install -y -q libegl1 libgl1 libgles2 >/dev/null 2>&1 \
    || { apt-get update -q >/dev/null 2>&1 && apt-get install -y -q libegl1 libgl1 libgles2 >/dev/null 2>&1; }
fi

# Python packages (faster-whisper skipped: transcription goes through ElevenLabs)
if ! python3 -c "import scipy, imageio_ffmpeg, skia, soundfile, cv2" >/dev/null 2>&1; then
  python3 -m pip install -q --root-user-action=ignore \
    scipy imageio-ffmpeg skia-python soundfile opencv-python-headless
fi

# Cut-out tools (rembg + MediaPipe + their models) in the background, so the session starts at once.
# Done when ~/.cache/vibe/extras.ok exists; log in /tmp/vibe-extras.log.
VIBE_CACHE="$HOME/.cache/vibe"
if [ ! -f "$VIBE_CACHE/extras.ok" ]; then
  mkdir -p "$VIBE_CACHE"
  nohup bash -c '
    set -e
    python3 -c "import rembg, onnxruntime, mediapipe" >/dev/null 2>&1 \
      || python3 -m pip install -q --root-user-action=ignore rembg onnxruntime mediapipe
    [ -s "$0/selfie_multiclass.tflite" ] || curl -sSfL -o "$0/selfie_multiclass.tflite" \
      https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite
    python3 -c "from rembg import new_session; new_session(\"u2net_human_seg\")"
    touch "$0/extras.ok"
  ' "$VIBE_CACHE" > /tmp/vibe-extras.log 2>&1 &
fi

# Lemo-Opuscar film style library (skill lemo-opuscar) in the background: clone to ~/lemo-opuscar, core packages.
# Done when ~/.cache/vibe/lemo.ok exists; log in /tmp/lemo-setup.log.
if [ ! -f "$VIBE_CACHE/lemo.ok" ]; then
  LEMO_SETUP="$(cd "$(dirname "$0")/.." && pwd)/skills/lemo-opuscar/scripts/setup.sh"
  nohup bash -c '
    set -e
    BIN=$HOME/.local/lemo-bin; mkdir -p "$BIN"
    ln -sf "$(python3 -c "import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())")" "$BIN/ffmpeg"
    ln -sf "$(command -v ffprobe)" "$BIN/ffprobe"
    export PATH="$BIN:$PATH"
    cd "$HOME"
    sh "$0"
    sh "$0" deps
    touch "$1/lemo.ok"
  ' "$LEMO_SETUP" "$VIBE_CACHE" > /tmp/lemo-setup.log 2>&1 &
fi

# OpenAI Codex CLI in the background (sign-in is per session: codex login --device-auth). Log in /tmp/codex-install.log.
if ! command -v codex >/dev/null 2>&1; then
  nohup npm install -g @openai/codex > /tmp/codex-install.log 2>&1 &
fi
echo "Reminder (user rule): in your reply to the user's first message, start the Codex device sign-in and give them the link and code. See the OpenAI Codex CLI rule in CLAUDE.md."

# Renderer path for HyperFrames
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  # newest preinstalled headless shell (the folder name changes with the image: -1194/chrome-linux/headless_shell, later
  # -1243/chrome-headless-shell-linux64/chrome-headless-shell)
  HF=$(ls -d /opt/pw-browsers/chromium_headless_shell-*/chrome-*/*headless*shell 2>/dev/null | grep -v '\.' | sort -V | tail -1)
  if [ -n "$HF" ]; then echo "export HYPERFRAMES_BROWSER_PATH=$HF" >> "$CLAUDE_ENV_FILE"; fi
fi
