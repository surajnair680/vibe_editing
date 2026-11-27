"""ElevenLabs music / SFX generation with 429 back-off (one request at a time; shared account, max 2 concurrent).
Paid audio is committed under assets/el/ and never regenerated if the file exists.
Usage: python3 work/el_gen.py music <name> <seconds> "<prompt>"
       python3 work/el_gen.py sfx <name> <seconds> "<prompt>"
"""
import os, sys, time, json, requests
kind, name, sec, prompt = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
out = f"assets/el/{name}.mp3"
if os.path.exists(out) and os.path.getsize(out) > 1000:
    print("exists", out); sys.exit(0)
url = "https://api.elevenlabs.io/v1/music" if kind == "music" else "https://api.elevenlabs.io/v1/sound-generation"
body = {"prompt": prompt, "music_length_ms": int(sec * 1000)} if kind == "music" else \
       {"text": prompt, "duration_seconds": sec, "prompt_influence": 0.5}
for wait in (0, 5, 10, 20, 40):
    time.sleep(wait)
    r = requests.post(url, json=body, headers={"xi-api-key": "dummy"}, timeout=600)
    if r.status_code == 200:
        open(out, "wb").write(r.content); print("ok", out, len(r.content)); break
    print(r.status_code, r.text[:200])
    if r.status_code != 429:
        break
with open("assets/el/prompts.json", "a") as fh:
    fh.write(json.dumps({"kind": kind, "name": name, "sec": sec, "prompt": prompt}) + "\n")
