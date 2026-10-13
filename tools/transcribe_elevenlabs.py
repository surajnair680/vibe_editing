"""transcribe_elevenlabs: speech -> word-level timestamps with ElevenLabs Scribe.

Drop-in replacement for the skill's vibe/transcribe.py. Writes the same files:
    words.json       [{"w": "Hello", "s": 0.12, "e": 0.40, "p": 0.98}, ...]   seconds
    segments.json    sentence-level segments
    transcript.txt   readable transcript with timestamps

    python3 tools/transcribe_elevenlabs.py raw/take1.mp4 -o work/words.json
    python3 tools/transcribe_elevenlabs.py raw/take1.mp4 --lang en

The xi-api-key header is added by the environment's network secret, so no key is needed here.
"""

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

API = "https://api.elevenlabs.io/v1/speech-to-text"


def fmt_time(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("-o", "--out", default="work/words.json")
    ap.add_argument("--lang", default=None, help="ISO code like en, hi (auto-detect if omitted)")
    ap.add_argument("--model", default="scribe_v1")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / "audio.mp3"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.media,
                        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", str(audio)], check=True)
        cmd = ["curl", "-sS", "--fail-with-body", "-X", "POST", API,
               "-F", f"model_id={a.model}", "-F", "timestamps_granularity=word",
               "-F", "tag_audio_events=false", "-F", f"file=@{audio}"]
        if a.lang:
            cmd += ["-F", f"language_code={a.lang}"]
        print("sending audio to ElevenLabs Scribe ...")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Scribe request failed: {r.stdout or r.stderr}")
        data = json.loads(r.stdout)

    words = [{"w": w["text"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3),
              "p": round(math.exp(w.get("logprob", 0.0)), 3)}
             for w in data.get("words", []) if w.get("type") == "word" and w["text"].strip()]

    # Sentence segments: split on end punctuation or a gap longer than 0.8 s
    segs, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if nxt is None or w["w"][-1:] in ".?!" or nxt["s"] - w["e"] > 0.8:
            segs.append({"s": cur[0]["s"], "e": cur[-1]["e"], "text": " ".join(x["w"] for x in cur)})
            cur = []
    lines = [f"[{fmt_time(s['s'])} - {fmt_time(s['e'])}] {s['text']}" for s in segs]

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(words, indent=0))
    (out.parent / "segments.json").write_text(json.dumps(segs, indent=1))
    (out.parent / "transcript.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nlanguage: {data.get('language_code')}  {len(words)} words -> {out}")
    low = [w for w in words if w["p"] < 0.5]
    if low:
        print(f"{len(low)} low-confidence words (check spelling):",
              ", ".join(f"{w['w']}@{w['s']:.1f}s" for w in low[:20]))


if __name__ == "__main__":
    main()
