# Vibe editing project

Video editing with the Vibe Editing System skills in `.claude/skills/` (start with `vibe-talking-head` for talking-head footage).

## Rules
- **Transcription:** never use Whisper or the skill's `vibe/transcribe.py`. Use ElevenLabs Scribe instead:
  `python3 tools/transcribe_elevenlabs.py raw/take1.mp4 -o work/words.json`
  It writes the same `words.json`, `segments.json` and `transcript.txt` the skill expects. The API key is injected
  by the environment's network secret, so never ask the user for it.
- **Rendering with HyperFrames:** `HYPERFRAMES_BROWSER_PATH` is set by the session start hook
  (`/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`). CLI: `npx hyperframes@0.8.150`.
- **Setup:** `.claude/hooks/session-start.sh` installs the Python packages and system libraries each new session.
  Heavy extras (rembg for cutouts, kokoro-onnx for AI voice) are installed only when a brief needs them.
- The user wants plain, human language and never uses em dashes. Keep that style in messages and on-screen text.
