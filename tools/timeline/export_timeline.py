"""Export a project's edit as one standard timeline file for the timeline editor page.

  python3 tools/timeline/export_timeline.py projects/<name> --version rough-v2 [--voice work/audio/full_iso.wav]

Reads (all paths inside the project):
  work/cut_plan.json   {"fps", "segments": [{"src_in", "src_out", "text", ...}]}  times in the joined source (required)
  work/parts.json      {"parts", "offsets", "length"}  how raw parts map onto source time (optional)
  work/words_full.json [{"w", "s", "e"}] word timings in source time (optional, words track)
  work/timeline_extra.json  extra tracks (optional), see SKILL.md:
       {"tracks": [{"id": "sfx", "label": "Sound effects", "items": [
           {"id": "s1", "label": "whoosh", "start": 12.4, "end": 13.1, "anchor": "edit" | "src", "detail": "..."}]}]}
     anchor "src": start/end are source times and move with the cuts; "edit" (default): edit times of this version.
  --voice  a mono WAV in source time; its envelope becomes the voice waveform (100 values a second).
Writes work/timeline/timeline.json. Media urls (preview render, live-cut proxy) are added by build_page.py.
"""
import argparse, base64, json, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("project"); ap.add_argument("--version", required=True)
ap.add_argument("--voice", default="work/audio/full_iso.wav")
ap.add_argument("--title", default=None)
a = ap.parse_args()
P = a.project.rstrip("/")
J = lambda p: json.load(open(os.path.join(P, p))) if os.path.exists(os.path.join(P, p)) else None

plan = J("work/cut_plan.json"); assert plan, "work/cut_plan.json missing"
fps = plan.get("fps", 30)
parts = J("work/parts.json")
src_len = parts["length"] if parts else max(g["src_out"] for g in plan["segments"])
sources = {"length": round(src_len, 4), "parts": []}
if parts:
    ends = parts["offsets"][1:] + [parts["length"]]
    for i, (p, o, e) in enumerate(zip(parts["parts"], parts["offsets"], ends)):
        sources["parts"].append({"label": f"Part {i + 1}", "file": os.path.basename(p), "start": o, "end": e})
else:
    sources["parts"].append({"label": "Source", "file": "", "start": 0, "end": src_len})

segs = [{"id": f"c{k + 1:02d}", "src_in": g["src_in"], "src_out": g["src_out"],
         "speed": g.get("speed", 1.0), "text": g.get("text", "")} for k, g in enumerate(plan["segments"])]
words = [{"w": w["w"], "s": w["s"], "e": w["e"]} for w in (J("work/words_full.json") or []) if w["w"].strip()]

peaks = None
vp = os.path.join(P, a.voice)
if os.path.exists(vp):
    import soundfile as sf
    x, sr = sf.read(vp)
    if x.ndim > 1: x = x.mean(1)
    h = sr // 100; n = len(x) // h
    rms = np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1))
    db = 20 * np.log10(rms + 1e-9)
    v = np.clip((db + 60) / 60, 0, 1)          # -60 dB .. 0 dB -> 0..1
    peaks = {"rate": 100, "data": base64.b64encode((v * 255).astype(np.uint8).tobytes()).decode()}

extra = J("work/timeline_extra.json") or {"tracks": []}
out = {"project": a.title or os.path.basename(P), "version": a.version, "fps": fps,
       "size": [1080, 1920], "sources": sources, "segments": segs, "words": words, "peaks": peaks,
       "tracks": extra.get("tracks", []), "media": {"preview": None, "proxy": None}}
os.makedirs(os.path.join(P, "work/timeline"), exist_ok=True)
json.dump(out, open(os.path.join(P, "work/timeline/timeline.json"), "w"), indent=0, ensure_ascii=False)
print("segments", len(segs), "words", len(words), "peaks", bool(peaks), "tracks", len(out["tracks"]))
