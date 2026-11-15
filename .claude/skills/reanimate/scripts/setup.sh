#!/usr/bin/env bash
# Installs the script dependencies once (bun) and checks that Chromium and ffmpeg are usable.
# Safe to re-run; it is a no-op when everything is already in place.
# Vibe editing patch: uses the container's preinstalled Chromium (/opt/pw-browsers/chromium) through
# lib.ts chromiumExecutable(); never runs "playwright install" (cloud rule in CLAUDE.md).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
if ! command -v bun >/dev/null; then echo "bun is required (https://bun.sh)"; exit 1; fi
if [ ! -d node_modules/playwright ] || [ ! -x node_modules/ffmpeg-static/ffmpeg ]; then
  bun install --silent
fi
bun -e 'const {chromium}=await import("playwright"); const {chromiumExecutable}=await import("./lib.ts"); const b=await chromium.launch({executablePath: chromiumExecutable()}); console.log("chromium ok", b.version()); await b.close()'
node_modules/ffmpeg-static/ffmpeg -hide_banner -version | head -1
echo "ready: $HERE"
