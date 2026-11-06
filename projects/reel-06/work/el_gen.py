"""ElevenLabs music / SFX generation, one request at a time, with 429 back-off.

python3 work/el_gen.py music  "<prompt>" 36000 assets/music/m1.mp3
python3 work/el_gen.py sfx    "<prompt>" 2.5   assets/sfx/riser.mp3
The API key is injected by the environment proxy (dummy header is replaced).
Never regenerates a file that already exists (paid audio).
"""
import json, os, sys, time, urllib.request, urllib.error

kind, prompt, length, out = sys.argv[1:5]
instrumental = (sys.argv[5] != "vocals") if len(sys.argv) > 5 else True
if os.path.exists(out):
    print("exists, skipping:", out); sys.exit(0)
os.makedirs(os.path.dirname(out), exist_ok=True)
if kind == "music":
    url = "https://api.elevenlabs.io/v1/music"
    body = {"prompt": prompt, "music_length_ms": int(length), "force_instrumental": instrumental}
else:
    url = "https://api.elevenlabs.io/v1/sound-generation"
    body = {"text": prompt, "duration_seconds": float(length), "prompt_influence": 0.5}
data = json.dumps(body).encode()
for wait in [0, 5, 10, 20, 40]:
    time.sleep(wait)
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json", "xi-api-key": "dummy", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            audio = r.read()
        open(out, "wb").write(audio)
        print("saved", out, len(audio), "bytes"); sys.exit(0)
    except urllib.error.HTTPError as e:
        msg = e.read()[:300]
        print("HTTP", e.code, msg)
        if e.code != 429:
            sys.exit(1)
sys.exit(1)
