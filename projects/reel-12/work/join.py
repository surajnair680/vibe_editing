"""Join the 4 phone parts into one continuous source (lines run across the seams).
Picture: work/full.mp4 (stream copy, all parts are 60 fps CFR, 2340+1860+1920+546 frames = 111.1 s).
Sound: work/audio/full.wav, each part decoded from its start, placed at its audio start_time, padded or trimmed
to its picture length, so audio and picture stay locked across every seam.
Part offsets in the joined timeline: p1 0, p2 39.0, p3 70.0, p4 102.0."""
import json, subprocess
import numpy as np, soundfile as sf
SR = 48000
parts = [f"raw/ghar_ka_khaana_p{i}.mp4" for i in range(1, 5)]
out, offs, t = [], [], 0.0
for p in parts:
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,start_time",
                                      "-of", "json", p], capture_output=True, text=True).stdout)["streams"]
    v = next(s for s in info if s["codec_type"] == "video"); a = next(s for s in info if s["codec_type"] == "audio")
    vd, ast = float(v["duration"]), float(a["start_time"])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    x = np.concatenate([np.zeros(int(round(ast * SR)), np.float32), x])
    n = int(round(vd * SR)); x = np.pad(x, (0, max(0, n - len(x))))[:n]
    out.append(x); offs.append(round(t, 4)); t += vd
sf.write("work/audio/full.wav", np.concatenate(out), SR, subtype="FLOAT")
with open("work/cut/join.txt", "w") as fh:
    fh.writelines(f"file '../../{p}'\n" for p in parts)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "work/cut/join.txt", "-an", "-c", "copy",
                "work/full.mp4"], check=True)
print("offsets", offs, "total", round(t, 3))
